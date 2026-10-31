"""
Pydantic Request & Response Schemas for Raahi Authentication.
Provides strict validation, email normalization, and password policy enforcement.
"""
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, description="Full Name of the commuter")
    email: str = Field(..., description="Valid commuter email address")
    password: str = Field(..., min_length=8, max_length=128, description="Strong account password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return cleaned

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not EMAIL_REGEX.match(cleaned):
            raise ValueError("Please provide a valid email address (e.g., commuter@raahi.in)")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError("Password must contain at least one letter and one number")
        return v

    @model_validator(mode="after")
    def verify_password_match(self) -> "SignUpRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match. Please re-enter identical passwords.")
        return self


class SignInRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, max_length=128, description="Account password")
    remember_me: bool = Field(default=True, description="Keep session active for 7 days")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str = "commuter"
    avatar_url: Optional[str] = None
    email_verified: bool = True
    status: str = "active"
    created_at: datetime
    last_login_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    token_type: str = "bearer"
    message: str = "Authentication successful"


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Registered account email")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=10, description="Password reset verification token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New strong password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError("Password must contain at least one letter and one number")
        return v

    @model_validator(mode="after")
    def verify_password_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match. Please confirm identically.")
        return self


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def verify_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("New passwords do not match")
        return self

