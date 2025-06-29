from typing import Dict

class PedidoBuilder:
    def __init__(self):
        self.cliente_id = None
        self.total = 0.0
        self.detalles = {}

    def set_cliente(self, cliente_id: int):
        self.cliente_id = cliente_id
        return self

    def add_detalle(self, trago_id: int, cantidad: int, precio_unitario: float):
        self.detalles[trago_id] = cantidad
        self.total += precio_unitario * cantidad
        return self

    def build(self) -> Dict:
        if self.cliente_id is None:
            raise ValueError("Cliente no definido para el pedido")
        if not self.detalles:
            raise ValueError("No hay detalles en el pedido")
        return {
            "cliente_id": self.cliente_id,
            "total": self.total,
            "detalles": self.detalles
        }
