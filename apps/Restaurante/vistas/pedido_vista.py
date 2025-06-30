import customtkinter as ctk
from tkinter import ttk, messagebox as CTkM
from estructura.crud.pedido_crud import PedidoCRUD
from estructura.crud.cliente_crud import ClienteCRUD
from estructura.crud.menu_crud import MenuCRUD
from estructura.models_folder.models_restaurente import Pedido

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
        self.apply_filter_button.pack(side="left", padx=5)

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
        self.clear_filter_button.pack(side="left", padx=5)

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
            treeview.column(column, anchor='center')
        return treeview

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
            menus = ", ".join([f"{menu['cantidad']}x {MenuCRUD.get_menu_by_id(self.db, menu['id']).nombre}" 
                             for menu in pedido.menus])
            self.pedido_list.insert("", "end", values=(
                pedido.id, 
                pedido.descripcion, 
                pedido.total, 
                pedido.fecha, 
                pedido.cliente_rut,
                menus
            ))

    def delete_pedido(self):
        selected_item = self.pedido_list.selection()
        if not selected_item:
            CTkM.showerror("Error", "Selecciona un pedido de la lista.")
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
        CTkM.showinfo("Información", message)