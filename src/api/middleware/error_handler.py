from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI):
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error occurred"}
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        logger.error(f"Database integrity error: {exc}")
        
        # Handle common integrity errors
        error_msg = str(exc.orig)
        if "unique constraint" in error_msg.lower():
            if "email" in error_msg.lower():
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Email address already exists"}
                )
            elif "course_code" in error_msg.lower():
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Course code already exists"}
                )
        
        return JSONResponse(
            status_code=400,
            content={"detail": "Data integrity constraint violated"}
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        logger.error(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()}
        )

    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):
        logger.error(f"Value error: {exc}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)}
        )

    # Let FastAPI handle HTTPException naturally to preserve specific error messages
    # @app.exception_handler(HTTPException) - removed to preserve specific 404 messages