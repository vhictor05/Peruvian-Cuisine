import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Ingrediente

class IngredienteCRUD:

    @staticmethod
    def create_ingrediente(db: Session, nombre: str, tipo: str, cantidad: float, unidad: str):
        try:
            ingrediente_existente = db.query(Ingrediente).filter_by(nombre=nombre).first()
            if ingrediente_existente:
                logging.warning(f"El ingrediente con el nombre '{nombre}' ya existe.")
                return ingrediente_existente

            nuevo_ingrediente = Ingrediente(nombre=nombre, tipo=tipo, cantidad=cantidad, unidad=unidad)
            db.add(nuevo_ingrediente)
            db.commit()
            db.refresh(nuevo_ingrediente)
            return nuevo_ingrediente

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al crear ingrediente: {e}")
            return None

    @staticmethod
    def get_ingredientes(db: Session):
        try:
            return db.query(Ingrediente).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al obtener ingredientes: {e}")
            return []

    @staticmethod
    def get_ingrediente_by_id(db: Session, ingrediente_id: int):
        try:
            return db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error al buscar ingrediente por ID '{ingrediente_id}': {e}")
            return None

    @staticmethod
    def get_ingrediente_by_nombre(db: Session, nombre: str):
        try:
            return db.query(Ingrediente).filter(Ingrediente.nombre == nombre).first()
        except SQLAlchemyError as e:
            logging.error(f"Error al buscar ingrediente por nombre '{nombre}': {e}")
            return None

    @staticmethod
    def update_ingrediente(db: Session, ingrediente_id: int, nombre : str = None,cantidad: float = None, tipo: str = None, unidad: str = None):
        try:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
            if not ingrediente:
                logging.error(f"No se encontró el ingrediente con ID '{ingrediente_id}'.")
                return None
            
            if nombre is not None:
                ingrediente.nombre = nombre

            if cantidad is not None:
                ingrediente.cantidad = cantidad
            if tipo is not None:
                ingrediente.tipo = tipo
            if unidad is not None:
                ingrediente.unidad = unidad

            db.commit()
            db.refresh(ingrediente)
            return ingrediente

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al actualizar ingrediente: {e}")
            return None

    @staticmethod
    def delete_ingrediente(db: Session, ingrediente_id: int):
        try:
            ingrediente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente_id).first()
            if not ingrediente:
                logging.error(f"No se encontró el ingrediente con ID '{ingrediente_id}'.")
                return None

            db.delete(ingrediente)
            db.commit()
            return ingrediente

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al eliminar ingrediente: {e}")
            return None
