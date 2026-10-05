from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.department import Department
from app.models.user import User
from app.models.event import Event
from app.models.enums import UserRole
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentWithStats


class DepartmentService:
    @staticmethod
    def get_by_id(db: Session, department_id: int) -> Department:
        dept = db.query(Department).filter(Department.id == department_id).first()
        if not dept:
            raise NotFoundException("Department", department_id)
        return dept

    @staticmethod
    def list_departments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> List[Department]:
        query = db.query(Department)
        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.filter(
                (Department.name.ilike(search_pattern)) | (Department.code.ilike(search_pattern))
            )
        return query.order_by(Department.name.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def list_departments_with_stats(db: Session) -> List[DepartmentWithStats]:
        departments = db.query(Department).order_by(Department.name.asc()).all()
        results = []
        for dept in departments:
            student_count = (
                db.query(func.count(User.id))
                .filter(User.department_id == dept.id, User.role == UserRole.STUDENT)
                .scalar()
                or 0
            )
            faculty_count = (
                db.query(func.count(User.id))
                .filter(User.department_id == dept.id, User.role == UserRole.FACULTY)
                .scalar()
                or 0
            )
            event_count = (
                db.query(func.count(Event.id))
                .filter(Event.department_id == dept.id)
                .scalar()
                or 0
            )

            results.append(
                DepartmentWithStats(
                    id=dept.id,
                    name=dept.name,
                    code=dept.code,
                    description=dept.description,
                    head_of_department=dept.head_of_department,
                    created_at=dept.created_at,
                    updated_at=dept.updated_at,
                    total_students=student_count,
                    total_faculty=faculty_count,
                    total_events=event_count,
                )
            )
        return results

    @staticmethod
    def create_department(db: Session, dept_data: DepartmentCreate) -> Department:
        name_clean = dept_data.name.strip()
        code_clean = dept_data.code.strip().upper()

        if db.query(Department).filter(Department.name.ilike(name_clean)).first():
            raise AlreadyExistsException("Department", "name", name_clean)

        if db.query(Department).filter(Department.code == code_clean).first():
            raise AlreadyExistsException("Department", "code", code_clean)

        dept = Department(
            name=name_clean,
            code=code_clean,
            description=dept_data.description.strip() if dept_data.description else None,
            head_of_department=dept_data.head_of_department.strip() if dept_data.head_of_department else None,
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept

    @staticmethod
    def update_department(db: Session, department_id: int, dept_data: DepartmentUpdate) -> Department:
        dept = DepartmentService.get_by_id(db, department_id)

        if dept_data.name is not None:
            name_clean = dept_data.name.strip()
            if db.query(Department).filter(Department.name.ilike(name_clean), Department.id != department_id).first():
                raise AlreadyExistsException("Department", "name", name_clean)
            dept.name = name_clean

        if dept_data.code is not None:
            code_clean = dept_data.code.strip().upper()
            if db.query(Department).filter(Department.code == code_clean, Department.id != department_id).first():
                raise AlreadyExistsException("Department", "code", code_clean)
            dept.code = code_clean

        if dept_data.description is not None:
            dept.description = dept_data.description.strip() if dept_data.description else None

        if dept_data.head_of_department is not None:
            dept.head_of_department = dept_data.head_of_department.strip() if dept_data.head_of_department else None

        db.commit()
        db.refresh(dept)
        return dept

    @staticmethod
    def delete_department(db: Session, department_id: int) -> bool:
        dept = DepartmentService.get_by_id(db, department_id)
        db.delete(dept)
        db.commit()
        return True
