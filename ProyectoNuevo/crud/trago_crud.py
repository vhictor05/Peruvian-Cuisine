from sqlalchemy.orm import Session
from models import Trago
from typing import Optional, List

class TragoCRUD:
    @staticmethod
    def crear_trago(db: Session, nombre: str, precio: float, descripcion: str = None, categoria: str = None):
        trago = Trago(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria=categoria
        )
        db.add(trago)
        db.commit()
        db.refresh(trago)
        return trago

    @staticmethod
    def obtener_todos(db: Session) -> List[Trago]:
        return db.query(Trago).filter(Trago.disponible == True).all()

    @staticmethod
    def obtener_por_id(db: Session, trago_id: int) -> Optional[Trago]:
        return db.query(Trago).filter(Trago.id == trago_id).first()

    @staticmethod
    def actualizar_trago(db: Session, trago_id: int, **kwargs):
        trago = db.query(Trago).filter(Trago.id == trago_id).first()
        if trago:
            for key, value in kwargs.items():
                setattr(trago, key, value)
            db.commit()
        return trago

    @staticmethod
    def eliminar_trago(db: Session, trago_id: int) -> bool:
        trago = db.query(Trago).filter(Trago.id == trago_id).first()
        if trago:
            trago.disponible = False
            db.commit()
            return True
        return False