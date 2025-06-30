# facade/disco_facade.py

from estructura.crud.evento_crud import EventoCRUD
from estructura.crud.cliente_disco_crud import ClienteDiscotecaCRUD
from estructura.crud.trago_crud import TragoCRUD
from estructura.models_folder.models_disco import PedidoTrago

class DiscotecaFacade:
    def __init__(self, db):
        self.db = db

    # ==== EVENTOS ====
    def registrar_evento(self, evento_data):
        return EventoCRUD.crear(self.db, evento_data)

    def actualizar_evento(self, evento_id, nuevos_datos):
        return EventoCRUD.actualizar(self.db, evento_id, nuevos_datos)

    def eliminar_evento(self, evento_id):
        return EventoCRUD.eliminar(self.db, evento_id)

    def obtener_evento(self, evento_id):
        return EventoCRUD.obtener_por_id(self.db, evento_id)

    def listar_eventos(self):
        return EventoCRUD.obtener_todos(self.db)

    # ==== CLIENTES ====
    def registrar_cliente(self, cliente_data):
        return ClienteDiscotecaCRUD.crear(self.db, cliente_data)

    def editar_cliente(self, cliente_id, nuevos_datos):
        return ClienteDiscotecaCRUD.actualizar(self.db, cliente_id, nuevos_datos)

    def eliminar_cliente(self, cliente_id):
        return ClienteDiscotecaCRUD.eliminar(self.db, cliente_id)

    def actualizar_cliente(self, cliente_id, nuevos_datos):
        return ClienteDiscotecaCRUD.actualizar(self.db, cliente_id, nuevos_datos)

    def obtener_cliente_por_rut(self, rut):
        return ClienteDiscotecaCRUD.obtener_por_rut(self.db, rut)

    def listar_clientes(self):
        return ClienteDiscotecaCRUD.obtener_todos(self.db)

    # ==== TRAGOS ====
    def obtener_trago_por_nombre(self, nombre):
        return TragoCRUD.obtener_por_nombre(self.db, nombre)

    def actualizar_precio_trago(self, trago_id, nuevo_precio):
        return TragoCRUD.actualizar_precio(self.db, trago_id, nuevo_precio)

    def actualizar_stock_trago(self, trago_id, nuevo_stock):
        return TragoCRUD.actualizar_stock(self.db, trago_id, nuevo_stock)

    def cambiar_disponibilidad_trago(self, trago_id, disponible):
        return TragoCRUD.cambiar_disponibilidad(self.db, trago_id, disponible)

    def listar_tragos(self):
        return TragoCRUD.obtener_todos(self.db)

    # ==== PEDIDOS ====
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
