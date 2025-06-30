import customtkinter as ctk
from tkinter import ttk, messagebox
import re
from crud.cliente_crud import ClienteCRUD
from models_folder.models_restaurente import Cliente

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
        rut_container.pack(fill="x", pady=2, padx=5)

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
        self.rut_entry.pack(fill="x", pady=(0,10))

        # Botones de acción
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=30, sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2), weight=1)

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

        # Inicializar lista
        self.refresh_list()

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
            treeview.column(column, anchor='center')
        return treeview

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
            messagebox.showerror("Error", f"El cliente con el RUT '{rut}' ya existe.")
            return

        cliente = ClienteCRUD.create_cliente(self.db, rut, nombre, email)
        if cliente:
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado con éxito.")
            self.clear_fields()
        else:
            messagebox.showerror("Error", f"No se pudo registrar el cliente '{nombre}'.")
        self.refresh_list()

    def clear_fields(self):
        self.rut_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.nombre_entry.delete(0, "end")

    def open_edit_window(self):
        selected_item = self.cliente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un cliente de la lista.")
            return

        cliente_rut = self.cliente_list.item(selected_item)["values"][0]
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

        if not nombre or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if not self.validar_nombre(nombre):
            messagebox.showerror("Error", "El nombre solo debe contener letras y espacios.")
            return

        if not self.validar_correo(email):
            messagebox.showerror("Error", "El correo electrónico no tiene un formato válido.")
            return

        cliente = ClienteCRUD.update_cliente(self.db, rut_anterior, nombre, email, rut_anterior)
        if cliente:
            messagebox.showinfo("Éxito", f"Cliente con RUT '{rut_anterior}' actualizado con éxito.")
            self.edit_window.destroy()
        else:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente '{nombre}'.")
        self.refresh_list()

    def delete_cliente(self):
        selected_item = self.cliente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un cliente para eliminar.")
            return

        values = self.cliente_list.item(selected_item)["values"]
        if not values:
            messagebox.showerror("Error", "No se pudo obtener la información del cliente.")
            return

        cliente_rut = values[0]
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Estás seguro de que deseas eliminar al cliente con RUT {cliente_rut}?"
        )
        
        if confirmacion:
            eliminado = ClienteCRUD.delete_cliente(self.db, cliente_rut)
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
            self.cliente_list.insert("", "end", values=(cliente.rut, cliente.email, cliente.nombre))