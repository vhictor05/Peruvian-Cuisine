from sqlalchemy.orm import Session
from datetime import datetime
from models import Reserva, Habitacion
from sqlalchemy import and_

class ReservaCRUD:
    @staticmethod
    def crear_reserva(db: Session, huesped_id: int, habitacion_id: int, 
                    fecha_entrada: datetime, fecha_salida: datetime):
        # Verificar disponibilidad
        if not ReservaCRUD.habitacion_disponible(db, habitacion_id, fecha_entrada, fecha_salida):
            raise ValueError("La habitación no está disponible en esas fechas")
        
        reserva = Reserva(
            huesped_id=huesped_id,
            habitacion_id=habitacion_id,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            estado="Confirmada"
        )
        db.add(reserva)
        db.commit()
        return reserva

    @staticmethod
    def habitacion_disponible(db: Session, habitacion_id: int, 
                            fecha_entrada: datetime, fecha_salida: datetime):
        # Verificar que no haya reservas superpuestas
        reserva_existente = db.query(Reserva).filter(
            Reserva.habitacion_id == habitacion_id,
            and_(
                Reserva.fecha_entrada < fecha_salida,
                Reserva.fecha_salida > fecha_entrada
            ),
            Reserva.estado == "Confirmada"
        ).first()
        
        return reserva_existente is None

    @staticmethod
    def obtener_reservas_por_huesped(db: Session, huesped_id: int):
        return db.query(Reserva).filter(Reserva.huesped_id == huesped_id).all()

    @staticmethod
    def obtener_reservas_activas(db: Session):
        hoy = datetime.now()
        return db.query(Reserva).filter(
            Reserva.fecha_entrada <= hoy,
            Reserva.fecha_salida >= hoy,
            Reserva.estado == "Confirmada"
        ).all()