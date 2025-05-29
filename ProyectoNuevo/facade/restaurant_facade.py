from models_folder.models_restaurente import Cliente, Menu, Pedido
from sqlalchemy.orm import Session

class RestaurantFacade:
    def __init__(self, db: Session):
        self.db = db

    # ======== CLIENTE ========
    def crear_cliente(self, nombre: str, rut: str, email: str = None) -> Cliente:
        cliente = Cliente(nombre=nombre, rut=rut, email=email)
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def obtener_clientes(self):
        return self.db.query(Cliente).all()

    def obtener_cliente_por_rut(self, rut: str) -> Cliente:
        return self.db.query(Cliente).filter(Cliente.rut == rut).first()

    def actualizar_cliente(self, rut: str, nombre: str, email: str) -> Cliente:
        cliente = self.db.query(Cliente).filter(Cliente.rut == rut).first()
        if cliente:
            cliente.nombre = nombre
            cliente.email = email
            self.db.commit()
            return cliente
        else:
            raise ValueError("Cliente no encontrado")

    def eliminar_cliente(self, rut: str) -> bool:
        cliente = self.db.query(Cliente).filter(Cliente.rut == rut).first()
        if cliente:
            self.db.delete(cliente)
            self.db.commit()
            return True
        return False

    # ======== MENU ========
    def crear_menu(self, nombre: str, descripcion: str, precio: float, ing_necesarios: dict) -> Menu:
        menu = Menu(nombre=nombre, descripcion=descripcion, precio=precio, ing_necesarios=ing_necesarios)
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return menu

    def obtener_menus(self):
        return self.db.query(Menu).all()

    # ======== PEDIDO ========
    def registrar_pedido(self, rut_cliente: str, descripcion: str, total: float, fecha, menus_ids: list[int]) -> Pedido:
        cliente = self.obtener_cliente_por_rut(rut_cliente)
        if not cliente:
            raise ValueError("Cliente no encontrado")

        pedido = Pedido(
            descripcion=descripcion,
            total=total,
            fecha=fecha,
            cliente_rut=rut_cliente,
            menus=menus_ids
        )
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido