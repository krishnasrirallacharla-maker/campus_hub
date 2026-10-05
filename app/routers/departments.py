from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_admin, get_current_faculty_or_admin
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    DepartmentWithStats,
)
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments Management"])


@router.get(
    "",
    response_model=List[DepartmentResponse],
    summary="List all departments",
)
def list_departments(
    search: Optional[str] = Query(None, description="Search by name or code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return DepartmentService.list_departments(db, skip=skip, limit=limit, search=search)


@router.get(
    "/with-stats",
    response_model=List[DepartmentWithStats],
    summary="List all departments with statistics (Faculty & Admin)",
)
def list_departments_with_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_faculty_or_admin),
):
    return DepartmentService.list_departments_with_stats(db)


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Get department details by ID",
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    return DepartmentService.get_by_id(db, department_id)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new department (Admin only)",
)
def create_department(
    dept_data: DepartmentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return DepartmentService.create_department(db, dept_data)


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    summary="Update a department (Admin only)",
)
def update_department(
    department_id: int,
    dept_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return DepartmentService.update_department(db, department_id, dept_data)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a department (Admin only)",
)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    DepartmentService.delete_department(db, department_id)
    return {"message": "Department deleted successfully"}
