import customtkinter as ctk
from tkinter import ttk, messagebox
from crud.menu_crud import MenuCRUD
from crud.cliente_crud import ClienteCRUD
from facade.compra_facade import CompraFacade
from crud.ingrediente_crud import IngredienteCRUD

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
        self.total_label = ctk.CTkLabel(
            self, 
            text="Total: $0.00", 
            font=("Arial", 16, "bold"), 
            text_color="white"
        )
        self.total_label.grid(row=4, column=0, pady=10, columnspan=2)

        # Lista interna para almacenar los productos seleccionados
        self.cart = []  # Aquí guardaremos los productos y cantidades seleccionadas

        self.load_clientes()  # Ensure clients are loaded into the combobox
        self.load_menus()  # Ensure menus are loaded into the combobox

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

        menu = next((menu for menu in MenuCRUD.get_menus(self.db) 
                    if menu.nombre == selected_menu), None)
        if menu:
            if not self.verificar_disponibilidad_ingredientes(menu, cantidad):
                messagebox.showerror("Error", 
                                   "No hay suficientes ingredientes para agregar este menú al carrito.")
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