import customtkinter as ctk
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from tkinter import messagebox 
import customtkinter as ctk
from crud.ingrediente_crud import IngredienteCRUD
from crud.cliente_crud import ClienteCRUD
from crud.menu_crud import MenuCRUD
from crud.pedido_crud import PedidoCRUD
from database import get_db, engine, Base
from models import Pedido,Ingrediente,Cliente,MenuIngrediente,Pedido,Menu
from tkinter import ttk
from fpdf import FPDF
from tkinter import messagebox as CTkM
from datetime import datetime
import tkinter as tk
import matplotlib.pyplot as plt
from graficos import  graficar_menus_mas_comprados, graficar_uso_ingredientes,graficar_ventas_por_fecha

# Configuración global de estilos
ctk.set_appearance_mode("dark")  # Opciones: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"

Base.metadata.create_all(bind=engine)

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Restaurante")
        self.geometry("1300x700")
        self.configure(fg_color="#1c1c1c")  # Fondo oscuro

        # Menú lateral
        self.menu_frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        self.menu_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        # Contenedor principal
        self.main_frame = ctk.CTkFrame(self, fg_color="#1c1c1c", corner_radius=10, width=800, height=700)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Título del menú
        self.app_title = ctk.CTkLabel(self.menu_frame, text="Restaurante App", font=("Arial", 24, "bold"))
        self.app_title.grid(row=0, column=0, pady=20)

        # Botones de navegación
        self.create_menu_button("Clientes", "ClientePanel", 1)
        self.create_menu_button("Ingredientes", "IngredientePanel", 2)
        self.create_menu_button("Menu", "MenuPanel", 3)
        self.create_menu_button("Panel de compra", "PanelCompra", 4)
        self.create_menu_button("Pedidos", "PanelPedido", 5)
        self.create_menu_button("Graficos", "GraficosPanel", 6)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_menu_button(self, text, panel_name, row):
        button = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=lambda: self.load_panel(panel_name),
            font=("Arial", 16, "bold"),
            corner_radius=10,
            height=40,
            fg_color="#3c99dc",
            hover_color="#4da9eb",
        )
        button.grid(row=row, column=0, pady=15, padx=10, sticky="ew")

    def load_panel(self, panel_name):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        db_session = next(get_db())
        panel = PanelFactory.create_panel(panel_name, self.main_frame, db_session)
        panel.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        if hasattr(panel, 'refresh_list'):
            panel.refresh_list()

class PanelFactory:  ## utilizacion de factory method para crear los paneles de la aplicacion de manera dinamica 
    @staticmethod
    def create_panel(panel_name, parent, db):
        if panel_name == "ClientePanel":
            return ClientePanel(parent, db)
        elif panel_name == "IngredientePanel":
            return IngredientePanel(parent, db)
        elif panel_name == "MenuPanel":
            return MenuPanel(parent, db)
        elif panel_name == "PanelCompra":
            return PanelCompra(parent, db)
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
        self.configure(fg_color="#1c1c1c")

        # Título
        self.label_title = ctk.CTkLabel(self, text="Gestión de Clientes", font=("Arial", 22, "bold"))
        self.label_title.grid(row=0, column=0, pady=10)

        # Formulario
        self.nombre_entry = self.create_form_entry("Nombre del Cliente", 1)
        self.email_entry = self.create_form_entry("Email del Cliente", 2)
        self.rut_entry = self.create_form_entry("Rut del Cliente", 3)

        # Botones de acción
        self.add_button = ctk.CTkButton(self, text="Registrar Cliente", command=self.add_cliente, corner_radius=10)
        self.add_button.grid(row=4, column=0, pady=10)

        self.update_button = ctk.CTkButton(self, text="Editar Cliente", command=self.open_edit_window, corner_radius=10)
        self.update_button.grid(row=5, column=0, pady=10)

        self.delete_button = ctk.CTkButton(self, text="Eliminar Cliente", command=self.delete_cliente, corner_radius=10)
        self.delete_button.grid(row=6, column=0, pady=10)

        # Lista de clientes
        self.cliente_list = self.create_treeview(Cliente)
        self.cliente_list.grid(row=7, column=0, pady=20, sticky="nsew")
        self.cliente_list.bind("<<TreeviewSelect>>", self.on_select)  # Bind select event
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.refresh_list()

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
        return treeview

    def create_form_entry(self, label_text, row):
        frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=0, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

    def add_cliente(self):
        rut = self.rut_entry.get()
        email = self.email_entry.get()
        nombre = self.nombre_entry.get()
        
        if not nombre or not email or not rut:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        cliente_existente = ClienteCRUD.get_cliente_by_rut(self.db, rut)
        if (cliente_existente):
            messagebox.showinfo("Error", f"El cliente con el rut '{rut}' ya existe.")
            return
        else:
            cliente = ClienteCRUD.create_cliente(self.db, rut, nombre, email)
            if (cliente):
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

            self.edit_nombre_entry = self.create_form_entry_in_window("Nombre del Cliente", 1, cliente.nombre)
            self.edit_email_entry = self.create_form_entry_in_window("Email del Cliente", 2, cliente.email)
            self.edit_rut_entry = self.create_form_entry_in_window("Rut del Cliente", 3, cliente.rut)
            self.edit_rut_entry.configure(state="disabled")

            self.save_button = ctk.CTkButton(self.edit_window, text="Guardar Cambios", command=lambda: self.update_cliente(cliente_rut), corner_radius=10)
            self.save_button.grid(row=5, column=0, pady=10)

    def create_form_entry_in_window(self, label_text, row, value):
        frame = ctk.CTkFrame(self.edit_window, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10, width=200)
        entry.insert(0, value)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry
    
    def update_cliente(self, cliente_rut):
        nombre = self.edit_nombre_entry.get()
        email = self.edit_email_entry.get()
        rut = self.edit_rut_entry.get()

        if not nombre or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios para actualizar un cliente.")
            return

        cliente = ClienteCRUD.update_cliente(self.db, rut, nombre, email)
        if (cliente):
            messagebox.showinfo("Éxito", f"Cliente n°rut:'{rut}' actualizado a: Nombre:'{nombre}'// Email:'{email}'")
            self.edit_window.destroy()
        else:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente '{nombre}//{rut}'.")
        self.refresh_list()

    def delete_cliente(self):
        email_actual = self.get_selected_email()
        if not email_actual:
            messagebox.showerror("Error", "Selecciona un cliente de la lista.")
            return

        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de eliminar al cliente '{email_actual}'?")
        if confirm:
            cliente = ClienteCRUD.delete_cliente(self.db, email_actual)
            if (cliente):
                messagebox.showinfo("Éxito", f"Cliente '{email_actual}' eliminado con éxito.")
            else:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente '{email_actual}'.")
        self.refresh_list()

    def refresh_list(self):
        for item in self.cliente_list.get_children():
            self.cliente_list.delete(item)
        clientes = ClienteCRUD.get_clientes(self.db)
        for cliente in clientes:
            self.cliente_list.insert("", "end", values=(cliente.rut, cliente.email, cliente.nombre))  # Asegúrate de incluir el rut

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
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#1c1c1c")

        self.label_title = ctk.CTkLabel(self, text="Gestión de Ingredientes", font=("Arial", 22, "bold"))
        self.label_title.grid(row=0, column=0, pady=10)

        self.nombre_entry = self.create_form_entry("Nombre", 1)
        self.tipo_entry = self.create_form_entry("Tipo", 2)
        self.cantidad_entry = self.create_form_entry("Cantidad", 3)
        self.unidad_entry = self.create_form_entry("Unidad de Medida", 4)

        self.add_button = ctk.CTkButton(self, text="Añadir Ingrediente", command=self.add_ingrediente, corner_radius=10)
        self.add_button.grid(row=5, column=0, pady=10)

        self.upgrade_button = ctk.CTkButton(self, text="Actualizar Ingrediente", command=self.open_edit_window, corner_radius=10)
        self.upgrade_button.grid(row=6, column=0, pady=10)

        self.delete_button = ctk.CTkButton(self, text="Eliminar Ingrediente", command=self.delete_ingrediente, corner_radius=10)
        self.delete_button.grid(row=7, column=0, pady=10)

        self.ingrediente_list = self.create_treeview(Ingrediente)
        self.ingrediente_list.grid(row=8, column=0, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.refresh_list()

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns if column.name != 'id']
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
        return treeview

    def create_form_entry(self, label_text, row):
        frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10, width=200)
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

            self.save_button = ctk.CTkButton(self.edit_window, text="Guardar Cambios", command=lambda: self.update_ingrediente(ingrediente.id), corner_radius=10)
            self.save_button.grid(row=5, column=0, pady=10)

    def create_form_entry_in_window(self, label_text, row, value):
        frame = ctk.CTkFrame(self.edit_window, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew") 

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10, width=200)   
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
            cantidad = float(cantidad)
            ingrediente = IngredienteCRUD.update_ingrediente(self.db, ingrediente_id,nombre, cantidad, tipo, unidad)
            if (ingrediente):
                messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' actualizado con éxito.")
                self.edit_window.destroy()
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
        self.configure(fg_color="#1c1c1c")

        self.label_title = ctk.CTkLabel(self, text="Gestión de Menú", font=("Arial", 22, "bold"))
        self.label_title.grid(row=0, column=0, pady=10)

        self.nombre_entry = self.create_form_entry("Nombre del Menú", 1)
        self.descripcion_entry = self.create_form_entry("Descripción del Menú", 2)
        self.precio_entry = self.create_form_entry("Precio del Menú", 3)

        self.ingredientes_frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        self.ingredientes_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
        self.ingredientes_label = ctk.CTkLabel(self.ingredientes_frame, text="Ingredientes", font=("Arial", 14))
        self.ingredientes_label.grid(row=0, column=0, padx=10, pady=5)

        self.ingredientes_combobox = ctk.CTkComboBox(self.ingredientes_frame, values=[], width=200, corner_radius=10)
        self.ingredientes_combobox.grid(row=1, column=0, padx=10, pady=5)

        self.cantidad_entry = ctk.CTkEntry(self.ingredientes_frame, corner_radius=10, width=100)
        self.cantidad_entry.grid(row=1, column=1, padx=10, pady=5)

        self.add_ingrediente_button = ctk.CTkButton(self.ingredientes_frame, text="Añadir Ingrediente", command=self.add_ingrediente, corner_radius=10)
        self.add_ingrediente_button.grid(row=1, column=2, padx=10, pady=5)

        self.update_ingrediente_button = ctk.CTkButton(self.ingredientes_frame, text="Actualizar Ingrediente", command=self.update_ingrediente, corner_radius=10)
        self.update_ingrediente_button.grid(row=1, column=3, padx=10, pady=5)

        self.delete_ingrediente_button = ctk.CTkButton(self.ingredientes_frame, text="Eliminar Ingrediente", command=self.delete_ingrediente, corner_radius=10)
        self.delete_ingrediente_button.grid(row=1, column=4, padx=10, pady=5)

        self.ingredientes_list = self.create_treeview_ingredientes()
        self.ingredientes_list.grid(row=2, column=0, columnspan=5, pady=10, sticky="nsew")

        self.button_frame = ctk.CTkFrame(self, fg_color="#1c1c1c")
        self.button_frame.grid(row=5, column=0, pady=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.button_frame, text="Registrar Menú", command=self.add_menu, corner_radius=10)
        self.add_button.grid(row=0, column=0, padx=5)

        self.update_button = ctk.CTkButton(self.button_frame, text="Editar Menú", command=self.open_edit_window, corner_radius=10)
        self.update_button.grid(row=0, column=1, padx=5)

        self.delete_button = ctk.CTkButton(self.button_frame, text="Eliminar Menú", command=self.delete_menu, corner_radius=10)
        self.delete_button.grid(row=0, column=2, padx=5)

        self.menu_list = self.create_treeview(Menu)
        self.menu_list.grid(row=6, column=0, pady=20, sticky="nsew")
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
            messagebox.showerror("Error", "La cantidad debe ser un número.")
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

            self.edit_ingredientes_frame = ctk.CTkFrame(self.edit_window, fg_color="#2c2c2c", corner_radius=10)
            self.edit_ingredientes_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

            self.edit_ingredientes_label = ctk.CTkLabel(self.edit_ingredientes_frame, text="Ingredientes", font=("Arial", 14))
            self.edit_ingredientes_label.grid(row=0, column=0, padx=10, pady=5)

            self.edit_ingredientes_combobox = ctk.CTkComboBox(self.edit_ingredientes_frame, values=[], width=200, corner_radius=10)
            self.edit_ingredientes_combobox.grid(row=1, column=0, padx=10, pady=5)

            self.edit_cantidad_entry = ctk.CTkEntry(self.edit_ingredientes_frame, corner_radius=10, width=100)
            self.edit_cantidad_entry.grid(row=1, column=1, padx=10, pady=5)

            self.edit_add_ingrediente_button = ctk.CTkButton(self.edit_ingredientes_frame, text="Añadir Ingrediente", command=self.edit_add_ingrediente, corner_radius=10)
            self.edit_add_ingrediente_button.grid(row=1, column=2, padx=10, pady=5)

            self.edit_update_ingrediente_button = ctk.CTkButton(self.edit_ingredientes_frame, text="Actualizar Ingrediente", command=self.edit_update_ingrediente, corner_radius=10)
            self.edit_update_ingrediente_button.grid(row=1, column=3, padx=10, pady=5)

            self.edit_delete_ingrediente_button = ctk.CTkButton(self.edit_ingredientes_frame, text="Eliminar Ingrediente", command=self.edit_delete_ingrediente, corner_radius=10)
            self.edit_delete_ingrediente_button.grid(row=1, column=4, padx=10, pady=5)

            self.edit_ingredientes_list = self.create_treeview_ingredientes()
            self.edit_ingredientes_list.grid(row=2, column=0, columnspan=5, pady=10, sticky="nsew")

            for ingrediente in menu.ingredientes:
                self.edit_ingredientes_list.insert("", "end", values=(ingrediente.ingrediente.nombre, ingrediente.cantidad))

            self.save_button = ctk.CTkButton(self.edit_window, text="Guardar Cambios", command=lambda: self.update_menu(menu.id), corner_radius=10)
            self.save_button.grid(row=5, column=0, pady=10)

            self.load_ingredientes()

    def create_form_entry_in_window(self, label_text, row, value):
        frame = ctk.CTkFrame(self.edit_window, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10, width=200)
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
        frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=0, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

class PanelCompra(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db  
        self.configure(fg_color="#1c1c1c")

        # Título del Panel de Compra
        self.label_title = ctk.CTkLabel(self, text="Panel de Compra", font=("Arial", 24, "bold"), text_color="white")
        self.label_title.grid(row=0, column=0, pady=20, columnspan=2) 

        # Frame para la entrada de productos y cantidad
        self.entry_frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        self.entry_frame.grid(row=1, column=0, pady=10, padx=20, sticky="ew", columnspan=2)

        # Combobox para seleccionar un menú
        self.menu_combobox = ctk.CTkComboBox(self.entry_frame, values=[], width=300, corner_radius=10)
        self.menu_combobox.set("Selecciona un menú")  # Texto por defecto
        self.menu_combobox.grid(row=0, column=0, padx=10)

        # Entrada de cantidad
        self.cantidad_entry = self.create_form_entry("Cantidad", 0, 1)  # Adjust column index
        self.cantidad_entry.grid(row=0, column=1, padx=10)

        # Botón para agregar al carrito
        self.add_button = ctk.CTkButton(self.entry_frame, text="Agregar al carrito", command=self.add_to_cart, corner_radius=10)
        self.add_button.grid(row=0, column=2, padx=10)  # Adjust column index

        # Lista de productos en el carrito
        self.cart_list = self.create_treeview()
        self.cart_list.grid(row=2, column=0, pady=10, sticky="nsew", columnspan=2)

        # Botón para realizar compra
        self.buy_button = ctk.CTkButton(self, text="Realizar Compra", command=self.complete_purchase, corner_radius=10, fg_color="#3c99dc")
        self.buy_button.grid(row=3, column=0, pady=10, columnspan=2)

        # Label para el total
        self.total_label = ctk.CTkLabel(self, text="Total: $0.00", font=("Arial", 16, "bold"), text_color="white")
        self.total_label.grid(row=4, column=0, pady=10, columnspan=2)

        # Lista interna para almacenar los productos seleccionados
        self.cart = []  # Aquí guardaremos los productos y cantidades seleccionadas

        self.cliente_combobox = ctk.CTkComboBox(self.entry_frame, values=[], width=300, corner_radius=10)
        self.cliente_combobox.set("Selecciona un cliente")  # Texto por defecto
        self.cliente_combobox.grid(row=0, column=3, padx=10)  # Adjust column index

        self.load_clientes()  # Ensure clients are loaded into the combobox
        self.load_menus()  # Ensure menus are loaded into the combobox

    def create_form_entry(self, label_text, row, column):
        frame = ctk.CTkFrame(self.entry_frame, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=row, column=column, pady=10, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14), text_color="white")
        label.grid(row=0, column=0, padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10)
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

        menus = []
        for item in self.cart:
            menu_nombre, cantidad, _ = item
            menu = MenuCRUD.get_menu_by_nombre(self.db, menu_nombre)
            if menu:
                if not self.verificar_disponibilidad_ingredientes(menu, cantidad):
                    messagebox.showerror("Error", f"No hay suficientes ingredientes para el menú '{menu_nombre}'.")
                    return
                menus.append({"id": menu.id, "cantidad": cantidad})

        nuevo_pedido = PedidoCRUD.crear_pedido(
            self.db,
            cliente_rut=cliente_rut,
            descripcion="Compra Realizada",
            total=sum(item[2] for item in self.cart),
            fecha=datetime.now(),
            menus=menus
        )

        if nuevo_pedido:
            generador_boleta = Generarboleta(nuevo_pedido, self.db)
            generador_boleta.generar_boleta()
            messagebox.showinfo("Compra Realizada", "¡Gracias por tu compra!")
            self.cart.clear()
            self.refresh_cart_list()
            self.db.add(nuevo_pedido)
            self.db.commit()
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
        self.configure(fg_color="#1c1c1c")

        # Título del Panel de Pedido
        self.label_title = ctk.CTkLabel(self, text="Panel de Pedidos", font=("Arial", 24, "bold"), text_color="white")
        self.label_title.grid(row=0, column=0, pady=20, columnspan=3)

        # Filtros
        self.filter_frame = ctk.CTkFrame(self, fg_color="#2c2c2c", corner_radius=10)
        self.filter_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew", columnspan=3)

        self.cliente_filter = self.create_filter_combobox("Filtrar por Cliente (RUT)", 0)
        self.fecha_filter = self.create_filter_entry("Filtrar por Fecha (YYYY-MM-DD)", 1)
        self.monto_filter = self.create_filter_entry("Filtrar por Monto Mayor a", 2)

        self.apply_filter_button = ctk.CTkButton(self.filter_frame, text="Aplicar Filtros", command=self.apply_filters, corner_radius=10)
        self.apply_filter_button.grid(row=0, column=3, padx=10)

        self.clear_filter_button = ctk.CTkButton(self.filter_frame, text="Limpiar Filtros", command=self.clear_filters, corner_radius=10)
        self.clear_filter_button.grid(row=0, column=4, padx=10)

        # Treeview para mostrar los pedidos
        self.pedido_list = self.create_treeview(Pedido)
        self.pedido_list.grid(row=2, column=0, pady=20, sticky="nsew", columnspan=3)

        # Botones para agregar, editar y eliminar pedidos
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=3, column=0, pady=5, columnspan=3)

        self.btn_edit = ctk.CTkButton(self.btn_frame, text="Editar Pedido", command=self.edit_pedido)
        self.btn_edit.grid(row=0, column=1, padx=5)

        self.btn_delete = ctk.CTkButton(self.btn_frame, text="Eliminar Pedido", command=self.delete_pedido)
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

    def create_filter_entry(self, label_text, column):
        frame = ctk.CTkFrame(self.filter_frame, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=0, column=column, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        entry = ctk.CTkEntry(frame, corner_radius=10, width=200)
        entry.pack(side="right", fill="x", expand=True, padx=10)

        return entry

    def create_filter_combobox(self, label_text, column):
        frame = ctk.CTkFrame(self.filter_frame, fg_color="#2c2c2c", corner_radius=10)
        frame.grid(row=0, column=column, pady=5, padx=10, sticky="ew")

        label = ctk.CTkLabel(frame, text=label_text, font=("Arial", 14))
        label.pack(side="left", padx=10)

        combobox = ctk.CTkComboBox(frame, values=[], width=200, corner_radius=10)
        combobox.pack(side="right", fill="x", expand=True, padx=10)

        return combobox

    def load_clientes(self):
        clientes = ClienteCRUD.get_clientes(self.db)
        cliente_ruts = [cliente.rut for cliente in clientes]
        self.cliente_filter.configure(values=cliente_ruts)
        self.cliente_filter.set("")

    def apply_filters(self):
        cliente_rut = self.cliente_filter.get()
        fecha = self.fecha_filter.get()
        monto = self.monto_filter.get()

        if cliente_rut and cliente_rut != "Selecciona un cliente":
            pedidos = PedidoCRUD.filtrar_pedidos_por_cliente(self.db, cliente_rut)
        elif fecha:
            if cliente_rut or monto:
                messagebox.showerror("Error", "Solo se puede aplicar un filtro a la vez, porfavor borra los contenidos de los filtros.")
                return
            try:
                datetime.strptime(fecha, "%Y-%m-%d")
                pedidos = PedidoCRUD.filtrar_pedidos_por_fecha(self.db, fecha)
            except ValueError:
                messagebox.showerror("Error", "La fecha debe tener el formato YYYY-MM-DD.")
                return
        elif monto:
            if cliente_rut or fecha:
                messagebox.showerror("Error", "Solo se puede aplicar un filtro a la vez, porfavor borra los contenidos de los filtros.")
                return
            try:
                monto = float(monto)
                pedidos = PedidoCRUD.filtrar_pedidos_por_monto_mayor_que(self.db, monto)
            except ValueError:
                messagebox.showerror("Error", "El monto debe ser un número.")
                return
        else:
            pedidos = PedidoCRUD.leer_pedidos(self.db)

        self.refresh_list(pedidos)

    def clear_filters(self):
        self.cliente_filter.set("Selecciona un cliente")
        self.fecha_filter.delete(0, tk.END)
        self.monto_filter.delete(0, tk.END)
        self.refresh_list()

    def refresh_list(self, pedidos=None):
        for item in self.pedido_list.get_children():
            self.pedido_list.delete(item)
        if pedidos is None:
            pedidos = PedidoCRUD.leer_pedidos(self.db)
        for pedido in pedidos:
            menus = ", ".join([f"{menu['cantidad']}x {MenuCRUD.get_menu_by_id(self.db, menu['id']).nombre}" for menu in pedido.menus])
            self.pedido_list.insert("", "end", values=(pedido.id, pedido.descripcion, pedido.total, pedido.fecha, pedido.cliente_rut,menus))



    def edit_pedido(self):
        selected_item = self.pedido_list.selection()
        if not selected_item:
            CTkM.showwarning("Advertencia", "Selecciona un pedido para editar.")
            return

        # Obtener el ID del pedido seleccionado
        pedido_id = self.pedido_list.item(selected_item)['values'][0]
        pedido = next((p for p in PedidoCRUD.leer_pedidos(self.db) if p.id == pedido_id), None)

        if not pedido:
            CTkM.showerror("Error", f"No se encontró el pedido con ID {pedido_id}.")
            return

        # Crear ventana para editar descripción
        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("Editar Descripción del Pedido")
        self.edit_window.geometry("400x200")
        self.edit_window.configure(fg_color="#1c1c1c")

        # Etiqueta y campo de entrada para la descripción
        label_desc = ctk.CTkLabel(self.edit_window, text="Nueva Descripción:", font=("Arial", 14))
        label_desc.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        entry_desc = ctk.CTkEntry(self.edit_window, width=300, corner_radius=10)
        entry_desc.insert(0, pedido.descripcion)  # Descripción actual
        entry_desc.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Botón para guardar cambios
        save_button = ctk.CTkButton(
            self.edit_window,
            text="Guardar Cambios",
            command=lambda: self.save_pedido_description(pedido_id, entry_desc.get()),
            corner_radius=10
        )
        save_button.grid(row=1, column=0, columnspan=2, pady=20)

    def delete_pedido(self):
        selected_item = self.pedido_list.selection()
        if selected_item:
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
        else:
            CTkM.showwarning("Advertencia", "Selecciona un pedido para eliminar.")

    def on_item_double_click(self, event):
        self.edit_pedido()

    def save_pedido_description(self, pedido_id, nueva_descripcion):
        if not nueva_descripcion.strip():
            CTkM.showerror("Error", "La descripción no puede estar vacía.")
            return

        try:
            # Actualizar la descripción usando PedidoCRUD
            pedido_actualizado = PedidoCRUD.actualizar_pedido(self.db, pedido_id, nueva_descripcion)
            if pedido_actualizado:
                self.refresh_list()
                CTkM.showinfo("Éxito", "La descripción del pedido se actualizó correctamente.")
                self.edit_window.destroy()  # Cerrar la ventana
            else:
                CTkM.showerror("Error", "No se pudo actualizar la descripción del pedido.")
        except Exception as e:
            CTkM.showerror("Error", f"Error al actualizar descripción: {e}")

    def show_message(self, message):
        # Método para mostrar mensajes de confirmación o error
        messagebox.showinfo("Información", message)

class GraficosPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#1c1c1c")

        # Título del Panel de Gráficos
        self.label_title = ctk.CTkLabel(self, text="Panel de Gráficos", font=("Arial", 24, "bold"), text_color="white")
        self.label_title.pack(pady=20)

        # ComboBox para seleccionar el gráfico
        self.tipo_grafico = ctk.CTkComboBox(
            self, 
            values=["Ventas por Fecha", "Menús más Comprados", "Uso de Ingredientes"],
            width=300, 
            corner_radius=10
        )
        self.tipo_grafico.set("Selecciona un gráfico")  # Texto predeterminado
        self.tipo_grafico.pack(pady=10)

        # Botón para generar el gráfico
        self.bttn_generar_grafico = ctk.CTkButton(
            self,
            text="Generar Gráfico",
            command=self.generar_grafico,
            corner_radius=10
        )
        self.bttn_generar_grafico.pack(pady=20)

        # Frame donde se dibujarán los gráficos
        self.graph_frame = ctk.CTkFrame(self, fg_color="#1c1c1c")
        self.graph_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def generar_grafico(self):
        """Genera el gráfico basado en la selección del ComboBox"""
        tipo = self.tipo_grafico.get()
        
        if (tipo == "Ventas por Fecha"):
            self.graficar_ventas_por_fecha()
        elif (tipo == "Menús más Comprados"):
            self.graficar_menus_mas_comprados()
        elif (tipo == "Uso de Ingredientes"):
            self.graficar_uso_ingredientes()
        else:
            CTkM(title="Error", message="Seleccione un tipo de gráfico válido.", icon="cancel")

    def graficar_ventas_por_fecha(self):
        graficar_ventas_por_fecha(self.db)

    def graficar_menus_mas_comprados(self):
        graficar_menus_mas_comprados(self.db)

    def graficar_uso_ingredientes(self):
        graficar_uso_ingredientes(self.db)
class Generarboleta:
    def __init__(self, pedido, db):
        self.pedido = pedido
        self.db = db

    def generar_boleta(self):
        if not self.pedido.menus:
            messagebox.showwarning("Pedido Vacío", "No hay menús en el pedido para generar la boleta.")
            return

        # Crear una instancia de FPDF
        pdf = FPDF()
        pdf.add_page()

        # Encabezado de la boleta
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "Boleta Restaurante bakano", ln=True, align="C")
        pdf.ln(10)

        # Detalles del restaurante (se pueden personalizar)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, "Razón Social del Negocio mas bakano:", ln=True)
        pdf.cell(0, 10, "RUT: 66.999.666-9", ln=True)
        pdf.cell(0, 10, "Dirección: Calle Falsa 123", ln=True)
        pdf.cell(0, 10, "Teléfono: +56 9 1234 5678", ln=True)
        pdf.ln(10)

        # Detalles del pedido
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 10, "Nombre", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(50, 10, "Precio Unitario", 1)
        pdf.cell(50, 10, "Subtotal", 1)
        pdf.ln()

        pdf.set_font("Arial", size=12)

        menuses = {}
        
        for menu in self.pedido.menus:
            menu_obj = MenuCRUD.get_menu_by_id(self.db, menu["id"])
            if menu_obj.nombre in menuses:
                menuses[menu_obj.nombre]['cantidad'] += menu["cantidad"]
                menuses[menu_obj.nombre]['precio_total'] += menu_obj.precio * menu["cantidad"]
            else:
                menuses[menu_obj.nombre] = {'cantidad': menu["cantidad"], 'precio_total': menu_obj.precio * menu["cantidad"]}

        for menu, datos in menuses.items():
            pdf.cell(50, 10, menu, 1)
            pdf.cell(30, 10, str(datos['cantidad']), 1)
            pdf.cell(50, 10, f"${datos['precio_total'] / datos['cantidad']:.2f}", 1)
            pdf.cell(50, 10, f"${datos['precio_total']:.2f}", 1)
            pdf.ln()

        total = self.pedido.total
        iva = total * 0.19
        total_con_iva = total + iva
        
        # Mostrar subtotales y totales
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Subtotal: ${total:.2f}", 0, 1, "R")
        pdf.cell(0, 10, f"IVA (19%): ${iva:.2f}", 0, 1, "R")
        pdf.cell(0, 10, f"Total: ${total_con_iva:.2f}", 0, 1, "R")
        pdf.ln(10)

        pdf.set_font("Arial", "I", 12)
        pdf.cell(0, 10, "Gracias por la compra", ln=True, align="C")
        pdf.cell(0, 10, "No se aceptan devoluciones", ln=True, align="C")
        pdf.cell(0, 10, "Contacto: restaurante@gmail.com", ln=True, align="C")
        pdf.ln()

        # Guardar el archivo PDF
        rutapdf = "boleta.pdf" 
        pdf.output(rutapdf)

        messagebox.showinfo("Boleta Generada", f"Boleta generada con éxito en la siguiente ruta: '{rutapdf}'.")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
