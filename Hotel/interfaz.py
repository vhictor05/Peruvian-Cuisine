import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from Hotel.huespedes.huespedes_vista import HuespedesVista
from Hotel.habitaciones.habitaciones_vista import HabitacionesVista
from Hotel.reservas.reservas_vista import ReservasVista
from Database.DB import get_db
from facade.hotelfacade import HotelFacade

class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Hotel")
        self.geometry("1100x650")
        self.db = next(get_db())
        self.hotel_facade = HotelFacade(self.db)
        self.configure(fg_color="#1e1e2d", corner_radius=15)
        
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

    def configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
            background="#1e1e2d",
            foreground="white",
            fieldbackground="#1e1e2d",
            bordercolor="#3b3b3b",
            borderwidth=0
        )
        style.configure("Treeview.Heading",
            background="#1e1e2d",
            foreground="white",
            borderwidth=1
        )
        style.map('Treeview', 
            background=[('selected', '#f72585')],
            foreground=[('selected', 'white')]
        )

    def create_title_frame(self):
        self.title_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            height=60,
            corner_radius=0
        )
        self.title_frame.grid(row=0, column=0, padx=30, pady=65, sticky="ew")
        self.title_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            self.title_frame,
            text="HOTEL",
            font=("Arial", 26, "bold"),
            text_color="#f72585"
        ).place(relx=0.2, rely=0.3, anchor="w")

        ctk.CTkLabel(
            self.title_frame,
            text="MANAGER",
            font=("Arial", 23),
            text_color="#fa5c9c"
        ).place(relx=0.2, rely=0.7, anchor="w")

    def create_menu_frame(self):
        self.menu_frame = ctk.CTkFrame(
            self, 
            width=200,
            fg_color="#25253a",
            corner_radius=15
        )
        self.menu_frame.grid(row=1, column=0, sticky="nsw", padx=30, pady=(0, 30))
        self.menu_frame.grid_propagate(False)
        
        self.create_menu_button("    Huéspedes", self.show_huespedes)
        self.create_menu_button("    Habitaciones", self.show_habitaciones)
        self.create_menu_button("    Reservas", self.show_reservas)

    def create_menu_button(self, text, command):
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=command,
            font=("Arial", 20),
            height=50,
            width=240,
            corner_radius=0,
            fg_color="#25253a",
            hover_color="#fa5c9c",
            anchor="w",
            text_color="white",
        )
        btn.pack(side="top", fill="x", pady=15)

    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(
            self, 
            corner_radius=15, 
            fg_color="#25253a"
        )
        self.main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10,30), pady=30)

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