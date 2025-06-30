from sqlalchemy.orm import Session
from  estructura.models_folder.models_restaurente import Mesa
from typing import Optional

class MesaCRUD:
    @staticmethod
    def crear(db: Session, mesa_data: dict) -> Mesa:
        mesa = Mesa(**mesa_data)
        db.add(mesa)
        db.commit()
        db.refresh(mesa)
        return mesa

    @staticmethod
    def obtener_todas(db: Session) -> list[Mesa]:
        return db.query(Mesa).all()

    @staticmethod
    def obtener_por_id(db: Session, mesa_id: int) -> Optional[Mesa]:
        return db.query(Mesa).filter(Mesa.id == mesa_id).first()

    @staticmethod
    def obtener_por_numero(db: Session, numero: str) -> Optional[Mesa]:
        return db.query(Mesa).filter(Mesa.numero == numero).first()

    @staticmethod
    def buscar_por_ubicacion(db: Session, ubicacion: str) -> list[Mesa]:
        return db.query(Mesa).filter(Mesa.ubicacion.ilike(f"%{ubicacion}%")).all()

    @staticmethod
    def actualizar(db: Session, mesa_id: int, nuevos_datos: dict) -> Optional[Mesa]:
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if mesa:
            for key, value in nuevos_datos.items():
                setattr(mesa, key, value)
            db.commit()
            db.refresh(mesa)
        return mesa

    @staticmethod
    def eliminar(db: Session, mesa_id: int) -> bool:
        mesa = db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if mesa:
            db.delete(mesa)
            db.commit()
            return True
        return False