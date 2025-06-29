import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models_folder.models_restaurente import Cliente
class ClienteCRUD:

    @staticmethod
    def create_cliente(db: Session, rut: str, nombre: str, email: str):
        try:
            cliente_existente = db.query(Cliente).filter_by(rut=rut).first()
            if cliente_existente:
                logging.warning(f"El cliente con el rut '{rut}' ya existe.")
                return cliente_existente
            
            cliente = Cliente(rut=rut, nombre=nombre, email=email)
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            return cliente

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al crear cliente: {e}")
            return None

    @staticmethod
    def get_clientes(db: Session): #Es como un Select * from clientes
        try:
            return db.query(Cliente).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al obtener clientes: {e}")
            return []

    @staticmethod
    def get_cliente_by_rut(db: Session, rut: str): #Se filtra por rut 
        try:
            return db.query(Cliente).filter(Cliente.rut == rut).first()
        except SQLAlchemyError as e:
            logging.error(f"Error al buscar cliente por RUT '{rut}': {e}")
            return None

    @staticmethod
    def update_cliente(db, rut_anterior, nombre, email, rut_nuevo=None):
        # Si rut_nuevo no se usa (no se permite editar el rut), ignóralo
        cliente = db.query(Cliente).filter(Cliente.rut == rut_anterior).first()
        if cliente:
            cliente.nombre = nombre
            cliente.email = email
            # No actualiza el rut
            db.commit()
            return cliente
        return None


    @staticmethod
    def delete_cliente(db, rut):
        cliente = db.query(Cliente).filter_by(rut=rut).first()
        if cliente:
            db.delete(cliente)
            db.commit()
            return True
        else:
            logging.warning(f"No se encontró el cliente con el RUT '{rut}'.")  # Antes decía "email", corregido a "RUT"
            return False
