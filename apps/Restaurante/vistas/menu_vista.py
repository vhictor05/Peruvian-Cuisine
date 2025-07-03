import requests
import json
import customtkinter as ctk
from tkinter import messagebox
import tkinter.ttk as ttk

# URL base de tu API
API_BASE_URL = "http://127.0.0.1:8000/api/v1/restaurant"

class MenuPanel(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db  # Solo para compatibilidad, no se usará
        self.configure(fg_color="#25253a", corner_radius=15)
        self.selected_menu_id = None  # Para rastrear el menú seleccionado

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
        self.menu_list = self.create_treeview_menu()
        self.menu_list.grid(row=4, column=0, pady=10, sticky="nsew")

        # Configuración del grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Inicialización
        self.refresh_list()
        self.load_ingredientes()

    def create_treeview_menu(self):
        """Crear treeview para menús sin depender de SQLAlchemy"""
        columns = ["Nombre", "Descripcion", "Precio", "Ing_necesarios"]
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
        """Cargar ingredientes de ejemplo - ya no usar SQLAlchemy"""
        # Ingredientes de ejemplo (podrías crear otro endpoint de API para esto)
        ingredientes_ejemplo = ["Tomate", "Cebolla", "Ají", "Pescado", "Limón", "Cilantro", 
                              "Papas", "Carne", "Pollo", "Arroz", "Frijoles"]
        self.ingredientes_combobox.configure(values=ingredientes_ejemplo)
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

    def add_menu(self):
        """Crear menú usando SOLO la API"""
        nombre = self.nombre_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        precio = self.precio_entry.get().strip()

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

        # Recopilar ingredientes de la lista
        ingredientes = {}
        for item in self.ingredientes_list.get_children():
            ingrediente, cantidad = self.ingredientes_list.item(item, "values")
            ingredientes[ingrediente] = float(cantidad)

        # Llamar a la API
        try:
            response = requests.post(
                f"{API_BASE_URL}/menu",
                json={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "ingredientes": ingredientes
                },
                headers={"Content-Type": "application/json"
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Éxito", "Menú creado correctamente")
                self.refresh_list()
                # Limpiar campos
                self.nombre_entry.delete(0, "end")
                self.descripcion_entry.delete(0, "end")
                self.precio_entry.delete(0, "end")
                for item in self.ingredientes_list.get_children():
                    self.ingredientes_list.delete(item)
            else:
                error_detail = response.json().get("detail", "Error desconocido")
                messagebox.showerror("Error", f"Error al crear menú: {error_detail}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {str(e)}")

    def open_edit_window(self):
        """Abrir ventana de edición usando datos de la tabla"""
        selected_item = self.menu_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un menú de la lista.")
            return

        # Obtener datos del menú seleccionado
        item_tags = self.menu_list.item(selected_item[0])["tags"]
        if not item_tags:
            messagebox.showerror("Error", "No se pudo obtener el ID del menú.")
            return
        
        menu_id = item_tags[0]
        item_values = self.menu_list.item(selected_item[0])["values"]
        
        # Crear ventana de edición
        self.edit_window = ctk.CTkToplevel(self)
        self.edit_window.title("Editar Menú")
        self.edit_window.geometry("600x500")
        self.edit_window.configure(fg_color="#1c1c1c")
        
        # Campos de edición con valores actuales
        self.edit_nombre_entry = self.create_form_entry_in_window("Nombre", 1, item_values[0])
        self.edit_descripcion_entry = self.create_form_entry_in_window("Descripción", 2, item_values[1])
        self.edit_precio_entry = self.create_form_entry_in_window("Precio", 3, item_values[2])

        # Frame de ingredientes
        self.edit_ingredientes_frame = ctk.CTkFrame(
            self.edit_window, 
            fg_color="#2c2c2c", 
            corner_radius=10
        )
        self.edit_ingredientes_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        # Controles de ingredientes
        self.edit_ingredientes_label = ctk.CTkLabel(
            self.edit_ingredientes_frame, 
            text="Ingredientes:", 
            font=("Arial", 14)
        )
        self.edit_ingredientes_label.grid(row=0, column=0, padx=10, pady=5)

        self.edit_ingredientes_combobox = ctk.CTkComboBox(
            self.edit_ingredientes_frame, 
            values=["Tomate", "Cebolla", "Ají", "Pescado", "Limón", "Cilantro", 
                   "Papas", "Carne", "Pollo", "Arroz", "Frijoles"],
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
            text="Añadir", 
            command=self.edit_add_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0"
        )
        self.edit_add_ingrediente_button.grid(row=1, column=2, padx=5, pady=5)

        self.edit_update_ingrediente_button = ctk.CTkButton(
            self.edit_ingredientes_frame, 
            text="Actualizar", 
            command=self.edit_update_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0"
        )
        self.edit_update_ingrediente_button.grid(row=1, column=3, padx=5, pady=5)

        self.edit_delete_ingrediente_button = ctk.CTkButton(
            self.edit_ingredientes_frame, 
            text="Eliminar", 
            command=self.edit_delete_ingrediente, 
            corner_radius=15,
            fg_color="#4361ee",
            hover_color="#5a75f0"
        )
        self.edit_delete_ingrediente_button.grid(row=1, column=4, padx=5, pady=5)

        # Lista de ingredientes en la ventana de edición
        self.edit_ingredientes_list = self.create_treeview_ingredientes_for_edit()
        self.edit_ingredientes_list.grid(row=2, column=0, columnspan=5, pady=10, sticky="nsew")

        # Parsear y cargar ingredientes actuales
        ingredientes_str = item_values[3] if len(item_values) > 3 else ""
        if ingredientes_str:
            # Formato esperado: "1.0x Tomate, 0.5x Cebolla"
            for ingrediente_info in ingredientes_str.split(", "):
                if "x " in ingrediente_info:
                    cantidad_str, nombre = ingrediente_info.split("x ", 1)
                    try:
                        cantidad = float(cantidad_str)
                        self.edit_ingredientes_list.insert("", "end", values=(nombre, cantidad))
                    except:
                        pass

        # Botón guardar
        self.save_button = ctk.CTkButton(
            self.edit_window, 
            text="Guardar Cambios", 
            command=lambda: self.update_menu(menu_id), 
            corner_radius=50,
            fg_color="#4361ee",
            hover_color="#5a75f0"
        )
        self.save_button.grid(row=5, column=0, pady=10)

    def create_treeview_ingredientes_for_edit(self):
        """Crear treeview específico para la ventana de edición"""
        columns = ["Ingrediente", "Cantidad"]
        treeview = ttk.Treeview(self.edit_ingredientes_frame, columns=columns, show="headings", height=6)
        for column in columns:
            treeview.heading(column, text=column)
            treeview.column(column, width=150)
        return treeview

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

    def update_menu(self, menu_id):
        """Actualizar menú usando SOLO la API"""
        nombre = self.edit_nombre_entry.get().strip()
        descripcion = self.edit_descripcion_entry.get().strip()
        precio = self.edit_precio_entry.get().strip()

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

        # Recopilar ingredientes de la lista de edición
        ingredientes = {}
        for item in self.edit_ingredientes_list.get_children():
            ingrediente, cantidad = self.edit_ingredientes_list.item(item, "values")
            ingredientes[ingrediente] = float(cantidad)

        try:
            response = requests.put(
                f"{API_BASE_URL}/menu/{menu_id}",
                json={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "ingredientes": ingredientes
                },
                headers={"Content-Type": "application/json"
            })
            
            if response.status_code == 200:
                messagebox.showinfo("Éxito", f"Menú '{nombre}' actualizado con éxito.")
                self.edit_window.destroy()
                self.refresh_list()
            else:
                error_detail = response.json().get("detail", "Error desconocido")
                messagebox.showerror("Error", f"Error al actualizar menú: {error_detail}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {str(e)}")

    def delete_menu(self):
        """Eliminar menú usando SOLO la API"""
        selected_item = self.menu_list.selection()
        if not selected_item:
            messagebox.showerror("Error", "Selecciona un menú de la lista.")
            return

        # Obtener el ID del menú desde las tags
        item_tags = self.menu_list.item(selected_item[0])["tags"]
        if not item_tags:
            messagebox.showerror("Error", "No se pudo obtener el ID del menú.")
            return
        
        menu_id = item_tags[0]
        menu_nombre = self.menu_list.item(selected_item[0])["values"][0]
        
        confirm = messagebox.askyesno("Confirmar Eliminación", 
                                    f"¿Estás seguro de eliminar el menú '{menu_nombre}'?")
        if confirm:
            try:
                response = requests.delete(f"{API_BASE_URL}/menu/{menu_id}")
                
                if response.status_code == 204:
                    messagebox.showinfo("Éxito", f"Menú '{menu_nombre}' eliminado con éxito.")
                    self.refresh_list()
                else:
                    error_detail = response.json().get("detail", "Error desconocido")
                    messagebox.showerror("Error", f"Error al eliminar menú: {error_detail}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error de conexión: {str(e)}")

    def refresh_list(self):
        """Cargar menús desde la API"""
        try:
            # Limpiar lista actual
            for item in self.menu_list.get_children():
                self.menu_list.delete(item)
            
            # Obtener menús desde la API
            response = requests.get(f"{API_BASE_URL}/menu")
            
            if response.status_code == 200:
                menus = response.json()
                for menu in menus:
                    # Formatear ingredientes para mostrar
                    ingredientes_str = ", ".join([f"{cantidad}x {nombre}" 
                                                for nombre, cantidad in menu.get("ingredientes", {}).items()])
                    
                    # Insertar en la lista con el ID como tag
                    item = self.menu_list.insert("", "end", values=(
                        menu.get("nombre", ""),
                        menu.get("descripcion", ""),
                        menu.get("precio", ""),
                        ingredientes_str
                    ), tags=(menu.get("id"),))
            else:
                print(f"Error al cargar menús: {response.status_code}")
                
        except Exception as e:
            print(f"Error de conexión: {e}")
            messagebox.showerror("Error", "No se pudieron cargar los menús desde la API")