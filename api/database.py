import sqlite3
import os
import time

# Definir la ruta de la base de datos
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'main.db')
PRAGMAS_APPLIED = False

# Optimizador de conexión
def optimize_connection(conn):
    """Aplica optimizaciones a la conexión de SQLite"""
    # Write-Ahead Logging para mejor concurrencia
    conn.execute("PRAGMA journal_mode = WAL")
    # Menos durabilidad pero mejor rendimiento
    conn.execute("PRAGMA synchronous = NORMAL")
    # Incrementar caché a 64MB
    conn.execute("PRAGMA cache_size = -64000")
    # Almacenar tablas temporales en memoria
    conn.execute("PRAGMA temp_store = MEMORY")
    # Usar mapeo de memoria para archivos grandes
    conn.execute("PRAGMA mmap_size = 30000000")
    return conn

# Pool de conexiones simple para reutilizar conexiones
CONNECTION_POOL = []
MAX_POOL_SIZE = 5

# Función para obtener una conexión a la base de datos
def get_db_connection():
    global PRAGMAS_APPLIED
    
    # Intentar reutilizar una conexión del pool
    if CONNECTION_POOL:
        conn = CONNECTION_POOL.pop()
        return conn
    
    # Si no hay conexiones disponibles, crear una nueva
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Aplicar optimizaciones
    conn = optimize_connection(conn)
    
    # Crear índices si es la primera vez
    if not PRAGMAS_APPLIED:
        try:
            # Índices para acelerar búsquedas
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reportes_fecha ON reportes_errores(fecha_reporte)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reportes_modulo ON reportes_errores(modulo)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reportes_estado ON reportes_errores(estado)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reportes_mod_est ON reportes_errores(modulo, estado)")
            conn.commit()
            PRAGMAS_APPLIED = True
            print("Optimizaciones de base de datos aplicadas")
        except Exception as e:
            print(f"Error al aplicar optimizaciones: {str(e)}")
    
    return conn

# Función personalizada para cerrar la conexión o devolverla al pool
def close_connection(conn):
    """Cierra la conexión o la devuelve al pool si hay espacio"""
    try:
        # Si la conexión está en una transacción, hacemos rollback
        if conn.in_transaction:
            conn.rollback()
        
        # Si hay espacio en el pool, la añadimos
        if len(CONNECTION_POOL) < MAX_POOL_SIZE:
            CONNECTION_POOL.append(conn)
        else:
            conn.close()
    except:
        # Si hay cualquier error, cerramos la conexión
        try:
            conn.close()
        except:
            pass

def optimize_database_schema():
    """Optimiza la estructura de la base de datos"""
    conn = None
    try:
        conn = get_db_connection()
        
        # Compactar la base de datos (esto puede tomar tiempo)
        conn.execute("VACUUM")
        
        # Analizar la base de datos para mejorar el planificador de consultas
        conn.execute("ANALYZE")
        
        conn.commit()
        print("Optimización de esquema completada")
    except Exception as e:
        print(f"Error en optimización de esquema: {e}")
    finally:
        if conn:
            close_connection(conn)