from datetime import datetime
from estructura.models_folder.models_hotel import Reserva, Huesped, Habitacion

class HotelBuilder:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._reserva_data = {
            "huesped": None,
            "habitacion": None,
            "fecha_entrada": None,
            "fecha_salida": None,
            "precio_final": None,
            "estado": "Pendiente",
        }
    
    def set_reserva(self, huesped: Huesped, habitacion: Habitacion, 
                   fecha_entrada: datetime, fecha_salida: datetime,
                   precio_final: float):
        """Configura los datos básicos de la reserva"""
        self._reserva_data.update({
            "huesped": huesped,
            "habitacion": habitacion,
            "fecha_entrada": fecha_entrada,
            "fecha_salida": fecha_salida,
            "precio_final": precio_final
        })
        return self
    
    def set_estado(self, estado: str):
        """Configura el estado de la reserva"""
        self._reserva_data["estado"] = estado
        return self
    
    def get_result(self):
        """Construye y retorna el objeto Reserva con los datos configurados"""
        if None in [self._reserva_data["huesped"], self._reserva_data["habitacion"], 
                   self._reserva_data["fecha_entrada"], self._reserva_data["fecha_salida"]]:
            raise ValueError("Faltan datos esenciales para crear la reserva")
        
        reserva = Reserva(
            huesped_id=self._reserva_data["huesped"].id,
            habitacion_id=self._reserva_data["habitacion"].id,
            fecha_entrada=self._reserva_data["fecha_entrada"],
            fecha_salida=self._reserva_data["fecha_salida"],
            precio_final=self._reserva_data["precio_final"],
            estado=self._reserva_data["estado"],
        )
        
        # Mantener relaciones para acceso fácil
        reserva.huesped = self._reserva_data["huesped"]
        reserva.habitacion = self._reserva_data["habitacion"]
        
        self.reset()
        return {"reserva": reserva, "data": self._reserva_data}