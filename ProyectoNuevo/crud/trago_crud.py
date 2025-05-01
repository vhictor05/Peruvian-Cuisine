from sqlalchemy.orm import Session
from models_folder.models_disco import Trago
from typing import List, Optional

# Lista de tragos predefinidos
TRAGOS_PREDEFINIDOS = [
    {"nombre": "Piscola", "precio": 5000, "categoria": "Pisco"},
    {"nombre": "Pisco Sour", "precio": 6000, "categoria": "Pisco"},
    {"nombre": "Pisco con Redbull", "precio": 7000, "categoria": "Pisco"},
    {"nombre": "Cerveza Lata", "precio": 3000, "categoria": "Cerveza"},
    {"nombre": "Cerveza Botella", "precio": 3500, "categoria": "Cerveza"},
    {"nombre": "Roncola", "precio": 5500, "categoria": "Ron"},
    {"nombre": "Cubalibre", "precio": 6000, "categoria": "Ron"},
    {"nombre": "Jugo Natural", "precio": 2500, "categoria": "Bebida"},
    {"nombre": "Agua Mineral", "precio": 2000, "categoria": "Bebida"},
    {"nombre": "Bebida", "precio": 2500, "categoria": "Bebida"}
]

class TragoCRUD:
    @staticmethod
    def inicializar_tragos(db: Session):
        """Crea los tragos predefinidos si no existen"""
        for trago_data in TRAGOS_PREDEFINIDOS:
            if not db.query(Trago).filter(Trago.nombre == trago_data["nombre"]).first():
                trago = Trago(**trago_data)
                db.add(trago)
        db.commit()

    @staticmethod
    def obtener_todos(db: Session) -> List[Trago]:
        return db.query(Trago).filter(Trago.disponible == True).order_by(Trago.categoria, Trago.nombre).all()

    @staticmethod
    def obtener_por_id(db: Session, trago_id: int) -> Optional[Trago]:
        return db.query(Trago).filter(Trago.id == trago_id).first()

    @staticmethod
    def actualizar_precio(db: Session, trago_id: int, nuevo_precio: float) -> Optional[Trago]:
        trago = db.query(Trago).filter(Trago.id == trago_id).first()
        if trago:
            trago.precio = nuevo_precio
            db.commit()
            db.refresh(trago)
        return trago

    @staticmethod
    def cambiar_disponibilidad(db: Session, trago_id: int, disponible: bool) -> bool:
        trago = db.query(Trago).filter(Trago.id == trago_id).first()
        if trago:
            trago.disponible = disponible
            db.commit()
            return True
        return False