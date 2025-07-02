from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.hotel import (
    Huesped, HuespedCreate, HuespedUpdate,
    Habitacion, HabitacionCreate, HabitacionUpdate,
    Reserva, ReservaCreate, ReservaUpdate, ReservaDetallada
)
from datetime import datetime
from database import get_db_connection, close_connection
import time
import functools

router = APIRouter(
    prefix="/api/v1/hotel",
    tags=["hotel"]
)

# Caché para consultas frecuentes
hotel_cache = {}
CACHE_TTL = 60

def measure_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} ejecutado en {end_time - start_time:.4f} segundos")
        return result
    return wrapper

# ===== RUTAS DE HUÉSPEDES =====
@router.get("/huespedes", response_model=List[Huesped])
@measure_time
async def get_huespedes():
    """Obtiene todos los huéspedes"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nombre, rut, email, telefono, fecha_registro 
            FROM huespedes 
            ORDER BY fecha_registro DESC
        """)
        rows = cursor.fetchall()
        
        return [Huesped(
            id=row['id'],
            nombre=row['nombre'],
            rut=row['rut'],
            email=row['email'],
            telefono=row['telefono'],
            fecha_registro=datetime.fromisoformat(row['fecha_registro'])
        ) for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/huespedes", response_model=Huesped, status_code=201)
@measure_time
async def create_huesped(huesped: HuespedCreate):
    """Crea un nuevo huésped"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Verificar si el RUT ya existe
        cursor.execute("SELECT id FROM huespedes WHERE rut = ?", (huesped.rut,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe un huésped con este RUT")
        
        cursor.execute("""
            INSERT INTO huespedes (nombre, rut, email, telefono, fecha_registro)
            VALUES (?, ?, ?, ?, ?)
        """, (huesped.nombre, huesped.rut, huesped.email, huesped.telefono, current_time))
        
        huesped_id = cursor.lastrowid
        conn.commit()
        
        return Huesped(
            id=huesped_id,
            nombre=huesped.nombre,
            rut=huesped.rut,
            email=huesped.email,
            telefono=huesped.telefono,
            fecha_registro=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.put("/huespedes/{huesped_id}", response_model=Huesped)
@measure_time
async def update_huesped(huesped_id: int, huesped_update: HuespedUpdate):
    """Actualiza un huésped"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el huésped existe
        cursor.execute("SELECT * FROM huespedes WHERE id = ?", (huesped_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Huésped no encontrado")
        
        # Construir query dinámico
        updates = []
        params = []
        if huesped_update.nombre is not None:
            updates.append("nombre = ?")
            params.append(huesped_update.nombre)
        if huesped_update.email is not None:
            updates.append("email = ?")
            params.append(huesped_update.email)
        if huesped_update.telefono is not None:
            updates.append("telefono = ?")
            params.append(huesped_update.telefono)
        
        if updates:
            params.append(huesped_id)
            cursor.execute(f"UPDATE huespedes SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        
        # Obtener datos actualizados
        cursor.execute("SELECT * FROM huespedes WHERE id = ?", (huesped_id,))
        row = cursor.fetchone()
        
        return Huesped(
            id=row['id'],
            nombre=row['nombre'],
            rut=row['rut'],
            email=row['email'],
            telefono=row['telefono'],
            fecha_registro=datetime.fromisoformat(row['fecha_registro'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/huespedes/{huesped_id}")
@measure_time
async def delete_huesped(huesped_id: int):
    """Elimina un huésped"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si tiene reservas activas
        cursor.execute("""
            SELECT COUNT(*) as count FROM reservas 
            WHERE huesped_id = ? AND estado != 'Cancelada'
        """, (huesped_id,))
        if cursor.fetchone()['count'] > 0:
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar un huésped con reservas activas"
            )
        
        cursor.execute("DELETE FROM huespedes WHERE id = ?", (huesped_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Huésped no encontrado")
        
        conn.commit()
        return {"message": "Huésped eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

# ===== RUTAS DE HABITACIONES =====
@router.get("/habitaciones", response_model=List[Habitacion])
@measure_time
async def get_habitaciones(disponible: Optional[bool] = None):
    """Obtiene todas las habitaciones con filtro opcional de disponibilidad"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, numero, tipo, precio, disponible FROM habitaciones"
        params = []
        
        if disponible is not None:
            query += " WHERE disponible = ?"
            params.append(disponible)
        
        query += " ORDER BY numero"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [Habitacion(
            id=row['id'],
            numero=row['numero'],
            tipo=row['tipo'],
            precio=row['precio'],
            disponible=bool(row['disponible'])
        ) for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/habitaciones", response_model=Habitacion, status_code=201)
@measure_time
async def create_habitacion(habitacion: HabitacionCreate):
    """Crea una nueva habitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que no exista el número
        cursor.execute("SELECT id FROM habitaciones WHERE numero = ?", (habitacion.numero,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ya existe una habitación con este número")
        
        cursor.execute("""
            INSERT INTO habitaciones (numero, tipo, precio, disponible)
            VALUES (?, ?, ?, ?)
        """, (habitacion.numero, habitacion.tipo, habitacion.precio, habitacion.disponible))
        
        habitacion_id = cursor.lastrowid
        conn.commit()
        
        return Habitacion(
            id=habitacion_id,
            numero=habitacion.numero,
            tipo=habitacion.tipo,
            precio=habitacion.precio,
            disponible=habitacion.disponible
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

# ===== RUTAS DE RESERVAS =====
@router.get("/reservas", response_model=List[ReservaDetallada])
@measure_time
async def get_reservas(estado: Optional[str] = None):
    """Obtiene todas las reservas con información detallada"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT r.id, r.huesped_id, r.habitacion_id, r.fecha_entrada, r.fecha_salida,
                   r.precio_final, r.estado, r.fecha_reserva,
                   h.nombre as huesped_nombre, h.rut as huesped_rut,
                   hab.numero as habitacion_numero, hab.tipo as habitacion_tipo
            FROM reservas r
            JOIN huespedes h ON r.huesped_id = h.id
            JOIN habitaciones hab ON r.habitacion_id = hab.id
        """
        params = []
        
        if estado:
            query += " WHERE r.estado = ?"
            params.append(estado)
        
        query += " ORDER BY r.fecha_reserva DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [ReservaDetallada(
            id=row['id'],
            huesped_id=row['huesped_id'],
            habitacion_id=row['habitacion_id'],
            fecha_entrada=datetime.fromisoformat(row['fecha_entrada']),
            fecha_salida=datetime.fromisoformat(row['fecha_salida']),
            precio_final=row['precio_final'],
            estado=row['estado'],
            fecha_reserva=datetime.fromisoformat(row['fecha_reserva']),
            huesped_nombre=row['huesped_nombre'],
            huesped_rut=row['huesped_rut'],
            habitacion_numero=row['habitacion_numero'],
            habitacion_tipo=row['habitacion_tipo']
        ) for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/reservas", response_model=Reserva, status_code=201)
@measure_time
async def create_reserva(reserva: ReservaCreate):
    """Crea una nueva reserva"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Verificar disponibilidad de habitación
        cursor.execute("SELECT disponible FROM habitaciones WHERE id = ?", (reserva.habitacion_id,))
        habitacion = cursor.fetchone()
        if not habitacion or not habitacion['disponible']:
            raise HTTPException(status_code=400, detail="Habitación no disponible")
        
        # Verificar que huésped existe
        cursor.execute("SELECT id FROM huespedes WHERE id = ?", (reserva.huesped_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Huésped no encontrado")
        
        # Crear reserva
        cursor.execute("""
            INSERT INTO reservas (huesped_id, habitacion_id, fecha_entrada, fecha_salida, 
                                precio_final, estado, fecha_reserva)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            reserva.huesped_id, reserva.habitacion_id, 
            reserva.fecha_entrada.strftime('%Y-%m-%d %H:%M:%S'),
            reserva.fecha_salida.strftime('%Y-%m-%d %H:%M:%S'),
            reserva.precio_final, reserva.estado, current_time
        ))
        
        # Marcar habitación como no disponible
        cursor.execute("UPDATE habitaciones SET disponible = 0 WHERE id = ?", (reserva.habitacion_id,))
        
        reserva_id = cursor.lastrowid
        conn.commit()
        
        return Reserva(
            id=reserva_id,
            huesped_id=reserva.huesped_id,
            habitacion_id=reserva.habitacion_id,
            fecha_entrada=reserva.fecha_entrada,
            fecha_salida=reserva.fecha_salida,
            precio_final=reserva.precio_final,
            estado=reserva.estado,
            fecha_reserva=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.put("/reservas/{reserva_id}", response_model=Reserva)
@measure_time
async def update_reserva(reserva_id: int, reserva_update: ReservaUpdate):
    """Actualiza una reserva"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la reserva existe
        cursor.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        
        # Construir query dinámico
        updates = []
        params = []
        if reserva_update.fecha_entrada is not None:
            updates.append("fecha_entrada = ?")
            params.append(reserva_update.fecha_entrada.strftime('%Y-%m-%d %H:%M:%S'))
        if reserva_update.fecha_salida is not None:
            updates.append("fecha_salida = ?")
            params.append(reserva_update.fecha_salida.strftime('%Y-%m-%d %H:%M:%S'))
        if reserva_update.precio_final is not None:
            updates.append("precio_final = ?")
            params.append(reserva_update.precio_final)
        if reserva_update.estado is not None:
            updates.append("estado = ?")
            params.append(reserva_update.estado)
        
        if updates:
            params.append(reserva_id)
            cursor.execute(f"UPDATE reservas SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
        
        # Si se cancela la reserva, liberar habitación
        if reserva_update.estado == "Cancelada":
            cursor.execute("UPDATE habitaciones SET disponible = 1 WHERE id = ?", (existing['habitacion_id'],))
            conn.commit()
        
        # Obtener datos actualizados
        cursor.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
        row = cursor.fetchone()
        
        return Reserva(
            id=row['id'],
            huesped_id=row['huesped_id'],
            habitacion_id=row['habitacion_id'],
            fecha_entrada=datetime.fromisoformat(row['fecha_entrada']),
            fecha_salida=datetime.fromisoformat(row['fecha_salida']),
            precio_final=row['precio_final'],
            estado=row['estado'],
            fecha_reserva=datetime.fromisoformat(row['fecha_reserva'])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/reservas/{reserva_id}")
@measure_time
async def delete_reserva(reserva_id: int):
    """Elimina una reserva y libera la habitación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener datos de la reserva
        cursor.execute("SELECT habitacion_id FROM reservas WHERE id = ?", (reserva_id,))
        reserva = cursor.fetchone()
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        
        # Eliminar reserva
        cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
        
        # Liberar habitación
        cursor.execute("UPDATE habitaciones SET disponible = 1 WHERE id = ?", (reserva['habitacion_id'],))
        
        conn.commit()
        return {"message": "Reserva eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)
