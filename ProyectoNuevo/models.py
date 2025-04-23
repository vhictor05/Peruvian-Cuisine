from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON, Boolean 
from sqlalchemy.orm import relationship
from database import Base
from hotel_database import Base
from disco_database import Base
from datetime import datetime, timedelta

class Cliente(Base):
    __tablename__ = "clientes"
    rut = Column(String(9), primary_key=True, index=True)
    email = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    pedidos = relationship("Pedido", back_populates="cliente")

class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    tipo = Column(String, nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad = Column(String, nullable=False)
    menu_ingredientes = relationship("MenuIngrediente", back_populates="ingrediente")

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)  # New attribute to store the price of the menu
    ing_necesarios = Column(JSON, nullable=False)  # Dictionary to store ingredient name and quantity
    ingredientes = relationship("MenuIngrediente", back_populates="menu")

class MenuIngrediente(Base):
    __tablename__ = "menu_ingredientes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    ingrediente_id = Column(Integer, ForeignKey("ingredientes.id"), nullable=False)
    cantidad = Column(Float, nullable=False)
    menu = relationship("Menu", back_populates="ingredientes")
    ingrediente = relationship("Ingrediente", back_populates="menu_ingredientes")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descripcion = Column(String)
    total = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)
    cliente_rut = Column(String, ForeignKey('clientes.rut', onupdate="CASCADE"), nullable=False)
    cliente = relationship("Cliente", back_populates="pedidos")
    menus = Column(JSON, nullable=False)  # List to store selected menus

# MODELOS HOTEL
class Habitacion(Base):
    __tablename__ = 'habitaciones'
    id = Column(Integer, primary_key=True)
    numero = Column(String(10), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)  

class Huesped(Base):
    __tablename__ = 'huespedes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    rut = Column(String(12), unique=True, nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))

class Reserva(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True)
    fecha_entrada = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    huesped_id = Column(Integer, ForeignKey('huespedes.id'))
    habitacion_id = Column(Integer, ForeignKey('habitaciones.id'))
    estado = Column(String(20), default='Pendiente')
    
    huesped = relationship("Huesped")
    habitacion = relationship("Habitacion")


# MODELO DISCO

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
    estado = Column(String(20), default="Pendiente")  # Confirmada, Cancelada, etc.

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

class PedidoTrago(Base):
    __tablename__ = 'pedidos_tragos'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes_discoteca.id'))
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    estado = Column(String(20), default='Pendiente')
    detalles = Column(JSON)  # Almacenará {trago_id: cantidad}

    cliente = relationship("ClienteDiscoteca")

# Tabla de Reportes (BETA)
class ReporteError(Base):
    __tablename__ = 'reportes_errores'
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.now)
    titulo = Column(String(200), nullable=False)
    modulo = Column(String(50), nullable=False)
    urgencia = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), default="Abierto")
    reportado_por = Column(String(100))
    comentarios = Column(Text)
    fecha_resolucion = Column(DateTime)