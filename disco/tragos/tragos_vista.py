import customtkinter as ctk
from disco.tragos.registro_vista import RegistroTragosVista
from disco.tragos.pedidos_vista import PedidosTragosVista

class TragosVista:
    def __init__(self, parent, facade):
        self.parent = parent
        self.facade = facade
        
    def show(self):
        self.setup_title()
        self.setup_tabs()
        
    def setup_title(self):
        ctk.CTkLabel(
            self.parent,
            text="Gestión de Tragos",
            text_color="#7209b7",
            font=("Arial", 28, "bold")
        ).pack(pady=10)
        
    def setup_tabs(self):
        # Pestañas
        self.tabview = ctk.CTkTabview(
            self.parent,
            fg_color="#1e1e2d",
            corner_radius=15,
            segmented_button_fg_color="#1e1e2d",
            segmented_button_selected_color="#7209b7",
            segmented_button_selected_hover_color="#9d4dc7"
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Crear tabs
        self.tabview.add("Registro")
        self.tabview.add("Pedidos")
        
        # Inicializar vistas
        self.registro_vista = RegistroTragosVista(
            self.tabview.tab("Registro"),
            self.facade
        )
        self.pedidos_vista = PedidosTragosVista(
            self.tabview.tab("Pedidos"),
            self.facade
        )
        
        # Mostrar contenido inicial
        self.registro_vista.show()
        self.pedidos_vista.show()