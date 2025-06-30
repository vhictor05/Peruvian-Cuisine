from sqlalchemy.orm import Session
from  estructura.models_folder.models_hotel import Habitacion

class HabitacionCRUD:
    TIPOS_PERMITIDOS = {"VIP", "Penthouse", "Grande", "Mediana", "Pequeña"}

    @staticmethod
    def crear_habitacion(db: Session, numero: str, tipo: str, precio: float):
        if not numero.strip():
            raise ValueError("El número de habitación no puede estar vacío")

        if tipo not in HabitacionCRUD.TIPOS_PERMITIDOS:
            raise ValueError(f"Tipo de habitación inválido. Debe ser uno de {HabitacionCRUD.TIPOS_PERMITIDOS}")

        if precio <= 0:
            raise ValueError("El precio debe ser un número positivo")

        # Verificar que no exista habitación con el mismo número
        existente = db.query(Habitacion).filter(Habitacion.numero == numero).first()
        if existente:
            raise ValueError("Ya existe una habitación con ese número")

        habitacion = Habitacion(numero=numero, tipo=tipo, precio=precio, disponible=True)
        try:
            db.add(habitacion)
            db.commit()
            return habitacion
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def obtener_habitacion_por_numero(db: Session, numero: str):
        return db.query(Habitacion).filter(Habitacion.numero == numero).first()

    @staticmethod
    def obtener_habitaciones_disponibles(db: Session):
        return db.query(Habitacion).filter(Habitacion.disponible == True).all()

    @staticmethod
    def actualizar_estado(db: Session, habitacion_id: int, disponible: bool):
        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        if not habitacion:
            raise ValueError("Habitación no encontrada")
        try:
            habitacion.disponible = disponible
            db.commit()
            return habitacion
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def modificar_habitacion(db: Session, habitacion_id: int, numero: str, tipo: str, precio: float, disponible: bool):
        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        if not habitacion:
            raise ValueError("Habitación no encontrada")

        if not numero.strip():
            raise ValueError("El número de habitación no puede estar vacío")

        if tipo not in HabitacionCRUD.TIPOS_PERMITIDOS:
            raise ValueError(f"Tipo de habitación inválido. Debe ser uno de {HabitacionCRUD.TIPOS_PERMITIDOS}")

        if precio <= 0:
            raise ValueError("El precio debe ser un número positivo")

        # Verificar que no exista otra habitación con el mismo número
        existente = db.query(Habitacion).filter(Habitacion.numero == numero, Habitacion.id != habitacion_id).first()
        if existente:
            raise ValueError("Otra habitación ya tiene ese número")

        try:
            habitacion.numero = numero
            habitacion.tipo = tipo
            habitacion.precio = precio
            habitacion.disponible = disponible
            db.commit()
            return habitacion
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def verificar_habitaciones_en_bd(db: Session):
        habitaciones = db.query(Habitacion).all()
        for habitacion in habitaciones:
            print(f"ID: {habitacion.id}, Numero: {habitacion.numero}, Disponible: {habitacion.disponible}")

    @staticmethod
    def eliminar_habitacion(db: Session, habitacion_id: int):
        habitacion = db.query(Habitacion).filter(Habitacion.id == habitacion_id).first()
        if not habitacion:
            raise ValueError("Habitación no encontrada")
        try:
            db.delete(habitacion)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e