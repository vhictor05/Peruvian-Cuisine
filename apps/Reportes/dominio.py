class Reporte:
    def __init__(self):
        self.id = None
        self.titulo = None
        self.descripcion = None
        self.modulo = None
        self.urgencia = None
        self.estado = None
        self.fecha_reporte = None
        self.reportado_por = None

    @staticmethod
    def builder():
        return ReporteBuilder()

class ReporteBuilder:
    def __init__(self):
        self.reporte = Reporte()

    def con_id(self, id):  # Añadimos este método
        self.reporte.id = id
        return self

    def con_titulo(self, titulo):
        self.reporte.titulo = titulo
        return self

    def con_descripcion(self, descripcion):
        self.reporte.descripcion = descripcion
        return self

    def en_modulo(self, modulo):
        self.reporte.modulo = modulo
        return self

    def con_urgencia(self, urgencia):
        self.reporte.urgencia = urgencia
        return self

    def con_estado(self, estado):  # Añadimos este método
        self.reporte.estado = estado
        return self

    def con_fecha(self, fecha):  # Añadimos este método
        self.reporte.fecha_reporte = fecha
        return self

    def reportado_por(self, usuario):
        self.reporte.reportado_por = usuario
        return self

    def build(self):
        return self.reporte