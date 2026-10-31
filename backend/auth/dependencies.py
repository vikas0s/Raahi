"""
FastAPI Dependencies for Authentication, Session Resolution & Rate Limiting.
Supports dual-mode credential extraction: Authorization Bearer header or HttpOnly Cookie.
"""
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .security import decode_access_token
from .repository import user_repository
from .schemas import UserResponse

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> UserResponse:
    """
    Resolve the authenticated commuter from:
    1. HTTP Bearer Authorization Header
    2. Secure 'raahi_session' HttpOnly Cookie
    """
    token: Optional[str] = None

    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif "raahi_session" in request.cookies:
        token = request.cookies.get("raahi_session")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to access this feature.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload["sub"]
    user_doc = await user_repository.get_by_id(user_id)
    if not user_doc or user_doc.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return UserResponse(
        id=user_doc["_id"],
        name=user_doc.get("name", "Commuter"),
        email=user_doc.get("email", ""),
        role=user_doc.get("role", "commuter"),
        avatar_url=user_doc.get("avatar_url"),
        email_verified=user_doc.get("email_verified", True),
        status=user_doc.get("status", "active"),
        created_at=user_doc.get("created_at"),
        last_login_at=user_doc.get("last_login_at")
    )


async def get_optional_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> Optional[UserResponse]:
    """
    Optionally resolve current commuter without raising 401 if unauthenticated.
    Allows public endpoints (e.g., search, planner) to enhance results when signed in.
    """
    try:
        return await get_current_user(request, auth_header)
    except HTTPException:
        return None


# ------------------------------------------------------------------------------
# In-Memory Rate Limiter (Brute-Force & Credential Stuffing Abuse Protection)
# ------------------------------------------------------------------------------
class SimpleRateLimiter:
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, list] = {}

    def check(self, request: Request, key_prefix: str = "auth") -> None:
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        key = f"{key_prefix}:{client_ip}"

        # Clean expired timestamps
        history = [ts for ts in self._history.get(key, []) if now - ts < self.window_seconds]
        if len(history) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Please wait {self.window_seconds} seconds before trying again."
            )

        history.append(now)
        self._history[key] = history


rate_limiter = SimpleRateLimiter(max_requests=20, window_seconds=60)

