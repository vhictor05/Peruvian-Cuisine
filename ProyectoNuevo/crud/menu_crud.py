import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models import Menu, MenuIngrediente, Ingrediente

class MenuCRUD:

    @staticmethod
    def create_menu(db: Session, nombre: str, descripcion: str, precio: float, ingredientes: list):
        try:
            ing_necesarios = {}
            for ingrediente in ingredientes:
                ingrediente_existente = db.query(Ingrediente).filter(Ingrediente.id == ingrediente["id"]).first()
                if not ingrediente_existente:
                    logging.error(f"Ingrediente con ID '{ingrediente['id']}' no existe.")
                    return None
                if ingrediente_existente.cantidad < ingrediente["cantidad"]:
                    logging.error(f"No hay suficiente cantidad del ingrediente '{ingrediente_existente.nombre}'.")
                    return None
                ing_necesarios[ingrediente_existente.nombre] = ingrediente["cantidad"]

            menu = Menu(nombre=nombre, descripcion=descripcion, precio=precio, ing_necesarios=ing_necesarios)
            db.add(menu)
            db.commit()

            for ingrediente in ingredientes:
                menu_ingrediente = MenuIngrediente(
                    menu_id=menu.id,
                    ingrediente_id=ingrediente["id"],
                    cantidad=ingrediente["cantidad"]
                )
                db.add(menu_ingrediente)
                

            db.commit()
            db.refresh(menu)
            return menu

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al crear menú: {e}")
            return None

    @staticmethod
    def get_menus(db: Session):
        try:
            return db.query(Menu).all()
        except SQLAlchemyError as e:
            logging.error(f"Error al obtener menús: {e}")
            return []

    @staticmethod
    def get_menu_by_nombre(db: Session, nombre: str):
        try:
            return db.query(Menu).filter(Menu.nombre == nombre).first()
        except SQLAlchemyError as e:
            logging.error(f"Error al buscar menú por nombre '{nombre}': {e}")
            return None

    @staticmethod
    def get_menu_by_id(db: Session, menu_id: int):
        try:
            return db.query(Menu).filter(Menu.id == menu_id).first()
        except SQLAlchemyError as e:
            logging.error(f"Error al buscar menú por ID '{menu_id}': {e}")
            return None

    @staticmethod
    def update_menu(db: Session, menu_id: int, nuevo_nombre: str = None, nueva_descripcion: str = None, nuevo_precio: float = None, nuevos_ingredientes: list = None):
        try:
            menu = db.query(Menu).get(menu_id)
            if not menu:
                logging.error(f"No se encontró el menú con el ID '{menu_id}'.")
                return None

            if nuevo_nombre:
                menu.nombre = nuevo_nombre
            if nueva_descripcion:
                menu.descripcion = nueva_descripcion
            if nuevo_precio is not None:
                menu.precio = nuevo_precio

            if nuevos_ingredientes is not None:
                db.query(MenuIngrediente).filter_by(menu_id=menu_id).delete()
                for ingrediente in nuevos_ingredientes:
                    nuevo_menu_ingrediente = MenuIngrediente(
                        menu_id=menu_id,
                        ingrediente_id=ingrediente["id"],
                        cantidad=ingrediente["cantidad"]
                    )
                    db.add(nuevo_menu_ingrediente)

            db.commit()
            db.refresh(menu)
            return menu

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al actualizar menú: {e}")
            return None

    @staticmethod
    def delete_menu(db: Session, menu_id: int):
        try:
            menu = db.query(Menu).get(menu_id)
            if menu:
                # Return ingredients to the database
                menu_ingredientes = db.query(MenuIngrediente).filter_by(menu_id=menu_id).all()
                for menu_ingrediente in menu_ingredientes:
                    ingrediente = db.query(Ingrediente).filter_by(id=menu_ingrediente.ingrediente_id).first()
                    if ingrediente:
                        ingrediente.cantidad += menu_ingrediente.cantidad
                    db.delete(menu_ingrediente)
                
                db.delete(menu)
                db.commit()
                return menu

            logging.error(f"No se encontró el menú con el ID '{menu_id}'.")
            return None

        except SQLAlchemyError as e:
            db.rollback()
            logging.error(f"Error al eliminar menú: {e}")
            return None

    @staticmethod
    def verificar_disponibilidad_menu(db: Session, menu_id: int):
        try:
            menu = db.query(Menu).get(menu_id)
            if not menu:
                logging.error(f"No se encontró el menú con el ID '{menu_id}'.")
                return False

            for ingrediente_nombre, cantidad_necesaria in menu.ing_necesarios.items():
                ingrediente = db.query(Ingrediente).filter(Ingrediente.nombre == ingrediente_nombre).first()
                if not ingrediente or ingrediente.cantidad < cantidad_necesaria:
                    logging.error(f"No hay suficiente cantidad del ingrediente '{ingrediente_nombre}'.")
                    return False

            return True

        except SQLAlchemyError as e:
            logging.error(f"Error al verificar disponibilidad del menú: {e}")
            return False
