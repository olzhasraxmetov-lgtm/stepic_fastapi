from fastapi import status, HTTPException

class BaseAppException(HTTPException):
    """Базовый класс, который умеет хранить статус и сообщение"""
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    message="Internal Server Error"
    log_message = None

    def __init__(self, message: str = None, log_message: str = None):
        super().__init__(
            status_code=self.status_code,
            detail=message or self.message
        )
        self.message = message or self.message
        self.log_message = log_message or self.message

class NotFoundException(BaseAppException):
    status_code=status.HTTP_404_NOT_FOUND
    message="Not Found"

class BadRequestException(BaseAppException):
    status_code=status.HTTP_400_BAD_REQUEST
    message="Bad Request"

class UnauthorizedException(BaseAppException):
    status_code=status.HTTP_401_UNAUTHORIZED
    message="Could not authenticate user"

class ConflictException(BaseAppException):
    status_code=status.HTTP_409_CONFLICT
    message="Resource already exists"

class ForbiddenException(BaseAppException):
    status_code=status.HTTP_403_FORBIDDEN
    message="Forbidden"