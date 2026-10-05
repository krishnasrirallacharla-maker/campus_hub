from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.security import get_password_hash
from app.core.exceptions import AlreadyExistsException, NotFoundException, BadRequestException
from app.models.enums import UserRole
from app.models.user import User
from app.models.department import Department
from app.schemas.user import UserCreate, UserProfileUpdate, UserUpdate


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User", user_id)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def list_users(
        db: Session,
        role: Optional[UserRole] = None,
        department_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        query = db.query(User)

        if role is not None:
            query = query.filter(User.role == role)
        if department_id is not None:
            query = query.filter(User.department_id == department_id)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.roll_number.ilike(search_pattern),
                )
            )

        return query.order_by(User.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_users(
        db: Session,
        role: Optional[UserRole] = None,
        department_id: Optional[int] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        query = db.query(User)
        if role is not None:
            query = query.filter(User.role == role)
        if department_id is not None:
            query = query.filter(User.department_id == department_id)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.roll_number.ilike(search_pattern),
                )
            )
        return query.count()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        email_clean = user_data.email.lower().strip()
        if db.query(User).filter(User.email == email_clean).first():
            raise AlreadyExistsException("User", "email", email_clean)

        if user_data.roll_number:
            if db.query(User).filter(User.roll_number == user_data.roll_number.strip()).first():
                raise AlreadyExistsException("User", "roll_number", user_data.roll_number)

        if user_data.department_id:
            dept = db.query(Department).filter(Department.id == user_data.department_id).first()
            if not dept:
                raise NotFoundException("Department", user_data.department_id)

        user = User(
            email=email_clean,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name.strip(),
            role=user_data.role,
            department_id=user_data.department_id,
            roll_number=user_data.roll_number.strip() if user_data.roll_number else None,
            phone=user_data.phone.strip() if user_data.phone else None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        user = UserService.get_by_id(db, user_id)

        if user_data.email and user_data.email.lower().strip() != user.email:
            email_clean = user_data.email.lower().strip()
            if db.query(User).filter(User.email == email_clean, User.id != user_id).first():
                raise AlreadyExistsException("User", "email", email_clean)
            user.email = email_clean

        if user_data.roll_number is not None:
            if user_data.roll_number and user_data.roll_number.strip() != user.roll_number:
                if db.query(User).filter(User.roll_number == user_data.roll_number.strip(), User.id != user_id).first():
                    raise AlreadyExistsException("User", "roll_number", user_data.roll_number)
            user.roll_number = user_data.roll_number.strip() if user_data.roll_number else None

        if user_data.department_id is not None:
            if user_data.department_id:
                dept = db.query(Department).filter(Department.id == user_data.department_id).first()
                if not dept:
                    raise NotFoundException("Department", user_data.department_id)
            user.department_id = user_data.department_id

        if user_data.full_name is not None:
            user.full_name = user_data.full_name.strip()
        if user_data.role is not None:
            user.role = user_data.role
        if user_data.phone is not None:
            user.phone = user_data.phone.strip() if user_data.phone else None
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_profile(db: Session, user: User, profile_data: UserProfileUpdate) -> User:
        if profile_data.full_name is not None:
            user.full_name = profile_data.full_name.strip()
        if profile_data.phone is not None:
            user.phone = profile_data.phone.strip() if profile_data.phone else None
        if profile_data.roll_number is not None and user.role == UserRole.STUDENT:
            if profile_data.roll_number and profile_data.roll_number.strip() != user.roll_number:
                if db.query(User).filter(User.roll_number == profile_data.roll_number.strip(), User.id != user.id).first():
                    raise AlreadyExistsException("User", "roll_number", profile_data.roll_number)
            user.roll_number = profile_data.roll_number.strip() if profile_data.roll_number else None
        if profile_data.department_id is not None:
            if profile_data.department_id:
                dept = db.query(Department).filter(Department.id == profile_data.department_id).first()
                if not dept:
                    raise NotFoundException("Department", profile_data.department_id)
            user.department_id = profile_data.department_id

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_by_id(db, user_id)
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def reset_password(db: Session, user_id: int, new_password: str) -> bool:
        user = UserService.get_by_id(db, user_id)
        if len(new_password) < 6:
            raise BadRequestException("Password must be at least 6 characters long")
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
