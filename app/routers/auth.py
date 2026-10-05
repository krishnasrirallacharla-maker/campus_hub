from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.token import LoginRequest, PasswordChangeRequest, Token
from app.schemas.user import StudentRegister, UserProfileUpdate, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=Token,
    summary="Login user and obtain JWT token",
    description="Authenticates Admin, Faculty, or Student with email and password.",
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.authenticate_user(db, login_data)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def register_student(reg_data: StudentRegister, db: Session = Depends(get_db)):
    return AuthService.register_student(db, reg_data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current logged-in user profile",
)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current logged-in user profile",
)
def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService.update_profile(db, current_user, profile_data)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change own password",
)
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService.change_password(db, current_user, data)
    return {"message": "Password changed successfully"}
