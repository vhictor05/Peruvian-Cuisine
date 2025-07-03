from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .base import BaseDBModel

# Modelos para Evento
class EventoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha: datetime
    precio_entrada: float
    aforo_maximo: int

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    id: int
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}

# Modelos para ClienteDiscoteca
class ClienteDiscotecaBase(BaseModel):
    nombre: str
    rut: str
    email: Optional[str] = None
    telefono: Optional[str] = None

class ClienteDiscotecaCreate(ClienteDiscotecaBase):
    pass

class ClienteDiscoteca(ClienteDiscotecaBase):
    id: int
    class Config:
        from_attributes = True

# Modelos para Entrada
class EntradaBase(BaseModel):
    evento_id: int
    cliente_id: int
    fecha_compra: datetime
    precio_pagado: float

class EntradaCreate(EntradaBase):
    pass

class Entrada(EntradaBase):
    id: int
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}

# Modelos para Mesa
class MesaBase(BaseModel):
    numero: str
    capacidad: int
    ubicacion: Optional[str] = None

class MesaCreate(MesaBase):
    pass

class Mesa(MesaBase):
    id: int
    class Config:
        from_attributes = True

# Modelos para ReservaMesa
class ReservaMesaBase(BaseModel):
    evento_id: int
    cliente_id: int
    mesa_id: int
    fecha_reserva: datetime
    estado: Optional[str] = "Pendiente"

class ReservaMesaCreate(ReservaMesaBase):
    pass

class ReservaMesa(ReservaMesaBase):
    id: int
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')}

# Modelos para Trago
class TragoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria: Optional[str] = None
    disponible: Optional[bool] = True
    stock: Optional[int] = 0

class TragoCreate(TragoBase):
    pass

class Trago(TragoBase):
    id: int
    class Config:
        from_attributes = True
