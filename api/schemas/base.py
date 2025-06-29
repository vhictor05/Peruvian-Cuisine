from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BaseResponse(BaseModel):
    message: str
    status: str = "success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    status: str = "error"
    detail: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int