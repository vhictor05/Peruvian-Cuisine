from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseDBModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        orm_mode = True
