from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .base import BaseDBModel

class Menu(BaseDBModel):
    name: str
    description: Optional[str]
    price: float
    category: str
    available: bool = True

class Order(BaseDBModel):
    client_id: int
    items: List[int]  # Lista de IDs de menú
    total: float
    status: str  # 'pending', 'preparing', 'completed', 'cancelled'
    
class Client(BaseDBModel):
    name: str
    email: Optional[str]
    phone: Optional[str]
    
class Ingredient(BaseDBModel):
    name: str
    quantity: float
    unit: str  # 'kg', 'g', 'l', 'ml', etc.
    minimum_stock: float
