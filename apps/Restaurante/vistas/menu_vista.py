import customtkinter as ctk
from tkinter import ttk, messagebox
from estructura.crud.menu_crud import MenuCRUD
from estructura.crud.ingrediente_crud import IngredienteCRUD
from estructura.models_folder.models_restaurente import Menu

class MenuPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.configure(fg_color="#25253a", corner_radius=15)

        # Título
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

        # Mantener el campo Precio
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
        
        # Botones de menú
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

        # Frame de ingredientes
        self.ingredientes_frame = ctk.CTkFrame(
            self, 
            fg_color="#25253a", 
            corner_radius=15,
            width=400
        )
        self.ingredientes_frame.grid(row=3, column=0, pady=10, padx=30, sticky="nsew")
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
        self.cantidad_label.grid(row=0, column=1, padx=10, pady=(5,2))

        self.cantidad_entry = ctk.CTkEntry(
            self.ingredientes_frame, 
            corner_radius=5,
            height=30,
            width=150,
            fg_color="#25253a",
            border_color="#4361ee",
            border_width=1
        )
        self.cantidad_entry.grid(row=1, column=1, padx=10, pady=(0,5))

        # Botones de ingredientes
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

        # Lista de ingredientes
        self.ingredientes_list = self.create_treeview_ingredientes()
        self.ingredientes_list.grid(row=2, column=0, columnspan=5, pady=10, sticky="nsew")

        # Lista de menús
        self.menu_list = self.create_treeview(Menu)
        self.menu_list.grid(row=4, column=0, pady=10, sticky="nsew")

        # Configuración del grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Inicialización
        self.refresh_list()
        self.load_ingredientes()

    def create_treeview(self, model_class):
        columns = [column.name for column in model_class.__table__.columns if column.name not in ['id']] + ["ing_necesarios"]
        treeview = ttk.Treeview(self, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column.capitalize())
            treeview.column(column, width=150)
        return treeview

    def create_treeview_ingredientes(self):
        columns = ["Ingrediente", "Cantidad"]
        treeview = ttk.Treeview(self.ingredientes_frame, columns=columns, show="headings")
        for column in columns:
            treeview.heading(column, text=column)
            treeview.column(column, width=150)
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

        # Verificar si el ingrediente ya existe en la lista
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

        # Verificar duplicados excepto el seleccionado
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
        if menu_existente:
            messagebox.showerror("Error", f"El menú '{nombre}' ya existe.")
            return

        ingredientes = self.get_ingredientes_from_list()
        if not ingredientes:
            messagebox.showerror("Error", "Debe agregar al menos un ingrediente al menú.")
            return

        menu = MenuCRUD.create_menu(self.db, nombre, descripcion, precio, ingredientes)
        if menu:
            messagebox.showinfo("Éxito", f"Menú '{nombre}' registrado con éxito.")
            self.refresh_list()
            # Limpiar campos
            self.nombre_entry.delete(0, "end")
            self.descripcion_entry.delete(0, "end")
            self.precio_entry.delete(0, "end")
            for item in self.ingredientes_list.get_children():
                self.ingredientes_list.delete(item)
        else:
            messagebox.showerror("Error", f"Error al registrar el menú '{nombre}'.")

    def open_edit_window(self):
        selected_item = self.menu_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un menú de la lista.")
            return

        menu_nombre = self.menu_list.item(selected_item)["values"][0]
        menu = MenuCRUD.get_menu_by_nombre(self.db, menu_nombre)

        if menu:
            self.edit_window = ctk.CTkToplevel(self)
            self.edit_window.title("Editar Menú")
            self.edit_window.geometry("400x400")
            self.edit_window.configure(fg_color="#1c1c1c")
            
            self.edit_nombre_entry = self.create_form_entry_in_window("Nombre", 1, menu.nombre)
            self.edit_descripcion_entry = self.create_form_entry_in_window("Descripción", 2, menu.descripcion)
            self.edit_precio_entry = self.create_form_entry_in_window("Precio", 3, str(menu.precio))

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

            # Botones para gestionar ingredientes
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

            # Cargar ingredientes existentes
            for ingrediente in menu.ingredientes:
                self.edit_ingredientes_list.insert("", "end", 
                    values=(ingrediente.ingrediente.nombre, ingrediente.cantidad))

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
            corner_radius=10, 
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

        # Verificar duplicados
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

        # Verificar duplicados excepto el seleccionado
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
        if not ingredientes:
            messagebox.showerror("Error", "Debe agregar al menos un ingrediente al menú.")
            return

        menu = MenuCRUD.update_menu(self.db, menu_id, nombre, descripcion, precio, ingredientes)
        if menu:
            messagebox.showinfo("Éxito", f"Menú '{nombre}' actualizado con éxito.")
            self.edit_window.destroy()
            self.refresh_list()
        else:
            messagebox.showerror("Error", f"Error al actualizar el menú '{nombre}'.")

    def delete_menu(self):
        selected_item = self.menu_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un menú de la lista.")
            return

        menu_nombre = self.menu_list.item(selected_item)["values"][0]
        confirm = messagebox.askyesno("Confirmar Eliminación", 
                                    f"¿Estás seguro de eliminar el menú '{menu_nombre}'?")
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
            ing_necesarios = ", ".join([f"{ing.cantidad}x {ing.ingrediente.nombre}" 
                                      for ing in menu.ingredientes])
            self.menu_list.insert("", "end", values=(
                menu.nombre,
                menu.descripcion,
                menu.precio,
                ing_necesarios
            ))            