from sqlalchemy.orm import Session
from  estructura.models_folder.models_disco import Evento
from typing import Optional

class EventoCRUD:
    @staticmethod
    def crear(db: Session, evento_data: dict) -> Evento:
        evento = Evento(**evento_data)
        db.add(evento)
        db.commit()
        db.refresh(evento)
        return evento

    @staticmethod
    def obtener_todos(db: Session) -> list[Evento]:
        return db.query(Evento).all()

    @staticmethod
    def obtener_por_id(db: Session, evento_id: int) -> Optional[Evento]:
        return db.query(Evento).filter(Evento.id == evento_id).first()

    @staticmethod
    def obtener_por_nombre(db: Session, nombre: str) -> Optional[Evento]:
        return db.query(Evento).filter(Evento.nombre.ilike(f"%{nombre}%")).first()

    @staticmethod
    def actualizar(db: Session, evento_id: int, nuevos_datos: dict) -> Optional[Evento]:
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if evento:
            for key, value in nuevos_datos.items():
                setattr(evento, key, value)
            db.commit()
            db.refresh(evento)
        return evento

    @staticmethod
    def eliminar(db: Session, evento_id: int) -> bool:
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if evento:
            db.delete(evento)
            db.commit()
            return True
        return False

    @staticmethod
    def filtrar_por_fecha(db: Session, fecha_inicio, fecha_fin) -> list[Evento]:
        return db.query(Evento).filter(Evento.fecha.between(fecha_inicio, fecha_fin)).all()