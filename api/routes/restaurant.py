import sqlite3
import json
import os
from fastapi import APIRouter, HTTPException, status
from typing import List

# Import limpio usando import absoluto
try:
    from models.restaurant import Menu, MenuCreate, MenuUpdate
except ImportError:
    # Fallback si hay problema con el import
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from models.restaurant import Menu, MenuCreate, MenuUpdate

router = APIRouter(
    prefix="/api/v1/restaurant",
    tags=["restaurant"]
)

# Función para obtener conexión a la base de datos
def get_restaurant_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'main.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Crear tabla menus al importar el módulo
def init_menu_table():
    try:
        conn = get_restaurant_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                ing_necesarios TEXT DEFAULT '{}'
            )
        """)
        
        # Agregar datos de ejemplo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM menus")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO menus (nombre, descripcion, precio, ing_necesarios)
                VALUES 
                    ('Ceviche Peruano', 'Ceviche fresco con pescado del día', 25.5, '{"pescado": 0.5, "limón": 0.2, "cebolla": 0.1}'),
                    ('Lomo Saltado', 'Lomo saltado tradicional con papas fritas', 18.0, '{"carne": 0.3, "papas": 0.2, "cebolla": 0.1}'),
                    ('Ají de Gallina', 'Tradicional ají de gallina peruano', 16.5, '{"pollo": 0.4, "ají amarillo": 0.1, "leche": 0.2}')
            """)
        
        conn.commit()
        conn.close()
    except Exception as e:
        pass

# Inicializar tabla
init_menu_table()

@router.get("/menu", response_model=List[Menu])
async def get_menus():
    """Obtener todos los menús"""
    conn = None
    try:
        conn = get_restaurant_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nombre, descripcion, precio, ing_necesarios FROM menus ORDER BY id ASC")
        rows = cursor.fetchall()
        
        menus = []
        for row in rows:
            try:
                ingredientes = json.loads(row['ing_necesarios']) if row['ing_necesarios'] else {}
            except:
                ingredientes = {}
            
            menu = Menu(
                id=row['id'],
                nombre=row['nombre'],
                descripcion=row['descripcion'] or "",
                precio=row['precio'],
                ingredientes=ingredientes
            )
            menus.append(menu)
        
        return menus
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.post("/menu", response_model=Menu, status_code=201)
async def create_menu(menu: MenuCreate):
    """Crear un nuevo menú"""
    conn = None
    try:
        conn = get_restaurant_db()
        cursor = conn.cursor()
        
        ingredientes_json = json.dumps(menu.ingredientes)
        
        cursor.execute("""
            INSERT INTO menus (nombre, descripcion, precio, ing_necesarios)
            VALUES (?, ?, ?, ?)
        """, (menu.nombre, menu.descripcion, menu.precio, ingredientes_json))
        
        menu_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT id, nombre, descripcion, precio, ing_necesarios FROM menus WHERE id = ?", (menu_id,))
        row = cursor.fetchone()
        
        try:
            ingredientes = json.loads(row['ing_necesarios']) if row['ing_necesarios'] else {}
        except:
            ingredientes = {}
        
        return Menu(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'] or "",
            precio=row['precio'],
            ingredientes=ingredientes
        )
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/menu/{menu_id}", response_model=Menu)
async def get_menu(menu_id: int):
    """Obtener un menú específico"""
    conn = None
    try:
        conn = get_restaurant_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, nombre, descripcion, precio, ing_necesarios FROM menus WHERE id = ?", (menu_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        try:
            ingredientes = json.loads(row['ing_necesarios']) if row['ing_necesarios'] else {}
        except:
            ingredientes = {}
        
        return Menu(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'] or "",
            precio=row['precio'],
            ingredientes=ingredientes
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.put("/menu/{menu_id}", response_model=Menu)
async def update_menu(menu_id: int, menu: MenuUpdate):
    """Actualizar un menú existente"""
    conn = None
    try:
        conn = get_restaurant_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM menus WHERE id = ?", (menu_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        update_fields = []
        params = []
        
        if menu.nombre is not None:
            update_fields.append("nombre = ?")
            params.append(menu.nombre)
        
        if menu.descripcion is not None:
            update_fields.append("descripcion = ?")
            params.append(menu.descripcion)
        
        if menu.precio is not None:
            update_fields.append("precio = ?")
            params.append(menu.precio)
        
        if menu.ingredientes is not None:
            update_fields.append("ing_necesarios = ?")
            params.append(json.dumps(menu.ingredientes))
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        query = f"UPDATE menus SET {', '.join(update_fields)} WHERE id = ?"
        params.append(menu_id)
        
        cursor.execute(query, params)
        conn.commit()
        
        cursor.execute("SELECT id, nombre, descripcion, precio, ing_necesarios FROM menus WHERE id = ?", (menu_id,))
        row = cursor.fetchone()
        
        try:
            ingredientes = json.loads(row['ing_necesarios']) if row['ing_necesarios'] else {}
        except:
            ingredientes = {}
        
        return Menu(
            id=row['id'],
            nombre=row['nombre'],
            descripcion=row['descripcion'] or "",
            precio=row['precio'],
            ingredientes=ingredientes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.delete("/menu/{menu_id}", status_code=204)
async def delete_menu(menu_id: int):
    """Eliminar un menú"""
    conn = None
    try:
        conn = get_restaurant_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM menus WHERE id = ?", (menu_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Menú no encontrado")
        
        cursor.execute("DELETE FROM menus WHERE id = ?", (menu_id,))
        conn.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        if conn:
            conn.close()