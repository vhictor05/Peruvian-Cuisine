import requests
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class HotelAPIFacade:
    def __init__(self):
        self.API_URL = "http://localhost:8000/api/v1/hotel"
        
    # ===== MÉTODOS COMPATIBLES CON LA INTERFAZ EXISTENTE =====
    
    # Métodos de Huéspedes
    def crear_huesped(self, nombre: str, rut: str, email: str = None, telefono: str = None):
        """Método compatible con la interfaz existente"""
        try:
            datos = {
                'nombre': nombre.strip() if nombre else '',
                'rut': rut.strip() if rut else '',
                'email': email.strip() if email else None,
                'telefono': telefono.strip() if telefono else None
            }
            
            # Validaciones básicas del lado del cliente
            if not datos['nombre']:
                raise ValueError("El nombre es requerido")
            if not datos['rut']:
                raise ValueError("El RUT es requerido")
            
            success, message = self._crear_huesped_api(datos)
            if not success:
                raise Exception(message)
            return True
            
        except Exception as e:
            logger.error(f"Error en crear_huesped: {str(e)}")
            raise

    def obtener_todos_huespedes(self):
        """Obtiene todos los huéspedes"""
        try:
            return self._obtener_huespedes_api()
        except Exception as e:
            logger.error(f"Error en obtener_todos_huespedes: {str(e)}")
            raise Exception(f"Error al obtener huéspedes: {str(e)}")

    def obtener_huesped_por_rut(self, rut: str):
        """Obtiene un huésped por RUT"""
        try:
            huespedes = self.obtener_todos_huespedes()
            for huesped in huespedes:
                if huesped.rut == rut:
                    return huesped
            return None
        except Exception as e:
            logger.error(f"Error en obtener_huesped_por_rut: {str(e)}")
            raise
    
    def eliminar_huesped(self, huesped_id: int):
        """Elimina un huésped"""
        try:
            success, message = self._eliminar_huesped_api(huesped_id)
            if not success:
                raise Exception(message)
            return True
        except Exception as e:
            logger.error(f"Error en eliminar_huesped: {str(e)}")
            raise
    
    # Métodos de Habitaciones
    def crear_habitacion(self, numero: str, tipo: str, precio: float):
        """Crea una nueva habitación"""
        datos = {
            'numero': numero,
            'tipo': tipo,
            'precio': precio,
            'disponible': True
        }
        success, message = self._crear_habitacion_api(datos)
        if not success:
            raise Exception(message)
        return True
    
    def obtener_todas_habitaciones(self):
        """Obtiene todas las habitaciones"""
        try:
            return self._obtener_habitaciones_api()
        except Exception as e:
            raise Exception(f"Error al obtener habitaciones: {str(e)}")
    
    def obtener_habitaciones_disponibles(self):
        """Obtiene habitaciones disponibles"""
        try:
            return self._obtener_habitaciones_api(disponible=True)
        except Exception as e:
            raise Exception(f"Error al obtener habitaciones disponibles: {str(e)}")
    
    def modificar_habitacion(self, habitacion_id: int, numero: str, tipo: str, precio: float, disponible: bool):
        """Modifica una habitación"""
        datos = {
            'numero': numero,
            'tipo': tipo,
            'precio': precio,
            'disponible': disponible
        }
        success, message = self._actualizar_habitacion_api(habitacion_id, datos)
        if not success:
            raise Exception(message)
        return True
    
    def eliminar_habitacion(self, habitacion_id: int):
        """Elimina una habitación"""
        success, message = self._eliminar_habitacion_api(habitacion_id)
        if not success:
            raise Exception(message)
        return True
    
    # Métodos de Reservas
    def crear_reserva(self, huesped_id: int, habitacion_id: int, fecha_entrada, fecha_salida, precio_final: float):
        """Crea una nueva reserva"""
        datos = {
            'huesped_id': huesped_id,
            'habitacion_id': habitacion_id,
            'fecha_entrada': fecha_entrada,
            'fecha_salida': fecha_salida,
            'precio_final': precio_final
        }
        success, message = self._crear_reserva_api(datos)
        if not success:
            raise Exception(message)
        return True
    
    def obtener_todas_reservas(self):
        """Obtiene todas las reservas"""
        try:
            return self._obtener_reservas_api()
        except Exception as e:
            raise Exception(f"Error al obtener reservas: {str(e)}")
    
    def actualizar_reserva(self, reserva_id: int, **kwargs):
        """Actualiza una reserva"""
        success, message = self._actualizar_reserva_api(reserva_id, kwargs)
        if not success:
            raise Exception(message)
        return True
    
    def eliminar_reserva(self, reserva_id: int):
        """Elimina una reserva"""
        success, message = self._eliminar_reserva_api(reserva_id)
        if not success:
            raise Exception(message)
        return True
    
    # ===== MÉTODOS INTERNOS DE LA API =====
    
    def _crear_huesped_api(self, datos: Dict[str, Any]) -> tuple[bool, str]:
        """Crea un nuevo huésped"""
        try:
            logger.info(f"Enviando solicitud de creación de huésped: {datos}")
            
            huesped_data = {
                "nombre": str(datos['nombre']).strip(),
                "rut": str(datos['rut']).strip(),
                "email": datos.get('email'),
                "telefono": datos.get('telefono')
            }
            
            # Limpiar campos vacíos
            if huesped_data['email'] == '':
                huesped_data['email'] = None
            if huesped_data['telefono'] == '':
                huesped_data['telefono'] = None
            
            response = requests.post(
                f"{self.API_URL}/huespedes", 
                json=huesped_data,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            logger.info(f"Respuesta API: {response.status_code}")
            
            if response.status_code == 201:
                return True, "Huésped creado exitosamente"
            else:
                try:
                    error_detail = response.json().get('detail', 'Error desconocido')
                except:
                    error_detail = response.text
                logger.error(f"Error de API: {error_detail}")
                return False, f"Error al crear huésped: {error_detail}"
                
        except requests.ConnectionError:
            error_msg = "No se pudo conectar con la API. Verifique que el servidor esté ejecutándose."
            logger.error(error_msg)
            return False, error_msg
        except requests.Timeout:
            error_msg = "Tiempo de espera agotado al conectar con la API."
            logger.error(error_msg)
            return False, error_msg
        except requests.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _obtener_huespedes_api(self) -> List[Any]:
        """Obtiene todos los huéspedes"""
        try:
            response = requests.get(f"{self.API_URL}/huespedes", timeout=30)
            
            if response.status_code == 200:
                huespedes_api = response.json()
                return [self._convertir_huesped_api(h) for h in huespedes_api]
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                raise Exception(f"Error al obtener huéspedes: {error_detail}")
                
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
    
    def _eliminar_huesped_api(self, huesped_id: int) -> tuple[bool, str]:
        """Elimina un huésped"""
        try:
            response = requests.delete(f"{self.API_URL}/huespedes/{huesped_id}", timeout=30)
            
            if response.status_code == 200:
                return True, "Huésped eliminado exitosamente"
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                return False, f"Error al eliminar huésped: {error_detail}"
                
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
    
    def _parse_fecha(self, fecha_str: str) -> datetime:
        """Convierte string de fecha a datetime"""
        try:
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                return datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now()

    # ===== MÉTODOS ADICIONALES PARA HABITACIONES Y RESERVAS =====
    # (Implementar métodos similares para habitaciones y reservas...)