from fastapi import HTTPException, status
from typing import Optional
from pydantic import ValidationError


class CourtAlertFatalException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)


class CourtAlertNonFatalException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class CourtAlertValidationException(HTTPException):
    def __init__(self, validation_error: Optional[ValidationError] = None, message: Optional[str] = None):
        if validation_error:
            error_messages = [error["msg"] for error in validation_error.errors()]
            detail = str(error_messages)
        else:
            detail = message or "Validation error occurred"
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def handle_pydantic_validation_error(validation_error: ValidationError) -> CourtAlertValidationException:
    return CourtAlertValidationException(validation_error=validation_error)
