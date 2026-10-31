"""
Raahi Authentication & Session Management Package.
Provides secure password hashing, JWT token issuance, HttpOnly cookie management,
and MongoDB-backed user session persistence.
"""
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_secure_token,
    hash_token
)
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
from .repository import UserRepository, user_repository
from .dependencies import (
    get_current_user,
    get_optional_current_user,
    rate_limiter
)
from .router import auth_router

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "generate_secure_token",
    "hash_token",
    "SignUpRequest",
    "SignInRequest",
    "UserResponse",
    "AuthResponse",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UpdateProfileRequest",
    "ChangePasswordRequest",
    "UserRepository",
    "user_repository",
    "get_current_user",
    "get_optional_current_user",
    "rate_limiter",
    "auth_router"
]

