from pydantic import BaseModel, Field
from typing import Optional, Dict

class MenuBase(BaseModel):
    nombre: str = Field(..., description="Nombre del menú")
    descripcion: Optional[str] = Field(None, description="Descripción del menú")
    precio: float = Field(..., gt=0, description="Precio del menú")
    ingredientes: Dict[str, float] = Field({}, description="Ingredientes necesarios")

class MenuCreate(MenuBase):
    class Config:
        schema_extra = {
            "example": {
                "nombre": "Anticuchos",
                "descripcion": "Anticuchos peruanos tradicionales",
                "precio": 15.0,
                "ingredientes": {
                    "corazón": 0.3,
                    "ají panca": 0.1,
                    "papa": 0.2
                }
            }
        }

class MenuUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    ingredientes: Optional[Dict[str, float]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "nombre": "Anticuchos Premium",
                "descripcion": "Anticuchos peruanos con ingredientes premium",
                "precio": 18.0,
                "ingredientes": {
                    "corazón": 0.4,
                    "ají panca": 0.15,
                    "papa": 0.25
                }
            }
        }

class Menu(MenuBase):
    id: int
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "nombre": "Ceviche Peruano",
                "descripcion": "Ceviche fresco con pescado del día",
                "precio": 25.5,
                "ingredientes": {
                    "pescado": 0.5,
                    "limón": 0.2,
                    "cebolla": 0.1
                }
            }
        }
