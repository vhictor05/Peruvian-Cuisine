from crud.huesped_crud import HuespedCRUD
from crud.habitacion_crud import HabitacionCRUD
from crud.reserva_crud import ReservaCRUD
from models_folder.models_hotel import Reserva, Habitacion, Huesped

class HotelFacade:
    def __init__(self, db_session):
        self.db = db_session

    # ===== Huéspedes =====
    def crear_huesped(self, *, nombre, rut, email=None, telefono=None):
        return HuespedCRUD.crear_huesped(self.db, nombre, rut, email, telefono)

    def obtener_huesped_por_rut(self, rut):
        return HuespedCRUD.obtener_huesped_por_rut(self.db, rut)

    def actualizar_huesped(self, huesped_id, **kwargs):
        return HuespedCRUD.actualizar_huesped(self.db, huesped_id, **kwargs)

    def eliminar_huesped(self, huesped_id):
        return HuespedCRUD.eliminar_huesped(self.db, huesped_id)

    # ===== Habitaciones =====
    def crear_habitacion(self, numero, tipo, precio):
        return HabitacionCRUD.crear_habitacion(self.db, numero, tipo, precio)

    def obtener_habitacion_por_numero(self, numero):
        return HabitacionCRUD.obtener_habitacion_por_numero(self.db, numero)

    def obtener_habitaciones_disponibles(self):
        return HabitacionCRUD.obtener_habitaciones_disponibles(self.db)

    def actualizar_estado_habitacion(self, habitacion_id, disponible):
        return HabitacionCRUD.actualizar_estado(self.db, habitacion_id, disponible)

    def modificar_habitacion(self, habitacion_id, numero, tipo, precio, disponible):
        return HabitacionCRUD.modificar_habitacion(self.db, habitacion_id, numero, tipo, precio, disponible)

    def eliminar_habitacion(self, habitacion_id):
        return HabitacionCRUD.eliminar_habitacion(self.db, habitacion_id)

    # ===== Reservas =====
    def crear_reserva(self, huesped_id, habitacion_id, fecha_entrada, fecha_salida, precio_final):
        return ReservaCRUD.crear_reserva(self.db, huesped_id, habitacion_id, fecha_entrada, fecha_salida, precio_final)

    def obtener_todas_reservas(self):
        return ReservaCRUD.obtener_todas_reservas(self.db)

    def eliminar_reserva(self, reserva_id):
        reserva = self.db.query(Reserva).get(reserva_id)
        if not reserva:
            raise ValueError("La reserva no existe")
        # Marca la habitación como disponible
        habitacion = self.db.query(Habitacion).get(reserva.habitacion_id)
        if habitacion:
            habitacion.disponible = True
        self.db.delete(reserva)
        self.db.commit()
        return True

    def actualizar_reserva(self, reserva_id, **kwargs):
        return ReservaCRUD.actualizar_reserva(self.db, reserva_id, **kwargs)
    
    def guardar_reserva(self, reserva_obj):
        """Guarda un objeto Reserva ya construido"""
        self.db.add(reserva_obj)
        # marcar habitación como no disponible
        if reserva_obj.habitacion:
            reserva_obj.habitacion.disponible = False
        self.db.commit()



