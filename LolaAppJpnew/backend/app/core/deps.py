"""
Dependency injection for FastAPI endpoints
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.models import User, UserRole


# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session

    Returns:
        User object of authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    """
    Dependency to check user role authorization

    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: User = Depends(RoleChecker([UserRole.ADMIN]))):
            return {"message": "Admin access granted"}
    """

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        """
        Verify user has required role

        Role hierarchy (descending):
        ADMIN > TORISHIMARIYAKU > KEIRI > TANTOSHA > HAKEN_SHAIN > UKEOI

        ADMIN can access everything.
        """
        # ADMIN has access to everything
        if user.role == UserRole.ADMIN:
            return user

        # Check if user role is in allowed roles
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in self.allowed_roles]}",
            )

        return user


# Pre-defined role checkers
require_admin = RoleChecker([UserRole.ADMIN])
require_torishimariyaku = RoleChecker([UserRole.ADMIN, UserRole.TORISHIMARIYAKU])
require_keiri = RoleChecker([UserRole.ADMIN, UserRole.TORISHIMARIYAKU, UserRole.KEIRI])
require_tantosha = RoleChecker([UserRole.ADMIN, UserRole.TORISHIMARIYAKU, UserRole.KEIRI, UserRole.TANTOSHA])
