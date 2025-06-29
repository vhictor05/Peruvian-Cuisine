from abc import ABC, abstractmethod

class Reporte:
    def __init__(self, titulo, modulo, urgencia, descripcion, reportado_por, estado="Abierto"):
        self.titulo = titulo
        self.modulo = modulo
        self.urgencia = urgencia
        self.descripcion = descripcion
        self.estado = estado
        self.reportado_por = reportado_por

    @staticmethod
    def builder():
        return ReporteBuilder()

class ReporteBuilder:
    def __init__(self):
        self.titulo = None
        self.modulo = "General"
        self.urgencia = "Media"
        self.descripcion = None
        self.usuario_reporte = None
        self.estado = "Abierto"

    def con_titulo(self, titulo):
        self.titulo = titulo
        return self

    def en_modulo(self, modulo):
        self.modulo = modulo
        return self

    def con_urgencia(self, urgencia):
        self.urgencia = urgencia
        return self

    def con_descripcion(self, descripcion):
        self.descripcion = descripcion
        return self

    def reportado_por(self, usuario):
        self.usuario_reporte = usuario
        return self

    def con_estado(self, estado):
        self.estado = estado
        return self

    def build(self):
        if not self.titulo:
            raise ValueError("El título es obligatorio")
        if not self.descripcion:
            raise ValueError("La descripción es obligatoria")
        if not self.usuario_reporte:
            raise ValueError("El usuario es obligatorio")
        return Reporte(
            titulo=self.titulo,
            modulo=self.modulo,
            urgencia=self.urgencia,
            descripcion=self.descripcion,
            reportado_por=self.usuario_reporte,
            estado=self.estado
        )

class OperacionReporte(ABC):
    def ejecutar(self) -> tuple[bool, str]:
        try:
            self.validar()
            resultado = self.operacion_principal()
            return self.procesar_resultado(resultado)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

    @abstractmethod
    def validar(self):
        pass

    @abstractmethod
    def operacion_principal(self):
        pass

    @abstractmethod
    def procesar_resultado(self, resultado):
        pass

class CrearReporteOperacion(OperacionReporte):
    def __init__(self, service, datos: dict):
        self.service = service
        self.datos = datos

    def validar(self):
        if not self.datos['titulo']:
            raise ValueError("El título es obligatorio")
        if not self.datos['descripcion']:
            raise ValueError("La descripción es obligatoria")
        if not self.datos['usuario']:
            raise ValueError("El usuario es obligatorio")

    def operacion_principal(self):
        reporte = (Reporte.builder()
                .con_titulo(self.datos['titulo'])
                .en_modulo(self.datos.get('modulo'))
                .con_urgencia(self.datos.get('urgencia'))
                .con_descripcion(self.datos['descripcion'])
                .reportado_por(self.datos['usuario'])
                .build())
        return self.service.repository.crear(reporte)

    def procesar_resultado(self, resultado):
        return True, f"Reporte {resultado} creado exitosamente"

class ActualizarEstadoOperacion(OperacionReporte):
    def __init__(self, service, ids: list[int], nuevo_estado: str):
        self.service = service
        self.ids = ids
        self.nuevo_estado = nuevo_estado

    def validar(self):
        if not self.ids:
            raise ValueError("No hay reportes seleccionados")

    def operacion_principal(self):
        success_count = 0
        for id_reporte in self.ids:
            if self.service.repository.actualizar_estado(id_reporte, self.nuevo_estado):
                success_count += 1
        return success_count

    def procesar_resultado(self, resultado):
        if resultado == 0:
            return False, "No se actualizó ningún reporte"
        return True, f"Se actualizaron {resultado} reportes a '{self.nuevo_estado}'"

class EliminarReporteOperacion(OperacionReporte):
    def __init__(self, service, ids: list[int]):
        self.service = service
        self.ids = ids

    def validar(self):
        if not self.ids:
            raise ValueError("No hay reportes seleccionados")

    def operacion_principal(self):
        success_count = 0
        for id_reporte in self.ids:
            if self.service.repository.eliminar(id_reporte):
                success_count += 1
        return success_count

    def procesar_resultado(self, resultado):
        if resultado == 0:
            return False, "No se eliminó ningún reporte"
        return True, f"Se eliminaron {resultado} reporte(s) correctamente"