# facade/discoteca_facade.py
from crud.evento_crud import EventoCRUD
from crud.cliente_disco_crud import ClienteDiscotecaCRUD
from crud.trago_crud import TragoCRUD
from models import PedidoTrago

class DiscotecaFacade:
    def __init__(self, db):
        self.db = db

    # ================== EVENTOS ==================

    def registrar_evento(self, datos):
        return EventoCRUD.crear(self.db, datos)

    def listar_eventos(self):
        return EventoCRUD.obtener_todos(self.db)

    # ================== CLIENTES ==================

    def registrar_cliente(self, datos):
        return ClienteDiscotecaCRUD.crear(self.db, datos)

    def listar_clientes(self):
        return ClienteDiscotecaCRUD.obtener_todos(self.db)

    def obtener_cliente_por_rut(self, rut):
        return ClienteDiscotecaCRUD.obtener_por_rut(self.db, rut)

    # ================== TRAGOS ==================

    def listar_tragos(self):
        return TragoCRUD.obtener_todos(self.db)

    def actualizar_precio_trago(self, trago_id, nuevo_precio):
        return TragoCRUD.actualizar_precio(self.db, trago_id, nuevo_precio)

    def cambiar_disponibilidad_trago(self, trago_id, disponible):
        return TragoCRUD.cambiar_disponibilidad(self.db, trago_id, disponible)

    # ================== PEDIDOS ==================

    def crear_pedido(self, cliente_id, total, detalles):
        pedido = PedidoTrago(
            cliente_id=cliente_id,
            total=total,
            detalles=detalles,
            estado="Confirmado"
        )
        self.db.add(pedido)
        self.db.commit()
        return pedido
    
    # Obtener trago por nombre
def obtener_trago_por_nombre(self, nombre):
    return self.db.query(Trago).filter(Trago.nombre == nombre).first()

# Listar todos los tragos
def listar_tragos(self):
    return TragoCRUD.obtener_todos(self.db)

# Actualizar precio
def actualizar_precio_trago(self, trago_id, nuevo_precio):
    return TragoCRUD.actualizar_precio(self.db, trago_id, nuevo_precio)

# Cambiar disponibilidad
def cambiar_disponibilidad_trago(self, trago_id, disponible):
    return TragoCRUD.cambiar_disponibilidad(self.db, trago_id, disponible)

