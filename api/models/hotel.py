from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

# ===== HUÉSPEDES =====
class HuespedBase(BaseModel):
    nombre: str
    rut: str
    email: Optional[str] = None
    telefono: Optional[str] = None

class HuespedCreate(HuespedBase):
    @field_validator('rut')
    @classmethod
    def validate_rut(cls, v):
        # Validación básica de RUT chileno
        if not v:
            raise ValueError('RUT es requerido')
        
        # Permitir diferentes formatos de RUT
        rut_clean = v.replace('-', '').replace('.', '').strip()
        if len(rut_clean) < 8:
            raise ValueError('RUT debe tener al menos 8 caracteres')
        
        return v

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('Nombre es requerido')
        return v.strip()

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email debe tener formato válido')
        return v

class HuespedUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

class Huesped(HuespedBase):
    id: int
    fecha_registro: Optional[datetime] = None  # HACER OPCIONAL

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S') if v else None
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
