from sqlalchemy.orm import Session
from models_folder.models_hotel import Huesped
import re

class HuespedCRUD:
    @staticmethod
    def crear_huesped(db: Session, nombre: str, rut: str, email: str = None, telefono: str = None):
        # Validaciones en el CRUD (ejemplo)
        if not re.match(r'^[A-Za-z\s]+$', nombre):
            raise ValueError("El nombre solo debe contener letras y espacios")

        if not re.match(r'^\d{2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise ValueError("El RUT debe tener formato xx.xxx.xxx-x")

        if email and not re.match(r'^[\w\.-]+@gmail\.com$', email):
            raise ValueError("El email debe tener formato válido y terminar en @gmail.com")

        if telefono and (not telefono.isdigit() or len(telefono) != 9):
            raise ValueError("El teléfono debe contener exactamente 9 dígitos numéricos")

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