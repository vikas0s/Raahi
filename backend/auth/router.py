"""
FastAPI Router for Raahi Authentication & User Identity Management.
Mounts /api/auth endpoints with dual-mode cookie/bearer tokens.
"""
import os
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends

from .schemas import (
    SignUpRequest,
    SignInRequest,
    UserResponse,
    AuthResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UpdateProfileRequest,
    ChangePasswordRequest
)
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_secure_token,
    hash_token,
    REMEMBER_ME_DAYS,
    DEFAULT_SESSION_HOURS
)
from .repository import user_repository
from .dependencies import get_current_user, rate_limiter

logger = logging.getLogger("raahi.auth.router")

auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])

IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"


def _set_auth_cookie(response: Response, token: str, remember_me: bool = True) -> None:
    """Set secure, HttpOnly session cookie."""
    max_age_seconds = REMEMBER_ME_DAYS * 86400 if remember_me else DEFAULT_SESSION_HOURS * 3600
    response.set_cookie(
        key="raahi_session",
        value=token,
        max_age=max_age_seconds,
        expires=max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=IS_PRODUCTION,
        path="/"
    )


def _clear_auth_cookie(response: Response) -> None:
    """Clear session cookie on logout."""
    response.delete_cookie(
        key="raahi_session",
        path="/",
        httponly=True,
        samesite="lax",
        secure=IS_PRODUCTION
    )


@auth_router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Raahi commuter account"
)
async def signup(req: SignUpRequest, request: Request, response: Response):
    rate_limiter.check(request, "signup")

    # Check if normalized email is already registered
    existing = await user_repository.get_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists. Please sign in instead."
        )

    # Hash password securely
    hashed_pwd = hash_password(req.password)

    # Persist in MongoDB
    user_doc = await user_repository.create_user(
        name=req.name,
        email=req.email,
        password_hash=hashed_pwd
    )

    user_resp = UserResponse(
        id=user_doc["_id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc.get("role", "commuter"),
        avatar_url=user_doc.get("avatar_url"),
        email_verified=user_doc.get("email_verified", True),
        status=user_doc.get("status", "active"),
        created_at=user_doc["created_at"],
        last_login_at=user_doc.get("last_login_at")
    )

    # Issue JWT token
    token = create_access_token(
        data={"sub": user_resp.id, "email": user_resp.email, "name": user_resp.name, "role": user_resp.role},
        remember_me=True
    )

    _set_auth_cookie(response, token, remember_me=True)

    return AuthResponse(
        user=user_resp,
        token=token,
        token_type="bearer",
        message="Account created successfully. Welcome to Raahi!"
    )


@auth_router.post(
    "/signin",
    response_model=AuthResponse,
    summary="Authenticate with email & password"
)
async def signin(req: SignInRequest, request: Request, response: Response):
    rate_limiter.check(request, "signin")

    user_doc = await user_repository.get_by_email(req.email)
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    # Verify password hash
    stored_hash = user_doc.get("password_hash", "")
    if not verify_password(req.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please verify your credentials."
        )

    if user_doc.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support."
        )

    # Update login timestamp
    await user_repository.update_last_login(user_doc["_id"])

    user_resp = UserResponse(
        id=user_doc["_id"],
        name=user_doc["name"],
        email=user_doc["email"],
        role=user_doc.get("role", "commuter"),
        avatar_url=user_doc.get("avatar_url"),
        email_verified=user_doc.get("email_verified", True),
        status=user_doc.get("status", "active"),
        created_at=user_doc["created_at"],
        last_login_at=user_doc.get("last_login_at")
    )

    token = create_access_token(
        data={"sub": user_resp.id, "email": user_resp.email, "name": user_resp.name, "role": user_resp.role},
        remember_me=req.remember_me
    )

    _set_auth_cookie(response, token, remember_me=req.remember_me)

    return AuthResponse(
        user=user_resp,
        token=token,
        token_type="bearer",
        message=f"Welcome back, {user_resp.name}!"
    )


@auth_router.post(
    "/logout",
    summary="Sign out and invalidate session cookie"
)
async def logout(response: Response):
    _clear_auth_cookie(response)
    return {"status": "logged_out", "message": "Successfully signed out of Raahi."}


@auth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated commuter profile"
)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@auth_router.post(
    "/forgot-password",
    summary="Initiate password reset process"
)
async def forgot_password(req: ForgotPasswordRequest, request: Request):
    rate_limiter.check(request, "forgot")
    
    user_doc = await user_repository.get_by_email(req.email)
    raw_token = None
    if user_doc:
        raw_token = generate_secure_token()
        token_hash = hash_token(raw_token)
        await user_repository.create_password_reset(user_doc["_id"], token_hash, expires_in_hours=1)
        logger.info(f"Password reset initiated for user {user_doc['_id']}")

    # Return safe generic response to avoid account enumeration
    res = {
        "status": "success",
        "message": "If an account with this email exists, a password reset link has been prepared."
    }
    # For local developer / demo convenience, provide the token in dev mode
    if not IS_PRODUCTION and raw_token:
        res["demo_reset_token"] = raw_token
        
    return res


@auth_router.post(
    "/reset-password",
    summary="Complete password reset with verification token"
)
async def reset_password(req: ResetPasswordRequest, request: Request):
    rate_limiter.check(request, "reset")

    token_hash = hash_token(req.token.strip())
    user_id = await user_repository.verify_and_consume_password_reset(token_hash)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The password reset link is invalid or has expired. Please request a new one."
        )

    new_hash = hash_password(req.new_password)
    updated = await user_repository.update_password(user_id, new_hash)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password. Please try again."
        )

    return {
        "status": "success",
        "message": "Your password has been successfully reset. You can now sign in."
    }


@auth_router.put(
    "/profile",
    response_model=UserResponse,
    summary="Update profile details"
)
async def update_profile(
    req: UpdateProfileRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    updates = {}
    if req.name is not None and len(req.name.strip()) >= 2:
        updates["name"] = req.name.strip()
    if req.avatar_url is not None:
        updates["avatar_url"] = req.avatar_url

    updated_doc = await user_repository.update_profile(current_user.id, updates)
    if not updated_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=updated_doc["_id"],
        name=updated_doc["name"],
        email=updated_doc["email"],
        role=updated_doc.get("role", "commuter"),
        avatar_url=updated_doc.get("avatar_url"),
        email_verified=updated_doc.get("email_verified", True),
        status=updated_doc.get("status", "active"),
        created_at=updated_doc["created_at"],
        last_login_at=updated_doc.get("last_login_at")
    )


@auth_router.post(
    "/change-password",
    summary="Change account password while authenticated"
)
async def change_password(
    req: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    user_doc = await user_repository.get_by_id(current_user.id)
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(req.current_password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Current password incorrect")

    new_hash = hash_password(req.new_password)
    await user_repository.update_password(current_user.id, new_hash)
    return {"status": "success", "message": "Password changed successfully"}

