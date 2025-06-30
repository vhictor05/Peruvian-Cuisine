import customtkinter as ctk
from Database.DB import get_db, Base, engine
from apps.Hotel.interfaz import HotelApp

# Configurar tema oscuro
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # Obtener sesión de base de datos
    db_session = next(get_db())
    
    # Crear la aplicación
    app = HotelApp()
    
    try:
        app.mainloop()
    finally:
        db_session.close()