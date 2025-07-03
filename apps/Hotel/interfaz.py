import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from apps.Hotel.huespedes.huespedes_vista import HuespedesVista
from apps.Hotel.habitaciones.habitaciones_vista import HabitacionesVista
from apps.Hotel.reservas.reservas_vista import ReservasVista
from Database.DB import get_db, Base, engine
from estructura.facade.hotelfacade import HotelFacade
from estructura.facade.hotel_api_facade import HotelAPIFacade
from utils.report_button import create_report_button
import requests

class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Hotel")
        self.geometry("1100x650")
        self.configure(fg_color="#1e1e2d", corner_radius=15)
        
        # Configurar tema oscuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Crear tablas si no existen (para compatibilidad)
        Base.metadata.create_all(bind=engine)
        
        # Inicializar facade (API o base de datos local)
        self._initialize_facade()
        
        # Configurar el estilo del Treeview
        self.configure_treeview_style()
        
        # Configurar el grid del contenedor principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Crear componentes principales
        self.create_title_frame()
        self.create_menu_frame()
        self.create_main_frame()
        
        # Mostrar panel de huéspedes por defecto
        self.show_huespedes()
    
    def _initialize_facade(self):
        """Inicializa el facade API o base de datos local"""
        try:
            # Intentar conectar con la API
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Hotel conectado a la API")
                self.hotel_facade = HotelAPIFacade()
                self.use_api = True
            else:
                print("⚠️ API no disponible - Hotel usando base de datos local")
                self.db = next(get_db())
                self.hotel_facade = HotelFacade(self.db)
                self.use_api = False
        except requests.RequestException:
            print("⚠️ API no disponible - Hotel usando base de datos local")
            self.db = next(get_db())
            self.hotel_facade = HotelFacade(self.db)
            self.use_api = False
        except Exception as e:
            print(f"❌ Error al inicializar facade: {e}")
            self.db = next(get_db())
            self.hotel_facade = HotelFacade(self.db)
            self.use_api = False

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                        background="#25253a",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#25253a",
                        bordercolor="#f72585",
                        borderwidth=2)
        
        style.map("Treeview",
                  background=[('selected', '#f72585')])
        
        style.configure("Treeview.Heading",
                        background="#f72585",
                        foreground="white",
                        relief="flat")
        
        style.map("Treeview.Heading",
                  background=[('active', '#fa5c9c')])

    def create_title_frame(self):
        self.title_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.title_frame.grid(row=0, column=0, columnspan=2, pady="30", sticky="ew")
        
        self.app_title = ctk.CTkLabel(
            self.title_frame, 
            text="HOTEL", 
            text_color="#f72585", 
            font=("Arial", 26, "bold")
        )
        self.app_title.pack(pady=0, padx=(20,0), anchor="w")

    def create_menu_frame(self):
        self.menu_frame = ctk.CTkFrame(
            self, 
            width=200,
            fg_color="#25253a",
            corner_radius=15
        )
        self.menu_frame.grid(row=1, column=0, sticky="nsw", padx=30, pady=(0, 30))
        self.menu_frame.grid_propagate(False)

        # Agregar el botón de reporte al principio
        self.report_button = create_report_button(self.menu_frame, self)
        self.report_button.pack(side="top", pady=(15,5))
            
        self.create_menu_button("    Huéspedes", self.show_huespedes)
        self.create_menu_button("    Habitaciones", self.show_habitaciones)
        self.create_menu_button("    Reservas", self.show_reservas)

    def create_menu_button(self, text, command):
        button = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=command,
            font=("Arial", 20),
            corner_radius=0,
            height=40,
            width=200,
            fg_color="#25253a",
            hover_color="#f72585",
            anchor="w",
        )
        button.pack(pady=15)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#25253a", 
            corner_radius=15, 
            width=800, 
            height=700
        )
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 30), pady=(0, 30))
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_huespedes(self):
        self.clear_main_frame()
        huespedes_vista = HuespedesVista(self.main_frame, self.hotel_facade)
        huespedes_vista.pack(fill="both", expand=True)

    def show_habitaciones(self):
        self.clear_main_frame()
        habitaciones_vista = HabitacionesVista(self.main_frame, self.hotel_facade)
        habitaciones_vista.pack(fill="both", expand=True)

    def show_reservas(self):
        self.clear_main_frame()
        reservas_vista = ReservasVista(self.main_frame, self.hotel_facade)
        reservas_vista.pack(fill="both", expand=True)
    
    def destroy(self):
        """Limpiar recursos al cerrar"""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
        except:
            pass
        super().destroy()