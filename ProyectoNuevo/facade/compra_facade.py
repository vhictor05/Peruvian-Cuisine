# compra_facade.py

from crud.pedido_crud import PedidoCRUD
from crud.ingrediente_crud import IngredienteCRUD
from crud.menu_crud import MenuCRUD
from fpdf import FPDF
from generar_boleta import Generarboleta  
from datetime import datetime

class CompraFacade:
    def __init__(self, db_session, observer_manager=None):
        self.db = db_session
        self.observer_manager = observer_manager

    def verificar_ingredientes(self, menu, cantidad):
        for item in menu.ingredientes:
            ingrediente = IngredienteCRUD.get_ingrediente_by_id(self.db, item.ingrediente_id)
            if not ingrediente or ingrediente.cantidad < item.cantidad * cantidad:
                return False
        return True

    def procesar_compra(self, cliente_rut, carrito):
        total = sum(item[2] for item in carrito)
        menus = []

        for menu_nombre, cantidad, _ in carrito:
            menu = MenuCRUD.get_menu_by_nombre(self.db, menu_nombre)
            if not menu or not self.verificar_ingredientes(menu, cantidad):
                return None
            
            # Descontar ingredientes
            for item in menu.ingredientes:
                ingrediente = IngredienteCRUD.get_ingrediente_by_id(self.db, item.ingrediente_id)
                if ingrediente:
                    cantidad_usada = item.cantidad * cantidad
                    nueva_cantidad = ingrediente.cantidad - cantidad_usada
                    if self.observer_manager:
                        self.observer_manager.notify_inventory_change(ingrediente.nombre, ingrediente.cantidad, nueva_cantidad)
                    ingrediente.cantidad = nueva_cantidad

            menus.append({"id": menu.id, "cantidad": cantidad})

        nuevo_pedido = PedidoCRUD.crear_pedido(
            self.db,
            cliente_rut=cliente_rut,
            descripcion="Compra Realizada",
            total=total,
            fecha=datetime.now(),
            menus=menus
        )

        if nuevo_pedido:
            if self.observer_manager:
                self.observer_manager.notify_new_order(nuevo_pedido)

            Generarboleta(nuevo_pedido, self.db).generar_boleta()
            self.db.add(nuevo_pedido)
            self.db.commit()
            return nuevo_pedido
        
        return None
