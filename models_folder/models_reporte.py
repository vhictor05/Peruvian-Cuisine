from sqlalchemy import Column, Integer, String, Text, DateTime
from Database.DB import Base  # Cambiamos ReportBase por Base
from datetime import datetime

class ReporteError(Base):  # Cambiamos ReportBase por Base
    __tablename__ = "reportes_errores"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    modulo = Column(String(50), nullable=False)
    urgencia = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), nullable=False, default="Abierto")
    reportado_por = Column(String(100), nullable=False)
    fecha_reporte = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, onupdate=datetime.utcnow)