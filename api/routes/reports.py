from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.reports import Report, ReportCreate, ReportUpdate
from datetime import datetime
from database import get_db_connection, close_connection
import time
import functools

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["reports"]
)

# Caché en memoria para resultados frecuentes
report_cache = {}
CACHE_TTL = 60  # segundos

# Función para medir el tiempo de ejecución (solo con time, sin cProfile)
def measure_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Función {func.__name__} ejecutada en {execution_time:.4f} segundos")
        return result
    return wrapper

def parse_date(date_str: str) -> datetime:
    """
    Intenta parsear la fecha en varios formatos comunes
    """
    if not date_str:
        return datetime.now()
    
    # Intentamos primero el formato más común para evitar iterar
    try:
        return datetime.strptime(date_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    
    formats = [
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
@measure_time
async def get_reports(
    modulo: Optional[str] = None,
    estado: Optional[str] = None
):
    """
    Obtiene todos los reportes.
    Opcionalmente filtra por módulo y estado.
    """
    # Verificar caché primero
    cache_key = f"reports_{modulo}_{estado}"
    current_time = time.time()
    if cache_key in report_cache:
        cached_time, cached_data = report_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo datos de caché para {cache_key}")
            return cached_data
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consulta optimizada: seleccionar sólo columnas necesarias
        query = """
        SELECT id, titulo, descripcion, modulo, urgencia, estado, reportado_por, fecha_reporte 
        FROM reportes_errores
        """
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
        
        # Ordenamos por fecha descendente y limitamos para mejorar rendimiento
        query += " ORDER BY fecha_reporte DESC LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = [Report(
            id=row['id'],
            titulo=row['titulo'],
            descripcion=row['descripcion'],
            modulo=row['modulo'],
            urgencia=row['urgencia'],
            estado=row['estado'],
            reportado_por=row['reportado_por'],
            fecha_reporte=parse_date(row['fecha_reporte'])
        ) for row in rows]
        
        # Guardar en caché
        report_cache[cache_key] = (current_time, result)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/", response_model=Report, status_code=201)
@measure_time
async def create_report(report: ReportCreate):
    """
    Crea un nuevo reporte.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Iniciamos transacción explícita
        conn.execute("BEGIN IMMEDIATE")
        
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
        
        # Optimización: consulta más específica
        cursor.execute(
            "SELECT id, titulo, descripcion, modulo, urgencia, estado, reportado_por, fecha_reporte " +
            "FROM reportes_errores WHERE id = ?", 
            (report_id,)
        )
        row = cursor.fetchone()
        
        # Invalidar caché
        global report_cache
        report_cache = {}
        
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
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.get("/{report_id}", response_model=Report)
@measure_time
async def get_report(report_id: int):
    """
    Obtiene un reporte específico por ID.
    """
    # Verificar caché primero
    cache_key = f"report_{report_id}"
    current_time = time.time()
    if cache_key in report_cache:
        cached_time, cached_data = report_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo reporte {report_id} de caché")
            return cached_data
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Optimización: seleccionamos solo las columnas necesarias
        cursor.execute(
            "SELECT id, titulo, descripcion, modulo, urgencia, estado, reportado_por, fecha_reporte " +
            "FROM reportes_errores WHERE id = ?", 
            (report_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
        result = Report(
            id=row['id'],
            titulo=row['titulo'],
            descripcion=row['descripcion'],
            modulo=row['modulo'],
            urgencia=row['urgencia'],
            estado=row['estado'],
            reportado_por=row['reportado_por'],
            fecha_reporte=parse_date(row['fecha_reporte'])
        )
        
        # Guardar en caché
        report_cache[cache_key] = (current_time, result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.put("/{report_id}", response_model=Report)
@measure_time
async def update_report(report_id: int, report_update: ReportUpdate):
    """
    Actualiza el estado de un reporte.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Iniciamos transacción explícita
        conn.execute("BEGIN IMMEDIATE")
        
        # Primero verificamos si el reporte existe, pero solo consultamos el ID
        cursor.execute("SELECT id FROM reportes_errores WHERE id = ?", (report_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
        update_fields = []
        params = []
        if report_update.estado is not None:
            update_fields.append("estado = ?")
            params.append(report_update.estado)
        
        if not update_fields:
            conn.rollback()
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        query = f"UPDATE reportes_errores SET {', '.join(update_fields)} WHERE id = ?"
        params.append(report_id)
        
        cursor.execute(query, params)
        conn.commit()
        
        # Consultamos solo las columnas necesarias
        cursor.execute(
            "SELECT id, titulo, descripcion, modulo, urgencia, estado, reportado_por, fecha_reporte " +
            "FROM reportes_errores WHERE id = ?", 
            (report_id,)
        )
        row = cursor.fetchone()
        
        # Invalidar caché
        global report_cache
        report_cache = {}
        
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
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/{report_id}", status_code=204)
@measure_time
async def delete_report(report_id: int):
    """
    Elimina un reporte.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Iniciamos transacción explícita
        conn.execute("BEGIN IMMEDIATE")
        
        # Solo consultamos el ID para verificar existencia
        cursor.execute("SELECT id FROM reportes_errores WHERE id = ?", (report_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
        cursor.execute("DELETE FROM reportes_errores WHERE id = ?", (report_id,))
        conn.commit()
        
        # Invalidar caché
        global report_cache
        report_cache = {}
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)