import customtkinter as ctk
from Database.DB import get_db, Base, engine
from apps.Hotel.interfaz import HotelApp
from estructura.facade.hotel_api_facade import HotelAPIFacade

# Configurar tema oscuro
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Crear tablas si no existen (para compatibilidad)
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    try:
        # Intentar usar la API primero
        api_facade = HotelAPIFacade()
        
        # Verificar conectividad con la API
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Conectado a la API - Usando modo API")
                app = HotelApp(use_api=True, api_facade=api_facade)
            else:
                print("⚠️ API no disponible - Usando base de datos local")
                db_session = next(get_db())
                app = HotelApp(use_api=False, db_session=db_session)
        except requests.RequestException:
            print("⚠️ API no disponible - Usando base de datos local")
            db_session = next(get_db())
            app = HotelApp(use_api=False, db_session=db_session)
        
        app.mainloop()
        
    except Exception as e:
        print(f"❌ Error al inicializar la aplicación: {e}")
        # Fallback a base de datos local
        db_session = next(get_db())
        app = HotelApp(use_api=False, db_session=db_session)
        app.mainloop()
    finally:
        try:
            if 'db_session' in locals():
                db_session.close()
        except:
            pass