from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(AppException):
    def __init__(self, resource: str, identifier: Any = None):
        detail = f"{resource} not found" if identifier is None else f"{resource} with identifier '{identifier}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class AlreadyExistsException(AppException):
    def __init__(self, resource: str, field: str, value: Any):
        detail = f"{resource} with {field} '{value}' already exists"
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(AppException):
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
