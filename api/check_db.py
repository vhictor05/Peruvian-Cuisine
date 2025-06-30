import sqlite3
import os

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

if __name__ == "__main__":
    check_database()