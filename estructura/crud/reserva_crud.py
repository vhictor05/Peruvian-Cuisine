from sqlalchemy.orm import Session
from datetime import datetime
from  estructura.models_folder.models_hotel import Reserva, Habitacion, Huesped
from sqlalchemy import and_

class ReservaCRUD:
    @staticmethod
    def crear_reserva(db: Session, huesped_id: int, habitacion_id: int, 
                    fecha_entrada: datetime, fecha_salida: datetime, precio_final: float):
        # Validar fechas
        if fecha_entrada >= fecha_salida:
            raise ValueError("La fecha de entrada debe ser anterior a la fecha de salida")
        if fecha_entrada < datetime.now():
            raise ValueError("La fecha de entrada no puede ser en el pasado")

        # Validar existencia de huésped y habitación
        huesped = db.query(Huesped).filter(Huesped.id == huesped_id).first()
        if not huesped:
            raise ValueError("El huésped no existe")

        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        if not habitacion:
            raise ValueError("La habitación no existe")

        # Verificar disponibilidad
        if not ReservaCRUD.habitacion_disponible(db, habitacion_id, fecha_entrada, fecha_salida):
            raise ValueError("La habitación no está disponible en esas fechas")

        reserva = Reserva(
            huesped_id=huesped_id,
            habitacion_id=habitacion_id,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            estado="Confirmada",
            precio_final=precio_final  # <-- OK
        )
        try:
            db.add(reserva)
            db.commit()

            # Cambiar estado habitación a no disponible
            if habitacion.disponible:
                habitacion.disponible = False
                db.commit()
            else:
                raise ValueError("La habitación ya está ocupada o no está disponible en este momento")

            return reserva
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def habitacion_disponible(db: Session, habitacion_id: int, 
                            fecha_entrada: datetime, fecha_salida: datetime) -> bool:
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
    def eliminar_reserva(db: Session, reserva_id: int):
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            raise ValueError("La reserva no existe")
        try:
            # Marcar la habitación como disponible antes de eliminar la reserva
            habitacion = db.query(Habitacion).filter(Habitacion.id == reserva.habitacion_id).first()
            if habitacion:
                habitacion.disponible = True
            db.delete(reserva)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def actualizar_reserva(db, reserva_id: int, **kwargs):
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            raise ValueError("Reserva no encontrada")

        try:
            habitacion_anterior_id = reserva.habitacion_id
            habitacion_nueva_id = kwargs.get("habitacion_id", habitacion_anterior_id)

            # Solo validar y cambiar disponibilidad si la habitación cambia
            if "habitacion_id" in kwargs and habitacion_nueva_id != habitacion_anterior_id:
                # Aquí deberías tener tu lógica para validar disponibilidad
                if not ReservaCRUD.habitacion_disponible(db, habitacion_nueva_id, reserva.fecha_entrada, reserva.fecha_salida):
                    raise ValueError("No hay habitaciones disponibles para ese tipo")

                # Marcar la habitación anterior como disponible
                habitacion_anterior = db.query(Habitacion).filter(Habitacion.id == habitacion_anterior_id).first()
                if habitacion_anterior:
                    habitacion_anterior.disponible = True

                # Marcar la nueva habitación como no disponible
                habitacion_nueva = db.query(Habitacion).filter(Habitacion.id == habitacion_nueva_id).first()
                if habitacion_nueva:
                    habitacion_nueva.disponible = False

            # Actualizar los campos de la reserva (precio, fechas, etc.)
            for key, value in kwargs.items():
                setattr(reserva, key, value)
            db.commit()
            return reserva
        except Exception as e:
            db.rollback()
            raise e
        
    @staticmethod
    def obtener_todas_reservas(db: Session):
        return db.query(Reserva).all()
