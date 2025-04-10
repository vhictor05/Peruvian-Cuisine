from sqlalchemy.orm import Session
from datetime import datetime
from models import Reserva

class ReservaCRUD:
    @staticmethod
    def crear_reserva(db: Session, huesped_id: int, habitacion_id: int, 
                     fecha_entrada: datetime, fecha_salida: datetime):
        reserva = Reserva(
            huesped_id=huesped_id,
            habitacion_id=habitacion_id,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida
        )
        db.add(reserva)
        db.commit()
        return reserva

    @staticmethod
    def obtener_reservas_por_huesped(db: Session, huesped_id: int):
        return db.query(Reserva).filter(Reserva.huesped_id == huesped_id).all()

    @staticmethod
    def obtener_reservas_activas(db: Session):
        hoy = datetime.now()
        return db.query(Reserva).filter(
            Reserva.fecha_entrada <= hoy,
            Reserva.fecha_salida >= hoy
        ).all()