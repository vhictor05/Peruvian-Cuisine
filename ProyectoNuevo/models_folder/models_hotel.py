from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from hotel_database import Base

class Habitacion(Base):
    __tablename__ = "habitaciones"
    id = Column(Integer, primary_key=True)
    numero = Column(String(10), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)

    reservas = relationship("Reserva", back_populates="habitacion")

class Huesped(Base):
    __tablename__ = 'huespedes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    rut = Column(String(12), unique=True, nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    
    reservas = relationship("Reserva", back_populates="huesped")

class Reserva(Base):
    __tablename__ = 'reservas'
    
    id = Column(Integer, primary_key=True)
    huesped_id = Column(Integer, ForeignKey('huespedes.id'), nullable=False)
    habitacion_id = Column(Integer, ForeignKey('habitaciones.id'), nullable=False)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    estado = Column(String, default="Confirmada")
    precio_final = Column(Float, nullable=True)
    
    huesped = relationship("Huesped", back_populates="reservas")
    habitacion = relationship("Habitacion", back_populates="reservas")