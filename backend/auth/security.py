"""
Security, Cryptography & Token Utilities for Raahi Authentication.
Uses standard salted bcrypt (12 rounds) and HS256 JWT with secure defaults.
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
import jwt

# Secure 64-character default key meets RFC 7518 HMAC-SHA256 requirements
DEFAULT_JWT_SECRET = "raahi_mission_bharat_transit_jwt_secret_key_2026_dev_p05_ultra_secure"
JWT_SECRET = os.getenv("JWT_SECRET", DEFAULT_JWT_SECRET)
JWT_ALGORITHM = "HS256"

# Session expiration policies
DEFAULT_SESSION_HOURS = 24
REMEMBER_ME_DAYS = 7


def hash_password(plain_password: str) -> str:
    """Hash password using bcrypt with 12 salt rounds."""
    if not plain_password:
        raise ValueError("Password cannot be empty")
    # Apply reasonable length check (max 128 characters to prevent bcrypt DoS)
    if len(plain_password) > 128:
        raise ValueError("Password exceeds maximum allowed length of 128 characters")
    
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    data: Dict[str, Any],
    remember_me: bool = False,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Issue a cryptographically signed JWT access token."""
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now_utc + expires_delta
    elif remember_me:
        expire = now_utc + timedelta(days=REMEMBER_ME_DAYS)
    else:
        expire = now_utc + timedelta(hours=DEFAULT_SESSION_HOURS)
        
    to_encode.update({
        "iat": now_utc,
        "exp": expire,
        "iss": "raahi-transit-platform"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and cryptographically verify a JWT access token."""
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            issuer="raahi-transit-platform"
        )
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def generate_secure_token() -> str:
    """Generate a high-entropy URL-safe random token for password resets or verification."""
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    """Store only cryptographic SHA-256 hash of tokens in database to prevent exposure."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

