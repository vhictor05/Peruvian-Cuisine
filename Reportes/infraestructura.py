from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from models_folder.models_reporte import ReporteError

class IReporteRepository(ABC):
    @abstractmethod
    def crear(self, reporte):
        pass

    @abstractmethod
    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        pass

    @abstractmethod
    def obtener_por_filtros(self, filtros: dict) -> list:
        pass

    @abstractmethod
    def eliminar(self, id_reporte: int) -> bool:
        pass

class SQLAlchemyReporteRepository(IReporteRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def crear(self, reporte):
        entidad = ReporteError(
            titulo=reporte.titulo,
            modulo=reporte.modulo,
            urgencia=reporte.urgencia,
            descripcion=reporte.descripcion,
            estado=reporte.estado,
            reportado_por=reporte.reportado_por
        )
        self.db.add(entidad)
        self.db.commit()
        return entidad.id

    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        reporte = self.db.query(ReporteError).get(id_reporte)
        if reporte:
            reporte.estado = nuevo_estado
            self.db.commit()
            return True
        return False

    def obtener_por_filtros(self, filtros: dict) -> list:
        query = self.db.query(ReporteError)
        if filtros.get('modulo') and filtros['modulo'] != "Todos":
            query = query.filter(ReporteError.modulo == filtros['modulo'])
        if filtros.get('urgencia') and filtros['urgencia'] != "Todos":
            query = query.filter(ReporteError.urgencia == filtros['urgencia'])
        if filtros.get('estado') and filtros['estado'] != "Todos":
            query = query.filter(ReporteError.estado == filtros['estado'])
        if filtros.get('usuario') and filtros['usuario'] != "Todos":
            query = query.filter(ReporteError.reportado_por == filtros['usuario'])
        return query.order_by(ReporteError.fecha_reporte.desc()).all()

    def eliminar(self, id_reporte: int) -> bool:
        reporte = self.db.query(ReporteError).get(id_reporte)
        if reporte:
            self.db.delete(reporte)
            self.db.commit()
            return True
        return False