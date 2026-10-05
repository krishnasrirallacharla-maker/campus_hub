from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.exceptions import AlreadyExistsException, BadRequestException, UnauthorizedException
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.token import LoginRequest, PasswordChangeRequest, Token
from app.schemas.user import StudentRegister


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, login_data: LoginRequest) -> Token:
        """Authenticate user by email and password, returning JWT token."""
        user = db.query(User).filter(User.email == login_data.email.lower().strip()).first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is inactive or deactivated")

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            email=user.email,
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            role=user.role,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
        )

    @staticmethod
    def register_student(db: Session, reg_data: StudentRegister) -> User:
        """Register a new student account."""
        email_clean = reg_data.email.lower().strip()
        existing_user = db.query(User).filter(User.email == email_clean).first()
        if existing_user:
            raise AlreadyExistsException("User", "email", email_clean)

        if reg_data.roll_number:
            existing_roll = db.query(User).filter(User.roll_number == reg_data.roll_number.strip()).first()
            if existing_roll:
                raise AlreadyExistsException("User", "roll_number", reg_data.roll_number)

        user = User(
            email=email_clean,
            hashed_password=get_password_hash(reg_data.password),
            full_name=reg_data.full_name.strip(),
            role=UserRole.STUDENT,
            department_id=reg_data.department_id,
            roll_number=reg_data.roll_number.strip() if reg_data.roll_number else None,
            phone=reg_data.phone.strip() if reg_data.phone else None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, data: PasswordChangeRequest) -> bool:
        """Change user's own password."""
        if not verify_password(data.current_password, user.hashed_password):
            raise BadRequestException("Current password does not match")

        if len(data.new_password) < 6:
            raise BadRequestException("New password must be at least 6 characters long")

        user.hashed_password = get_password_hash(data.new_password)
        db.commit()
        return True
