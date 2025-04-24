from sqlalchemy.orm import Session
from models import Huesped

class HuespedCRUD:
    @staticmethod
    def crear_huesped(db: Session, nombre: str, rut: str, email: str = None, telefono: str = None):
        huesped = Huesped(nombre=nombre, rut=rut, email=email, telefono=telefono)
        db.add(huesped)
        db.commit()
        return huesped

    @staticmethod
    def obtener_huesped_por_rut(db: Session, rut: str):
        return db.query(Huesped).filter(Huesped.rut == rut).first()

    @staticmethod
    def actualizar_huesped(db: Session, huesped_id: int, **kwargs):
        huesped = db.query(Huesped).filter(Huesped.id == huesped_id).first()
        if huesped:
            for key, value in kwargs.items():
                setattr(huesped, key, value)
            db.commit()
        return huesped

    @staticmethod
    def eliminar_huesped(db: Session, huesped_id: int):
        huesped = db.query(Huesped).filter(Huesped.id == huesped_id).first()
        if huesped:
            db.delete(huesped)
            db.commit()
            return True
        return False