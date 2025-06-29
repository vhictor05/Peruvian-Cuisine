from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MenuBase(BaseModel):
    nombre: str = Field(..., example="Ensalada César")
    descripcion: Optional[str] = Field(None, example="Ensalada fresca con pollo")
    precio: float = Field(..., example=12.99)
    
class MenuCreate(MenuBase):
    ingredientes: List[dict] = Field(..., example=[
        {"id": 1, "cantidad": 2}
    ])

class Menu(MenuBase):
    id: int
    
    class Config:
        orm_mode = True