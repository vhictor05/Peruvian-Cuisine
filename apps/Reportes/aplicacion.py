from apps.Reportes.dominio import CrearReporteOperacion, ActualizarEstadoOperacion, EliminarReporteOperacion

class ReporteService:
    def __init__(self, repository):
        self.repository = repository

    def crear_reporte(self, datos: dict) -> tuple[bool, str]:
        operacion = CrearReporteOperacion(self, datos)
        return operacion.ejecutar()

    def actualizar_estados(self, ids: list[int], nuevo_estado: str) -> tuple[bool, str]:
        operacion = ActualizarEstadoOperacion(self, ids, nuevo_estado)
        return operacion.ejecutar()

    def eliminar_reporte(self, ids: list[int]) -> tuple[bool, str]:
        operacion = EliminarReporteOperacion(self, ids)
        return operacion.ejecutar()

    def obtener_reportes(self, filtros: dict) -> list:
        return self.repository.obtener_por_filtros(filtros)