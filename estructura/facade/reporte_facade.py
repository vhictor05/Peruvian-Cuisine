from Database.DB import get_db, init_report_db
from estructura.models_folder.models_reporte import ReporteError
from estructura.crud.reporte_crud import SQLAlchemyReporteRepository
from estructura.services.reporte_service import ReporteService

class ReporteFacade:
    def __init__(self):
        init_report_db()
        db_session = next(get_db())  # Cambiado de get_report_db a get_db
        repository = SQLAlchemyReporteRepository(db_session)
        self.service = ReporteService(repository)
        self.usuarios_disponibles = ["Admin", "Manager", "Recepcionista", "Cocina", "Limpieza", "Seguridad", "Otro"]

    # ... resto del código igual ...

    def obtener_usuarios(self) -> list:
        return self.usuarios_disponibles

    def crear_reporte(self, datos: dict) -> tuple[bool, str]:
        return self.service.crear_reporte(datos)

    def actualizar_estados(self, ids: list[int], nuevo_estado: str) -> tuple[bool, str]:
        return self.service.actualizar_estados(ids, nuevo_estado)

    def eliminar_reporte(self, ids: list[int]) -> tuple[bool, str]:
        return self.service.eliminar_reporte(ids)

    def obtener_reportes_filtrados(self, filtros: dict) -> list:
        return self.service.obtener_reportes(filtros)

    def get_opciones_filtro(self) -> dict:
        return {
            'modulo': ["Todos", "Restaurante", "Discoteca", "Hotel", "General"],
            'urgencia': ["Todos", "Baja", "Media", "Alta", "Crítica"],
            'estado': ["Todos", "Abierto", "En progreso", "Resuelto"],
            'usuario': ["Todos"] + self.usuarios_disponibles
        }