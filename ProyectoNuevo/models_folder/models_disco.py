from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from disco_database import Base
from datetime import datetime

class Evento(Base):
    __tablename__ = 'eventos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha = Column(DateTime, nullable=False)
    precio_entrada = Column(Float, nullable=False)
    aforo_maximo = Column(Integer, nullable=False)

    entradas = relationship("Entrada", back_populates="evento")
    reservas_mesa = relationship("ReservaMesa", back_populates="evento")

class ClienteDiscoteca(Base):
    __tablename__ = 'clientes_discoteca'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    rut = Column(String(12), unique=True, nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))

    entradas = relationship("Entrada", back_populates="cliente")
    reservas_mesa = relationship("ReservaMesa", back_populates="cliente")

class Entrada(Base):
    __tablename__ = 'entradas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey('eventos.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes_discoteca.id'), nullable=False)
    fecha_compra = Column(DateTime, nullable=False)
    precio_pagado = Column(Float, nullable=False)

    evento = relationship("Evento", back_populates="entradas")
    cliente = relationship("ClienteDiscoteca", back_populates="entradas")

class Mesa(Base):
    __tablename__ = 'mesas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(10), unique=True, nullable=False)
    capacidad = Column(Integer, nullable=False)
    ubicacion = Column(String(100))

    reservas = relationship("ReservaMesa", back_populates="mesa")

class ReservaMesa(Base):
    __tablename__ = 'reservas_mesa'
    id = Column(Integer, primary_key=True, autoincrement=True)
    evento_id = Column(Integer, ForeignKey('eventos.id'), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes_discoteca.id'), nullable=False)
    mesa_id = Column(Integer, ForeignKey('mesas.id'), nullable=False)
    fecha_reserva = Column(DateTime, nullable=False)
    estado = Column(String(20), default="Pendiente")

    evento = relationship("Evento", back_populates="reservas_mesa")
    cliente = relationship("ClienteDiscoteca", back_populates="reservas_mesa")
    mesa = relationship("Mesa", back_populates="reservas")

class Trago(Base):
    __tablename__ = 'tragos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    categoria = Column(String(50))
    disponible = Column(Boolean, default=True)
    stock = Column(Integer, default=0)

class PedidoTrago(Base):
    __tablename__ = 'pedidos_tragos'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes_discoteca.id'))
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    estado = Column(String(20), default='Pendiente')
    detalles = Column(JSON)

    cliente = relationship("ClienteDiscoteca")