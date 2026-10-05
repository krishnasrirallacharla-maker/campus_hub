from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_admin
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.token import PasswordResetRequest
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users Management (Admin)"])


@router.get(
    "",
    response_model=List[UserResponse],
    summary="List users with filtering (Admin only)",
)
def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    search: Optional[str] = Query(None, description="Search by name, email, or roll number"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return UserService.list_users(
        db,
        role=role,
        department_id=department_id,
        search=search,
        is_active=is_active,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Admin only)",
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return UserService.create_user(db, user_data)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user details by ID (Admin only)",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return UserService.get_by_id(db, user_id)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user details (Admin only)",
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return UserService.update_user(db, user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user (Admin only)",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    UserService.delete_user(db, user_id)
    return {"message": "User deleted successfully"}


@router.post(
    "/{user_id}/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset a user's password (Admin only)",
)
def reset_user_password(
    user_id: int,
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    UserService.reset_password(db, user_id, data.new_password)
    return {"message": "User password reset successfully"}
