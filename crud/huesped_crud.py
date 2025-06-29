from sqlalchemy.orm import Session
from models_folder.models_hotel import Huesped
import re

class HuespedCRUD:
    @staticmethod
    def crear_huesped(db: Session, nombre: str, rut: str, email: str = None, telefono: str = None):
        # Validaciones básicas
        if not re.match(r'^[A-Za-z\s]+$', nombre):
            raise ValueError("El nombre solo debe contener letras y espacios")

        if not re.match(r'^\d{2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise ValueError("El RUT debe tener formato xx.xxx.xxx-x")

        if email and not re.match(r'^[\w\.-]+@gmail\.com$', email):
            raise ValueError("El email debe tener formato válido y terminar en @gmail.com")

        if telefono and (not telefono.isdigit() or len(telefono) != 9):
            raise ValueError("El teléfono debe contener exactamente 9 dígitos numéricos")

        # Verificar que no exista un huésped con el mismo RUT
        existente = db.query(Huesped).filter(Huesped.rut == rut).first()
        if existente:
            raise ValueError("Ya existe un huésped registrado con ese RUT")

        huesped = Huesped(nombre=nombre, rut=rut, email=email, telefono=telefono)
        try:
            db.add(huesped)
            db.commit()
            return huesped
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def obtener_huesped_por_rut(db: Session, rut: str):
        return db.query(Huesped).filter(Huesped.rut == rut).first()

    @staticmethod
    def actualizar_huesped(db: Session, huesped_id: int, **kwargs):
        huesped = db.query(Huesped).filter(Huesped.id == huesped_id).first()
        if not huesped:
            raise ValueError("Huésped no encontrado")

        # Validaciones similares a crear para los campos que se actualizan
        if 'nombre' in kwargs:
            if not re.match(r'^[A-Za-z\s]+$', kwargs['nombre']):
                raise ValueError("El nombre solo debe contener letras y espacios")

        if 'rut' in kwargs:
            if not re.match(r'^\d{2}\.\d{3}\.\d{3}-[\dkK]$', kwargs['rut']):
                raise ValueError("El RUT debe tener formato xx.xxx.xxx-x")
            # Verificar que no exista otro huésped con ese RUT
            existente = db.query(Huesped).filter(Huesped.rut == kwargs['rut'], Huesped.id != huesped_id).first()
            if existente:
                raise ValueError("Otro huésped ya tiene ese RUT")

        if 'email' in kwargs:
            email = kwargs['email']
            if email and not re.match(r'^[\w\.-]+@gmail\.com$', email):
                raise ValueError("El email debe tener formato válido y terminar en @gmail.com")

        if 'telefono' in kwargs:
            telefono = kwargs['telefono']
            if telefono and (not telefono.isdigit() or len(telefono) != 9):
                raise ValueError("El teléfono debe contener exactamente 9 dígitos numéricos")

        try:
            for key, value in kwargs.items():
                setattr(huesped, key, value)
            db.commit()
            return huesped
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def eliminar_huesped(db: Session, huesped_id: int):
        huesped = db.query(Huesped).filter(Huesped.id == huesped_id).first()
        if not huesped:
            return False
        try:
            db.delete(huesped)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
