from sqlalchemy.orm import Session
from models import Habitacion

class HabitacionCRUD:
    @staticmethod
    def crear_habitacion(db: Session, numero: str, tipo: str, precio: float):
        habitacion = Habitacion(numero=numero, tipo=tipo, precio=precio)
        db.add(habitacion)
        db.commit()
        return habitacion

    @staticmethod
    def obtener_habitacion_por_numero(db: Session, numero: str):
        return db.query(Habitacion).filter(Habitacion.numero == numero).first()

    @staticmethod
    def obtener_habitaciones_disponibles(db: Session):
        return db.query(Habitacion).filter(Habitacion.disponible == True).all()

    @staticmethod
    def actualizar_estado(db: Session, habitacion_id: int, disponible: bool):
        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        if habitacion:
            habitacion.disponible = disponible
            db.commit()
        return habitacion