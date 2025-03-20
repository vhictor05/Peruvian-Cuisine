from database import SessionLocal
from crud.cliente_crud import ClienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD
from crud.ingrediente_crud import IngredienteCRUD

db = SessionLocal()

# Crear cliente
cliente = ClienteCRUD.create_cliente(db, nombre="Juan Pérez", email="juan@example.com")

# Crear ingrediente
ingrediente = IngredienteCRUD.create_ingrediente(db, nombre="Tomate", tipo="Vegetal", cantidad=10, unidad="kg")

# Crear menú
menu = MenuCRUD.create_menu(db, nombre="Ensalada Mixta", descripcion="Deliciosa ensalada con tomate y lechuga", precio=10.0, ingredientes=[{"id": ingrediente.id, "cantidad": 2}])

# Crear pedido
pedido = PedidoCRUD.crear_pedido(db, descripcion="Pedido de ensalada", total=100, fecha="2024-11-26", cliente_rut=cliente.rut, menus=[{"id": menu.id, "cantidad": 1}])
