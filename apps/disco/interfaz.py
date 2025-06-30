import customtkinter as ctk
from apps.disco.eventos.eventos_vista import EventosVista
from apps.disco.clientes.clientes_vista import ClientesVista
from apps.disco.tragos.tragos_vista import TragosVista
from Database.DB import get_db
from estructura.facade.discofacade import DiscotecaFacade
from utils.report_button import create_report_button

class DiscotecaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Discoteca")
        self.geometry("950x600")
        self.configure(fg_color="#1e1e2d")
        self.db = next(get_db())
        self.facade = DiscotecaFacade(self.db)
        
        self.setup_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        self.setup_title_frame()
        self.setup_menu_frame()
        self.setup_main_frame()
        
        # Configurar pesos de columnas/filas
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Inicializar vistas
        self.eventos_vista = EventosVista(self.main_frame, self.facade)
        self.clientes_vista = ClientesVista(self.main_frame, self.facade)
        self.tragos_vista = TragosVista(self.main_frame, self.facade)
        
        # Mostrar vista inicial
        self.show_eventos()

    def setup_title_frame(self):
        self.title_frame = ctk.CTkFrame(
            self,
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.title_frame.grid(row=0, column=0, pady="65", sticky="ew")

        ctk.CTkLabel(
            self.title_frame,
            text="DISCO",
            font=("Arial", 27, "bold"),
            text_color="#7209b7"
        ).pack(pady=0, padx=(20,0), anchor="w")

        ctk.CTkLabel(
            self.title_frame,
            text="MANAGER",
            font=("Arial", 23),
            text_color="#9d4dc7"
        ).pack(pady=0, padx=(20,0), anchor="w")

    def setup_menu_frame(self):
        self.menu_frame = ctk.CTkFrame(
            self,
            fg_color="#25253a",
            corner_radius=15
        )
        self.menu_frame.grid(row=1, column=0, sticky="ns", padx=20, pady=20)

        # Agregar botón de reporte al principio del menú
        self.report_button = create_report_button(self.menu_frame, self)
        self.report_button.pack(side="top", pady=(10,20), padx=(20,0))
        
        self.create_menu_button("Eventos", self.show_eventos)
        self.create_menu_button("Clientes", self.show_clientes)
        self.create_menu_button("Tragos", self.show_tragos)

    def setup_main_frame(self):
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#25253a",
            corner_radius=15
        )
        self.main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=20, pady=20)

    def create_menu_button(self, text, command):
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=command,
            fg_color="#25253a",
            hover_color="#9d4dc7",
            font=("Arial", 20),
            corner_radius=0,
            width=200,
            height=50,
            anchor="w"
        )
        btn.pack(side="top", pady=10, padx=(20,0))

    def show_eventos(self):
        self.clear_main_frame()
        self.eventos_vista.show()

    def show_clientes(self):
        self.clear_main_frame()
        self.clientes_vista.show()

    def show_tragos(self):
        self.clear_main_frame()
        self.tragos_vista.show()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    def on_closing(self):
        try:
            self.destroy()
        except Exception:
            pass