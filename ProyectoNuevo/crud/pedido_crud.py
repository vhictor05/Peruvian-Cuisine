import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Pedido, Cliente, Ingrediente, Menu
from crud.menu_crud import MenuCRUD

class PedidoCRUD:

    @staticmethod
    def crear_pedido(db: Session, cliente_rut: str, descripcion: str, total: float, fecha: str, menus: list):
        try:
            cliente = db.query(Cliente).filter_by(rut=cliente_rut).first()
            if not cliente:
                logging.error(f"No se encontró el cliente con el RUT '{cliente_rut}'.")
                return None

            # Verificar disponibilidad de ingredientes
            for menu in menus:
                if not MenuCRUD.verificar_disponibilidad_menu(db, menu["id"]):
                    logging.error(f"No hay suficientes ingredientes para el menú con ID '{menu['id']}'.")
                    return None

            # Descontar ingredientes necesarios
            for menu in menus:
                menu_obj = MenuCRUD.get_menu_by_id(db, menu["id"])
                for ing_nombre, cantidad in menu_obj.ing_necesarios.items():
                    ingrediente = db.query(Ingrediente).filter(Ingrediente.nombre == ing_nombre).first()
                    if ingrediente:
                        ingrediente.cantidad -= cantidad * menu["cantidad"]

            pedido = Pedido(descripcion=descripcion, total=total, fecha=fecha, cliente=cliente, menus=menus)
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            return pedido

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al crear pedido: {e}")
            return None

    @staticmethod
    def leer_pedidos(db: Session):
        try:
            return db.query(Pedido).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al leer pedidos: {e}")
            return []

    @staticmethod
    def actualizar_pedido(db: Session, pedido_id: int, nueva_descripcion: str):
        try:
            pedido = db.query(Pedido).get(pedido_id)
            if not pedido:
                logging.error(f"No se encontró el pedido con el ID '{pedido_id}'.")
                return None

            pedido.descripcion = nueva_descripcion
            db.commit()
            db.refresh(pedido)
            return pedido

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al actualizar pedido: {e}")
            return None

    @staticmethod
    def get_ingredientes_usados(db: Session, pedido: Pedido):
        ingredientes_usados = {}
        for menu in pedido.menus:
            menu_obj = db.query(Menu).filter(Menu.id == menu["id"]).first()
            for ing_nombre, cantidad in menu_obj.ing_necesarios.items():
                if ing_nombre in ingredientes_usados:
                    ingredientes_usados[ing_nombre] += cantidad * menu["cantidad"]
                else:
                    ingredientes_usados[ing_nombre] = cantidad * menu["cantidad"]
        return ingredientes_usados

    @staticmethod
    def borrar_pedido(db: Session, pedido_id: int):
        try:
            pedido = db.query(Pedido).get(pedido_id)
            if pedido:
                ingredientes_usados = PedidoCRUD.get_ingredientes_usados(db, pedido)
                for ing_nombre, cantidad in ingredientes_usados.items():
                    ingrediente = db.query(Ingrediente).filter(Ingrediente.nombre == ing_nombre).first()
                    if ingrediente:
                        ingrediente.cantidad += cantidad
                db.delete(pedido)
                db.commit()
                return pedido

            logging.error(f"No se encontró el pedido con el ID '{pedido_id}'.")
            return None

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al borrar pedido: {e}")
            return None

    @staticmethod
    def filtrar_pedidos_por_cliente(db: Session, cliente_rut: str):
        try:
            return db.query(Pedido).filter(Pedido.cliente_rut == cliente_rut).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al filtrar pedidos por cliente: {e}")
            return []

    @staticmethod
    def filtrar_pedidos_por_fecha(db: Session, fecha: str):
        try:
            return db.query(Pedido).filter(Pedido.fecha == fecha).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al filtrar pedidos por fecha: {e}")
            return []

    @staticmethod
    def filtrar_pedidos_por_monto_mayor_que(db: Session, monto: float):
        try:
            return db.query(Pedido).filter(Pedido.total > monto).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al filtrar pedidos por monto: {e}")
            return []
