from sqlalchemy.orm import Session
from datetime import datetime
from models import Reserva, Habitacion
from sqlalchemy import and_

class ReservaCRUD:
    @staticmethod
    def crear_reserva(db: Session, huesped_id: int, habitacion_id: int, 
                      fecha_entrada: datetime, fecha_salida: datetime):
        # Verificar disponibilidad de la habitación
        if not ReservaCRUD.habitacion_disponible(db, habitacion_id, fecha_entrada, fecha_salida):
            raise ValueError("La habitación no está disponible en esas fechas")
        
        # Crear la nueva reserva
        reserva = Reserva(
            huesped_id=huesped_id,
            habitacion_id=habitacion_id,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            estado="Confirmada"
        )
        db.add(reserva)
        db.commit()

        # Cambiar el estado de la habitación a no disponible
        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        
        # Verificar que la habitación existe y actualizar su disponibilidad
        if habitacion:
            if habitacion.disponible:  # Solo actualizar si está disponible
                habitacion.disponible = False
                db.commit()
            else:
                raise ValueError("La habitación ya está ocupada o no está disponible en este momento")
        else:
            raise ValueError("La habitación no existe en la base de datos")

        return reserva
    
    @staticmethod
    def habitacion_disponible(db: Session, habitacion_id: int, 
                            fecha_entrada: datetime, fecha_salida: datetime) -> bool:
        """
        Verifica si una habitación está disponible en el rango de fechas solicitado.
        """
        # Consultar si ya existe alguna reserva confirmada en el rango de fechas
        reserva_existente = db.query(Reserva).filter(
            Reserva.habitacion_id == habitacion_id,
            and_(
                Reserva.fecha_entrada < fecha_salida,  # Verificar que la entrada solicitada sea antes de la salida existente
                Reserva.fecha_salida > fecha_entrada   # Verificar que la salida solicitada sea después de la entrada existente
            ),
            Reserva.estado == "Confirmada"  # Solo considerar reservas confirmadas
        ).first()

        print(f"Verificando disponibilidad de la habitación {habitacion_id}: {'Disponible' if reserva_existente is None else 'No disponible'}")

        return reserva_existente is None  # Si no hay reservas existentes, la habitación está disponible


    @staticmethod
    def obtener_reservas_activas(db: Session):
        """Obtiene todas las reservas activas (que están dentro del rango de fechas actual)."""
        hoy = datetime.now()
        return db.query(Reserva).filter(
            Reserva.fecha_entrada <= hoy,
            Reserva.fecha_salida >= hoy,
            Reserva.estado == "Confirmada"
        ).all()

    @staticmethod
    def eliminar_reserva(db: Session, reserva_id: int):
        """Elimina una reserva por su ID."""
        # Buscar la reserva por ID
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            raise ValueError("La reserva no existe")
        
        # Eliminar la reserva
        db.delete(reserva)
        db.commit()
