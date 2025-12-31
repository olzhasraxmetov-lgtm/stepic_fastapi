from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import BaseAppException, NotFoundException
from loguru import logger

def add_exception_handler(app: FastAPI):
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException):
        logger.warning(f"App error: {exc.log_message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )