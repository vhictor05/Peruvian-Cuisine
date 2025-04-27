from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from datetime import datetime

class ReporteError(Base):
    __tablename__ = 'reportes_errores'
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.now)
    titulo = Column(String(200), nullable=False)
    modulo = Column(String(50), nullable=False)
    urgencia = Column(String(20), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), default="Abierto")
    reportado_por = Column(String(100))
    comentarios = Column(Text)
    fecha_resolucion = Column(DateTime)