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
        # Obtener la reserva actual
        reserva_actual = self.db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva_actual:
            raise ValueError("Reserva no encontrada")

        campos_a_actualizar = {}

        # Solo agregar los campos que realmente cambiaron
        nuevo_huesped_id = kwargs.get("huesped_id")
        if nuevo_huesped_id is not None and nuevo_huesped_id != reserva_actual.huesped_id:
            campos_a_actualizar["huesped_id"] = nuevo_huesped_id

        nueva_habitacion_id = kwargs.get("habitacion_id")
        if nueva_habitacion_id is not None and nueva_habitacion_id != reserva_actual.habitacion_id:
            campos_a_actualizar["habitacion_id"] = nueva_habitacion_id

        nueva_fecha_entrada = kwargs.get("fecha_entrada")
        if nueva_fecha_entrada is not None and nueva_fecha_entrada != reserva_actual.fecha_entrada:
            campos_a_actualizar["fecha_entrada"] = nueva_fecha_entrada

        nueva_fecha_salida = kwargs.get("fecha_salida")
        if nueva_fecha_salida is not None and nueva_fecha_salida != reserva_actual.fecha_salida:
            campos_a_actualizar["fecha_salida"] = nueva_fecha_salida

        nuevo_tipo_precio = kwargs.get("tipo_precio")
        if nuevo_tipo_precio is not None and nuevo_tipo_precio != getattr(reserva_actual, "tipo_precio", None):
            campos_a_actualizar["tipo_precio"] = nuevo_tipo_precio

        nuevo_precio = kwargs.get("precio")
        if nuevo_precio is not None and nuevo_precio != reserva_actual.precio:
            campos_a_actualizar["precio"] = nuevo_precio

        nuevo_precio_final = kwargs.get("precio_final")
        if nuevo_precio_final is not None and nuevo_precio_final != reserva_actual.precio_final:
            campos_a_actualizar["precio_final"] = nuevo_precio_final

        if not campos_a_actualizar:
            # Nada que actualizar
            return reserva_actual

        from crud.reserva_crud import ReservaCRUD
        return ReservaCRUD.actualizar_reserva(self.db, reserva_id, **campos_a_actualizar)
    
    def guardar_reserva(self, reserva_obj):
        """Guarda un objeto Reserva ya construido"""
        self.db.add(reserva_obj)
        # marcar habitación como no disponible
        if reserva_obj.habitacion:
            reserva_obj.habitacion.disponible = False
        self.db.commit()



