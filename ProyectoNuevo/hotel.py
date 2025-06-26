import customtkinter as ctk
import tkinter as tk
import re
from tkinter import messagebox, ttk
from datetime import datetime
from sqlalchemy.orm import Session
from Hotel.hotel_database import get_db, Base, recreate_db, engine
from models_folder.models_hotel import Huesped, Habitacion, Reserva
from datetime import datetime, timedelta
from tkcalendar import DateEntry, Calendar
from facade.hotel_facade import HotelFacade
from estrategy.hotel_estrategy import PrecioStrategyFactory, CalculadoraPrecio
from builder.hotel_builder import HotelBuilder

#recreate_db()  Recreate the database with the new schema
Base.metadata.create_all(bind=engine)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Hotel")
        self.geometry("1100x650")
        self.db = next(get_db())
        self.hotel_facade = HotelFacade(self.db)
        self.configure(fg_color="#1e1e2d", corner_radius=15)
        
        # Configurar el estilo del Treeview al inicio
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
            background="#1e1e2d",          # Color de fondo para las filas
            foreground="white",            # Color del texto
            fieldbackground="#1e1e2d",     # Color de fondo para el área de datos
            bordercolor="#3b3b3b",
            borderwidth=0
        )
        # Color para la cabecera (nombres de columnas)
        style.configure("Treeview.Heading",
            background="#1e1e2d",         # Color de fondo de la cabecera
            foreground="white",           # Color del texto de la cabecera
            borderwidth=1
        )
        # Color cuando se selecciona una fila
        style.map('Treeview', 
            background=[('selected', '#f72585')],     # Color rosa cuando se selecciona
            foreground=[('selected', 'white')]        # Color del texto cuando se selecciona
        )

        # Configurar el grid del contenedor principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Frame del título
        self.title_frame = ctk.CTkFrame(
            self, 
            fg_color="#1e1e2d",
            height=60,  # Altura fija
            corner_radius=0
        )
        self.title_frame.grid(row=0, column=0, padx=30, pady=65, sticky="ew")
        self.title_frame.grid_propagate(False)  # Mantener altura fija
        
        # Label del título principal
        ctk.CTkLabel(
            self.title_frame,
            text="HOTEL",
            font=("Arial", 26, "bold"),
            text_color="#f72585"
        ).place(relx=0.2, rely=0.3, anchor="w")  # Cambiado a anchor="w" y relx=0.2

        # Label subtítulo
        ctk.CTkLabel(
            self.title_frame,
            text="MANAGER",
            font=("Arial", 23),
            text_color="#fa5c9c"
        ).place(relx=0.2, rely=0.7, anchor="w")  # Cambiado a anchor="w" y mismo relx
        
        # Menú lateral (ahora usando grid)
        self.menu_frame = ctk.CTkFrame(
            self, 
            width=200,
            fg_color="#25253a",
            corner_radius=15
        )
        self.menu_frame.grid(row=1, column=0, sticky="nsw", padx=30, pady=(0, 30))
        self.menu_frame.grid_propagate(False)  # Mantener el ancho fijo
        
        # Contenido principal (ahora usando grid)
        self.main_frame = ctk.CTkFrame(
            self, 
            corner_radius=15, 
            fg_color="#25253a"
        )
        self.main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10,30), pady=30)

        # Botones del menú (ahora apilados verticalmente)
        self.create_menu_button("    Huéspedes", self.show_huespedes)
        self.create_menu_button("    Habitaciones", self.show_habitaciones)
        self.create_menu_button("    Reservas", self.show_reservas)
        
        # Mostrar panel de huéspedes por defecto
        self.show_huespedes()

    def create_menu_button(self, text, command):
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=command,
            font=("Arial", 20),
            height=50,
            width=240,
            corner_radius=0,
            fg_color="#25253a",  # Color principal
            hover_color="#fa5c9c",
            anchor="w",  # Alinear texto a la izquierda
            text_color="white",  # Color del texto
        )
        btn.pack(side="top", fill="x", pady=15)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ===== PANEL HUÉSPEDES =====
    def show_huespedes(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Huéspedes",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=10)

        # Campos del formulario organizados con grid()
        # Nombre y RUT
        ctk.CTkLabel(
            form_frame, 
            text="Nombre:", 
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.huesped_nombre = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1
        )
        self.huesped_nombre.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")

        ctk.CTkLabel(
            form_frame, 
            text="RUT:", 
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")
        
        self.huesped_rut = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1
        )
        self.huesped_rut.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        # Email y Teléfono
        ctk.CTkLabel(
            form_frame, 
            text="Email:", 
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.huesped_email = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1
        )
        self.huesped_email.grid(row=3, column=0, padx=10, pady=(5,10), sticky="ew")

        ctk.CTkLabel(
            form_frame, 
            text="Teléfono:", 
            font=("Arial", 14)
        ).grid(row=2, column=1, padx=10, pady=(10,0), sticky="w")
        
        self.huesped_telefono = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1
        )
        self.huesped_telefono.grid(row=3, column=1, padx=10, pady=(5,10), sticky="ew")

        # Configurar las columnas del formulario para que las entradas se expandan
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Frame para botones
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#25253a", corner_radius=15)
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="📋 Registrar",
            command=self.registrar_huesped,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🔍 Buscar",
            command=self.buscar_huesped,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        # Tabla de huéspedes
        columns = ["ID", "Nombre", "RUT", "Email", "Teléfono"]
        self.huesped_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.huesped_tree.heading(col, text=col)
            if col == "ID":
                self.huesped_tree.column(col, width=15)  # ID más estrecho
            else:
                self.huesped_tree.column(col, width=100)

        self.huesped_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Configurar las columnas del main_frame para que la tabla se expanda
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Llamar al método para actualizar la lista de huéspedes
        self.actualizar_lista_huespedes()

    # ===== MÉTODOS AUXILIARES =====
    def registrar_huesped(self):
        nombre = self.huesped_nombre.get().strip()
        rut = self.huesped_rut.get().strip()
        email = self.huesped_email.get().strip()
        telefono = self.huesped_telefono.get().strip()

        try:
            self.hotel_facade.crear_huesped(nombre, rut, email, telefono)
            messagebox.showinfo("Éxito", "Huésped registrado correctamente")
            self.actualizar_lista_huespedes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")
        

    # ===== PANEL HABITACIONES =====
    def show_habitaciones(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Habitaciones",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=10)

        # Campos del formulario organizados con grid()
        # Número y Tipo (en la misma fila)
        ctk.CTkLabel(
            form_frame, 
            text="Número:", 
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.habitacion_numero = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1
        )
        self.habitacion_numero.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")

        ctk.CTkLabel(
            form_frame, 
            text="Tipo:", 
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")
        
        self.habitacion_tipo = ctk.CTkComboBox(
            form_frame,
            values=["Penthouse", "Grande", "Mediana", "Pequeña",],
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.habitacion_tipo.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        # Precio (debajo de Número)
        ctk.CTkLabel(
            form_frame, 
            text="Precio:", 
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.habitacion_precio = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1
        )
        self.habitacion_precio.grid(row=3, column=0, padx=10, pady=(5,10), sticky="ew")

        # Configurar las columnas del formulario para que las entradas se expandan
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Frame para botones
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#25253a", corner_radius=15)
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="📋 Registrar",
            command=self.registrar_habitacion,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="📝 Modificar",
            command=self.modificar_habitacion,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑 Eliminar",
            command=self.eliminar_habitacion,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        # Tabla de habitaciones
        columns = ["ID", "Número", "Tipo", "Precio", "Disponible"]
        self.habitacion_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.habitacion_tree.heading(col, text=col)
            if col == "ID":
                self.habitacion_tree.column(col, width=15)  # ID más estrecho
            else:
                self.habitacion_tree.column(col, width=100)

        self.habitacion_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.habitacion_tree.bind("<<TreeviewSelect>>", self.cargar_datos_habitacion)


        # Configurar las columnas del main_frame para que la tabla se expanda
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Llamar al método para actualizar la lista de habitaciones
        self.actualizar_lista_habitaciones()

    def registrar_habitacion(self):
        # Obtener los valores ingresados en los campos
        numero = self.habitacion_numero.get()
        tipo = self.habitacion_tipo.get().strip().capitalize()
        precio = self.habitacion_precio.get().strip()

        if not all([numero, tipo, precio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            self.hotel_facade.crear_habitacion(numero, tipo, precio)
            messagebox.showinfo("Éxito", "Habitación registrada correctamente")
            self.actualizar_lista_habitaciones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la habitación: {str(e)}")
    
    # Método para modificar habitación
    def modificar_habitacion(self):
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para modificar")
            return

        habitacion_id = self.habitacion_tree.item(selected_item, "values")[0]

        numero = self.habitacion_numero.get()
        tipo = self.habitacion_tipo.get()
        precio = self.habitacion_precio.get()
        disponible = messagebox.askyesno("Disponibilidad", "¿Está disponible esta habitación?")

        if not all([numero, tipo, precio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            self.hotel_facade.modificar_habitacion(habitacion_id, numero, tipo, precio, disponible)
            messagebox.showinfo("Éxito", "Habitación modificada correctamente")
            self.actualizar_lista_habitaciones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar la habitación: {str(e)}")    
        
    
    def actualizar_lista_habitaciones(self):
        # Verificar si el TreeView está disponible
        if not hasattr(self, 'habitacion_tree') or not self.habitacion_tree.winfo_exists():
            print("El TreeView de habitaciones no está disponible o ha sido destruido.")
            return  # Evita errores si el TreeView no existe
        
        # Limpiar los elementos del TreeView
        for item in self.habitacion_tree.get_children():
            self.habitacion_tree.delete(item)
        
        # Obtener todas las habitaciones de la base de datos
        habitaciones = self.db.query(Habitacion).all()
        if not habitaciones:
            print("No se encontraron habitaciones en la base de datos.")
        
        # Insertar cada habitación en el TreeView
        for hab in habitaciones:
            print(f"Insertando habitación: {hab.id}, {hab.numero}, {hab.tipo}")
            self.habitacion_tree.insert("", "end", values=(
                hab.id,
                hab.numero,
                hab.tipo,
                f"${hab.precio:.2f}",
                "Sí" if hab.disponible else "No"
            ))

    def cargar_datos_habitacion(self, event=None):
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            return

        valores = self.habitacion_tree.item(selected_item, "values")
        habitacion_id, numero, tipo, precio, disponible = valores

        self.habitacion_numero.delete(0, tk.END)
        self.habitacion_numero.insert(0, numero)

        self.habitacion_tipo.set(tipo)

        # Eliminar símbolo $ y convertir a formato editable
        precio_valor = precio.replace("$", "").replace(",", "")
        self.habitacion_precio.delete(0, tk.END)
        self.habitacion_precio.insert(0, precio_valor)

    
    # ===== PANEL RESERVAS =====
    def show_reservas(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Reservas",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=10)

        # Huésped y Tipo de Habitación (en columnas separadas)
        ctk.CTkLabel(
            form_frame, 
            text="Huésped:", 
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")

        self.reserva_huesped = ctk.CTkComboBox(
            form_frame,
            values=self.obtener_huespedes_combobox(),
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.reserva_huesped.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")

        ctk.CTkLabel(
            form_frame, 
            text="Tipo de Habitación:", 
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")

        self.habitacion_tipo = ctk.CTkComboBox(
            form_frame,
            values=["Penthouse", "Grande", "Mediana", "Pequeña"],
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.habitacion_tipo.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        # Fecha Entrada y Fecha Salida (campos solo para mostrar la fecha seleccionada)
        ctk.CTkLabel(
            form_frame, 
            text="Fecha Entrada:", 
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=10, pady=(10,0), sticky="w")

        self.fecha_entrada_entry = ctk.CTkEntry(
            form_frame,
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.fecha_entrada_entry.grid(row=3, column=0, padx=10, pady=(5,10), sticky="ew")

        ctk.CTkLabel(
            form_frame, 
            text="Fecha Salida:", 
            font=("Arial", 14)
        ).grid(row=2, column=1, padx=10, pady=(10,0), sticky="w")

        self.fecha_salida_entry = ctk.CTkEntry(
            form_frame,
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.fecha_salida_entry.grid(row=3, column=1, padx=10, pady=(5,10), sticky="ew")

        # Crear un frame contenedor para centrar el botón
        boton_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        boton_frame.grid(row=4, column=0, columnspan=2, pady=(5,10), sticky="ew")

        # Configurar las columnas para centrar el contenido del frame
        boton_frame.columnconfigure(0, weight=1)
        boton_frame.columnconfigure(1, weight=1)
        boton_frame.columnconfigure(2, weight=1)

        # Botón más corto y centrado en la columna 1 del frame
        ctk.CTkButton(
            boton_frame,
            text="Seleccionar Fechas",
            command=self.abrir_calendario,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 14),
            corner_radius=10,
            width=200  # Ajusta este valor a lo que prefieras
        ).grid(row=0, column=1)

        # Selector de estrategia de precio (Strategy)
        ctk.CTkLabel(
            form_frame, 
            text="Tipo de Precio:", 
            font=("Arial", 14)
        ).grid(row=5, column=0, padx=10, pady=(10,0), sticky="w")

        self.tipo_precio = ctk.CTkComboBox(
            form_frame,
            values=["Normal", "Con Descuento", "Con IVA"],
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.tipo_precio.set("Normal")
        self.tipo_precio.grid(row=6, column=0, padx=10, pady=(5,10), sticky="ew")

        # Configurar columnas del formulario
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Botones
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#25253a", corner_radius=15)
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="📄 Crear Reserva",
            command=self.crear_reserva,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📝 Modificar Reserva",
            command=self.modificar_reserva,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=180,
            corner_radius=15
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🗑 Eliminar Reserva",
            command=self.eliminar_reserva,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        # Tabla de reservas
        columns = ["ID", "Huésped", "Numero", "Tipo", "Precio", "Entrada", "Salida", "Estado"]
        self.reserva_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.reserva_tree.heading(col, text=col)
            if col == "ID":
                self.reserva_tree.column(col, width=15)  # ID más estrecho
            else:
                self.reserva_tree.column(col, width=100)

        self.reserva_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Configurar las columnas del main_frame para que la tabla se expanda
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Llamar al método para actualizar la lista de reservas
        self.actualizar_lista_reservas()

    def abrir_calendario(self):
        ventana_calendario = ctk.CTkToplevel()
        ventana_calendario.title("Seleccionar Fechas")
        ventana_calendario.geometry("750x350")  # Ajusta el tamaño de la ventana

        ctk.CTkLabel(ventana_calendario, text="Fecha Entrada:").grid(row=0, column=0, padx=10, pady=10)
        calendario_entrada = Calendar(
            ventana_calendario,
            date_pattern="yyyy-mm-dd",
            font=("Arial", 14),  # Aumenta el tamaño de la fuente para mejor visibilidad
            selectmode="day"
        )
        calendario_entrada.grid(row=1, column=0, padx=10, pady=5)

        ctk.CTkLabel(ventana_calendario, text="Fecha Salida:").grid(row=0, column=1, padx=10, pady=10)
        calendario_salida = Calendar(
            ventana_calendario,
            date_pattern="yyyy-mm-dd",
            font=("Arial", 14),  # Aumenta el tamaño de la fuente para mejor visibilidad
            selectmode="day"
        )
        calendario_salida.grid(row=1, column=1, padx=10, pady=5)

        def confirmar_fechas():
            fecha_entrada = calendario_entrada.get_date()
            fecha_salida = calendario_salida.get_date()
            self.fecha_entrada_entry.delete(0, tk.END)
            self.fecha_entrada_entry.insert(0, fecha_entrada)
            self.fecha_salida_entry.delete(0, tk.END)
            self.fecha_salida_entry.insert(0, fecha_salida)
            ventana_calendario.destroy()

        ctk.CTkButton(ventana_calendario, text="Confirmar", command=confirmar_fechas).grid(row=2, column=0, columnspan=2, pady=10)


    
    # Función que obtiene los huéspedes para el combobox, asegurándonos de que devuelvan tanto el nombre como el rut
    def obtener_huespedes_combobox(self):
        huespedes = self.db.query(Huesped).all()  # Obtener todos los huéspedes de la base de datos
        return [f"{huesped.nombre} ({huesped.rut})" for huesped in huespedes]  # Formato: Nombre (Rut)

    def obtener_habitaciones_disponibles_combobox(self):
        habitaciones = self.db.query(Habitacion).filter(Habitacion.disponible == True).all()
        return [f"{h.numero} - {h.tipo}" for h in habitaciones]

    def actualizar_lista_reservas(self):
        try:
            if not hasattr(self, 'reserva_tree') or not self.reserva_tree.winfo_exists():
                print("El TreeView no está disponible o ha sido destruido.")
                return
        except Exception as e:
            print(f"Error al acceder al TreeView: {e}")
            return

        for item in self.reserva_tree.get_children():
            self.reserva_tree.delete(item)

        reservas = reservas = self.hotel_facade.obtener_todas_reservas()
        if not reservas:
            print("No hay reservas activas.")

        for res in reservas:
            self.reserva_tree.insert("", "end", values=(
                res.id,
                res.huesped.nombre if res.huesped else "",
                res.habitacion.numero if res.habitacion else "",
                res.habitacion.tipo if res.habitacion else "",
                f"${res.precio_final:.2f}" if res.precio_final else "",
                res.fecha_entrada.strftime("%Y-%m-%d"),
                res.fecha_salida.strftime("%Y-%m-%d"),
                res.estado
            ))


    # Método para crear reserva
    def crear_reserva(self):
        try:
            huesped_info = self.reserva_huesped.get()
            huesped_rut = huesped_info.split("(")[-1].rstrip(")")
            huesped = self.hotel_facade.obtener_huesped_por_rut(huesped_rut)
            if not huesped:
                raise ValueError(f"El huésped con rut {huesped_rut} no existe")

            fecha_entrada = datetime.strptime(self.fecha_entrada_entry.get(), "%Y-%m-%d")
            fecha_salida = datetime.strptime(self.fecha_salida_entry.get(), "%Y-%m-%d")
            if fecha_entrada >= fecha_salida:
                raise ValueError("La fecha de salida debe ser posterior a la fecha de entrada")

            habitacion_tipo = self.habitacion_tipo.get()
            habitaciones_disponibles = self.db.query(Habitacion).filter(
                Habitacion.tipo == habitacion_tipo,
                Habitacion.disponible == True
            ).first()
            if not habitaciones_disponibles:
                habitaciones_disponibles = self.db.query(Habitacion).filter(
                    Habitacion.disponible == True
                ).first()
            if not habitaciones_disponibles:
                raise ValueError("No hay habitaciones disponibles en este momento")

            tipo = self.tipo_precio.get()
            estrategia = PrecioStrategyFactory.obtener_estrategia(tipo)
            calculadora = CalculadoraPrecio(estrategia)

            precio_final = calculadora.calcular(habitaciones_disponibles.precio)
            messagebox.showinfo("Precio final", f"Precio final de la habitación: ${precio_final:.2f}")


            builder = HotelBuilder()
            reserva_data = builder.set_reserva(
                huesped=huesped,
                habitacion=habitaciones_disponibles,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida,
                precio_final=precio_final
            ).set_estado("Confirmada").get_result()

            reserva_obj = reserva_data["reserva"]
            self.hotel_facade.guardar_reserva(reserva_obj)


            messagebox.showinfo("Éxito", "Reserva creada correctamente")
            self.actualizar_lista_reservas()
            self.actualizar_lista_habitaciones()

            builder = HotelBuilder()
            reserva_data = builder.set_reserva(
                huesped=huesped,
                habitacion=habitaciones_disponibles,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida,
                precio_final=precio_final
            ).set_estado("Confirmada").get_result()
            
            reserva_obj = reserva_data["reserva"]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la reserva: {str(e)}")
        
    def modificar_reserva(self):
        selected_item = self.reserva_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para modificar")
            return

        reserva_id = int(self.reserva_tree.item(selected_item, "values")[0])

        try:
            # Obtener la reserva actual de la base de datos
            reserva_actual = self.db.query(Reserva).filter(Reserva.id == reserva_id).first()
            if not reserva_actual:
                raise ValueError("Reserva no encontrada")

            # Obtener datos nuevos del formulario
            huesped_info = self.reserva_huesped.get()
            huesped_rut = huesped_info.split("(")[-1].rstrip(")")
            huesped = self.hotel_facade.obtener_huesped_por_rut(huesped_rut)
            if not huesped:
                raise ValueError(f"Huésped con RUT {huesped_rut} no existe")

            fecha_entrada = datetime.strptime(self.fecha_entrada_entry.get(), "%Y-%m-%d")
            fecha_salida = datetime.strptime(self.fecha_salida_entry.get(), "%Y-%m-%d")
            if fecha_entrada >= fecha_salida:
                raise ValueError("La fecha de salida debe ser posterior a la de entrada")

            habitacion_tipo = self.habitacion_tipo.get()
            habitacion_nueva = self.db.query(Habitacion).filter(Habitacion.tipo == habitacion_tipo).first()
            if not habitacion_nueva:
                raise ValueError("No se encontró la habitación del tipo seleccionado")

            tipo_precio = self.tipo_precio.get() if hasattr(self, "tipo_precio") else None

            # === Cálculo de precio usando Strategy, siempre desde el precio base de la habitación ===
            estrategia_precio = PrecioStrategyFactory.obtener_estrategia(tipo_precio)
            precio_calculado = estrategia_precio.calcular_precio(habitacion_nueva.precio)

            # Armar los campos a actualizar solo si cambiaron
            campos_a_actualizar = {}

            if huesped.id != reserva_actual.huesped_id:
                campos_a_actualizar["huesped_id"] = huesped.id

            if habitacion_nueva and habitacion_nueva.id != reserva_actual.habitacion_id:
                if not habitacion_nueva.disponible:
                    raise ValueError("No hay habitaciones disponibles para ese tipo")
                campos_a_actualizar["habitacion_id"] = habitacion_nueva.id

            if fecha_entrada != reserva_actual.fecha_entrada:
                campos_a_actualizar["fecha_entrada"] = fecha_entrada

            if fecha_salida != reserva_actual.fecha_salida:
                campos_a_actualizar["fecha_salida"] = fecha_salida

            # Si cambió el tipo de precio o la habitación, actualiza ambos campos
            if tipo_precio != getattr(reserva_actual, "tipo_precio", None) or habitacion_nueva.id != reserva_actual.habitacion_id:
                campos_a_actualizar["tipo_precio"] = tipo_precio
                campos_a_actualizar["precio_final"] = precio_calculado
            else:
                # Si sólo cambió el precio (por ejemplo, cambio de tarifa base de la habitación)
                if precio_calculado != reserva_actual.precio_final:
                    campos_a_actualizar["precio_final"] = precio_calculado

            if not campos_a_actualizar:
                messagebox.showinfo("Sin cambios", "No se detectaron cambios en la reserva.")
                return

            self.hotel_facade.actualizar_reserva(reserva_id, **campos_a_actualizar)

            messagebox.showinfo("Éxito", "Reserva modificada correctamente")
            self.actualizar_lista_reservas()
            self.actualizar_lista_habitaciones()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar la reserva: {str(e)}")

    
    def eliminar_reserva(self):
        # Obtener la reserva seleccionada en el TreeView
        selected_item = self.reserva_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para eliminar")
            return

        # Obtener el ID de la reserva seleccionada
        reserva_id = self.reserva_tree.item(selected_item, "values")[0]

        # Confirmar eliminación
        confirm = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta reserva?")
        if not confirm:
            return

        try:
            self.hotel_facade.eliminar_reserva(int(reserva_id))
            messagebox.showinfo("Éxito", "Reserva eliminada correctamente")
            if hasattr(self, 'reserva_tree') and self.reserva_tree.winfo_exists():
                self.actualizar_lista_reservas()
            # NUEVO: actualiza también la lista de habitaciones
            if hasattr(self, 'habitacion_tree') and self.habitacion_tree.winfo_exists():
                self.actualizar_lista_habitaciones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la reserva: {str(e)}")

    # ===== MÉTODOS AUXILIARES =====
    def create_form_entry(self, parent, label, row):
        frame = ctk.CTkFrame(parent, height=40)
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        
        ctk.CTkLabel(frame, text=label + ":", width=80).pack(side="left", padx=5)
        entry = ctk.CTkEntry(frame)
        entry.pack(side="right", fill="x", expand=True, padx=5)
        
        return entry

    def actualizar_lista_huespedes(self):
        for item in self.huesped_tree.get_children():
            self.huesped_tree.delete(item)
            
        huespedes = self.db.query(Huesped).all()
        for huesped in huespedes:
            self.huesped_tree.insert("", "end", values=(
                huesped.id,
                huesped.nombre,
                huesped.rut,
                huesped.email or "",
                huesped.telefono or ""
            ))

    def actualizar_lista_habitaciones(self):
        # Verifica que el atributo exista antes de usarlo
        if not hasattr(self, "habitacion_tree") or self.habitacion_tree is None:
            print("habitacion_tree no está definido en esta instancia.")
            return

        for item in self.habitacion_tree.get_children():
            self.habitacion_tree.delete(item)
            
        habitaciones = self.db.query(Habitacion).all()
        for hab in habitaciones:
            self.habitacion_tree.insert("", "end", values=(
                hab.id,
                hab.numero,
                hab.tipo,
                f"${hab.precio:.2f}",
                "Sí" if hab.disponible else "No"
            ))

    def registrar_huesped(self):
        nombre = self.huesped_nombre.get()
        rut = self.huesped_rut.get()
        
        if not nombre or not rut:
            messagebox.showerror("Error", "Nombre y RUT son obligatorios")
            return
            
        try:
            self.hotel_facade.crear_huesped(
                nombre=nombre,
                rut=rut,
                email=self.huesped_email.get() or None,
                telefono=self.huesped_telefono.get() or None
            )
            messagebox.showinfo("Éxito", "Huésped registrado correctamente")
            self.actualizar_lista_huespedes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")

    def buscar_huesped(self):
        rut = self.huesped_rut.get()
        if not rut:
            messagebox.showwarning("Advertencia", "Ingrese un RUT para buscar")
            return

        huesped = self.hotel_facade.obtener_huesped_por_rut(rut)
        if huesped:
            self.huesped_nombre.delete(0, "end")
            self.huesped_nombre.insert(0, huesped.nombre)

            self.huesped_email.delete(0, "end")
            if huesped.email:
                self.huesped_email.insert(0, huesped.email)

            self.huesped_telefono.delete(0, "end")
            if huesped.telefono:
                self.huesped_telefono.insert(0, huesped.telefono)
        else:
            messagebox.showinfo("Información", "No se encontró el huésped")

    def registrar_habitacion(self):
        numero = self.habitacion_numero.get()
        tipo = self.habitacion_tipo.get().strip().capitalize()
        precio = self.habitacion_precio.get()
        
        if not all([numero, tipo, precio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        try:
            precio_str = self.habitacion_precio.get().replace(".", "").replace(",", ".")
            precio = float(precio_str)
            self.hotel_facade.crear_habitacion(
                numero=numero,
                tipo=tipo,
                precio=precio
            )
            messagebox.showinfo("Éxito", "Habitación registrada")
            self.actualizar_lista_habitaciones()
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la habitación: {str(e)}")

    def modificar_habitacion(self):
        # Obtener la habitación seleccionada en el TreeView
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para modificar")
            return

        # Obtener los valores de la habitación seleccionada
        habitacion_id = self.habitacion_tree.item(selected_item, "values")[0]

        # Obtener los nuevos valores del formulario
        numero = self.habitacion_numero.get()
        tipo = self.habitacion_tipo.get()
        precio = self.habitacion_precio.get()
        disponible = messagebox.askyesno("Disponibilidad", "¿Está disponible esta habitación?")

        if not all([numero, tipo, precio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            self.hotel_facade.modificar_habitacion(
                habitacion_id=habitacion_id,
                numero=numero,
                tipo=tipo,
                precio=precio,
                disponible=disponible
            )
            messagebox.showinfo("Éxito", "Habitación modificada correctamente")
            self.actualizar_lista_habitaciones()
        except ValueError:
            messagebox.showerror("Error", "Precio debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar la habitación: {str(e)}")

    def eliminar_habitacion(self):
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para eliminar")
            return

        habitacion_id = self.habitacion_tree.item(selected_item, "values")[0]

        confirmar = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar esta habitación?")
        if not confirmar:
            return

        try:
            self.hotel_facade.eliminar_habitacion(habitacion_id)
            messagebox.showinfo("Éxito", "Habitación eliminada correctamente")
            self.actualizar_lista_habitaciones()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la habitación: {str(e)}")

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()
