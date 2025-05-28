from sqlalchemy.orm import Session
from models_folder.models_disco import Trago
from typing import List, Optional

# Lista de tragos predefinidos
TRAGOS_PREDEFINIDOS = [
    {"nombre": "Piscola", "precio": 5000, "categoria": "Pisco", "stock": 100},
    {"nombre": "Pisco Sour", "precio": 6000, "categoria": "Pisco", "stock": 50},
    {"nombre": "Pisco con Redbull", "precio": 7000, "categoria": "Pisco", "stock": 30},
    {"nombre": "Cerveza Lata", "precio": 3000, "categoria": "Cerveza", "stock": 80},
    {"nombre": "Cerveza Botella", "precio": 3500, "categoria": "Cerveza", "stock": 80},
    {"nombre": "Roncola", "precio": 5500, "categoria": "Ron", "stock": 80},
    {"nombre": "Cubalibre", "precio": 6000, "categoria": "Ron", "stock": 80},
    {"nombre": "Jugo Natural", "precio": 2500, "categoria": "Bebida", "stock": 80},
    {"nombre": "Agua Mineral", "precio": 2000, "categoria": "Bebida", "stock": 80},
    {"nombre": "Bebida", "precio": 2500, "categoria": "Bebida", "stock": 80}
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
        return db.query(Trago).order_by(Trago.categoria, Trago.nombre).all()

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
            # No permitir marcar como disponible si el stock es 0
            if disponible and trago.stock <= 0:
                return False
            trago.disponible = disponible
            db.commit()
            return True
        return False

    @staticmethod
    def actualizar_stock(db: Session, trago_id: int, nuevo_stock: int) -> bool:
        trago = db.query(Trago).filter(Trago.id == trago_id).first()
        if trago:
            trago.stock = nuevo_stock
            # Si el stock llega a 0, marcar como no disponible
            if nuevo_stock <= 0:
                trago.disponible = False
            db.commit()
            return True
        return False