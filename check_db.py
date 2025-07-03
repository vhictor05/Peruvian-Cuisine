import sqlite3
import os

# Verificar qué está pasando con la base de datos
db_path = os.path.join("api", "main.db")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== DIAGNÓSTICO DE BASE DE DATOS ===")
    print(f"Archivo DB: {os.path.abspath(db_path)}")
    print(f"Archivo existe: {os.path.exists(db_path)}")
    
    # Ver todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = cursor.fetchall()
    
    print(f"\n📊 TABLAS EXISTENTES:")
    for tabla in tablas:
        cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {tabla[0]}: {count} registros")
        
        # Ver estructura de la tabla
        cursor.execute(f"PRAGMA table_info({tabla[0]})")
        columns = cursor.fetchall()
        print(f"    Columnas: {[col[1] for col in columns]}")
    
    # Verificar específicamente tabla reports
    print(f"\n🔍 VERIFICANDO TABLA REPORTS:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports';")
    reports_exists = cursor.fetchone()
    
    if reports_exists:
        print("✅ Tabla 'reports' existe")
        cursor.execute("SELECT * FROM reports LIMIT 3")
        reports_data = cursor.fetchall()
        print(f"📝 Primeros 3 reportes: {reports_data}")
    else:
        print("❌ Tabla 'reports' NO EXISTE")
    
    # Verificar tabla menus (restaurant)
    print(f"\n🍽️ VERIFICANDO TABLA MENUS (RESTAURANT):")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menus';")
    menus_exists = cursor.fetchone()
    
    if menus_exists:
        print("✅ Tabla 'menus' existe")
        cursor.execute("SELECT * FROM menus LIMIT 3")
        menus_data = cursor.fetchall()
        print(f"🍕 Primeros 3 menús: {menus_data}")
    else:
        print("❌ Tabla 'menus' NO EXISTE")
    
    conn.close()
    
except Exception as e:
    print(f"❌ ERROR AL ACCEDER A LA BASE DE DATOS: {e}")

print("\n=== FIN DIAGNÓSTICO ===")