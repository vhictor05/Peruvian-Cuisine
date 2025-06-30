from Database.DB import get_db, engine, Base
from Restaurante.vistas.menu_vista import MenuPanel
from Restaurante.vistas.pedido_vista import PanelPedido
from Restaurante.vistas.compra_vista import PanelCompra
from Restaurante.vistas.cliente_vista import ClientePanel
from Restaurante.vistas.ingrediente_vista import IngredientePanel
from observer.restaurant_observer import ObserverManager
import customtkinter as ctk

# Configuración global de estilos
ctk.set_appearance_mode("dark")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Restaurante")
        self.geometry("1100x650")
        self.db = next(get_db())
        # Corregido: Pasando self.db al ObserverManager
        self.observer_manager = ObserverManager(self.db)
        
        # Configuración de la interfaz
        self.configure_interface()
        self.create_menu()
        self.create_panels()
        
        # Mostrar panel inicial
        self.load_panel("MenuPanel")

    def configure_interface(self):
        self.configure(fg_color="#1e1e2d")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_menu(self):
        self.menu_frame = ctk.CTkFrame(self, fg_color="#25253a", width=200)
        self.menu_frame.grid(row=0, column=0, sticky="nsw", padx=20, pady=20)
        
        self.create_menu_button("   Menu", "MenuPanel", 3)
        self.create_menu_button("   Panel de compra", "PanelCompra", 4)
        self.create_menu_button("   Pedidos", "PanelPedido", 5)
        self.create_menu_button("   Clientes", "ClientePanel", 6)
        self.create_menu_button("   Ingredientes", "IngredientePanel", 7)

    def create_menu_button(self, text, panel_name, row):
        button = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=lambda: self.load_panel(panel_name),
            font=("Arial", 20),
            corner_radius=0,
            height=40,
            width=200,
            fg_color="#25253a",
            hover_color="#5a75f0",
            anchor="w",
        )
        button.grid(row=row, column=0, pady=15, sticky="w")

    def create_panels(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#25253a")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.panels = {
            "MenuPanel": lambda: MenuPanel(self.main_frame, self.db),
            "PanelCompra": lambda: PanelCompra(self.main_frame, self.db, self.observer_manager),
            "PanelPedido": lambda: PanelPedido(self.main_frame, self.db),
            "ClientePanel": lambda: ClientePanel(self.main_frame, self.db),
            "IngredientePanel": lambda: IngredientePanel(self.main_frame, self.db, self.observer_manager)
        }

    def load_panel(self, panel_name):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        if panel_name in self.panels:
            panel = self.panels[panel_name]()
            panel.pack(fill="both", expand=True)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app = MainApp()
    app.mainloop()