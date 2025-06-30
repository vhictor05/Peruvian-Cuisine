import requests
from datetime import datetime

class ReporteAPIAdapter:
    def __init__(self):
        self.API_URL = "http://localhost:8000/api/v1"
        
    def crear_reporte(self, datos):
        try:
            # Adaptar datos al formato de la API
            reporte_data = {
                "title": datos['titulo'],
                "description": datos['descripcion'],
                "module": datos['modulo'].lower(),
                "severity": self._convertir_urgencia(datos['urgencia']),
                "reported_by": datos['usuario']
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
            # Construir parámetros de consulta
            params = {}
            if filtros['modulo'] != "Todos":
                params['module'] = filtros['modulo'].lower()
            if filtros['estado'] != "Todos":
                params['status'] = self._convertir_estado(filtros['estado'])
                
            response = requests.get(f"{self.API_URL}/reports", params=params)
            
            if response.status_code == 200:
                reportes_api = response.json()
                # Convertir el formato de la API al formato esperado por la interfaz
                return [self._convertir_reporte_api(r) for r in reportes_api]
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
                    json={"status": estado_api}
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
    
    def _convertir_urgencia(self, urgencia):
        # Convertir urgencia de la interfaz al formato de la API
        mapping = {
            "Baja": "low",
            "Media": "medium",
            "Alta": "high",
            "Crítica": "critical"
        }
        return mapping.get(urgencia, "medium")
        
    def _convertir_estado(self, estado):
        # Convertir estado de la interfaz al formato de la API
        mapping = {
            "Abierto": "pending",
            "En progreso": "in_progress",
            "Resuelto": "resolved"
        }
        return mapping.get(estado, "pending")
        
    def _convertir_reporte_api(self, reporte_api):
        # Crear una clase que simule el objeto Reporte que espera tu interfaz
        class ReporteDTO:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
                    
        return ReporteDTO(
            id=reporte_api['id'],
            titulo=reporte_api['title'],
            descripcion=reporte_api['description'],
            modulo=reporte_api['module'].capitalize(),
            urgencia=self._convertir_urgencia_inverso(reporte_api['severity']),
            estado=self._convertir_estado_inverso(reporte_api['status']),
            fecha_reporte=datetime.fromisoformat(reporte_api['created_at']),
            reportado_por=reporte_api['reported_by']
        )
        
    def _convertir_urgencia_inverso(self, urgencia_api):
        # Convertir urgencia de la API al formato de la interfaz
        mapping = {
            "low": "Baja",
            "medium": "Media",
            "high": "Alta",
            "critical": "Crítica"
        }
        return mapping.get(urgencia_api, "Media")
        
    def _convertir_estado_inverso(self, estado_api):
        # Convertir estado de la API al formato de la interfaz
        mapping = {
            "pending": "Abierto",
            "in_progress": "En progreso",
            "resolved": "Resuelto"
        }
        return mapping.get(estado_api, "Abierto")