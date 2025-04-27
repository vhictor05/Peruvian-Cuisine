import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from disco_database import get_db, engine, Base
from models_folder.models_disco import Trago, PedidoTrago, Evento, ClienteDiscoteca, Entrada, Mesa, ReservaMesa
from crud.evento_crud import EventoCRUD
from crud.cliente_disco_crud import ClienteDiscotecaCRUD
from tkcalendar import Calendar, DateEntry
import tkinter as tk
from fpdf import FPDF
from crud.trago_crud import TragoCRUD

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DiscotecaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Discoteca")
        self.geometry("1200x700")
        self.configure(fg_color="#1e1e2d")
        self.db: Session = next(get_db())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frame secundario
        self.menu_frame = ctk.CTkFrame(
            self,
            fg_color="#25253a", 
            corner_radius=0
        )
        self.menu_frame.pack(
            side="right", 
            fill="y"
        )

        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self, fg_color="#25253a", 
            corner_radius=15
        )
        self.main_frame.pack(
            side="left", 
            fill="both", 
            expand=True, 
            padx=20, 
            pady=20)

        # Crear botones en el frame secundario
        self.create_menu_button("Eventos", self.show_eventos)
        self.create_menu_button("Clientes", self.show_clientes)
        self.create_menu_button("Tragos", self.show_tragos)
        TragoCRUD.inicializar_tragos(self.db)

        self.show_eventos()

    def on_closing(self):
        try:
            self.destroy()
        except Exception:
            pass

    def create_menu_button(self, text, command):
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=command,
            fg_color="#7209b7",  # Color principal del botón
            hover_color="#9d4dc7",  # Color más claro para el hover
            font=("Arial", 20),  # Fuente personalizada
            corner_radius=50,  # Bordes redondeados
            width=200,  # Ancho del botón
            height=50  # Alto del botón
        )
        btn.pack(side="top", padx=20, pady=40)  # Espaciado mejorado
        
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_form_entry(self, parent, label, row):
        frame = ctk.CTkFrame(
            parent, 
            fg_color="#1e1e2d"
        ) 
        frame.grid(
            row=row, 
            column=0, 
            sticky="ew", 
            pady=5
        )
        ctk.CTkLabel(
            frame, 
            text=label + ":", 
            fg_color="#1e1e2d"
        ).pack(side="left", padx=5)
        entry = ctk.CTkEntry(
            frame,
            fg_color="#1e1e2d",  # Fondo interno del cuadro
            border_color="#7209b7",  # Color del borde
            border_width=2  # Ancho del borde
        )
        entry.pack(
            side="right", 
            fill="x", 
            expand=True, 
            padx=5
        )
        return entry

    # ===== EVENTOS =====
    def show_eventos(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Eventos",
            text_color="#7209b7",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=20)

        # Campos del formulario organizados con grid()
        ctk.CTkLabel(form_frame, text="Nombre:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.evento_nombre = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.evento_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Descripción:", font=("Arial", 14)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.evento_descripcion = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.evento_descripcion.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Precio Entrada:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.evento_precio = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.evento_precio.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Aforo Máximo:", font=("Arial", 14)).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.evento_aforo = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.evento_aforo.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Configurar las columnas para que las entradas se expandan
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Frame para fecha y hora
        fecha_frame = ctk.CTkFrame(form_frame, fg_color="#1e1e2d")
        fecha_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10, padx=10)

        ctk.CTkLabel(fecha_frame, text="Fecha:", font=("Arial", 14)).pack(side="left", padx=10)
        self.cal = DateEntry(
            fecha_frame,
            date_pattern="yyyy-mm-dd",
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2
        )
        self.cal.pack(side="left", padx=10)

        # Selector de hora
        hora_frame = ctk.CTkFrame(fecha_frame, fg_color="#1e1e2d")
        hora_frame.pack(side="left", padx=10)

        ctk.CTkLabel(hora_frame, text="Hora:", font=("Arial", 14)).pack(side="left")
        self.hora_spinbox = ttk.Spinbox(hora_frame, from_=0, to=23, width=2, format="%02.0f")
        self.hora_spinbox.pack(side="left", padx=5)
        self.hora_spinbox.set("20")

        ctk.CTkLabel(hora_frame, text=":", font=("Arial", 14)).pack(side="left")
        self.minuto_spinbox = ttk.Spinbox(hora_frame, from_=0, to=59, width=2, format="%02.0f")
        self.minuto_spinbox.pack(side="left", padx=5)
        self.minuto_spinbox.set("00")

        # Botón para registrar evento
        ctk.CTkButton(
            self.main_frame,
            text="Registrar Evento",
            command=self.registrar_evento,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 16),
            corner_radius=50
    ).pack(pady=10)

        # Tabla de eventos
        self.evento_tree = self.create_treeview(["ID", "Nombre", "Fecha", "Precio", "Aforo"])
        self.actualizar_lista_eventos()

    def registrar_evento(self):
        try:
            # Obtener fecha y hora de los nuevos controles
            fecha = self.cal.get_date()
            hora = int(self.hora_spinbox.get())
            minuto = int(self.minuto_spinbox.get())
            
            fecha_hora = datetime(
                year=fecha.year,
                month=fecha.month,
                day=fecha.day,
                hour=hora,
                minute=minuto
            )
            
            evento_data = {
                "nombre": self.evento_nombre.get(),
                "descripcion": self.evento_descripcion.get(),
                "fecha": fecha_hora,
                "precio_entrada": float(self.evento_precio.get()),
                "aforo_maximo": int(self.evento_aforo.get())
            }
            
            EventoCRUD.crear(self.db, evento_data)
            messagebox.showinfo("Éxito", "Evento registrado")
            self.actualizar_lista_eventos()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_lista_eventos(self):
        self.evento_tree.delete(*self.evento_tree.get_children())
        for e in EventoCRUD.obtener_todos(self.db):
            self.evento_tree.insert("", "end", values=(e.id, e.nombre, e.fecha, e.precio_entrada, e.aforo_maximo))

    # ===== CLIENTES =====
    def show_clientes(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Clientes",
            font=("Arial", 28, "bold"),
            text_color="#7209b7"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=20, pady=10)

        # Campos del formulario organizados con grid()
        ctk.CTkLabel(form_frame, text="Nombre:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.cliente_nombre = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.cliente_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="RUT:", font=("Arial", 14)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.cliente_rut = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.cliente_rut.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.cliente_email = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.cliente_email.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Teléfono:", font=("Arial", 14)).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.cliente_telefono = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.cliente_telefono.grid(row=1, column=3, padx=10, pady=10, sticky="ew")

        # Configurar las columnas para que las entradas se expandan
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        # Botón para registrar cliente
        ctk.CTkButton(
            self.main_frame,
            text="Registrar Cliente",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            command=self.registrar_cliente,
            corner_radius=50
        ).pack(pady=10)
        # Tabla de clientes
        self.cliente_tree = self.create_treeview(["ID", "Nombre", "RUT", "Email", "Teléfono"])
        self.actualizar_lista_clientes()

    def registrar_cliente(self):
        try:
            cliente_data = {
                "nombre": self.cliente_nombre.get(),
                "rut": self.cliente_rut.get(),
                "email": self.cliente_email.get(),
                "telefono": self.cliente_telefono.get()
            }
            ClienteDiscotecaCRUD.crear(self.db, cliente_data)
            messagebox.showinfo("Éxito", "Cliente registrado")
            self.actualizar_lista_clientes()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_lista_clientes(self):
        self.cliente_tree.delete(*self.cliente_tree.get_children())
        for c in ClienteDiscotecaCRUD.obtener_todos(self.db):
            self.cliente_tree.insert("", "end", values=(c.id, c.nombre, c.rut, c.email or "", c.telefono or ""))

    def create_treeview(self, columns):
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        return tree
    


    def show_tragos(self):
            self.clear_main_frame()
            
            # Título
            ctk.CTkLabel(
                self.main_frame, 
                text="Gestión de Tragos", 
                text_color="#7209b7", 
                font=("Arial", 28, "bold")
            ).pack(pady=10)
            
            # Pestañas
            tabview = ctk.CTkTabview(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
            tabview.pack(fill="both", expand=True, padx=20, pady=10)
            
            tabview.add("Registro")
            tabview.add("Pedidos")
            
            # Pestaña de Registro
            self.setup_tragos_registro_tab(tabview.tab("Registro"))
            
            # Pestaña de Pedidos
            self.setup_tragos_pedidos_tab(tabview.tab("Pedidos"))

    def setup_tragos_registro_tab(self, tab):
        form_frame = ctk.CTkFrame(tab, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Combobox para seleccionar trago existente
        ctk.CTkLabel(form_frame, text="Seleccionar Trago:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.trago_seleccionado = ctk.CTkComboBox(form_frame, state="readonly")
        self.trago_seleccionado.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Campo para modificar precio (a la derecha de "Seleccionar Trago")
        ctk.CTkLabel(form_frame, text="Precio:", font=("Arial", 14)).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.trago_precio = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#7209b7", border_width=2)
        self.trago_precio.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Checkbox para disponibilidad
        self.trago_disponible = ctk.CTkCheckBox(
            form_frame, 
            text="Disponible", 
            fg_color="#7209b7", 
            hover_color="#9d4dc7"
        )
        self.trago_disponible.grid(
            row=1, 
            column=0, 
            columnspan=2, 
            padx=10, 
            pady=10, 
            sticky="w"
        )

        # Botones
        btn_frame = ctk.CTkFrame(tab, fg_color="#1e1e2d")
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            btn_frame, 
            text="Actualizar Precio",
            command=self.actualizar_precio_trago,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            corner_radius=50
        ).pack(side="left", padx=5)

        ctk.CTkButton(
             btn_frame, 
            text="Cambiar Disponibilidad",
            command=self.cambiar_disponibilidad_trago,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            corner_radius=50
        ).pack(side="left", padx=10)

        # Actualizar lista de tragos
        self.actualizar_lista_tragos_combobox()
        self.trago_seleccionado.bind("<<ComboboxSelected>>", self.on_trago_selected)

        # Lista de tragos
        columns = ["ID", "Nombre", "Precio", "Categoría", "Disponible"]
        self.trago_tree = ttk.Treeview(tab, columns=columns, show="headings")
        for col in columns:
            self.trago_tree.heading(col, text=col)
            self.trago_tree.column(col, width=120)

        self.trago_tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.actualizar_lista_tragos()

    def setup_tragos_pedidos_tab(self, tab):
        # Frame de instrucciones
        instrucciones_frame = ctk.CTkFrame(tab, fg_color="transparent")
        instrucciones_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(
            instrucciones_frame, 
            text="① Seleccione cliente → ② Añada tragos → ③ Confirme pedido",
            font=("Arial", 12, "bold"),
            text_color="#7209b7"
        ).pack()

        # Frame superior para selección de cliente con búsqueda
        cliente_frame = ctk.CTkFrame(tab, fg_color="#1e1e2d", corner_radius=15)
        cliente_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Búsqueda de cliente
        ctk.CTkLabel(cliente_frame, text="Buscar Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.busqueda_cliente = ctk.CTkEntry(
            cliente_frame,
            fg_color="#1e1e2d",  # Fondo interno del cuadro
            border_color="#7209b7",  # Color del borde
            border_width=2  # Ancho del borde
        )
        self.busqueda_cliente.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.busqueda_cliente.bind("<KeyRelease>", self.filtrar_clientes)

        # Combobox de clientes filtrados
        self.lista_clientes = ctk.CTkComboBox(cliente_frame, state="readonly")
        self.lista_clientes.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky="ew")
        self.actualizar_lista_clientes_combo()

        # Panel de info del cliente seleccionado
        self.cliente_info_frame = ctk.CTkFrame(tab, fg_color="#25253e", corner_radius=15)
        self.cliente_info_frame.pack(fill="x", padx=10, pady=(0, 15))
        self.cliente_seleccionado_label = ctk.CTkLabel(
            self.cliente_info_frame, 
            text="Ningún cliente seleccionado",
            font=("Arial", 12)
        )
        self.cliente_seleccionado_label.pack(pady=5)

        # Frame para agregar tragos
        tragos_frame = ctk.CTkFrame(tab, fg_color="#25253e", corner_radius=15)
        tragos_frame.pack(fill="x", padx=10, pady=10)

        # Búsqueda de tragos
        ctk.CTkLabel(tragos_frame, text="Buscar Trago:").grid(row=0, column=0, padx=5, pady=5)
        self.busqueda_trago = ctk.CTkEntry(
            tragos_frame,
            fg_color="#1e1e2d",  # Fondo interno del cuadro
            border_color="#7209b7",  # Color del borde
            border_width=2  # Ancho del borde
        )
        self.busqueda_trago.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.busqueda_trago.bind("<KeyRelease>", self.filtrar_tragos)

        # Combobox de tragos filtrados
        self.lista_tragos = ctk.CTkComboBox(tragos_frame, state="readonly")
        self.lista_tragos.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.actualizar_lista_tragos_combo()

        # Cantidad
        ctk.CTkLabel(tragos_frame, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        self.trago_cantidad = ctk.CTkEntry(tragos_frame, width=60)
        self.trago_cantidad.grid(row=1, column=1, padx=5, pady=5)
        self.trago_cantidad.insert(0, "1")

        # Botón para agregar
        agregar_btn = ctk.CTkButton(
            tragos_frame, 
            text="➕ Agregar",
            command=self.agregar_trago_pedido,
            width=80,
            fg_color="#2e8b57",
            hover_color="#3cb371"
        )
        agregar_btn.grid(row=1, column=2, padx=5, pady=5)

        # Lista de pedidos actuales
        columns = ["Trago", "Cantidad", "Precio Unitario", "Subtotal", "✖"]
        self.pedido_tree = ttk.Treeview(
            tab,
            columns=columns,
            show="headings",
            height=8,
            selectmode="browse"
        )
        
        # Configurar columnas
        col_widths = [150, 80, 120, 100, 40]
        for col, width in zip(columns, col_widths):
            self.pedido_tree.heading(col, text=col)
            self.pedido_tree.column(col, width=width, anchor="center")
        
        # Estilo para el Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            bordercolor="#3b3b3b",
            borderwidth=0
        )
        style.map('Treeview', background=[('selected', '#3a7ebf')])
        
        self.pedido_tree.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Frame inferior con total y botón
        bottom_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.pedido_total = ctk.CTkLabel(
            bottom_frame, 
            text="Total: $0.00", 
            font=("Arial", 14, "bold"),
            text_color="#f0f0f0"
        )
        self.pedido_total.pack(side="left", padx=10)

        confirmar_btn = ctk.CTkButton(
            bottom_frame,
            text="✅ Confirmar Pedido",
            command=self.confirmar_pedido_tragos,
            fg_color="#7209b7",
            hover_color="#9d4dc7"
        )
        confirmar_btn.pack(side="right")

    def registrar_trago(self):
        try:
            trago_data = {
                "nombre": self.trago_nombre.get(),
                "descripcion": self.trago_descripcion.get(),
                "precio": float(self.trago_precio.get()),
                "categoria": self.trago_categoria.get() or None
            }
            
            TragoCRUD.crear_trago(self.db, **trago_data)
            messagebox.showinfo("Éxito", "Trago registrado correctamente")
            self.actualizar_lista_tragos()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_lista_tragos(self):
        for item in self.trago_tree.get_children():
            self.trago_tree.delete(item)
            
        tragos = TragoCRUD.obtener_todos(self.db)
        for trago in tragos:
            self.trago_tree.insert("", "end", values=(
                trago.id,
                trago.nombre,
                trago.descripcion or "",
                f"${trago.precio:.2f}",
                trago.categoria or ""
            ))

    def obtener_tragos_combobox(self):
        tragos = TragoCRUD.obtener_todos(self.db)
        return [f"{t.nombre} (${t.precio:.2f})" for t in tragos]

    def agregar_trago_pedido(self):
        try:
            trago_str = self.lista_tragos.get()
            cantidad = int(self.trago_cantidad.get())
            
            if not trago_str or cantidad <= 0:
                messagebox.showwarning("Advertencia", "Seleccione un trago y cantidad válida")
                return
            
            # Extraer nombre del trago
            trago_nombre = trago_str.split(" ($")[0]
            trago = self.db.query(Trago).filter(Trago.nombre == trago_nombre).first()
            
            if not trago:
                messagebox.showerror("Error", "Trago no encontrado")
                return
            
            subtotal = trago.precio * cantidad
            
            # Insertar con botón de eliminar
            item_id = self.pedido_tree.insert("", "end", values=(
                trago.nombre,
                cantidad,
                f"${trago.precio:.2f}",
                f"${subtotal:.2f}",
                "✖"
            ))
            
            # Configurar evento para eliminar
            self.pedido_tree.tag_bind(item_id, "<Button-1>", lambda e: self.eliminar_item_pedido(e, item_id))
            
            self.actualizar_total_pedido()
            self.trago_cantidad.delete(0, "end")
            self.trago_cantidad.insert(0, "1")
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número entero")

    def eliminar_item_pedido(self, event, item_id):
        # Verificar si se hizo click en la columna de eliminar (última columna)
        column = self.pedido_tree.identify_column(event.x)
        if column == "#5":
            self.pedido_tree.delete(item_id)
            self.actualizar_total_pedido()

    def actualizar_total_pedido(self):
        total = 0.0
        for item in self.pedido_tree.get_children():
            subtotal_str = self.pedido_tree.item(item, "values")[3]
            subtotal = float(subtotal_str.replace("$", ""))
            total += subtotal
        
        self.pedido_total.configure(text=f"Total: ${total:.2f}")

    def confirmar_pedido_tragos(self):
        cliente_str = self.lista_clientes.get()
        items = self.pedido_tree.get_children()
        
        if not cliente_str:
            messagebox.showwarning("Advertencia", "Seleccione un cliente primero")
            return
        
        if not items:
            messagebox.showwarning("Advertencia", "Agregue al menos un trago al pedido")
            return
        
        try:
            # Obtener RUT del cliente
            cliente_rut = cliente_str.split("(")[-1].rstrip(")")
            cliente = ClienteDiscotecaCRUD.obtener_por_rut(self.db, cliente_rut)
            
            if not cliente:
                messagebox.showerror("Error", "Cliente no encontrado")
                return
            
            # Preparar detalles del pedido
            detalles = {}
            for item in items:
                values = self.pedido_tree.item(item, "values")
                trago_nombre = values[0]
                cantidad = int(values[1])
                
                trago = self.db.query(Trago).filter(Trago.nombre == trago_nombre).first()
                detalles[trago.id] = cantidad
            
            # Calcular total
            total = sum(
                self.db.query(Trago.precio).filter(Trago.id == trago_id).scalar() * cantidad
                for trago_id, cantidad in detalles.items()
            )
            
            # Crear pedido
            pedido = PedidoTrago(
                cliente_id=cliente.id,
                total=total,
                detalles=detalles,
                estado="Confirmado"
            )
            
            self.db.add(pedido)
            self.db.commit()
            
            # Generar boleta
            self.generar_boleta_tragos(pedido.id)
            
            messagebox.showinfo("Éxito", f"Pedido #{pedido.id} registrado\nBoleta generada: boleta_pedido_{pedido.id}.pdf")
            self.limpiar_pedido()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar el pedido: {str(e)}")

    def actualizar_lista_tragos_combobox(self):
        tragos = TragoCRUD.obtener_todos(self.db)
        valores = [f"{t.nombre} (${t.precio:.2f})" for t in tragos]
        self.trago_seleccionado.configure(values=valores)

    def on_trago_selected(self, event):
        trago_str = self.trago_seleccionado.get()
        if trago_str:
            trago_nombre = trago_str.split(" ($")[0]
            trago = self.db.query(Trago).filter(Trago.nombre == trago_nombre).first()
            if trago:
                self.trago_precio.delete(0, "end")
                self.trago_precio.insert(0, str(trago.precio))
                self.trago_disponible.select() if trago.disponible else self.trago_disponible.deselect()

    def actualizar_precio_trago(self):
        try:
            trago_str = self.trago_seleccionado.get()
            nuevo_precio = float(self.trago_precio.get())
            
            if not trago_str:
                messagebox.showwarning("Advertencia", "Seleccione un trago primero")
                return
                
            trago_nombre = trago_str.split(" ($")[0]
            trago = self.db.query(Trago).filter(Trago.nombre == trago_nombre).first()
            
            if trago:
                TragoCRUD.actualizar_precio(self.db, trago.id, nuevo_precio)
                messagebox.showinfo("Éxito", "Precio actualizado correctamente")
                self.actualizar_lista_tragos()
                self.actualizar_lista_tragos_combobox()
                self.actualizar_lista_tragos_combo()  # Para la pestaña de pedidos
        except ValueError:
            messagebox.showerror("Error", "Ingrese un precio válido")

    def cambiar_disponibilidad_trago(self):
        trago_str = self.trago_seleccionado.get()
        if not trago_str:
            messagebox.showwarning("Advertencia", "Seleccione un trago primero")
            return
            
        trago_nombre = trago_str.split(" ($")[0]
        trago = self.db.query(Trago).filter(Trago.nombre == trago_nombre).first()
        
        if trago:
            nueva_disponibilidad = self.trago_disponible.get()
            TragoCRUD.cambiar_disponibilidad(self.db, trago.id, nueva_disponibilidad)
            estado = "disponible" if nueva_disponibilidad else "no disponible"
            messagebox.showinfo("Éxito", f"Trago marcado como {estado}")
            self.actualizar_lista_tragos()
            self.actualizar_lista_tragos_combobox()
            self.actualizar_lista_tragos_combo()  # Para la pestaña de pedidos

    def generar_boleta_tragos(self, pedido_id):
        pedido = self.db.query(PedidoTrago).filter(PedidoTrago.id == pedido_id).first()
        cliente = self.db.query(ClienteDiscoteca).filter(ClienteDiscoteca.id == pedido.cliente_id).first()
        
        pdf = FPDF()
        pdf.add_page()
        
        # Encabezado
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Boleta de Pedido - Discoteca", 0, 1, "C")
        pdf.ln(10)
        
        # Información del cliente
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Cliente: {cliente.nombre}", 0, 1)
        pdf.cell(0, 10, f"RUT: {cliente.rut}", 0, 1)
        pdf.cell(0, 10, f"Fecha: {pedido.fecha.strftime('%Y-%m-%d %H:%M')}", 0, 1)
        pdf.ln(10)
        
        # Detalles del pedido
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 10, "Trago", 1)
        pdf.cell(30, 10, "Cantidad", 1)
        pdf.cell(40, 10, "Precio Unitario", 1)
        pdf.cell(40, 10, "Subtotal", 1)
        pdf.ln()
        
        pdf.set_font("Arial", "", 12)
        for trago_id, cantidad in pedido.detalles.items():
            trago = self.db.query(Trago).filter(Trago.id == trago_id).first()
            subtotal = trago.precio * cantidad
            
            pdf.cell(40, 10, trago.nombre, 1)
            pdf.cell(30, 10, str(cantidad), 1)
            pdf.cell(40, 10, f"${trago.precio:.2f}", 1)
            pdf.cell(40, 10, f"${subtotal:.2f}", 1)
            pdf.ln()
        
        # Total
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Total: ${pedido.total:.2f}", 0, 1, "R")
        pdf.ln(10)
        
        # Pie de página
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "¡Gracias por su compra!", 0, 1, "C")
        
        # Guardar PDF
        nombre_archivo = f"boleta_pedido_{pedido_id}.pdf"
        pdf.output(nombre_archivo)
        messagebox.showinfo("Éxito", f"Boleta generada: {nombre_archivo}")

    def limpiar_pedido(self):
        # Limpiar Treeview
        for item in self.pedido_tree.get_children():
            self.pedido_tree.delete(item)
        
        # Resetear controles
        self.pedido_total.configure(text="Total: $0.00")
        self.lista_clientes.set("")
        self.busqueda_cliente.delete(0, "end")
        self.lista_tragos.set("")
        self.busqueda_trago.delete(0, "end")
        self.trago_cantidad.delete(0, "end")
        self.trago_cantidad.insert(0, "1")
        self.cliente_seleccionado_label.configure(
            text="Ningún cliente seleccionado",
            font=("Arial", 12)
        )

    def actualizar_lista_clientes_combo(self):
        clientes = ClienteDiscotecaCRUD.obtener_todos(self.db)
        valores = [f"{c.nombre} ({c.rut})" for c in clientes]
        self.lista_clientes.configure(values=valores)

    def filtrar_clientes(self, event):
        busqueda = self.busqueda_cliente.get().lower()
        clientes = ClienteDiscotecaCRUD.obtener_todos(self.db)
        
        if busqueda:
            filtrados = [f"{c.nombre} ({c.rut})" for c in clientes 
                        if busqueda in c.nombre.lower() or busqueda in c.rut]
        else:
            filtrados = [f"{c.nombre} ({c.rut})" for c in clientes]
        
        self.lista_clientes.configure(values=filtrados)
        self.lista_clientes.set("")

    def actualizar_lista_tragos_combo(self):
        tragos = TragoCRUD.obtener_todos(self.db)
        valores = [f"{t.nombre} (${t.precio:.2f})" for t in tragos]
        self.lista_tragos.configure(values=valores)

    def filtrar_tragos(self, event):
        busqueda = self.busqueda_trago.get().lower()
        tragos = TragoCRUD.obtener_todos(self.db)
        
        if busqueda:
            filtrados = [f"{t.nombre} (${t.precio:.2f})" for t in tragos 
                        if busqueda in t.nombre.lower() or 
                        busqueda in (t.categoria.lower() if t.categoria else "")]
        else:
            filtrados = [f"{t.nombre} (${t.precio:.2f})" for t in tragos]
        
        self.lista_tragos.configure(values=filtrados)
        self.lista_tragos.set("")

    def on_cliente_seleccionado(self, event=None):
        cliente_str = self.lista_clientes.get()
        if cliente_str:
            self.cliente_seleccionado_label.configure(
                text=f"Cliente seleccionado: {cliente_str.split('(')[0].strip()}",
                font=("Arial", 12, "bold")
            )
        else:
            self.cliente_seleccionado_label.configure(
                text="Ningún cliente seleccionado",
                font=("Arial", 12)
            )       

if __name__ == "__main__":
    app = DiscotecaApp()
    app.mainloop()