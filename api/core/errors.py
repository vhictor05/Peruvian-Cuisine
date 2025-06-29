from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from api.schemas.base import ErrorResponse
from datetime import datetime

def add_error_handlers(app: FastAPI):
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Database error occurred",
                detail=str(exc),
                timestamp=datetime.utcnow()
            ).dict()
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                message="Internal server error",
                detail=str(exc),
                timestamp=datetime.utcnow()
            ).dict()
        )