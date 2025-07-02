from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from .base import BaseDBModel

# ===== HUÉSPEDES =====
class HuespedBase(BaseModel):
    nombre: str
    rut: str
    email: Optional[str] = None
    telefono: Optional[str] = None

class HuespedCreate(HuespedBase):
    @validator('rut')
    def validate_rut(cls, v):
        # Validación básica de RUT chileno
        if not v or len(v.replace('-', '').replace('.', '')) < 8:
            raise ValueError('RUT inválido')
        return v

class HuespedUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

class Huesped(HuespedBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }

# ===== HABITACIONES =====
class HabitacionBase(BaseModel):
    numero: str
    tipo: str
    precio: float

class HabitacionCreate(HabitacionBase):
    disponible: bool = True

class HabitacionUpdate(BaseModel):
    numero: Optional[str] = None
    tipo: Optional[str] = None
    precio: Optional[float] = None
    disponible: Optional[bool] = None

class Habitacion(HabitacionBase):
    id: int
    disponible: bool

    class Config:
        from_attributes = True

# ===== RESERVAS =====
class ReservaBase(BaseModel):
    huesped_id: int
    habitacion_id: int
    fecha_entrada: datetime
    fecha_salida: datetime
    precio_final: float

class ReservaCreate(ReservaBase):
    estado: str = "Pendiente"

class ReservaUpdate(BaseModel):
    fecha_entrada: Optional[datetime] = None
    fecha_salida: Optional[datetime] = None
    precio_final: Optional[float] = None
    estado: Optional[str] = None

class Reserva(ReservaBase):
    id: int
    estado: str
    fecha_reserva: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }

# ===== RESPUESTAS EXTENDIDAS =====
class ReservaDetallada(Reserva):
    huesped_nombre: str
    huesped_rut: str
    habitacion_numero: str
    habitacion_tipo: str
