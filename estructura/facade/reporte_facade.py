import requests
from datetime import datetime

class ReporteFacade:
    def __init__(self):
        self.API_URL = "http://localhost:8000/api/v1"
        
    def crear_reporte(self, datos):
        try:
            # Adaptar datos al formato de la API (campos en español)
            reporte_data = {
                "titulo": datos['titulo'],
                "descripcion": datos['descripcion'],
                "modulo": datos['modulo'].lower(),
                "urgencia": self._convertir_urgencia(datos['urgencia']),
                "reportado_por": datos['usuario']
            }
            
            response = requests.post(f"{self.API_URL}/reports", json=reporte_data)
            
            if response.status_code == 201:
                return True, "Reporte creado exitosamente"
            else:
                return False, f"Error al crear reporte: {response.json().get('detail', 'Error desconocido')}"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
            
    def obtener_reportes_filtrados(self, filtros):
        try:
            # Construir parámetros de consulta (usar nombres de la API)
            params = {}
            if filtros['modulo'] != "Todos":
                params['modulo'] = filtros['modulo'].lower()
            if filtros['estado'] != "Todos":
                params['estado'] = self._convertir_estado(filtros['estado'])
                
            response = requests.get(f"{self.API_URL}/reports", params=params)
            
            if response.status_code == 200:
                reportes_api = response.json()
                return [self._convertir_a_reporte(r) for r in reportes_api]
            else:
                raise Exception(f"Error al obtener reportes: {response.json().get('detail', 'Error desconocido')}")
                
        except requests.RequestException as e:
            raise Exception(f"Error de conexión: {str(e)}")
            
    def actualizar_estados(self, ids, nuevo_estado):
        try:
            estado_api = self._convertir_estado(nuevo_estado)
            exitos = 0
            
            for id_reporte in ids:
                response = requests.put(
                    f"{self.API_URL}/reports/{id_reporte}",
                    json={"estado": estado_api}
                )
                if response.status_code == 200:
                    exitos += 1
                    
            if exitos == len(ids):
                return True, f"Se actualizaron {exitos} reportes exitosamente"
            elif exitos > 0:
                return True, f"Se actualizaron {exitos} de {len(ids)} reportes"
            else:
                return False, "No se pudo actualizar ningún reporte"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
            
    def eliminar_reporte(self, ids):
        try:
            exitos = 0
            
            for id_reporte in ids:
                response = requests.delete(f"{self.API_URL}/reports/{id_reporte}")
                if response.status_code == 204:
                    exitos += 1
                    
            if exitos == len(ids):
                return True, f"Se eliminaron {exitos} reportes exitosamente"
            elif exitos > 0:
                return True, f"Se eliminaron {exitos} de {len(ids)} reportes"
            else:
                return False, "No se pudo eliminar ningún reporte"
                
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"

    def obtener_usuarios(self):
        # Por ahora retornamos una lista estática de usuarios
        return ["admin", "usuario1", "usuario2"]
        
    def get_opciones_filtro(self):
        return {
            'modulo': ["Todos", "Restaurante", "Discoteca", "Hotel", "General"],
            'urgencia': ["Todos", "Baja", "Media", "Alta", "Crítica"],
            'estado': ["Todos", "Abierto", "En progreso", "Resuelto"],
            'usuario': ["Todos", "admin", "usuario1", "usuario2"]
        }
        
    def _convertir_urgencia(self, urgencia):
        mapping = {
            "Baja": "low",
            "Media": "medium",
            "Alta": "high",
            "Crítica": "critical"
        }
        return mapping.get(urgencia, "medium")
        
    def _convertir_estado(self, estado):
        mapping = {
            "Abierto": "pending",
            "En progreso": "in_progress",
            "Resuelto": "resolved"
        }
        return mapping.get(estado, "pending")

    def _convertir_a_reporte(self, datos_api):
        from apps.Reportes.dominio import Reporte
        
        # CORREGIDO: Usar los nombres de campo reales de la API (en español)
        return (Reporte.builder()
            .con_id(datos_api['id'])
            .con_titulo(datos_api['titulo'])  # ✅ 'titulo' no 'title'
            .con_descripcion(datos_api['descripcion'])  # ✅ 'descripcion' no 'description'
            .en_modulo(datos_api['modulo'].capitalize())  # ✅ 'modulo' no 'module'
            .con_urgencia(self._convertir_urgencia_inverso(datos_api['urgencia']))  # ✅ 'urgencia' no 'severity'
            .con_estado(self._convertir_estado_inverso(datos_api['estado']))  # ✅ 'estado' no 'status'
            .reportado_por(datos_api['reportado_por'])  # ✅ 'reportado_por' no 'reported_by'
            .con_fecha(self._parse_fecha(datos_api['fecha_reporte']))  # ✅ 'fecha_reporte' no 'created_at'
            .build())

    def _convertir_urgencia_inverso(self, urgencia_api):
        mapping = {
            "low": "Baja",
            "medium": "Media",
            "high": "Alta",
            "critical": "Crítica"
        }
        return mapping.get(urgencia_api, "Media")
        
    def _convertir_estado_inverso(self, estado_api):
        mapping = {
            "pending": "Abierto",
            "in_progress": "En progreso",
            "resolved": "Resuelto"
        }
        return mapping.get(estado_api, "Abierto")

    def _parse_fecha(self, fecha_str):
        """Convierte la fecha de string a datetime"""
        try:
            if isinstance(fecha_str, str):
                # Intentar varios formatos de fecha
                formatos = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f'
                ]
                
                for formato in formatos:
                    try:
                        return datetime.strptime(fecha_str.split('.')[0], formato)
                    except ValueError:
                        continue
                        
                # Si no funciona ningún formato, usar el formato por defecto
                return datetime.strptime(fecha_str[:19], '%Y-%m-%d %H:%M:%S')
            else:
                return fecha_str
        except Exception:
            return datetime.now()