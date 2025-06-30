import sqlite3
from contextlib import contextmanager
import os

# Obtén la ruta absoluta al directorio raíz del proyecto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(ROOT_DIR, 'main.db')

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Esto permite acceder a las columnas por nombre
    try:
        yield conn
    finally:
        conn.close()