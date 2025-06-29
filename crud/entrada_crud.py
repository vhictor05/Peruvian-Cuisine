from sqlalchemy.orm import Session
from models_folder.models_disco import Entrada
from typing import Optional
from datetime import datetime

class EntradaCRUD:
    @staticmethod
    def crear(db: Session, entrada_data: dict) -> Entrada:
        entrada = Entrada(**entrada_data)
        db.add(entrada)
        db.commit()
        db.refresh(entrada)
        return entrada

    @staticmethod
    def obtener_todos(db: Session) -> list[Entrada]:
        return db.query(Entrada).all()

    @staticmethod
    def obtener_por_id(db: Session, entrada_id: int) -> Optional[Entrada]:
        return db.query(Entrada).filter(Entrada.id == entrada_id).first()

    @staticmethod
    def obtener_por_cliente(db: Session, cliente_id: int) -> list[Entrada]:
        return db.query(Entrada).filter(Entrada.cliente_id == cliente_id).all()

    @staticmethod
    def obtener_por_evento(db: Session, evento_id: int) -> list[Entrada]:
        return db.query(Entrada).filter(Entrada.evento_id == evento_id).all()

    @staticmethod
    def filtrar_por_fecha(db: Session, fecha_inicio: datetime, fecha_fin: datetime) -> list[Entrada]:
        return db.query(Entrada).filter(Entrada.fecha_compra.between(fecha_inicio, fecha_fin)).all()

    @staticmethod
    def actualizar(db: Session, entrada_id: int, nuevos_datos: dict) -> Optional[Entrada]:
        entrada = db.query(Entrada).filter(Entrada.id == entrada_id).first()
        if entrada:
            for key, value in nuevos_datos.items():
                setattr(entrada, key, value)
            db.commit()
            db.refresh(entrada)
        return entrada

    @staticmethod
    def eliminar(db: Session, entrada_id: int) -> bool:
        entrada = db.query(Entrada).filter(Entrada.id == entrada_id).first()
        if entrada:
            db.delete(entrada)
            db.commit()
            return True
        return False
