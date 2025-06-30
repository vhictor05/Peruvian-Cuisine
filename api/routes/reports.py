from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.reports import Report, ReportCreate, ReportUpdate
from datetime import datetime
from database import get_db_connection

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["reports"]
)

def parse_date(date_str: str) -> datetime:
    """
    Intenta parsear la fecha en varios formatos comunes
    """
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.split('.')[0], fmt)
        except ValueError:
            continue
            
    # Si ningún formato funciona, intentamos limpiar la cadena
    cleaned_date = date_str.split('.')[0]  # Removemos microsegundos si existen
    try:
        return datetime.strptime(cleaned_date, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        raise ValueError(f"No se pudo convertir la fecha: {date_str}. Error: {str(e)}")

@router.get("/", response_model=List[Report])
async def get_reports(
    modulo: Optional[str] = None,
    estado: Optional[str] = None
):
    """
    Obtiene todos los reportes.
    Opcionalmente filtra por módulo y estado.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM reportes_errores"
            params = []
            
            if modulo or estado:
                conditions = []
                if modulo:
                    conditions.append("modulo = ?")
                    params.append(modulo.lower())
                if estado:
                    conditions.append("estado = ?")
                    params.append(estado.lower())
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [Report(
                id=row['id'],
                titulo=row['titulo'],
                descripcion=row['descripcion'],
                modulo=row['modulo'],
                urgencia=row['urgencia'],
                estado=row['estado'],
                reportado_por=row['reportado_por'],
                fecha_reporte=parse_date(row['fecha_reporte'])
            ) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Report, status_code=201)
async def create_report(report: ReportCreate):
    """
    Crea un nuevo reporte.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            query = """
            INSERT INTO reportes_errores (titulo, descripcion, modulo, urgencia, estado, reportado_por, fecha_reporte)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                report.titulo,
                report.descripcion,
                report.modulo.lower(),
                report.urgencia,
                'pending',
                report.reportado_por,
                current_time
            )
            
            cursor.execute(query, params)
            report_id = cursor.lastrowid
            conn.commit()
            
            cursor.execute("SELECT * FROM reportes_errores WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            
            return Report(
                id=row['id'],
                titulo=row['titulo'],
                descripcion=row['descripcion'],
                modulo=row['modulo'],
                urgencia=row['urgencia'],
                estado=row['estado'],
                reportado_por=row['reportado_por'],
                fecha_reporte=parse_date(row['fecha_reporte'])
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}", response_model=Report)
async def get_report(report_id: int):
    """
    Obtiene un reporte específico por ID.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reportes_errores WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            
            if row is None:
                raise HTTPException(status_code=404, detail="Report not found")
            
            return Report(
                id=row['id'],
                titulo=row['titulo'],
                descripcion=row['descripcion'],
                modulo=row['modulo'],
                urgencia=row['urgencia'],
                estado=row['estado'],
                reportado_por=row['reportado_por'],
                fecha_reporte=parse_date(row['fecha_reporte'])
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{report_id}", response_model=Report)
async def update_report(report_id: int, report_update: ReportUpdate):
    """
    Actualiza el estado de un reporte.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM reportes_errores WHERE id = ?", (report_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Report not found")
            
            update_fields = []
            params = []
            if report_update.estado is not None:
                update_fields.append("estado = ?")
                params.append(report_update.estado)
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            query = f"UPDATE reportes_errores SET {', '.join(update_fields)} WHERE id = ?"
            params.append(report_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            cursor.execute("SELECT * FROM reportes_errores WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            
            return Report(
                id=row['id'],
                titulo=row['titulo'],
                descripcion=row['descripcion'],
                modulo=row['modulo'],
                urgencia=row['urgencia'],
                estado=row['estado'],
                reportado_por=row['reportado_por'],
                fecha_reporte=parse_date(row['fecha_reporte'])
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: int):
    """
    Elimina un reporte.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM reportes_errores WHERE id = ?", (report_id,))
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Report not found")
            
            cursor.execute("DELETE FROM reportes_errores WHERE id = ?", (report_id,))
            conn.commit()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))