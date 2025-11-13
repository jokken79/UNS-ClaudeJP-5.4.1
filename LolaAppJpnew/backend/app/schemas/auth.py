"""
Authentication schemas for login, registration, and token management
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.models import UserRole


class LoginRequest(BaseModel):
    """Login request with username/password"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefreshRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserCreate(BaseModel):
    """Create new user"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: UserRole = UserRole.HAKEN_SHAIN
    employee_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Update existing user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response (public info)"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    employee_id: Optional[int]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str = Field(..., min_length=6)
