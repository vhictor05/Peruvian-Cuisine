from sqlalchemy.orm import Session
from models import ClienteDiscoteca
from typing import Optional

class ClienteDiscotecaCRUD:
    @staticmethod
    def crear(db: Session, cliente_data: dict) -> ClienteDiscoteca:
        cliente = ClienteDiscoteca(**cliente_data)
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        return cliente

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