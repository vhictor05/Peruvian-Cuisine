from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportBase(BaseModel):
    titulo: str
    descripcion: str
    modulo: str
    urgencia: str
    reportado_por: str

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    estado: Optional[str] = None

class Report(ReportBase):
    id: int
    estado: str
    fecha_reporte: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }