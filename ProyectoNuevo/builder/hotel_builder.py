from datetime import datetime
from models_folder.models_hotel import Huesped, Habitacion, Reserva

class HotelBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._producto = {}

    # Huesped
    def set_huesped(self, nombre, rut, email=None, telefono=None):
        self._producto['huesped'] = Huesped(
            nombre=nombre,
            rut=rut,
            email=email,
            telefono=telefono
        )
        return self

    # Habitacion
    def set_habitacion(self, numero, tipo, precio):
        self._producto['habitacion'] = Habitacion(
            numero=numero,
            tipo=tipo,
            precio=precio,
            disponible=True
        )
        return self

    # Reserva
    def set_reserva(self, huesped, habitacion, fecha_entrada, fecha_salida, precio_final):
        self._producto['reserva'] = Reserva(
            huesped_id=huesped.id,
            habitacion_id=habitacion.id,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            precio_final=precio_final,
            estado="Activa"
        )
        return self

    def get_result(self):
        result = self._producto
        self.reset()
        return result


class HotelDirector:
    def __init__(self, builder: HotelBuilder):
        self._builder = builder

    def construir_reserva_basica(self, huesped, habitacion, fecha_entrada, fecha_salida, precio_final):
        return self._builder.set_reserva(
            huesped, habitacion, fecha_entrada, fecha_salida, precio_final
        ).get_result()

    def construir_habitacion_default(self):
        return self._builder.set_habitacion("101", "Mediana", 50000).get_result()
