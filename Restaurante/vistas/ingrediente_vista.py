import customtkinter as ctk
from tkinter import ttk, messagebox
from crud.ingrediente_crud import IngredienteCRUD
from models_folder.models_restaurente import Ingrediente

class IngredientePanel(ctk.CTkFrame):
    def __init__(self, parent, db, observer_manager=None):
        super().__init__(parent)
        self.db = db
        self.observer_manager = observer_manager
        self.configure(fg_color="#25253a", corner_radius=15)

        # Título
        self.label_title = ctk.CTkLabel(
            self, 
            text="Gestión de Ingredientes", 
            text_color="#4361ee",
            font=("Arial", 28, "bold")
        )
        self.label_title.grid(row=0, column=0, columnspan=2, pady=20)

        # Frame para datos del ingrediente
        self.ingrediente_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            corner_radius=15,
            width=300,
            height=200
        )
        self.ingrediente_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=30, sticky="nsew")
        self.ingrediente_frame.grid_propagate(False)

        # Título del frame
        self.ingrediente_title = ctk.CTkLabel(
            self.ingrediente_frame,
            text="Datos del Ingrediente",
            text_color="#4361ee",
            font=("Arial", 18, "bold")
        )
        self.ingrediente_title.pack(pady=(10,5))

        # Contenedor para los campos
        self.fields_frame = ctk.CTkFrame(
            self.ingrediente_frame,
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.fields_frame.pack(pady=5, padx=20, fill="x")

        # Campo Nombre y Cantidad (primera fila)
        nombre_cantidad_frame = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        nombre_cantidad_frame.pack(fill="x", pady=2)

        # Campo Nombre (izquierda)
        nombre_container = ctk.CTkFrame(nombre_cantidad_frame, fg_color="#1e1e2d", corner_radius=0)
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

        # Campo Cantidad (derecha)
        cantidad_container = ctk.CTkFrame(nombre_cantidad_frame, fg_color="#1e1e2d", corner_radius=0)
        cantidad_container.pack(side="right", fill="x", expand=True, padx=5)

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
        self.cantidad_entry.pack(fill="x", pady=(0,2), padx=5)

        # Campo Unidad de Medida
        unidad_container = ctk.CTkFrame(self.fields_frame, fg_color="#1e1e2d", corner_radius=0)
        unidad_container.pack(fill="x", pady=2, padx=5)

        self.unidad_label = ctk.CTkLabel(unidad_container, text="Unidad de Medida:", font=("Arial", 14))
        self.unidad_label.pack(anchor="w", pady=1)
        self.unidad_combobox = ctk.CTkComboBox(
            unidad_container,
            values=["kg", "g", "l", "ml", "unidad"],
            fg_color="#25253a",
            border_color="#4361ee",
            button_color="#4361ee",
            button_hover_color="#5a75f0",
            dropdown_fg_color="#1e1e2d",
            height=30
        )
        self.unidad_combobox.pack(fill="x", pady=(0,10))
        self.unidad_combobox.set("Seleccione unidad")

        # Botones de acción
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=30, sticky="ew")
        btn_frame.grid_columnconfigure((0,1,2), weight=1)

        self.add_button = ctk.CTkButton(
            btn_frame,
            text="Registrar Ingrediente",
            command=self.add_ingrediente,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40,
            corner_radius=15
        )
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.update_button = ctk.CTkButton(
            btn_frame,
            text="Editar Ingrediente",
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
            text="Eliminar Ingrediente",
            command=self.delete_ingrediente,
            fg_color="#4361ee",
            hover_color="#5a75f0",
            font=("Arial", 16),
            height=40,
            corner_radius=15
        )
        self.delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Lista de ingredientes
        self.ingrediente_list = self.create_treeview(Ingrediente)
        self.ingrediente_list.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

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

    def add_ingrediente(self):
        nombre = self.nombre_entry.get()
        cantidad = self.cantidad_entry.get()
        unidad = self.unidad_combobox.get()

        if not nombre or not cantidad or unidad == "Seleccione unidad":
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            cantidad = float(cantidad)
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        ingrediente_existente = IngredienteCRUD.get_ingrediente_by_nombre(self.db, nombre)
        if ingrediente_existente:
            messagebox.showerror("Error", f"El ingrediente '{nombre}' ya existe.")
            return

        ingrediente = IngredienteCRUD.create_ingrediente(self.db, nombre, cantidad, unidad)
        if ingrediente:
            messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' registrado con éxito.")
            self.clear_fields()
            if self.observer_manager:
                self.observer_manager.notify_inventory_change(nombre, 0, cantidad)
        else:
            messagebox.showerror("Error", f"No se pudo registrar el ingrediente '{nombre}'.")
        self.refresh_list()

    def clear_fields(self):
        self.nombre_entry.delete(0, "end")
        self.cantidad_entry.delete(0, "end")
        self.unidad_combobox.set("Seleccione unidad")

    def open_edit_window(self):
        selected_item = self.ingrediente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return

        ingrediente_id = self.ingrediente_list.item(selected_item)["values"][0]
        ingrediente = IngredienteCRUD.get_ingrediente_by_id(self.db, ingrediente_id)

        if ingrediente:
            self.edit_window = ctk.CTkToplevel(self)
            self.edit_window.title("Editar Ingrediente")
            self.edit_window.geometry("400x300")
            self.edit_window.configure(fg_color="#1c1c1c")

            self.edit_nombre_entry = self.create_form_entry_in_window("Nombre:", 1, ingrediente.nombre)
            self.edit_cantidad_entry = self.create_form_entry_in_window("Cantidad:", 2, str(ingrediente.cantidad))

            unidad_frame = ctk.CTkFrame(self.edit_window, fg_color="#25253a", corner_radius=15)
            unidad_frame.grid(row=3, column=0, pady=5, padx=10, sticky="ew")

            unidad_label = ctk.CTkLabel(unidad_frame, text="Unidad de Medida:", font=("Arial", 14))
            unidad_label.pack(side="left", padx=10)

            self.edit_unidad_combobox = ctk.CTkComboBox(
                unidad_frame,
                values=["kg", "g", "l", "ml", "unidad"],
                fg_color="#25253a",
                border_color="#4361ee",
                button_color="#4361ee",
                button_hover_color="#5a75f0",
                dropdown_fg_color="#1e1e2d",
                height=30,
                width=200
            )
            self.edit_unidad_combobox.set(ingrediente.unidad_medida)
            self.edit_unidad_combobox.pack(side="right", fill="x", expand=True, padx=10)

            self.save_button = ctk.CTkButton(
                self.edit_window, 
                text="Guardar Cambios", 
                command=lambda: self.update_ingrediente(ingrediente_id), 
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
        cantidad = self.edit_cantidad_entry.get()
        unidad = self.edit_unidad_combobox.get()

        if not nombre or not cantidad or not unidad:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            cantidad = float(cantidad)
            if cantidad < 0:
                messagebox.showerror("Error", "La cantidad no puede ser negativa.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número.")
            return

        ingrediente_actual = IngredienteCRUD.get_ingrediente_by_id(self.db, ingrediente_id)
        if ingrediente_actual:
            cantidad_anterior = ingrediente_actual.cantidad
            ingrediente = IngredienteCRUD.update_ingrediente(self.db, ingrediente_id, nombre, cantidad, unidad)
            if ingrediente:
                messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' actualizado con éxito.")
                if self.observer_manager:
                    self.observer_manager.notify_inventory_change(nombre, cantidad_anterior, cantidad)
                self.edit_window.destroy()
            else:
                messagebox.showerror("Error", f"No se pudo actualizar el ingrediente '{nombre}'.")
            self.refresh_list()
        else:
            messagebox.showerror("Error", "No se encontró el ingrediente para actualizar.")

    def delete_ingrediente(self):
        selected_item = self.ingrediente_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un ingrediente de la lista.")
            return

        values = self.ingrediente_list.item(selected_item)["values"]
        if not values:
            messagebox.showerror("Error", "No se pudo obtener la información del ingrediente.")
            return

        ingrediente_id = values[0]
        ingrediente = IngredienteCRUD.get_ingrediente_by_id(self.db, ingrediente_id)
        
        if not ingrediente:
            messagebox.showerror("Error", "No se encontró el ingrediente.")
            return

        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Estás seguro de eliminar el ingrediente '{ingrediente.nombre}'?"
        )
        
        if confirm:
            if self.observer_manager:
                self.observer_manager.notify_inventory_change(ingrediente.nombre, ingrediente.cantidad, 0)
            
            if IngredienteCRUD.delete_ingrediente(self.db, ingrediente_id):
                messagebox.showinfo("Éxito", f"Ingrediente '{ingrediente.nombre}' eliminado con éxito.")
                self.refresh_list()
            else:
                messagebox.showerror(
                    "Error", 
                    f"No se pudo eliminar el ingrediente '{ingrediente.nombre}'. "
                    "Puede que esté siendo utilizado en algún menú."
                )

    def refresh_list(self):
        for item in self.ingrediente_list.get_children():
            self.ingrediente_list.delete(item)
        ingredientes = IngredienteCRUD.get_ingredientes(self.db)
        for ingrediente in ingredientes:
            self.ingrediente_list.insert("", "end", values=(
                ingrediente.id,
                ingrediente.nombre,
                ingrediente.cantidad,
                ingrediente.unidad_medida
            ))