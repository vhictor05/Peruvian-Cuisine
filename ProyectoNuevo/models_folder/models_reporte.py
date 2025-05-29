from sqlalchemy import Column, Integer, String, Text, DateTime
from report_database import ReportBase  # Cambiado de database a report_database
from datetime import datetime

class ReporteError(ReportBase):  # Usar ReportBase en lugar de Base
    __tablename__ = "reportes_errores"  # Asegúrate que coincida con tu BD
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    modulo = Column(String(50), nullable=False)
    urgencia = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), nullable=False, default="Abierto")
    reportado_por = Column(String(100), nullable=False)
    fecha_reporte = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)