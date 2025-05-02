from sqlalchemy.orm import Session
from models_folder.models_hotel import Habitacion

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

    @staticmethod
    def modificar_habitacion(db: Session, habitacion_id: int, numero: str, tipo: str, precio: float, disponible: bool):
        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        if not habitacion:
            raise Exception("Habitación no encontrada")
        
        habitacion.numero = numero
        habitacion.tipo = tipo
        habitacion.precio = precio
        habitacion.disponible = disponible
        db.commit()
        return habitacion
    @staticmethod
    def verificar_habitaciones_en_bd(db: Session):
        habitaciones = db.query(Habitacion).all()
        for habitacion in habitaciones:
            print(f"ID: {habitacion.id}, Numero: {habitacion.numero}, Disponible: {habitacion.disponible}")
