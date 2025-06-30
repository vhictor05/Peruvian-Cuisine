
from sqlalchemy.orm import Session
from  estructura.models_folder.models_disco import Evento, ClienteDiscoteca, Mesa, ReservaMesa

class ReservaMesaCRUD:
    @staticmethod
    def crear(db: Session, reserva_data: dict) -> ReservaMesa:
        reserva = ReservaMesa(**reserva_data)
        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        return reserva

    @staticmethod
    def obtener_todas(db: Session) -> list[ReservaMesa]:
        return db.query(ReservaMesa).all()

    @staticmethod
    def obtener_por_id(db: Session, reserva_id: int) -> ReservaMesa:
        return db.query(ReservaMesa).filter(ReservaMesa.id == reserva_id).first()

    @staticmethod
    def eliminar(db: Session, reserva_id: int) -> bool:
        reserva = db.query(ReservaMesa).filter(ReservaMesa.id == reserva_id).first()
        if reserva:
            db.delete(reserva)
            db.commit()
            return True
        return False

    @staticmethod
    def actualizar_estado(db: Session, reserva_id: int, nuevo_estado: str) -> ReservaMesa:
        reserva = db.query(ReservaMesa).filter(ReservaMesa.id == reserva_id).first()
        if reserva:
            reserva.estado = nuevo_estado
            db.commit()
            db.refresh(reserva)
        return reserva

    @staticmethod
    def obtener_por_cliente(db: Session, cliente_id: int) -> list[ReservaMesa]:
        return db.query(ReservaMesa).filter(ReservaMesa.cliente_id == cliente_id).all()

    @staticmethod
    def obtener_por_evento(db: Session, evento_id: int) -> list[ReservaMesa]:
        return db.query(ReservaMesa).filter(ReservaMesa.evento_id == evento_id).all()
