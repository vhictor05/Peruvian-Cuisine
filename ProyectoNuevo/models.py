from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from database import Base

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