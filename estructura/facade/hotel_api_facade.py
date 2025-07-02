import requests
from datetime import datetime
from typing import List, Optional, Dict, Any

class HotelAPIFacade:
    def __init__(self):
        self.API_URL = "http://localhost:8000/api/v1/hotel"
        
    # ===== HUÉSPEDES =====
    def crear_huesped(self, datos: Dict[str, Any]) -> tuple[bool, str]:
        """Crea un nuevo huésped"""
        try:
            huesped_data = {
                "nombre": datos['nombre'],
                "rut": datos['rut'],
                "email": datos.get('email'),
                "telefono": datos.get('telefono')
            }
            
            response = requests.post(f"{self.API_URL}/huespedes", json=huesped_data)
            
            if response.status_code == 201:
                return True, "Huésped creado exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al crear huésped: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    def obtener_huespedes(self) -> List[Any]:
        """Obtiene todos los huéspedes"""
        try:
            response = requests.get(f"{self.API_URL}/huespedes")
            
            if response.status_code == 200:
                huespedes_api = response.json()
                return [self._convertir_huesped_api(h) for h in huespedes_api]
            else:
                raise Exception(f"Error al obtener huéspedes: {response.json().get('detail', 'Error desconocido')}")
                
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
    
    def actualizar_huesped(self, huesped_id: int, datos: Dict[str, Any]) -> tuple[bool, str]:
        """Actualiza un huésped"""
        try:
            # Filtrar solo campos no nulos
            update_data = {k: v for k, v in datos.items() if v is not None}
            
            response = requests.put(f"{self.API_URL}/huespedes/{huesped_id}", json=update_data)
            
            if response.status_code == 200:
                return True, "Huésped actualizado exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al actualizar huésped: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    def eliminar_huesped(self, huesped_id: int) -> tuple[bool, str]:
        """Elimina un huésped"""
        try:
            response = requests.delete(f"{self.API_URL}/huespedes/{huesped_id}")
            
            if response.status_code == 200:
                return True, "Huésped eliminado exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al eliminar huésped: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    # ===== HABITACIONES =====
    def crear_habitacion(self, datos: Dict[str, Any]) -> tuple[bool, str]:
        """Crea una nueva habitación"""
        try:
            habitacion_data = {
                "numero": datos['numero'],
                "tipo": datos['tipo'],
                "precio": float(datos['precio']),
                "disponible": datos.get('disponible', True)
            }
            
            response = requests.post(f"{self.API_URL}/habitaciones", json=habitacion_data)
            
            if response.status_code == 201:
                return True, "Habitación creada exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al crear habitación: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    def obtener_habitaciones(self, disponible: Optional[bool] = None) -> List[Any]:
        """Obtiene todas las habitaciones"""
        try:
            params = {}
            if disponible is not None:
                params['disponible'] = disponible
                
            response = requests.get(f"{self.API_URL}/habitaciones", params=params)
            
            if response.status_code == 200:
                habitaciones_api = response.json()
                return [self._convertir_habitacion_api(h) for h in habitaciones_api]
            else:
                raise Exception(f"Error al obtener habitaciones: {response.json().get('detail', 'Error desconocido')}")
                
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
    
    # ===== RESERVAS =====
    def crear_reserva(self, datos: Dict[str, Any]) -> tuple[bool, str]:
        """Crea una nueva reserva"""
        try:
            reserva_data = {
                "huesped_id": int(datos['huesped_id']),
                "habitacion_id": int(datos['habitacion_id']),
                "fecha_entrada": datos['fecha_entrada'].isoformat(),
                "fecha_salida": datos['fecha_salida'].isoformat(),
                "precio_final": float(datos['precio_final']),
                "estado": datos.get('estado', 'Pendiente')
            }
            
            response = requests.post(f"{self.API_URL}/reservas", json=reserva_data)
            
            if response.status_code == 201:
                return True, "Reserva creada exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al crear reserva: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    def obtener_reservas(self, estado: Optional[str] = None) -> List[Any]:
        """Obtiene todas las reservas"""
        try:
            params = {}
            if estado:
                params['estado'] = estado
                
            response = requests.get(f"{self.API_URL}/reservas", params=params)
            
            if response.status_code == 200:
                reservas_api = response.json()
                return [self._convertir_reserva_api(r) for r in reservas_api]
            else:
                raise Exception(f"Error al obtener reservas: {response.json().get('detail', 'Error desconocido')}")
                
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
    
    def actualizar_reserva(self, reserva_id: int, datos: Dict[str, Any]) -> tuple[bool, str]:
        """Actualiza una reserva"""
        try:
            update_data = {}
            
            # Convertir fechas si están presentes
            if 'fecha_entrada' in datos and datos['fecha_entrada']:
                update_data['fecha_entrada'] = datos['fecha_entrada'].isoformat()
            if 'fecha_salida' in datos and datos['fecha_salida']:
                update_data['fecha_salida'] = datos['fecha_salida'].isoformat()
            if 'precio_final' in datos and datos['precio_final'] is not None:
                update_data['precio_final'] = float(datos['precio_final'])
            if 'estado' in datos and datos['estado']:
                update_data['estado'] = datos['estado']
            
            response = requests.put(f"{self.API_URL}/reservas/{reserva_id}", json=update_data)
            
            if response.status_code == 200:
                return True, "Reserva actualizada exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al actualizar reserva: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    def eliminar_reserva(self, reserva_id: int) -> tuple[bool, str]:
        """Elimina una reserva"""
        try:
            response = requests.delete(f"{self.API_URL}/reservas/{reserva_id}")
            
            if response.status_code == 200:
                return True, "Reserva eliminada exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al eliminar reserva: {error_detail}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
    
    # ===== MÉTODOS DE CONVERSIÓN =====
    def _convertir_huesped_api(self, huesped_api: Dict[str, Any]) -> Any:
        """Convierte datos de la API a formato esperado por la interfaz"""
        class HuespedDTO:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        return HuespedDTO(
            id=huesped_api['id'],
            nombre=huesped_api['nombre'],
            rut=huesped_api['rut'],
            email=huesped_api.get('email'),
            telefono=huesped_api.get('telefono'),
            fecha_registro=self._parse_fecha(huesped_api['fecha_registro'])
        )
    
    def _convertir_habitacion_api(self, habitacion_api: Dict[str, Any]) -> Any:
        """Convierte datos de habitación de la API"""
        class HabitacionDTO:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        return HabitacionDTO(
            id=habitacion_api['id'],
            numero=habitacion_api['numero'],
            tipo=habitacion_api['tipo'],
            precio=habitacion_api['precio'],
            disponible=habitacion_api['disponible']
        )
    
    def _convertir_reserva_api(self, reserva_api: Dict[str, Any]) -> Any:
        """Convierte datos de reserva de la API"""
        class ReservaDTO:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        return ReservaDTO(
            id=reserva_api['id'],
            huesped_id=reserva_api['huesped_id'],
            habitacion_id=reserva_api['habitacion_id'],
            fecha_entrada=self._parse_fecha(reserva_api['fecha_entrada']),
            fecha_salida=self._parse_fecha(reserva_api['fecha_salida']),
            precio_final=reserva_api['precio_final'],
            estado=reserva_api['estado'],
            fecha_reserva=self._parse_fecha(reserva_api['fecha_reserva']),
            # Campos adicionales si están disponibles
            huesped_nombre=reserva_api.get('huesped_nombre', ''),
            huesped_rut=reserva_api.get('huesped_rut', ''),
            habitacion_numero=reserva_api.get('habitacion_numero', ''),
            habitacion_tipo=reserva_api.get('habitacion_tipo', '')
        )
    
    def _parse_fecha(self, fecha_str: str) -> datetime:
        """Convierte string de fecha a datetime"""
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now()