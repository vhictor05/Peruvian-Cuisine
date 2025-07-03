import sqlite3
import os
from datetime import datetime

def check_database():
    # Apuntar a la raíz del proyecto, no a la carpeta api
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.db')
    
    print(f"Buscando base de datos en: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reportes_errores'")
        if not cursor.fetchone():
            print("ERROR: La tabla 'reportes_errores' no existe en la base de datos")
            return False
            
        # Verificar la estructura de la tabla
        cursor.execute("PRAGMA table_info(reportes_errores)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        required_columns = {
            'id': 'INTEGER',
            'titulo': 'TEXT',
            'descripcion': 'TEXT',
            'modulo': 'TEXT',
            'urgencia': 'TEXT',
            'estado': 'TEXT',
            'reportado_por': 'TEXT',
            'fecha_reporte': 'TEXT'
        }
        
        for col, col_type in required_columns.items():
            if col not in columns:
                print(f"ERROR: Falta la columna '{col}' en la tabla 'reportes_errores'")
                return False
        
        # Verificar si hay datos
        cursor.execute("SELECT COUNT(*) as count FROM reportes_errores")
        count = cursor.fetchone()['count']
        print(f"La tabla reportes_errores contiene {count} registros")
        
        # Verificar un registro de ejemplo si hay datos
        if count > 0:
            cursor.execute("SELECT * FROM reportes_errores LIMIT 1")
            row = cursor.fetchone()
            print("\nEstructura de un registro de ejemplo:")
            for key in row.keys():
                print(f"  {key}: {row[key]}")
        
        print("\nLa estructura de la base de datos parece correcta.")
        return True
        
    except Exception as e:
        print(f"ERROR al verificar la base de datos: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_and_create_tables():
    """Verifica y crea las tablas necesarias"""
    try:
        conn = sqlite3.connect('main.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Crear tabla de huéspedes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS huespedes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                rut TEXT UNIQUE NOT NULL,
                email TEXT,
                telefono TEXT,
                fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear tabla de habitaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habitaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                precio REAL NOT NULL,
                disponible BOOLEAN NOT NULL DEFAULT 1
            )
        ''')
        
        # Crear tabla de reservas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                huesped_id INTEGER NOT NULL,
                habitacion_id INTEGER NOT NULL,
                fecha_entrada TEXT NOT NULL,
                fecha_salida TEXT NOT NULL,
                precio_final REAL NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Pendiente',
                fecha_reserva TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (huesped_id) REFERENCES huespedes (id),
                FOREIGN KEY (habitacion_id) REFERENCES habitaciones (id)
            )
        ''')
        
        conn.commit()
        print("✅ Tablas verificadas/creadas correctamente")
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(huespedes)")
        columns = cursor.fetchall()
        print(f"📊 Estructura tabla huéspedes: {[col['name'] for col in columns]}")
        
        cursor.execute("SELECT COUNT(*) as count FROM huespedes")
        count = cursor.fetchone()['count']
        print(f"📊 Número de huéspedes en BD: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar BD: {e}")
        return False

if __name__ == "__main__":
    check_database()
    check_and_create_tables()