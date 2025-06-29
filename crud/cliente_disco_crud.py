from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models_folder.models_disco import ClienteDiscoteca
from typing import Optional

class ClienteDiscotecaCRUD:
    @staticmethod
    def crear(db: Session, cliente_data: dict) -> ClienteDiscoteca:
        rut = cliente_data.get("rut", "")
        telefono = cliente_data.get("telefono", "")

        # Validar que el RUT solo tenga dígitos
        if not rut.isdigit():
            raise ValueError("El RUT debe contener solo números.")
        # Validar que el teléfono solo tenga dígitos
        if not telefono.isdigit():
            raise ValueError("El teléfono debe contener solo números.")

        cliente = ClienteDiscoteca(**cliente_data)
        try:
            db.add(cliente)
            db.commit()
            db.refresh(cliente)
            return cliente
        except IntegrityError:
            db.rollback()
            raise ValueError("El cliente ya está registrado con ese RUT.")


    @staticmethod
    def obtener_todos(db: Session) -> list[ClienteDiscoteca]:
        return db.query(ClienteDiscoteca).all()

    @staticmethod
    def obtener_por_id(db: Session, cliente_id: int) -> Optional[ClienteDiscoteca]:
        return db.query(ClienteDiscoteca).filter(ClienteDiscoteca.id == cliente_id).first()

    @staticmethod
    def obtener_por_rut(db: Session, rut: str) -> Optional[ClienteDiscoteca]:
        return db.query(ClienteDiscoteca).filter(ClienteDiscoteca.rut == rut).first()

    @staticmethod
    def buscar_por_nombre(db: Session, nombre: str) -> list[ClienteDiscoteca]:
        return db.query(ClienteDiscoteca).filter(ClienteDiscoteca.nombre.ilike(f"%{nombre}%")).all()

    @staticmethod
    def actualizar(db: Session, cliente_id: int, nuevos_datos: dict) -> Optional[ClienteDiscoteca]:
        cliente = db.query(ClienteDiscoteca).filter(ClienteDiscoteca.id == cliente_id).first()
        if cliente:
            for key, value in nuevos_datos.items():
                setattr(cliente, key, value)
            db.commit()
            db.refresh(cliente)
        return cliente

    @staticmethod
    def eliminar(db: Session, cliente_id: int) -> bool:
        cliente = db.query(ClienteDiscoteca).filter(ClienteDiscoteca.id == cliente_id).first()
        if cliente:
            db.delete(cliente)
            db.commit()
            return True
        return False