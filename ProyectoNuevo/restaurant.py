
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tkinter import messagebox 
import re
import customtkinter as ctk
from crud.ingrediente_crud import IngredienteCRUD
from crud.cliente_crud import ClienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD
from Restaurante.database import get_db, engine, Base
from models_folder.models_restaurente import Pedido,Ingrediente,Cliente,MenuIngrediente,Pedido,Menu
from tkinter import ttk
from fpdf import FPDF
from tkinter import messagebox as CTkM
from datetime import datetime
import tkinter as tk
import matplotlib.pyplot as plt
from Restaurante.graficos import  graficar_menus_mas_comprados, graficar_uso_ingredientes,graficar_ventas_por_fecha
from observer.restaurant_observer import ObserverManager  # Importar el gestor de observers
from facade.compra_facade import CompraFacade
# Configuración global de estilos
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

Base.metadata.create_all(bind=engine)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Restaurante")
        self.geometry("1320x600")
        self.configure(fg_color="#1e1e2d")  # Fondo oscuro
        
        # TODO: Inicializar el gestor de observers
        self.db_session = next(get_db())
        self.observer_manager = ObserverManager(self.db_session)
        
        # Frame del título
        self.title_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.title_frame.grid(row=0, column=0, pady="65", sticky="ew")

        # Título RESTAURANTE
        self.app_title = ctk.CTkLabel(
            self.title_frame, 
            text="RESTAURANTE", 
            text_color="#4361ee", 
            font=("Arial", 26, "bold")
        )
        self.app_title.pack(pady=0, padx=(20,0), anchor="w")  
        
        # Menú lateral (ahora en row=1)
        self.menu_frame = ctk.CTkFrame(
            self, 
            fg_color="#25253a", 
            corner_radius=15
        )
        self.menu_frame.grid(row=1, column=0, sticky="nsw", padx=30, pady=(0, 30))

        # Contenedor principal (ahora en column=1)
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#25253a", 
            corner_radius=15, 
            width=800, 
            height=700
        )
        self.main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 30), pady=30)

        # Botones de navegación
        self.create_menu_button("   Clientes", "ClientePanel", 1)
        self.create_menu_button("   Ingredientes", "IngredientePanel", 2)
        self.create_menu_button("   Menu", "MenuPanel", 3)
        self.create_menu_button("   Panel de compra", "PanelCompra", 4)
        self.create_menu_button("   Pedidos", "PanelPedido", 5)
        self.create_menu_button("   Graficos", "GraficosPanel", 6)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    # Método para crear botones de menú
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

    def load_panel(self, panel_name):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        db_session = next(get_db())
        
        # TODO: Pasar el observer_manager a los paneles que lo necesiten
        if panel_name in ["IngredientePanel", "PanelCompra"]:
            panel = PanelFactory.create_panel(panel_name, self.main_frame, db_session, self.observer_manager)
        else:
            panel = PanelFactory.create_panel(panel_name, self.main_frame, db_session)
            
        panel.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        if hasattr(panel, 'refresh_list'):
            panel.refresh_list()

class PanelFactory:  ## utilizacion de factory method para crear los paneles de la aplicacion de manera dinamica 
    @staticmethod
    def create_panel(panel_name, parent, db, observer_manager=None):
        if panel_name == "ClientePanel":
            return ClientePanel(parent, db)
        elif panel_name == "IngredientePanel":
            return IngredientePanel(parent, db, observer_manager)
        elif panel_name == "MenuPanel":
            return MenuPanel(parent, db)
        elif panel_name == "PanelCompra":
            return PanelCompra(parent, db, observer_manager)
        elif panel_name == "PanelPedido":
            return PanelPedido(parent, db)
        elif panel_name == "GraficosPanel":
            return GraficosPanel(parent, db)
        else:
            raise ValueError(f"Panel '{panel_name}' no reconocido")

class ClientePanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#25253a", corner_radius=15)

        # Título
        self.label_title = ctk.CTkLabel(
            self, 
            text="Gestión de Clientes", 
            text_color="#4361ee",
            font=("Arial", 28, "bold")
        )
        self.label_title.grid(row=0, column=0, columnspan=2, pady=20)

        # Frame para datos del cliente
        self.cliente_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            corner_radius=15,
            width=300,
            height=200
        )
        self.cliente_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=30, sticky="nsew")
        self.cliente_frame.grid_propagate(False)

        # Título del frame
        self.cliente_title = ctk.CTkLabel(
            self.cliente_frame,
            text="Datos del Cliente",
            text_color="#4361ee",
            font=("Arial", 18, "bold")
        )
        self.cliente_title.pack(pady=(10,5))

        # Contenedor para los campos
        self.fields_frame = ctk.CTkFrame(
            self.cliente_frame,
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.fields_frame.pack(pady=5, padx=20, fill="x")

        # Campo Nombre y Email (primera fila)
        nombre_email_frame = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_email_frame.pack(fill="x", pady=2)

        # Campo Nombre (izquierda)
        nombre_container = ctk.CTkFrame(nombre_email_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_container.pack(side="left", fill="x", expand=True, padx=5)

        self.nombre_label = ctk.CTkLabel(nombre_container, text="Nombre:", font=("Arial", 14))
        self.nombre_label.pack(anchor="w", pady=1)
        self.nombre_entry = ctk.CTkEntry(
            nombre_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.nombre_entry.pack(fill="x", pady=(0,2), padx=5)

        # Campo Email (derecha)
        email_container = ctk.CTkFrame(nombre_email_frame, fg_color="#1e1e2d", corner_radius=0)
        email_container.pack(side="right", fill="x", expand=True, padx=5)

        self.email_label = ctk.CTkLabel(email_container, text="Email:", font=("Arial", 14))
        self.email_label.pack(anchor="w", pady=1)
        self.email_entry = ctk.CTkEntry(
            email_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.email_entry.pack(fill="x", pady=(0,2), padx=5)

        # Campo RUT (en una nueva fila)
        rut_container = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        rut_container.pack(fill="x", pady=2, padx=5)  # Añadido padx=5 para alinear con los contenedores superiores

        nombre_email_frame_width = nombre_container.winfo_reqwidth()  # Obtener el ancho del frame de nombre

        self.rut_label = ctk.CTkLabel(rut_container, text="RUT:", font=("Arial", 14))
        self.rut_label.pack(anchor="w", pady=1)
        self.rut_entry = ctk.CTkEntry(
            rut_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.rut_entry.pack(fill="x", pady=(0,10), padx=(5,nombre_container.winfo_reqwidth()))  # Ajustar el padx derecho

        # Botones de acción - Ajustar al mismo ancho que cliente_frame
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=30, sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2), weight=1)  # Distribuir el espacio equitativamente

        self.add_button = ctk.CTkButton(
            btn_frame,
            text="Registrar Cliente",
            command=self.add_cliente,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40,
            corner_radius=15
        )
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.update_button = ctk.CTkButton(
            btn_frame,
            text="Editar Cliente",
            command=self.open_edit_window,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40,
            corner_radius=15
        )
        self.update_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.delete_button = ctk.CTkButton(
            btn_frame,
            text="Eliminar Cliente",
            command=self.delete_cliente,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40,
            corner_radius=15
        )
        self.delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Lista de clientes (Treeview)
        self.cliente_list = self.create_treeview(Cliente)
        self.cliente_list.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        # Configuración de columnas y filas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(3, weight=1)

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
        return treeview

    def create_form_entry(self, label_text, row):
        frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
        frame.grid(row=row, column=0, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame, 
            fg_color="#25253a",
            border_color="#4361ee", 
            border_width=1, 
            corner_radius=10
        )
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

    def validar_rut(self, rut):
        return bool(re.match(r"^\d{7,8}-[0-9kK]$", rut))

    def validar_nombre(self, nombre):
        return bool(re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$", nombre))

    def validar_correo(self, correo):
        return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", correo))
    
    
    def add_cliente(self):
        rut = self.rut_entry.get()
        email = self.email_entry.get()
        nombre = self.nombre_entry.get()
        
        if not nombre or not email or not rut:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        
        if not self.validar_rut(rut):
            messagebox.showerror("Error", "El RUT ingresado no es válido. Debe tener el formato XXXXXXXX-Y.")
            return

        if not self.validar_nombre(nombre):
            messagebox.showerror("Error", "El nombre solo debe contener letras y espacios.")
            return

        if not self.validar_correo(email):
            messagebox.showerror("Error", "El correo electrónico no tiene un formato válido.")
            return

        cliente_existente = ClienteCRUD.get_cliente_by_rut(self.db, rut)
        if cliente_existente:
            messagebox.showinfo("Error", f"El cliente con el RUT '{rut}' ya existe.")
            return
        else:
            cliente = ClienteCRUD.create_cliente(self.db, rut, nombre, email)
            if cliente:
                messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado con éxito.")
            else:
                messagebox.showerror("Error", f"No se pudo registrar el cliente '{nombre}'.")
            self.refresh_list()
    
    def open_edit_window(self):
        selected_item = self.cliente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un cliente de la lista.")
            return
        cliente_rut = self.cliente_list.item(selected_item)["values"][0]  # Cambia el índice para obtener el rut
        cliente = ClienteCRUD.get_cliente_by_rut(self.db, cliente_rut)

        if cliente:
            self.edit_window = ctk.CTkToplevel(self)
            self.edit_window.title("Editar Cliente")
            self.edit_window.geometry("400x300")
            self.edit_window.configure(fg_color="#1c1c1c")

            self.edit_nombre_entry = self.create_form_entry_in_window("Nombre del Cliente:", 1, cliente.nombre)
            self.edit_email_entry = self.create_form_entry_in_window("Email del Cliente:", 2, cliente.email)
        

            self.save_button = ctk.CTkButton(
                self.edit_window, 
                text="Guardar Cambios", 
                command=lambda: self.update_cliente(cliente_rut), 
                corner_radius=50,
                fg_color="#4361ee",
                hover_color="#5a75f0"
            )
            self.save_button.grid(row=5, column=0, pady=10)

    def create_form_entry_in_window(self, label_text, row, value):
        frame = ctk.CTkFrame(self.edit_window, fg_color="#25253a", corner_radius=15)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame,
            corner_radius=10, 
            width=200,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1
        )
        entry.insert(0, value)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry
    
    def update_cliente(self, rut_anterior):
        nombre = self.edit_nombre_entry.get()
        email = self.edit_email_entry.get()
        # rut_nuevo = self.edit_rut_entry.get().replace(".", "").strip()  # Ya no será editable

        if not nombre or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if not self.validar_nombre(nombre):
            messagebox.showerror("Error", "El nombre solo debe contener letras y espacios.")
            return

        if not self.validar_correo(email):
            messagebox.showerror("Error", "El correo electrónico no tiene un formato válido.")
            return

        # No se valida ni solicita el rut_nuevo, solo se mantiene el anterior
        cliente = ClienteCRUD.update_cliente(self.db, rut_anterior, nombre, email, rut_anterior)
        if cliente:
            messagebox.showinfo("Éxito", f"Cliente con RUT '{rut_anterior}' actualizado con éxito.")
            self.edit_window.destroy()
        else:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente '{nombre}'.")
        self.refresh_list()


        self.edit_rut_entry.insert(0, self.formatear_rut(rut_anterior))
        import re

    def validar_rut(self, rut):
        # Acepta formato xx.xxx.xxx-x
        return re.match(r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$", rut) is not None

    
    def delete_cliente(self):
        selected_item = self.cliente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un cliente para eliminar.")
            return

        # Asegurar que se obtiene el RUT correctamente
        values = self.cliente_list.item(selected_item)["values"]
        if not values:
            messagebox.showerror("Error", "No se pudo obtener la información del cliente.")
            return

        cliente_rut = values[0]  # Asegurar que estamos obteniendo el RUT y no el email

        confirmacion = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de que deseas eliminar al cliente con RUT {cliente_rut}?")
        if confirmacion:
            eliminado = ClienteCRUD.delete_cliente(self.db, cliente_rut)  # Asegurar que ClienteCRUD busca por RUT
            if eliminado:
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente con RUT {cliente_rut}.")


    def refresh_list(self):
        for item in self.cliente_list.get_children():
            self.cliente_list.delete(item)
        clientes = ClienteCRUD.get_clientes(self.db)
        for cliente in clientes:
            self.cliente_list.insert("", "end", values=(cliente.rut, cliente.email, cliente.nombre))  # RUT debe ser el primer valor

    def get_selected_email(self):
        selected_item = self.cliente_list.selection()
        if selected_item:
            return self.cliente_list.item(selected_item)["values"][1]  # Cambia el índice para obtener el email
        return None

    def on_select(self, event):
        selected_item = self.cliente_list.selection()
        if selected_item:
            values = self.cliente_list.item(selected_item)["values"]
            self.rut_entry.delete(0, tk.END)
            self.rut_entry.insert(0, values[0])
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, values[1])
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, values[2])

class IngredientePanel(ctk.CTkFrame):
    def __init__(self, parent, db, observer_manager=None):
        super().__init__(parent)
        self.db = db
        self.observer_manager = observer_manager  # Agregar observer manager
        self.configure(fg_color="#25253a", corner_radius=15)

        # Título
        self.label_title = ctk.CTkLabel(
            self, 
            text="Gestión de Ingredientes", 
            text_color="#4361ee", 
            font=("Arial", 28, "bold")
        )
        self.label_title.grid(row=0, column=0, columnspan=2, pady=20)

        # Frame para contener los campos de entrada (mantener en row=1)
        self.form_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            corner_radius=15,
            width=400,
            height=300
        )
        self.form_frame.grid(row=1, column=0, columnspan=2, pady=(5,5), padx=30, sticky="nsew")
        self.form_frame.grid_propagate(False)

        # Título del frame
        self.form_title = ctk.CTkLabel(
            self.form_frame,
            text="Datos del Ingrediente",
            text_color="#4361ee",
            font=("Arial", 18, "bold")
        )
        self.form_title.pack(pady=(10,2))  # Reducido el pady

        # Contenedor para los campos
        self.fields_frame = ctk.CTkFrame(
            self.form_frame,
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.fields_frame.pack(pady=2, padx=20, fill="x")  # Reducido el pady

        # Campo Nombre y Tipo (primera fila)
        nombre_tipo_frame = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_tipo_frame.pack(fill="x", pady=2)

        # Campo Nombre (izquierda)
        nombre_container = ctk.CTkFrame(nombre_tipo_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_container.pack(side="left", fill="x", expand=True, padx=5)

        self.nombre_label = ctk.CTkLabel(nombre_container, text="Nombre:", font=("Arial", 14))
        self.nombre_label.pack(anchor="w", pady=1)
        self.nombre_entry = ctk.CTkEntry(
            nombre_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.nombre_entry.pack(fill="x", pady=(0,2), padx=5)

        # Campo Tipo (derecha)
        tipo_container = ctk.CTkFrame(nombre_tipo_frame, fg_color="#1e1e2d", corner_radius=0)
        tipo_container.pack(side="right", fill="x", expand=True, padx=5)

        self.tipo_label = ctk.CTkLabel(tipo_container, text="Tipo:", font=("Arial", 14))
        self.tipo_label.pack(anchor="w", pady=1)
        self.tipo_entry = ctk.CTkEntry(
            tipo_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.tipo_entry.pack(fill="x", pady=(0,2), padx=5)

        # Campo Cantidad y Unidad de Medida (segunda fila)
        cantidad_unidad_frame = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        cantidad_unidad_frame.pack(fill="x", pady=2)

        # Campo Cantidad (izquierda)
        cantidad_container = ctk.CTkFrame(cantidad_unidad_frame, fg_color="#1e1e2d", corner_radius=0)
        cantidad_container.pack(side="left", fill="x", expand=True, padx=5)

        self.cantidad_label = ctk.CTkLabel(cantidad_container, text="Cantidad:", font=("Arial", 14))
        self.cantidad_label.pack(anchor="w", pady=1)
        self.cantidad_entry = ctk.CTkEntry(
            cantidad_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.cantidad_entry.pack(fill="x", pady=(0,10), padx=5)

        # Campo Unidad de Medida (derecha)
        unidad_container = ctk.CTkFrame(cantidad_unidad_frame, fg_color="#1e1e2d", corner_radius=0)
        unidad_container.pack(side="right", fill="x", expand=True, padx=5)

        self.unidad_label = ctk.CTkLabel(unidad_container, text="Unidad de Medida:", font=("Arial", 14))
        self.unidad_label.pack(anchor="w", pady=1)
        self.unidad_entry = ctk.CTkEntry(
            unidad_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.unidad_entry.pack(fill="x", pady=(0,10), padx=5)

        # Botones de acción (mover a row=2)
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=30, sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2), weight=1)  # Distribuir el espacio equitativamente

        self.add_button = ctk.CTkButton(
            btn_frame, 
            text="Añadir Ingrediente", 
            command=self.add_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40
        )
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.update_button = ctk.CTkButton(
            btn_frame, 
            text="Actualizar Ingrediente", 
            command=self.open_edit_window, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40
        )
        self.update_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.delete_button = ctk.CTkButton(
            btn_frame, 
            text="Eliminar Ingrediente", 
            command=self.delete_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40
        )
        self.delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Lista de ingredientes (mover a row=3)
        self.ingrediente_list = self.create_treeview(Ingrediente)
        self.ingrediente_list.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        # Configuración de columnas y filas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(3, weight=1)

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns if column.name != 'id']
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
        return treeview

    def create_form_entry(self, label_text, row):
        frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
        frame.grid(row=row, column=0, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame, 
            fg_color="#25253a",
            border_color="#4361ee", 
            border_width=1, 
            corner_radius=10
        )
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

    def add_ingrediente(self):
        nombre = self.nombre_entry.get()
        tipo = self.tipo_entry.get()
        cantidad = self.cantidad_entry.get()
        unidad = self.unidad_entry.get()

        if not nombre or not tipo or not cantidad or not unidad:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        ingrediente_existente = IngredienteCRUD.get_ingrediente_by_nombre(self.db, nombre)
        if (ingrediente_existente):
            messagebox.showerror("Error", f"El ingrediente '{nombre}' ya existe.")
            return
        try:
            cantidad = float(cantidad)
            ingrediente = IngredienteCRUD.create_ingrediente(self.db, nombre, tipo, cantidad, unidad)
            if (ingrediente):
                messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' añadido con éxito.")
            else:
                messagebox.showerror("Error", f"Error al registrar el ingrediente '{nombre}'.")
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número.")
        finally:
            self.observer_manager.notify_inventory_change(nombre, 0, cantidad)
            self.refresh_list()

    def open_edit_window(self):
        selected_item = self.ingrediente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return
        
        ingrediente_nombre = self.ingrediente_list.item(selected_item)["values"][0]
        ingrediente = IngredienteCRUD.get_ingrediente_by_nombre(self.db, ingrediente_nombre)

        if ingrediente:
            self.edit_window = ctk.CTkToplevel(self)
            self.edit_window.title("Editar Ingrediente")
            self.edit_window.geometry("400x300")
            self.edit_window.configure(fg_color="#1c1c1c")
            
            self.edit_nombre_entry = self.create_form_entry_in_window("Nombre", 1, ingrediente.nombre)  # Cambia el índice
            self.edit_tipo_entry = self.create_form_entry_in_window("Tipo", 2, ingrediente.tipo)    
            self.edit_cantidad_entry = self.create_form_entry_in_window("Cantidad", 3, ingrediente.cantidad)
            self.edit_unidad_entry = self.create_form_entry_in_window("Unidad de Medida", 4, ingrediente.unidad)

            self.save_button = ctk.CTkButton(
                self.edit_window, 
                text="Guardar Cambios", 
                command=lambda: self.update_ingrediente(ingrediente.id), 
                corner_radius=50,
                fg_color="#4361ee",
                hover_color="#5a75f0"
            )
            self.save_button.grid(row=5, column=0, pady=10)

    def create_form_entry_in_window(self, label_text, row, value):
        frame = ctk.CTkFrame(self.edit_window, fg_color="#25253a", corner_radius=15)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame,
            corner_radius=10, 
            width=200,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1
        )
        entry.insert(0, value)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry    
    
    def update_ingrediente(self, ingrediente_id):
        nombre = self.edit_nombre_entry.get()   
        tipo = self.edit_tipo_entry.get()
        cantidad = self.edit_cantidad_entry.get()
        unidad = self.edit_unidad_entry.get()   

        if not nombre or not tipo or not cantidad or not unidad:    
            messagebox.showerror("Error", "Todos los campos son obligatorios para actualizar un ingrediente.")
            return
        
        try:
            nueva_cantidad = float(cantidad)
            
            # TODO: Obtener cantidad anterior para notificar el cambio
            ingrediente_anterior = IngredienteCRUD.get_ingrediente_by_id(self.db, ingrediente_id)
            cantidad_anterior = ingrediente_anterior.cantidad if ingrediente_anterior else 0
            
            ingrediente = IngredienteCRUD.update_ingrediente(self.db, ingrediente_id, nombre, nueva_cantidad, tipo, unidad)
            if ingrediente:
                messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' actualizado con éxito.")
                self.edit_window.destroy()
                
                # TODO: Notificar cambio en inventario usando observer
                if self.observer_manager:
                    self.observer_manager.notify_inventory_change(nombre, cantidad_anterior, nueva_cantidad)
            else:
                messagebox.showerror("Error", f"Error al actualizar el ingrediente '{nombre}'.")
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número.")
        finally:
            self.refresh_list()

    def delete_ingrediente(self):
        selected_item = self.ingrediente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return
        
        ingrediente_id = self.ingrediente_list.item(selected_item)["values"][-1]
        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar el ingrediente '{ingrediente_id}'?")
        if confirm:
            ingrediente = IngredienteCRUD.delete_ingrediente(self.db, ingrediente_id)
            if (ingrediente):
                messagebox.showinfo("Éxito", "Ingrediente eliminado con éxito.")
            else:
                messagebox.showerror("Error", "Error al eliminar el ingrediente.")
        self.refresh_list()

    def refresh_list(self):
        for item in self.ingrediente_list.get_children():
            self.ingrediente_list.delete(item)
        ingredientes = IngredienteCRUD.get_ingredientes(self.db)
        for ingrediente in ingredientes:
            self.ingrediente_list.insert("", "end", values=(ingrediente.nombre, ingrediente.tipo, ingrediente.cantidad, ingrediente.unidad,ingrediente.id))
        
    def on_select(self, event):
        selected_item = self.ingrediente_list.selection()
        if selected_item:
            values = self.ingrediente_list.item(selected_item)["values"]
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, values[0])
            self.tipo_entry.delete(0, tk.END)
            self.tipo_entry.insert(0, values[1])
            self.cantidad_entry.delete(0, tk.END)
            self.cantidad_entry.insert(0, values[2])
            self.unidad_entry.delete(0, tk.END)
            self.unidad_entry.insert(0, values[3])
            self.ingrediente_list.insert("", "end", values=())

class MenuPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#25253a", corner_radius=15)

        self.label_title = ctk.CTkLabel(
            self, 
            text="Gestión de Menú", 
            text_color="#4361ee",
            font=("Arial", 28, "bold")
        )
        self.label_title.grid(row=0, column=0, pady=20)

        # Frame para datos del menú
        self.menu_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            corner_radius=15,
            width=400,
            height=200
        )
        self.menu_frame.grid(row=1, column=0, pady=10, padx=30, sticky="nsew")
        self.menu_frame.grid_propagate(False)

        # Título del frame
        self.menu_title = ctk.CTkLabel(
            self.menu_frame,
            text="Datos del Menú",
            text_color="#4361ee",
            font=("Arial", 18, "bold")
        )
        self.menu_title.pack(pady=(10,5))

        # Contenedor para los campos
        self.fields_frame = ctk.CTkFrame(
            self.menu_frame,
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.fields_frame.pack(pady=5, padx=20, fill="x")

        # Campo Nombre y Descripción (primera fila)
        nombre_descripcion_frame = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_descripcion_frame.pack(fill="x", pady=2)

        # Campo Nombre (izquierda)
        nombre_container = ctk.CTkFrame(nombre_descripcion_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_container.pack(side="left", fill="x", expand=True, padx=5)

        self.nombre_label = ctk.CTkLabel(nombre_container, text="Nombre del Menú:", font=("Arial", 14))
        self.nombre_label.pack(anchor="w", pady=1)
        self.nombre_entry = ctk.CTkEntry(
            nombre_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.nombre_entry.pack(fill="x", pady=(0,2), padx=5)

        # Campo Descripción (derecha)
        descripcion_container = ctk.CTkFrame(nombre_descripcion_frame, fg_color="#1e1e2d", corner_radius=0)
        descripcion_container.pack(side="right", fill="x", expand=True, padx=5)

        self.descripcion_label = ctk.CTkLabel(descripcion_container, text="Descripción del Menú:", font=("Arial", 14))
        self.descripcion_label.pack(anchor="w", pady=1)
        self.descripcion_entry = ctk.CTkEntry(
            descripcion_container,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.descripcion_entry.pack(fill="x", pady=(0,2), padx=5)

        # Mantener el campo Precio como está
        self.precio_label = ctk.CTkLabel(self.fields_frame, text="Precio del Menú:", font=("Arial", 14))
        self.precio_label.pack(anchor="w", pady=2)
        self.precio_entry = ctk.CTkEntry(
            self.fields_frame,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            corner_radius=5,
            height=30
        )
        self.precio_entry.pack(fill="x", pady=(0,10))
        
        # Primero los botones de menú
        self.button_frame = ctk.CTkFrame(self, fg_color="#25253a")
        self.button_frame.grid(row=2, column=0, pady=10)

        self.add_button = ctk.CTkButton(
            self.button_frame, 
            text="Registrar Menú", 
            font=("Arial", 16),
            command=self.add_menu, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.add_button.grid(row=0, column=0, padx=5)

        self.update_button = ctk.CTkButton(
            self.button_frame, 
            text="Editar Menú",
            font=("Arial", 16),
            command=self.open_edit_window, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.update_button.grid(row=0, column=1, padx=5)

        self.delete_button = ctk.CTkButton(
            self.button_frame, 
            text="Eliminar Menú",
            font=("Arial", 16), 
            command=self.delete_menu, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.delete_button.grid(row=0, column=2, padx=5)

        # Después el frame de ingredientes
        self.ingredientes_frame = ctk.CTkFrame(
            self, 
            fg_color="#25253a", 
            corner_radius=15,
            width=400  # Mismo ancho que menu_frame
        )
        self.ingredientes_frame.grid(row=3, column=0, pady=10, padx=30, sticky="nsew")  # Cambiado a row=3
        self.ingredientes_frame.grid_propagate(False)

        self.ingredientes_label = ctk.CTkLabel(
            self.ingredientes_frame, 
            text="Ingredientes:", 
            font=("Arial", 14)
        )
        self.ingredientes_label.grid(row=0, column=0, padx=10, pady=(5,2))

        self.ingredientes_combobox = ctk.CTkComboBox(
            self.ingredientes_frame, 
            values=[], 
            height=30,
            width=200, 
            corner_radius=5,
            fg_color="#4361ee",
            button_color="#4361ee",
            button_hover_color="#5a75f0",
            dropdown_fg_color="#1e1e2d",
            border_color="#4361ee"
        )
        self.ingredientes_combobox.grid(row=1, column=0, padx=10, pady=(0,5))

        self.cantidad_label = ctk.CTkLabel(
            self.ingredientes_frame, 
            text="Cantidad de Ingredientes:", 
            font=("Arial", 14)
        )
        self.cantidad_label.grid(row=0, column=1, padx=10, pady=(5,2))  # Misma columna que el entry pero fila 0

        self.cantidad_entry = ctk.CTkEntry(
            self.ingredientes_frame, 
            corner_radius=5,
            height=30,
            width=150,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1
        )
        self.cantidad_entry.grid(row=1, column=1, padx=10, pady=(0,5))  # Se mantiene en fila 1

        self.add_ingrediente_button = ctk.CTkButton(
            self.ingredientes_frame, 
            text="Añadir Ingrediente",
            font=("Arial", 16),
            command=self.add_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.add_ingrediente_button.grid(row=1, column=2, padx=10, pady=5)

        self.update_ingrediente_button = ctk.CTkButton(
            self.ingredientes_frame, 
            text="Actualizar Ingrediente",
            font=("Arial", 16), 
            command=self.update_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.update_ingrediente_button.grid(row=1, column=3, padx=10, pady=5)

        self.delete_ingrediente_button = ctk.CTkButton(
            self.ingredientes_frame, 
            text="Eliminar Ingrediente", 
            font=("Arial", 16),
            command=self.delete_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.delete_ingrediente_button.grid(row=1, column=4, padx=10, pady=5)

        self.ingredientes_list = self.create_treeview_ingredientes()
        self.ingredientes_list.grid(row=2, column=0, columnspan=5, pady=10, sticky="nsew")

        self.button_frame = ctk.CTkFrame(self, fg_color="#25253a")
        self.button_frame.grid(row=5, column=0, pady=10, sticky="ew")

        self.menu_list = self.create_treeview(Menu)
        self.menu_list.grid(row=10, column=0, pady=40, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.refresh_list()
        self.load_ingredientes()

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns if column.name not in ['id']] + ["ing_necesarios"]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
        return treeview

    def create_treeview_ingredientes(self):
        columns = ["Ingrediente", "Cantidad"]
        treeview = ttk.Treeview(self.ingredientes_frame, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column)
        return treeview

    def load_ingredientes(self):
        ingredientes = IngredienteCRUD.get_ingredientes(self.db)
        ingrediente_names = [ingrediente.nombre for ingrediente in ingredientes]
        self.ingredientes_combobox.configure(values=ingrediente_names)
        self.ingredientes_combobox.set("Por favor selecciona un ingrediente")

    def add_ingrediente(self):
        ingrediente = self.ingredientes_combobox.get()
        cantidad = self.cantidad_entry.get()

        if not ingrediente or not cantidad:
            messagebox.showerror("Error", "Selecciona un ingrediente y especifica la cantidad.")
            return

        try:
            cantidad = float(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número.")
            return

        # Check if the ingredient already exists in the list
        for item in self.ingredientes_list.get_children():
            existing_ingrediente, _ = self.ingredientes_list.item(item, "values")
            if existing_ingrediente == ingrediente:
                messagebox.showerror("Error", "El ingrediente ya está en la lista.")
                return

        self.ingredientes_list.insert("", "end", values=(ingrediente, cantidad))
        self.cantidad_entry.delete(0, "end")

    def update_ingrediente(self):
        selected_item = self.ingredientes_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return

        ingrediente = self.ingredientes_combobox.get()
        cantidad = self.cantidad_entry.get()

        if not ingrediente or not cantidad:
            messagebox.showerror("Error", "Selecciona un ingrediente y especifica la cantidad.")
            return

        try:
            cantidad = float(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        # Check if the ingredient already exists in the list
        for item in self.ingredientes_list.get_children():
            if item != selected_item[0]:
                existing_ingrediente, _ = self.ingredientes_list.item(item, "values")
                if existing_ingrediente == ingrediente:
                    messagebox.showerror("Error", "El ingrediente ya está en la lista.")
                    return

        self.ingredientes_list.item(selected_item, values=(ingrediente, cantidad))
        self.cantidad_entry.delete(0, "end")

    def delete_ingrediente(self):
        selected_item = self.ingredientes_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return
        
        self.ingredientes_list.delete(selected_item)

    def get_ingredientes_from_list(self):
        ingredientes = []
        for item in self.ingredientes_list.get_children():
            ingrediente, cantidad = self.ingredientes_list.item(item, "values")
            ingrediente_obj = IngredienteCRUD.get_ingrediente_by_nombre(self.db, ingrediente)
            if ingrediente_obj:
                ingredientes.append({"id": ingrediente_obj.id, "cantidad": float(cantidad)})
        return ingredientes

    def add_menu(self):
        nombre = self.nombre_entry.get()
        descripcion = self.descripcion_entry.get()
        precio = self.precio_entry.get()

        if not nombre or not descripcion or not precio:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            precio = float(precio)
            if precio <= 0:
                messagebox.showerror("Error", "El precio debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")
            return

        menu_existente = MenuCRUD.get_menu_by_nombre(self.db, nombre)
        if (menu_existente):
            messagebox.showerror("Error", f"El menú '{nombre}' ya existe.")
            return

        ingredientes = self.get_ingredientes_from_list()

        menu = MenuCRUD.create_menu(self.db, nombre, descripcion, precio, ingredientes)
        if (menu):
            messagebox.showinfo("Éxito", f"Menú '{nombre}' registrado con éxito.")
        else:
            messagebox.showerror("Error", f"Error al registrar el menú '{nombre}'.")
        self.refresh_list()

    def open_edit_window(self):
        selected_item = self.menu_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un menú de la lista.")
            return

        menu_id = self.menu_list.item(selected_item)["values"][0]
        menu = MenuCRUD.get_menu_by_nombre(self.db, menu_id)

        if menu:
            self.edit_window = ctk.CTkToplevel(self)
            self.edit_window.title("Editar Menú")
            self.edit_window.geometry("400x400")
            self.edit_window.configure(fg_color="#1c1c1c")

            self.edit_nombre_entry = self.create_form_entry_in_window("Nombre del Menú", 1, menu.nombre)
            self.edit_descripcion_entry = self.create_form_entry_in_window("Descripción del Menú", 2, menu.descripcion)
            self.edit_precio_entry = self.create_form_entry_in_window("Precio del Menú", 3, menu.precio)

            self.edit_ingredientes_frame = ctk.CTkFrame(
                self.edit_window, 
                fg_color="#2c2c2c", 
                corner_radius=10
            )
            self.edit_ingredientes_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

            self.edit_ingredientes_label = ctk.CTkLabel(
                self.edit_ingredientes_frame, 
                text="Ingredientes:", 
                font=("Arial", 14)
            )
            self.edit_ingredientes_label.grid(row=0, column=0, padx=10, pady=5)

            self.edit_ingredientes_combobox = ctk.CTkComboBox(
                self.edit_ingredientes_frame, 
                values=[],
                height=30,
                width=200, 
                corner_radius=5
            )
            self.edit_ingredientes_combobox.grid(row=1, column=0, padx=10, pady=5)

            self.edit_cantidad_entry = ctk.CTkEntry(
                self.edit_ingredientes_frame, 
                corner_radius=5,
                height=30,
                width=100
            )
            self.edit_cantidad_entry.grid(row=1, column=1, padx=10, pady=5)

            self.edit_add_ingrediente_button = ctk.CTkButton(
                self.edit_ingredientes_frame, 
                text="Añadir Ingrediente", 
                command=self.edit_add_ingrediente, 
                corner_radius=15,
                fg_color="#4361ee",
                hover_color="#5a75f0"
            )
            self.edit_add_ingrediente_button.grid(row=1, column=2, padx=10, pady=5)

            self.edit_update_ingrediente_button = ctk.CTkButton(
                self.edit_ingredientes_frame, 
                text="Actualizar Ingrediente", 
                command=self.edit_update_ingrediente, 
                corner_radius=15,
                fg_color="#4361ee",
                hover_color="#5a75f0"
            )
            self.edit_update_ingrediente_button.grid(row=1, column=3, padx=10, pady=5)

            self.edit_delete_ingrediente_button = ctk.CTkButton(
                self.edit_ingredientes_frame, 
                text="Eliminar Ingrediente", 
                command=self.edit_delete_ingrediente, 
                corner_radius=15,
                fg_color="#4361ee",
                hover_color="#5a75f0"
            )
            self.edit_delete_ingrediente_button.grid(row=1, column=4, padx=10, pady=5)

            self.edit_ingredientes_list = self.create_treeview_ingredientes()
            self.edit_ingredientes_list.grid(row=2, column=0, columnspan=5, pady=10, sticky="nsew")

            for ingrediente in menu.ingredientes:
                self.edit_ingredientes_list.insert("", "end", values=(ingrediente.ingrediente.nombre, ingrediente.cantidad))

            self.save_button = ctk.CTkButton(
                self.edit_window, 
                text="Guardar Cambios", 
                command=lambda: self.update_menu(menu.id), 
                corner_radius=50,
                fg_color="#4361ee",
                hover_color="#5a75f0"
            )
            self.save_button.grid(row=5, column=0, pady=10)

            self.load_ingredientes()

    def create_form_entry_in_window(self, label_text, row, value):
        frame = ctk.CTkFrame(self.edit_window, fg_color="#25253a", corner_radius=15)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame,
            corner_radius=5,
            height=30,
            width=200,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1
        )
        entry.insert(0, value)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

    def edit_add_ingrediente(self):
        ingrediente = self.edit_ingredientes_combobox.get()
        cantidad = self.edit_cantidad_entry.get()

        if not ingrediente or not cantidad:
            messagebox.showerror("Error", "Selecciona un ingrediente y especifica la cantidad.")
            return

        try:
            cantidad = float(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        # Check if the ingredient already exists in the list
        for item in self.edit_ingredientes_list.get_children():
            existing_ingrediente, _ = self.edit_ingredientes_list.item(item, "values")
            if existing_ingrediente == ingrediente:
                messagebox.showerror("Error", "El ingrediente ya está en la lista.")
                return

        self.edit_ingredientes_list.insert("", "end", values=(ingrediente, cantidad))
        self.edit_cantidad_entry.delete(0, "end")

    def edit_update_ingrediente(self):
        selected_item = self.edit_ingredientes_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return

        ingrediente = self.edit_ingredientes_combobox.get()
        cantidad = self.edit_cantidad_entry.get()

        if not ingrediente or not cantidad:
            messagebox.showerror("Error", "Selecciona un ingrediente y especifica la cantidad.")
            return

        try:
            cantidad = float(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        # Check if the ingredient already exists in the list
        for item in self.edit_ingredientes_list.get_children():
            if item != selected_item[0]:
                existing_ingrediente, _ = self.edit_ingredientes_list.item(item, "values")
                if existing_ingrediente == ingrediente:
                    messagebox.showerror("Error", "El ingrediente ya está en la lista.")
                    return

        self.edit_ingredientes_list.item(selected_item, values=(ingrediente, cantidad))
        self.edit_cantidad_entry.delete(0, "end")

    def edit_delete_ingrediente(self):
        selected_item = self.edit_ingredientes_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return

        self.edit_ingredientes_list.delete(selected_item)

    def get_ingredientes_from_edit_list(self):
        ingredientes = []
        for item in self.edit_ingredientes_list.get_children():
            ingrediente, cantidad = self.edit_ingredientes_list.item(item, "values")
            ingrediente_obj = IngredienteCRUD.get_ingrediente_by_nombre(self.db, ingrediente)
            if ingrediente_obj:
                ingredientes.append({"id": ingrediente_obj.id, "cantidad": float(cantidad)})
        return ingredientes

    def update_menu(self, menu_id):
        nombre = self.edit_nombre_entry.get()
        descripcion = self.edit_descripcion_entry.get()
        precio = self.edit_precio_entry.get()

        if not nombre or not descripcion or not precio:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            precio = float(precio)
            if precio <= 0:
                messagebox.showerror("Error", "El precio debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")
            return

        ingredientes = self.get_ingredientes_from_edit_list()

        menu = MenuCRUD.update_menu(self.db, menu_id, nombre, descripcion, precio, ingredientes)
        if (menu):
            messagebox.showinfo("Éxito", f"Menú '{nombre}' actualizado con éxito.")
            self.edit_window.destroy()
        else:
            messagebox.showerror("Error", f"Error al actualizar el menú '{nombre}'.")
        self.refresh_list()

    def delete_menu(self):
        selected_item = self.menu_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un menú de la lista.")
            return

        menu_nombre = self.menu_list.item(selected_item, 'values')[0]
        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar el menú '{menu_nombre}'?")
        if confirm:
            menu = MenuCRUD.get_menu_by_nombre(self.db, menu_nombre)
            if menu:
                MenuCRUD.delete_menu(self.db, menu.id)
                messagebox.showinfo("Éxito", f"Menú '{menu_nombre}' eliminado con éxito.")
                self.refresh_list()
            else:
                messagebox.showerror("Error", f"No se pudo encontrar el menú '{menu_nombre}'.")

    def refresh_list(self):
        for item in self.menu_list.get_children():
            self.menu_list.delete(item)
        menus = MenuCRUD.get_menus(self.db)
        for menu in menus:
            ing_necesarios = ", ".join([f"{cantidad}x {nombre}" for nombre, cantidad in menu.ing_necesarios.items()])
            self.menu_list.insert("", "end", values=(menu.nombre, menu.descripcion, menu.precio, ing_necesarios))

    def on_select(self, event):
        selected_item = self.menu_list.selection()
        if selected_item:
            values = self.menu_list.item(selected_item)["values"]
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, values[0])
            self.descripcion_entry.delete(0, tk.END)
            self.descripcion_entry.insert(0, values[1])
            self.precio_entry.delete(0, tk.END)
            self.precio_entry.insert(0, values[2])

    def create_form_entry(self, label_text, row):
        frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)  # Updated color back to #25253e
        frame.grid(row=row, column=0, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame, 
            fg_color="#25253a",
            border_color="#4361ee", 
            border_width=1, 
            corner_radius=5,
            height=30
        )
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

class PanelCompra(ctk.CTkFrame):
    def __init__(self, parent, db, observer_manager=None):
        super().__init__(parent)
        self.db = db  
        self.carrito = []  # Lista para almacenar los productos del carrito
        self.facade = CompraFacade(db, observer_manager)
        self.configure(fg_color="#25253a")

        # Título del Panel de Compra
        self.label_title = ctk.CTkLabel(
            self, 
            text="Panel de Compra", 
            text_color="#4361ee",
            font=("Arial", 28, "bold")
        )
        self.label_title.grid(row=0, column=0, pady=20, columnspan=2) 

        # Frame para la entrada de productos y cantidad
        self.entry_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d", 
            corner_radius=15,
            width=300  # Ancho fijo para el frame
        )
        self.entry_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        self.entry_frame.grid_propagate(False)

        # Combobox para seleccionar un menú
        self.menu_combobox = ctk.CTkComboBox(
            self.entry_frame, 
            values=[],
            height=30,
            width=250, 
            corner_radius=10,
            fg_color="#4361ee",
            button_color="#4361ee",
            button_hover_color="#5a75f0",
            dropdown_fg_color="#1e1e2d",
            border_color="#4361ee"
        )
        self.menu_combobox.set("Selecciona un menú:")
        self.menu_combobox.pack(pady=(20,10), padx=10)

        # Entrada de cantidad
        cantidad_container = ctk.CTkFrame(self.entry_frame, fg_color="#1e1e2d")
        cantidad_container.pack(pady=10, padx=10, fill="x")

        self.cantidad_label = ctk.CTkLabel(cantidad_container, text="Cantidad:", font=("Arial", 14))
        self.cantidad_label.pack(anchor="w", padx=10)
        self.cantidad_entry = ctk.CTkEntry(
            cantidad_container,
            corner_radius=5,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1,
            height=30,
            width=250
        )
        self.cantidad_entry.pack(pady=5)

        # ComboBox para seleccionar cliente
        self.cliente_combobox = ctk.CTkComboBox(
            self.entry_frame, 
            values=[], 
            height=30,
            width=250, 
            corner_radius=10,
            fg_color="#4361ee",
            button_color="#4361ee",
            button_hover_color="#5a75f0",
            dropdown_fg_color="#1e1e2d",
            border_color="#4361ee"
        )
        self.cliente_combobox.set("Selecciona un cliente")
        self.cliente_combobox.pack(pady=10, padx=10)

        # Botón para agregar al carrito
        self.add_button = ctk.CTkButton(
            self.entry_frame, 
            text="Agregar al carrito",
            font=("Arial", 16),
            command=self.add_to_cart, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40,
            width=250
        )
        self.add_button.pack(pady=(10,20), padx=10)

        # Lista de productos en el carrito (mover a la derecha)
        self.cart_list = self.create_treeview()
        self.cart_list.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        # Configurar el peso de las columnas
        self.grid_columnconfigure(1, weight=1)  # La columna del treeview se expandirá

        # Botón para realizar compra
        self.buy_button = ctk.CTkButton(
            self, 
            text="Realizar Compra", 
            font=("Arial", 16),
            command=self.complete_purchase, 
            corner_radius=15, 
            fg_color="#4361ee", 
            hover_color="#5a75f0",
            height=40
        )
        self.buy_button.grid(row=3, column=0, pady=10, columnspan=2)

        # Label para el total
        self.total_label = ctk.CTkLabel(self, text="Total: $0.00", font=("Arial", 16, "bold"), text_color="white")
        self.total_label.grid(row=4, column=0, pady=10, columnspan=2)

        # Lista interna para almacenar los productos seleccionados
        self.cart = []  # Aquí guardaremos los productos y cantidades seleccionadas

        self.load_clientes()  # Ensure clients are loaded into the combobox
        self.load_menus()  # Ensure menus are loaded into the combobox

    def create_form_entry(self, label_text, row, column):
        frame = ctk.CTkFrame(self.entry_frame, fg_color="#25253a", corner_radius=15)
        frame.grid(row=row, column=column, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.grid(row=0, column=0, padx=10)

        entry = ctk.CTkEntry(
            frame, 
            fg_color="#25253a",
            border_color="#4361ee", 
            border_width=1, 
            corner_radius=5,
            height=30
        )
        entry.grid(row=0, column=1, padx=10)

        return entry

    def create_treeview(self):
        columns = ["Producto", "Cantidad", "Total"]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column)
        return treeview

    def load_menus(self):
        # Cargar los menús desde la Base de datos
        menus = MenuCRUD.get_menus(self.db)
        menu_names = [menu.nombre for menu in menus]
        if not menu_names:
            messagebox.showinfo("Sin menús", "No hay menús disponibles en el sistema.")
            return
        # Actualizar el combobox con los menús cargados
        self.menu_combobox.configure(values=menu_names)

    def load_clientes(self):

        clientes = ClienteCRUD.get_clientes(self.db)
        cliente_ruts = [cliente.rut for cliente in clientes]
        if not cliente_ruts:
            messagebox.showinfo("Sin clientes", "No hay clientes disponibles en el sistema.")
            return
        self.cliente_combobox.configure(values=cliente_ruts)

    def verificar_disponibilidad_ingredientes(self, menu, cantidad):
        ingredientes_necesarios = {}
        for item in menu.ingredientes:
            if item.ingrediente.nombre in ingredientes_necesarios:
                ingredientes_necesarios[item.ingrediente.nombre] += item.cantidad * cantidad
            else:
                ingredientes_necesarios[item.ingrediente.nombre] = item.cantidad * cantidad

        for ingrediente_nombre, cantidad_necesaria in ingredientes_necesarios.items():
            ingrediente = IngredienteCRUD.get_ingrediente_by_nombre(self.db, ingrediente_nombre)
            if not ingrediente or ingrediente.cantidad < cantidad_necesaria:
                return False
        return True

    def add_to_cart(self):
        selected_menu = self.menu_combobox.get()
        cantidad = self.cantidad_entry.get()

        if selected_menu == "Selecciona un menú":
            messagebox.showerror("Error", "Por favor, selecciona un menú.")
            return

        if not cantidad:
            messagebox.showerror("Error", "La cantidad es obligatoria.")
            return

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero.")
            return

        menu = next((menu for menu in MenuCRUD.get_menus(self.db) if menu.nombre == selected_menu), None)
        if menu:
            if not self.verificar_disponibilidad_ingredientes(menu, cantidad):
                messagebox.showerror("Error", "No hay suficientes ingredientes para agregar este menú al carrito.")
                return

            precio = menu.precio
            total_producto = precio * cantidad
            self.cart.append((selected_menu, cantidad, total_producto))

            self.refresh_cart_list()
            self.cantidad_entry.delete(0, "end")
        else:
            messagebox.showerror("Error", "No se pudo encontrar el menú seleccionado.")

    def complete_purchase(self):
        if not self.cart:
            messagebox.showerror("Error", "No hay productos en el carrito.")
            return

        cliente_rut = self.cliente_combobox.get()
        if cliente_rut == "Selecciona un cliente":
            messagebox.showerror("Error", "Por favor, selecciona un cliente.")
            return

        nuevo_pedido = self.facade.procesar_compra(cliente_rut, self.cart)

        if nuevo_pedido:
            messagebox.showinfo("Compra Realizada", "¡Gracias por tu compra!")
            self.cart.clear()
            self.refresh_cart_list()
        else:
            messagebox.showerror("Error", "No se pudo realizar la compra.")

    def refresh_cart_list(self):
        for item in self.cart_list.get_children():
            self.cart_list.delete(item)
        total = 0
        for item in self.cart:
            producto, cantidad, total_producto = item
            self.cart_list.insert("","end", values=(producto, cantidad, f"${total_producto:.2f}"))
            total += total_producto

        self.update_total(total)

    def update_total(self, total):
        self.total_label.configure(text=f"Total: ${total:.2f}")

    def calculate_menu_price(self, menu):
        # Simular la obtención del precio de un menú
        # Puedes calcular el precio total del menú sumando el precio de los ingredientes
        precio_total = 0
        for item in menu.ingredientes:
            ingrediente = IngredienteCRUD.get_ingrediente_by_id(self.db, item.ingrediente_id)
            if ingrediente:
                precio_total += ingrediente.cantidad * item.cantidad
        return precio_total

class PanelPedido(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#25253a")

        # Título del Panel de Pedido
        self.label_title = ctk.CTkLabel(
            self, 
            text="Panel de Pedidos", 
            font=("Arial", 28, "bold"), 
            text_color="#4361ee"
        )
        self.label_title.grid(row=0, column=0, pady=20, columnspan=3)

        # Filtros
        self.filter_frame = ctk.CTkFrame(self, fg_color="#1e1e2d", corner_radius=15)
        self.filter_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew", columnspan=3)

        # Modificar la disposición de los filtros cambiando la columna por fila
        self.cliente_filter = self.create_filter_combobox("Filtrar por Cliente (RUT):", row=0)
    

        # Crear un frame contenedor para los botones
        buttons_container = ctk.CTkFrame(self.filter_frame, fg_color="#1e1e2d", corner_radius=0)
        buttons_container.grid(row=0, column=1, rowspan=3, padx=10, pady=5, sticky="ns")

        # Botón Aplicar Filtros
        self.apply_filter_button = ctk.CTkButton(
            buttons_container, 
            text="Aplicar Filtros", 
            font=("Arial", 16),
            command=self.apply_filters, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40,
            width=150
        )
        self.apply_filter_button.pack(side="left", padx=5)  # Cambiado a side="left"

        # Botón Limpiar Filtros
        self.clear_filter_button = ctk.CTkButton(
            buttons_container, 
            text="Limpiar Filtros", 
            font=("Arial", 16),
            command=self.clear_filters, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40,
            width=150
        )
        self.clear_filter_button.pack(side="left", padx=5)  # Cambiado a side="left"

        # Treeview para mostrar los pedidos
        self.pedido_list = self.create_treeview(Pedido)
        self.pedido_list.grid(row=2, column=0, pady=20, sticky="nsew", columnspan=3)

        # Botones para agregar, editar y eliminar pedidos
        self.btn_frame = ctk.CTkFrame(self, fg_color="#25253a")
        self.btn_frame.grid(row=3, column=0, pady=5, columnspan=3)

        

        self.btn_delete = ctk.CTkButton(
            self.btn_frame, 
            text="Eliminar Pedido", 
            font=("Arial", 16),
            command=self.delete_pedido,
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.btn_delete.grid(row=0, column=2, padx=5)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.load_clientes()
        self.refresh_list()

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns] + ["menus"]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
            treeview.column(column, anchor='center')  # Centrar el texto
        return treeview

    def create_filter_entry(self, label_text, row):
        frame = ctk.CTkFrame(self.filter_frame, fg_color="#1e1e2d", corner_radius=15)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(
            frame, 
            corner_radius=5,
            height=30,
            width=200,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1
        )
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

    def create_filter_combobox(self, label_text, row):
        frame = ctk.CTkFrame(self.filter_frame, fg_color="#1e1e2d", corner_radius=15)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        combobox = ctk.CTkComboBox(
            frame, 
            values=[],
            height=30, 
            width=200, 
            corner_radius=5,
            fg_color="#4361ee",
            button_color="#4361ee",
            button_hover_color="#5a75f0",
            dropdown_fg_color="#1e1e2d",
            border_color="#4361ee"
        )
        combobox.pack(side="right", fill="x", expand=True, padx=10)

        return combobox

    def load_clientes(self):
        clientes = ClienteCRUD.get_clientes(self.db)
        cliente_ruts = [cliente.rut for cliente in clientes]
        self.cliente_filter.configure(values=cliente_ruts)
        self.cliente_filter.set("")

    def apply_filters(self):
        cliente_rut = self.cliente_filter.get()

        if cliente_rut and cliente_rut != "Selecciona un cliente":
            pedidos = PedidoCRUD.filtrar_pedidos_por_cliente(self.db, cliente_rut)
        else:
            pedidos = PedidoCRUD.leer_pedidos(self.db)

        self.refresh_list(pedidos)

    def clear_filters(self):
        self.cliente_filter.set("Selecciona un cliente")

        self.refresh_list()

    def refresh_list(self, pedidos=None):
        for item in self.pedido_list.get_children():
            self.pedido_list.delete(item)
        if pedidos is None:
            pedidos = PedidoCRUD.leer_pedidos(self.db)
        for pedido in pedidos:
            menus = ", ".join([f"{menu['cantidad']}x {MenuCRUD.get_menu_by_id(self.db, menu['id']).nombre}" for menu in pedido.menus])
            self.pedido_list.insert("", "end", values=(pedido.id, pedido.descripcion, pedido.total, pedido.fecha, pedido.cliente_rut,menus))

    

    def delete_pedido(self):
        selected_item = self.pedido_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un pedido de la lista.")
            return

        pedido_id = self.pedido_list.item(selected_item)['values'][0]
        confirm = CTkM.askyesno(
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el pedido con ID {pedido_id}?"
        )
        if confirm:
            try:
                PedidoCRUD.borrar_pedido(self.db, pedido_id)
                self.refresh_list()
                self.show_message("Pedido eliminado exitosamente.")
            except Exception as e:
                CTkM.showerror("Error", f"Error al eliminar pedido: {e}")

    

    def show_message(self, message):
        # Método para mostrar mensajes de confirmación o error
        messagebox.showinfo("Información", message)

class GraficosPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#25253a")

        # Título del Panel de Gráficos
        self.label_title = ctk.CTkLabel(
            self, 
            text="Panel de Gráficos", 
            text_color="#4361ee",
            font=("Arial", 28, "bold")
        )
        self.label_title.pack(pady=20)

        # ComboBox para seleccionar el gráfico
        self.tipo_grafico = ctk.CTkComboBox(
            self, 
            values=["Ventas por Fecha", "Menús más Comprados"],
            height=30,
            width=300, 
            corner_radius=10,
            fg_color="#4361ee",
            button_color="#4361ee",
            button_hover_color="#5a75f0",
            dropdown_fg_color="#1e1e2d",
            border_color="#4361ee"
        )
        self.tipo_grafico.set("Selecciona un gráfico")
        self.tipo_grafico.pack(pady=10)

        # Botón para generar el gráfico
        self.bttn_generar_grafico = ctk.CTkButton(
            self,
            text="Generar Gráfico",
            font=("Arial", 16),
            command=self.generar_grafico,
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            height=40
        )
        self.bttn_generar_grafico.pack(pady=20)

        # Frame donde se dibujarán los gráficos
        self.graph_frame = ctk.CTkFrame(self, fg_color="#1e1e2d")
        self.graph_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def generar_grafico(self):
        """Genera el gráfico basado en la selección del ComboBox"""
        tipo = self.tipo_grafico.get()
        
        if (tipo == "Ventas por Fecha"):
            self.graficar_ventas_por_fecha()
        elif (tipo == "Menús más Comprados"):
            self.graficar_menus_mas_comprados()
        else:
            CTkM(title="Error", message="Seleccione un tipo de gráfico válido.", icon="cancel")

    def graficar_ventas_por_fecha(self):
        graficar_ventas_por_fecha(self.db)

    def graficar_menus_mas_comprados(self):
        graficar_menus_mas_comprados(self.db)

class BoletaBuilder:
    """Builder para construir boletas PDF paso a paso"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reinicia el builder para construir una nueva boleta"""
        self.pdf = FPDF()
        self.pedido = None
        self.db = None
        return self
    
    def set_pedido(self, pedido):
        """Establece el pedido para la boleta"""
        self.pedido = pedido
        return self
    
    def set_database(self, db):
        """Establece la base de datos"""
        self.db = db
        return self
    
    def add_page(self):
        """Añade una nueva página al PDF"""
        self.pdf.add_page()
        return self
    
    def build_header(self):
        """Construye el encabezado de la boleta"""
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(200, 10, "Boleta Restaurante bakano", ln=True, align="C")
        self.pdf.ln(10)
        return self
    
    def build_restaurant_info(self):
        """Construye la información del restaurante"""
        self.pdf.set_font("Arial", size=12)
        self.pdf.cell(0, 10, "Razón Social del Negocio mas bakano:", ln=True)
        self.pdf.cell(0, 10, "RUT: 66.999.666-9", ln=True)
        self.pdf.cell(0, 10, "Dirección: Calle Falsa 123", ln=True)
        self.pdf.cell(0, 10, "Teléfono:+56 9 1234 5678", ln=True)
        self.pdf.ln(10)
        return self
    
    def build_table_header(self):
        """Construye el encabezado de la tabla de productos"""
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(50, 10, "Nombre", 1)
        self.pdf.cell(30, 10, "Cantidad", 1)
        self.pdf.cell(50, 10, "Precio Unitario", 1)
        self.pdf.cell(50, 10, "Subtotal", 1)
        self.pdf.ln()
        return self
    
    def build_menu_items(self):
        """Construye los elementos del menú en la tabla"""
        if not self.pedido or not self.pedido.menus:
            return self
        
        self.pdf.set_font("Arial", size=12)
        menuses = {}
        
        for menu in self.pedido.menus:
            menu_obj = MenuCRUD.get_menu_by_id(self.db, menu["id"])
            if menu_obj.nombre in menuses:
                menuses[menu_obj.nombre]['cantidad'] += menu["cantidad"]
                menuses[menu_obj.nombre]['precio_total'] += menu_obj.precio * menu["cantidad"]
            else:
                menuses[menu_obj.nombre] = {
                    'cantidad': menu["cantidad"], 
                    'precio_total': menu_obj.precio * menu["cantidad"]
                }

        for menu, datos in menuses.items():
            self.pdf.cell(50, 10, menu, 1)
            self.pdf.cell(30, 10, str(datos['cantidad']), 1)
            self.pdf.cell(50, 10, f"${datos['precio_total'] / datos['cantidad']:.2f}", 1)
            self.pdf.cell(50, 10, f"${datos['precio_total']:.2f}", 1)
            self.pdf.ln()
        
        return self
    
    def build_totals(self):
        """Construye la sección de totales"""
        if not self.pedido:
            return self
        
        total = self.pedido.total
        iva = total * 0.19
        total_con_iva = total + iva
        
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, f"Subtotal: ${total:.2f}", 0, 1, "R")
        self.pdf.cell(0, 10, f"IVA (19%): ${iva:.2f}", 0, 1, "R")
        self.pdf.cell(0, 10, f"Total: ${total_con_iva:.2f}", 0, 1, "R")
        self.pdf.ln(10)
        return self
    
    def build_footer(self):
        """Construye el pie de página"""
        self.pdf.set_font("Arial", "I", 12)
        self.pdf.cell(0, 10, "Gracias por la compra", ln=True, align="C")
        self.pdf.cell(0, 10, "No se aceptan devoluciones", ln=True, align="C")
        self.pdf.cell(0, 10, "Contacto: restaurante@gmail.com", ln=True, align="C")
        self.pdf.ln()
        return self
    
    def save_pdf(self, filename="boleta.pdf"):
        """Guarda el PDF en la ruta especificada"""
        self.pdf.output(filename)
        return filename
    
    def get_pdf(self):
        """Retorna el objeto PDF construido"""
        return self.pdf


class BoletaDirector:
    """Director que controla el proceso de construcción de la boleta"""
    
    def __init__(self, builder):
        self.builder = builder
    
    def construct_complete_boleta(self, pedido, db, filename="boleta.pdf"):
        """Construye una boleta completa siguiendo todos los pasos"""
        return (self.builder
                .reset()
                .set_pedido(pedido)
                .set_database(db)
                .add_page()
                .build_header()
                .build_restaurant_info()
                .build_table_header()
                .build_menu_items()
                .build_totals()
                .build_footer()
                .save_pdf(filename))
    
    def construct_simple_boleta(self, pedido, db, filename="boleta_simple.pdf"):
        """Construye una boleta simple sin información del restaurante"""
        return (self.builder
                .reset()
                .set_pedido(pedido)
                .set_database(db)
                .add_page()
                .build_header()
                .build_table_header()
                .build_menu_items()
                .build_totals()
                .save_pdf(filename))


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()