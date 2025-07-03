from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class PedidoDetalle(BaseModel):
    trago_id: int
    cantidad: int
    precio_unitario: float

class PedidoCreate(BaseModel):
    cliente_id: int
    total: float
    detalles: List[PedidoDetalle]

class Pedido(PedidoCreate):
    id: int
    fecha: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}
