from sqlalchemy.orm import Session
from estructura.models_folder.models_reporte import ReporteError

class SQLAlchemyReporteRepository:
    def __init__(self, session: Session):
        self.session = session

    def crear(self, reporte):
        db_reporte = ReporteError(
            titulo=reporte.titulo,
            descripcion=reporte.descripcion,
            modulo=reporte.modulo,
            urgencia=reporte.urgencia,
            estado=reporte.estado,
            reportado_por=reporte.reportado_por
        )
        self.session.add(db_reporte)
        self.session.commit()
        self.session.refresh(db_reporte)
        return db_reporte.id

    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        reporte = self.session.query(ReporteError).filter(ReporteError.id == id_reporte).first()
        if reporte:
            reporte.estado = nuevo_estado
            self.session.commit()
            return True
        return False

    def eliminar(self, id_reporte: int) -> bool:
        reporte = self.session.query(ReporteError).filter(ReporteError.id == id_reporte).first()
        if reporte:
            self.session.delete(reporte)
            self.session.commit()
            return True
        return False

    def obtener_todos(self, filtros: dict = None):
        query = self.session.query(ReporteError)
        
        if filtros:
            if filtros.get('modulo') and filtros['modulo'] != "Todos":
                query = query.filter(ReporteError.modulo == filtros['modulo'])
            if filtros.get('urgencia') and filtros['urgencia'] != "Todos":
                query = query.filter(ReporteError.urgencia == filtros['urgencia'])
            if filtros.get('estado') and filtros['estado'] != "Todos":
                query = query.filter(ReporteError.estado == filtros['estado'])
            if filtros.get('usuario') and filtros['usuario'] != "Todos":
                query = query.filter(ReporteError.reportado_por == filtros['usuario'])
        
        return query.order_by(ReporteError.fecha_reporte.desc()).all()

    def obtener_por_id(self, id_reporte: int):
        return self.session.query(ReporteError).filter(ReporteError.id == id_reporte).first()