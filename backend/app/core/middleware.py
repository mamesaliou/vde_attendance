from typing import Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger
from app.core.security import SecurityMiddleware
from app.core.request_logging import request_logging_middleware
from app.core.size_limit import request_size_middleware
from app.core.auth_middleware import verify_token
from app.core.rate_limit import rate_limit_middleware

logger = get_logger(__name__)

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except SQLAlchemyError as e:
        logger.error(
            "database_error",
            error=str(e),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Une erreur de base de données est survenue",
                "type": "database_error"
            }
        )
    except Exception as e:
        logger.error(
            "unhandled_error",
            error=str(e),
            path=request.url.path,
            method=request.method,
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Une erreur inattendue est survenue",
                "type": "internal_server_error"
            }
        )

MIDDLEWARE_MAPPING: Dict[str, Any] = {
    "request_logging_middleware": request_logging_middleware,
    "request_size_middleware": request_size_middleware,
    "rate_limit_middleware": rate_limit_middleware,
    "SecurityMiddleware": SecurityMiddleware,
    "verify_token": verify_token,
    "catch_exceptions_middleware": catch_exceptions_middleware
}

def setup_middlewares(app: FastAPI, settings) -> None:
    for middleware_config in settings.MIDDLEWARE_CONFIG:
        if middleware_config["enabled"]:
            middleware_class = MIDDLEWARE_MAPPING[middleware_config["class"]]
            
            if isinstance(middleware_class, type):
                logger.info(f"Adding class middleware: {middleware_config['name']} - {middleware_config['description']}")
                app.add_middleware(middleware_class)
            else:
                logger.info(f"Adding function middleware: {middleware_config['name']} - {middleware_config['description']}")
                app.middleware("http")(middleware_class)

__all__ = [
    "SecurityMiddleware",
    "request_logging_middleware",
    "request_size_middleware",
    "verify_token",
    "rate_limit_middleware",
    "catch_exceptions_middleware",
    "setup_middlewares"
]
