from typing import List, Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from app.database import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.models.enums import UserRole
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_token_from_header(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[str]:
    """Extract Bearer token from Authorization header."""
    if not auth:
        return None
    return auth.credentials


def get_current_user(
    token: Optional[str] = Depends(get_token_from_header),
    db: Session = Depends(get_db),
) -> User:
    """Validate access token and return the current user."""
    if not token:
        raise UnauthorizedException("Authentication token is required")

    try:
        payload = decode_access_token(token)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException("Invalid authentication credentials")
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise UnauthorizedException("Invalid or expired authentication token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedException("User no longer exists")
    if not user.is_active:
        raise ForbiddenException("User account is inactive or disabled")

    return user


def get_optional_current_user(
    token: Optional[str] = Depends(get_token_from_header),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Validate token if provided, otherwise return None."""
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_id = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.is_active:
            return user
        return None
    except Exception:
        return None


def require_roles(allowed_roles: List[UserRole]):
    """Role-based access control dependency factory."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            role_names = ", ".join([r.value for r in allowed_roles])
            raise ForbiddenException(
                f"Access denied. Required role(s): [{role_names}], but you have role '{current_user.role.value}'"
            )
        return current_user

    return role_checker


# Convenient role dependencies
get_current_admin = require_roles([UserRole.ADMIN])
get_current_faculty = require_roles([UserRole.FACULTY])
get_current_student = require_roles([UserRole.STUDENT])
get_current_faculty_or_admin = require_roles([UserRole.ADMIN, UserRole.FACULTY])
