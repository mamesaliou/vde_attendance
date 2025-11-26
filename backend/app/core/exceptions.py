from typing import Optional, Any, Dict

from fastapi import HTTPException
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    error_id: Optional[str] = None
    message: str
    code: int
    details: Optional[str] = None


class ApiErrorResponse(BaseModel):
    error: ErrorDetail


class ApiError(HTTPException):
    def __init__(
        self,
        message: str,
        details: Optional[Any] = None,
        status_code: Optional[int] = None,
        payload: Optional[Dict] = None
    ):
        self.message = message
        self.details = details or message
        self.status_code = status_code or 500
        self.payload = payload or {}
        
        error_response = ApiErrorResponse(
            error=ErrorDetail(
                message=self.message,
                code=self.status_code,
                details=self.details,
                **self.payload
            )
        )
        super().__init__(status_code=self.status_code, detail=error_response.model_dump())


class BadRequestError(ApiError):
    def __init__(self, message: str, details: Optional[Any] = None, payload: Optional[Dict] = None):
        super().__init__(message=message, details=details, status_code=400, payload=payload)


class ConflictError(ApiError):
    def __init__(self, message: str, details: Optional[Any] = None, payload: Optional[Dict] = None):
        super().__init__(message=message, details=details, status_code=409, payload=payload)


class ForbiddenError(ApiError):
    def __init__(self, message: str, details: Optional[Any] = None, payload: Optional[Dict] = None):
        super().__init__(message=message, details=details, status_code=403, payload=payload)


class NotFoundError(ApiError):
    def __init__(self, message: str, details: Optional[Any] = None, payload: Optional[Dict] = None):
        super().__init__(message=message, details=details, status_code=404, payload=payload)


class UnauthorizedError(ApiError):
    def __init__(self, message: str, details: Optional[Any] = None, payload: Optional[Dict] = None):
        super().__init__(message=message, details=details, status_code=401, payload=payload)
