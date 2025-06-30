from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from Database.DB import Base
from datetime import datetime

class ReporteError(Base):
    __tablename__ = "reportes_errores"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    modulo = Column(String(50), nullable=False)  # Restaurante, Discoteca, Hotel, General
    urgencia = Column(String(20), nullable=False)  # Baja, Media, Alta, Crítica
    estado = Column(String(20), default="Abierto")  # Abierto, En progreso, Resuelto
    reportado_por = Column(String(100), nullable=False)
    fecha_reporte = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)