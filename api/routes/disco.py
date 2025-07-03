from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.disco import (
    Evento, EventoCreate,
    ClienteDiscoteca, ClienteDiscotecaCreate,
    Entrada, EntradaCreate,
    Mesa, MesaCreate,
    ReservaMesa, ReservaMesaCreate
)
from models.disco import Trago, TragoCreate  # Importar modelos de Trago
from models.pedido import Pedido, PedidoCreate, PedidoDetalle
from datetime import datetime
from database import get_db_connection, close_connection
import time
import functools
import cProfile
import pstats
import io
import json

router = APIRouter(
    prefix="/api/v1/disco",
    tags=["disco"]
)

# Caché en memoria para resultados frecuentes
disco_cache = {}
CACHE_TTL = 60  # segundos

def measure_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        execution_time = end_time - start_time
        print(f"Función {func.__name__} ejecutada en {execution_time:.4f} segundos")
        print(s.getvalue())
        return result
    return wrapper

def parse_date(date_str: str) -> datetime:
    if not date_str:
        return datetime.now()
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
    cleaned_date = date_str.split('.')[0]
    try:
        return datetime.strptime(cleaned_date, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        raise ValueError(f"No se pudo convertir la fecha: {date_str}. Error: {str(e)}")

# --- Ejemplo de endpoints para Evento ---
@router.get("/eventos", response_model=List[Evento])
@measure_time
async def get_eventos(limit: int = 20, offset: int = 0):
    """
    Obtiene eventos paginados. Por defecto 20 por página.
    """
    cache_key = f"eventos_{limit}_{offset}"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo datos de caché para {cache_key}")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT id, nombre, descripcion, fecha, precio_entrada, aforo_maximo FROM eventos ORDER BY fecha DESC LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        result = [Evento(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            fecha=parse_date(row['fecha']),
            precio_entrada=row['precio_entrada'],
            aforo_maximo=row['aforo_maximo']
        ) for row in rows]
        disco_cache[cache_key] = (current_time, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/eventos", response_model=Evento, status_code=201)
@measure_time
async def create_evento(evento: EventoCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        query = """
        INSERT INTO eventos (nombre, descripcion, fecha, precio_entrada, aforo_maximo)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            evento.nombre,
            evento.descripcion,
            evento.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            evento.precio_entrada,
            evento.aforo_maximo
        )
        cursor.execute(query, params)
        evento_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT id, nombre, descripcion, fecha, precio_entrada, aforo_maximo FROM eventos WHERE id = ?",
            (evento_id,)
        )
        row = cursor.fetchone()
        global disco_cache
        disco_cache = {}
        return Evento(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            fecha=parse_date(row['fecha']),
            precio_entrada=row['precio_entrada'],
            aforo_maximo=row['aforo_maximo']
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

@router.get("/eventos/{evento_id}", response_model=Evento)
@measure_time
async def get_evento(evento_id: int):
    cache_key = f"evento_{evento_id}"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo evento {evento_id} de caché")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, descripcion, fecha, precio_entrada, aforo_maximo FROM eventos WHERE id = ?",
            (evento_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        result = Evento(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            fecha=parse_date(row['fecha']),
            precio_entrada=row['precio_entrada'],
            aforo_maximo=row['aforo_maximo']
        )
        disco_cache[cache_key] = (current_time, result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/eventos/{evento_id}", status_code=204)
@measure_time
async def delete_evento(evento_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM eventos WHERE id = ?", (evento_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        conn.commit()
        global disco_cache
        disco_cache = {}
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

# --- Endpoints para ClienteDiscoteca ---
@router.get("/clientes", response_model=List[ClienteDiscoteca])
@measure_time
async def get_clientes(limit: int = 20, offset: int = 0):
    cache_key = f"clientes_{limit}_{offset}"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo datos de caché para {cache_key}")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT id, nombre, rut, email, telefono FROM clientes_discoteca ORDER BY id DESC LIMIT ? OFFSET ?"
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        result = [ClienteDiscoteca(
            id=row['id'],
            nombre=row['nombre'],
            rut=row['rut'],
            email=row['email'],
            telefono=row['telefono']
        ) for row in rows]
        disco_cache[cache_key] = (current_time, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/clientes", response_model=ClienteDiscoteca, status_code=201)
@measure_time
async def create_cliente(cliente: ClienteDiscotecaCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        query = """
        INSERT INTO clientes_discoteca (nombre, rut, email, telefono)
        VALUES (?, ?, ?, ?)
        """
        params = (
            cliente.nombre,
            cliente.rut,
            cliente.email,
            cliente.telefono
        )
        cursor.execute(query, params)
        cliente_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT id, nombre, rut, email, telefono FROM clientes_discoteca WHERE id = ?",
            (cliente_id,)
        )
        row = cursor.fetchone()
        global disco_cache
        disco_cache = {}
        return ClienteDiscoteca(
            id=row['id'],
            nombre=row['nombre'],
            rut=row['rut'],
            email=row['email'],
            telefono=row['telefono']
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

@router.get("/clientes/{cliente_id}", response_model=ClienteDiscoteca)
@measure_time
async def get_cliente(cliente_id: int):
    cache_key = f"cliente_{cliente_id}"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo cliente {cliente_id} de caché")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, rut, email, telefono FROM clientes_discoteca WHERE id = ?",
            (cliente_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        result = ClienteDiscoteca(
            id=row['id'],
            nombre=row['nombre'],
            rut=row['rut'],
            email=row['email'],
            telefono=row['telefono']
        )
        disco_cache[cache_key] = (current_time, result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/clientes/{cliente_id}", status_code=204)
@measure_time
async def delete_cliente(cliente_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM clientes_discoteca WHERE id = ?", (cliente_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        cursor.execute("DELETE FROM clientes_discoteca WHERE id = ?", (cliente_id,))
        conn.commit()
        global disco_cache
        disco_cache = {}
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

# --- Endpoints para Entrada ---
@router.get("/entradas", response_model=List[Entrada])
@measure_time
async def get_entradas():
    cache_key = "entradas"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo datos de caché para {cache_key}")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT id, evento_id, cliente_id, fecha_compra, precio_pagado FROM entradas ORDER BY fecha_compra DESC LIMIT 100"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = [Entrada(
            id=row['id'],
            evento_id=row['evento_id'],
            cliente_id=row['cliente_id'],
            fecha_compra=parse_date(row['fecha_compra']),
            precio_pagado=row['precio_pagado']
        ) for row in rows]
        disco_cache[cache_key] = (current_time, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/entradas", response_model=Entrada, status_code=201)
@measure_time
async def create_entrada(entrada: EntradaCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        query = """
        INSERT INTO entradas (evento_id, cliente_id, fecha_compra, precio_pagado)
        VALUES (?, ?, ?, ?)
        """
        params = (
            entrada.evento_id,
            entrada.cliente_id,
            entrada.fecha_compra.strftime('%Y-%m-%d %H:%M:%S'),
            entrada.precio_pagado
        )
        cursor.execute(query, params)
        entrada_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT id, evento_id, cliente_id, fecha_compra, precio_pagado FROM entradas WHERE id = ?",
            (entrada_id,)
        )
        row = cursor.fetchone()
        global disco_cache
        disco_cache = {}
        return Entrada(
            id=row['id'],
            evento_id=row['evento_id'],
            cliente_id=row['cliente_id'],
            fecha_compra=parse_date(row['fecha_compra']),
            precio_pagado=row['precio_pagado']
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

@router.get("/entradas/{entrada_id}", response_model=Entrada)
@measure_time
async def get_entrada(entrada_id: int):
    cache_key = f"entrada_{entrada_id}"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo entrada {entrada_id} de caché")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, evento_id, cliente_id, fecha_compra, precio_pagado FROM entradas WHERE id = ?",
            (entrada_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
        result = Entrada(
            id=row['id'],
            evento_id=row['evento_id'],
            cliente_id=row['cliente_id'],
            fecha_compra=parse_date(row['fecha_compra']),
            precio_pagado=row['precio_pagado']
        )
        disco_cache[cache_key] = (current_time, result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/entradas/{entrada_id}", status_code=204)
@measure_time
async def delete_entrada(entrada_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM entradas WHERE id = ?", (entrada_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Entrada no encontrada")
        cursor.execute("DELETE FROM entradas WHERE id = ?", (entrada_id,))
        conn.commit()
        global disco_cache
        disco_cache = {}
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

# --- Endpoints para ReservaMesa ---
@router.get("/reservas", response_model=List[ReservaMesa])
@measure_time
async def get_reservas():
    cache_key = "reservas"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo datos de caché para {cache_key}")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT id, evento_id, cliente_id, mesa_id, fecha_reserva, estado FROM reservas_mesa ORDER BY fecha_reserva DESC LIMIT 100"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = [ReservaMesa(
            id=row['id'],
            evento_id=row['evento_id'],
            cliente_id=row['cliente_id'],
            mesa_id=row['mesa_id'],
            fecha_reserva=parse_date(row['fecha_reserva']),
            estado=row['estado']
        ) for row in rows]
        disco_cache[cache_key] = (current_time, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/reservas", response_model=ReservaMesa, status_code=201)
@measure_time
async def create_reserva(reserva: ReservaMesaCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        query = """
        INSERT INTO reservas_mesa (evento_id, cliente_id, mesa_id, fecha_reserva, estado)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            reserva.evento_id,
            reserva.cliente_id,
            reserva.mesa_id,
            reserva.fecha_reserva.strftime('%Y-%m-%d %H:%M:%S'),
            reserva.estado
        )
        cursor.execute(query, params)
        reserva_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT id, evento_id, cliente_id, mesa_id, fecha_reserva, estado FROM reservas_mesa WHERE id = ?",
            (reserva_id,)
        )
        row = cursor.fetchone()
        global disco_cache
        disco_cache = {}
        return ReservaMesa(
            id=row['id'],
            evento_id=row['evento_id'],
            cliente_id=row['cliente_id'],
            mesa_id=row['mesa_id'],
            fecha_reserva=parse_date(row['fecha_reserva']),
            estado=row['estado']
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

@router.get("/reservas/{reserva_id}", response_model=ReservaMesa)
@measure_time
async def get_reserva(reserva_id: int):
    cache_key = f"reserva_{reserva_id}"
    current_time = time.time()
    if cache_key in disco_cache:
        cached_time, cached_data = disco_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            print(f"Obteniendo reserva {reserva_id} de caché")
            return cached_data
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, evento_id, cliente_id, mesa_id, fecha_reserva, estado FROM reservas_mesa WHERE id = ?",
            (reserva_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        result = ReservaMesa(
            id=row['id'],
            evento_id=row['evento_id'],
            cliente_id=row['cliente_id'],
            mesa_id=row['mesa_id'],
            fecha_reserva=parse_date(row['fecha_reserva']),
            estado=row['estado']
        )
        disco_cache[cache_key] = (current_time, result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.delete("/reservas/{reserva_id}", status_code=204)
@measure_time
async def delete_reserva(reserva_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM reservas_mesa WHERE id = ?", (reserva_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        cursor.execute("DELETE FROM reservas_mesa WHERE id = ?", (reserva_id,))
        conn.commit()
        global disco_cache
        disco_cache = {}
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

# --- Endpoints para Trago ---
@router.get("/tragos", response_model=List[Trago])
@measure_time
async def get_tragos(nombre: Optional[str] = None, limit: int = 20, offset: int = 0):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if nombre:
            query = "SELECT id, nombre, descripcion, precio, categoria, disponible, stock FROM tragos WHERE nombre = ?"
            cursor.execute(query, (nombre,))
        else:
            query = "SELECT id, nombre, descripcion, precio, categoria, disponible, stock FROM tragos ORDER BY id DESC LIMIT ? OFFSET ?"
            cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        result = [Trago(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            precio=row['precio'],
            categoria=row['categoria'],
            disponible=row['disponible'],
            stock=row['stock']
        ) for row in rows]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)

@router.post("/tragos", response_model=Trago, status_code=201)
@measure_time
async def create_trago(trago: TragoCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        query = """
        INSERT INTO tragos (nombre, descripcion, precio, categoria, disponible, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            trago.nombre,
            trago.descripcion,
            trago.precio,
            trago.categoria,
            trago.disponible,
            trago.stock
        )
        cursor.execute(query, params)
        trago_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT id, nombre, descripcion, precio, categoria, disponible, stock FROM tragos WHERE id = ?",
            (trago_id,)
        )
        row = cursor.fetchone()
        global disco_cache
        disco_cache = {}
        return Trago(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            precio=row['precio'],
            categoria=row['categoria'],
            disponible=row['disponible'],
            stock=row['stock']
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

@router.put("/tragos/{trago_id}", response_model=Trago)
@measure_time
async def update_trago(trago_id: int, trago: TragoCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM tragos WHERE id = ?", (trago_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Trago no encontrado")
        query = """
        UPDATE tragos SET nombre=?, descripcion=?, precio=?, categoria=?, disponible=?, stock=? WHERE id=?
        """
        params = (
            trago.nombre,
            trago.descripcion,
            trago.precio,
            trago.categoria,
            trago.disponible,
            trago.stock,
            trago_id
        )
        cursor.execute(query, params)
        conn.commit()
        cursor.execute(
            "SELECT id, nombre, descripcion, precio, categoria, disponible, stock FROM tragos WHERE id = ?",
            (trago_id,)
        )
        row = cursor.fetchone()
        global disco_cache
        disco_cache = {}
        return Trago(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'],
            precio=row['precio'],
            categoria=row['categoria'],
            disponible=row['disponible'],
            stock=row['stock']
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

@router.delete("/tragos/{trago_id}", status_code=204)
@measure_time
async def delete_trago(trago_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        cursor.execute("SELECT id FROM tragos WHERE id = ?", (trago_id,))
        if cursor.fetchone() is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Trago no encontrado")
        cursor.execute("DELETE FROM tragos WHERE id = ?", (trago_id,))
        conn.commit()
        global disco_cache
        disco_cache = {}
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

# --- Endpoints para Pedidos ---
@router.post("/pedidos", response_model=Pedido, status_code=201)
@measure_time
async def create_pedido(pedido: PedidoCreate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.execute("BEGIN IMMEDIATE")
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Insertar en pedidos_tragos
        cursor.execute(
            """
            INSERT INTO pedidos_tragos (cliente_id, total, fecha, detalles)
            VALUES (?, ?, ?, ?)
            """,
            (pedido.cliente_id, pedido.total, fecha, json.dumps([detalle.dict() for detalle in pedido.detalles]))
        )
        pedido_id = cursor.lastrowid
        conn.commit()
        return Pedido(id=pedido_id, cliente_id=pedido.cliente_id, total=pedido.total, fecha=datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S'), detalles=pedido.detalles)
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

@router.get("/pedidos/{pedido_id}", response_model=Pedido)
@measure_time
async def get_pedido(pedido_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente_id, total, fecha, detalles FROM pedidos_tragos WHERE id = ?", (pedido_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        detalles = [PedidoDetalle(**d) for d in json.loads(row['detalles'])] if row['detalles'] else []
        return Pedido(id=row['id'], cliente_id=row['cliente_id'], total=row['total'], fecha=datetime.strptime(row['fecha'], '%Y-%m-%d %H:%M:%S'), detalles=detalles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            close_connection(conn)
