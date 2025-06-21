import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from Disco.disco_database import get_db, engine, Base
from models_folder.models_disco import Trago, PedidoTrago, Evento, ClienteDiscoteca, Entrada, Mesa, ReservaMesa
from crud.evento_crud import EventoCRUD
from crud.cliente_disco_crud import ClienteDiscotecaCRUD
from tkcalendar import Calendar, DateEntry
import tkinter as tk
from fpdf import FPDF
from crud.trago_crud import TragoCRUD
from facade.discofacade import DiscotecaFacade
from builder.pedido_builder import PedidoBuilder
import re
from datetime import datetime


# ====== VALIDADORES ======
def validar_rut(rut: str, dv: str) -> bool:
    rut = rut.replace(".", "").replace("-", "")
    if not rut.isdigit():
        return False
    if not dv or len(dv) != 1:
        return False
    dv = dv.upper()
    suma = 0
    multiplo = 2
    for c in reversed(rut):
        suma += int(c) * multiplo
        multiplo = multiplo + 1 if multiplo < 7 else 2
    dv_esperado = 11 - (suma % 11)
    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)
    return dv == dv_esperado

def validar_telefono(telefono: str) -> bool:
    return len(telefono) == 9 and telefono.startswith("9") and telefono.isdigit()

def validar_email(email: str) -> bool:
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(patron, email))

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DiscotecaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Discoteca")
        self.geometry("950x600")
        self.configure(fg_color="#1e1e2d")
        self.db: Session = next(get_db())
        self.facade = DiscotecaFacade(self.db)
    
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
            background=[('selected', '#7209b7')],     # Color morado cuando se selecciona
            foreground=[('selected', 'white')]        # Color del texto cuando se selecciona
        )

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Frame para el título DISCO MANAGER
        self.title_frame = ctk.CTkFrame(
            self,
            fg_color="#1e1e2d",
            corner_radius=0
        )
        self.title_frame.grid(row=0, column=0, pady="65", sticky="ew"
        )

        # Título DISCO MANAGER
        ctk.CTkLabel(
            self.title_frame,
            text="DISCO",
            font=("Arial", 27, "bold"),
            text_color="#7209b7"
        ).pack(pady=0, padx=(20,0), anchor="w")

        ctk.CTkLabel(
            self.title_frame,
            text="MANAGER",
            font=("Arial", 23),
            text_color="#9d4dc7"
        ).pack(pady=0, padx=(20,0), anchor="w")

        # Frame secundario(lateral): Entrada, Clientes y Tragos
        self.menu_frame = ctk.CTkFrame(
            self,
            fg_color="#25253a", 
            corner_radius=15
        )
        self.menu_frame.grid(row=1, column=0, sticky="ns", padx=20, pady=20
        )
        
        # Frame principal: Gestión de Eventos, Gestión de Clientes y Gestión de Tragos
        self.main_frame = ctk.CTkFrame(
            self, 
            fg_color="#25253a", 
            corner_radius=15
        )
        self.main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=20, pady=20)

        # Configurar el peso de las columnas y filas
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

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
            fg_color="#25253a",     
            hover_color="#9d4dc7",  
            font=("Arial", 20),     
            corner_radius=0,       
            width=200,              
            height=50,
            anchor="w"  # Alinear el texto a la izquierda
        )
        btn.pack(side="top", pady=10, padx=(20,0))  # Añadir padding izquierdo
        
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
            border_width=1  # Ancho del borde
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
        form_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#1e1e2d", 
            corner_radius=15
        )
        form_frame.pack(fill="x", padx=30, pady=20)

        # Campo Nombre
        ctk.CTkLabel(
            form_frame, 
            text="Nombre:", 
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(5,0), sticky="w")

        self.evento_nombre = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.evento_nombre.grid(row=1, column=0, columnspan=2, padx=10, sticky="ew")

        # Campo Descripción
        ctk.CTkLabel(
            form_frame, 
            text="Descripción:", 
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=10, pady=(5,0), sticky="w")

        self.evento_descripcion = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.evento_descripcion.grid(row=3, column=0, columnspan=2, padx=10, sticky="ew")

        # Configurar el peso de las columnas
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # Campo Precio Entrada
        ctk.CTkLabel(
            form_frame, 
            text="Precio Entrada:", 
            font=("Arial", 14)
        ).grid(row=4, column=0, padx=10, pady=(5,0), sticky="w")

        self.evento_precio = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.evento_precio.grid(row=5, column=0, padx=10, sticky="ew")

        # Campo Aforo Máximo (a la derecha de Precio Entrada)
        ctk.CTkLabel(
            form_frame, 
            text="Aforo Máximo:", 
            font=("Arial", 14)
        ).grid(row=4, column=1, padx=10, pady=(5,0), sticky="w")

        self.evento_aforo = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.evento_aforo.grid(row=5, column=1, padx=10, sticky="ew")

        # ===== NUEVO SISTEMA DE FECHA Y HORA =====
        # Fecha del Evento
        ctk.CTkLabel(
            form_frame, 
            text="Fecha del Evento:", 
            font=("Arial", 14)
        ).grid(row=6, column=0, padx=10, pady=(10,0), sticky="w")

        self.fecha_evento_entry = ctk.CTkEntry(
            form_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1,
            placeholder_text="Seleccione fecha y hora"
        )
        self.fecha_evento_entry.grid(row=7, column=0, padx=10, pady=(5,10), sticky="ew")

        # Crear un frame contenedor para centrar el botón
        boton_fecha_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        boton_fecha_frame.grid(row=7, column=1, pady=(5,10), padx=10, sticky="ew")

        # Configurar las columnas para centrar el contenido del frame
        boton_fecha_frame.columnconfigure(0, weight=1)
        boton_fecha_frame.columnconfigure(1, weight=1)
        boton_fecha_frame.columnconfigure(2, weight=1)

        # Botón para seleccionar fecha y hora
        ctk.CTkButton(
            boton_fecha_frame,
            text="📅 Seleccionar Fecha y Hora",
            command=self.abrir_calendario_evento,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 14),
            corner_radius=10,
            width=200
        ).grid(row=0, column=1)

        # Frame para botones
        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=10)

        # Botón para registrar evento
        ctk.CTkButton(
            button_frame,
            text="📄 Registrar Evento",
            command=self.registrar_evento,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 14),
            corner_radius=15,
            height=40,
            width=150
        ).pack(side="left", padx=5)

        # Botón para editar evento
        ctk.CTkButton(
            button_frame,
            text="🖊 Editar Evento",
            command=self.editar_evento,  # Aquí se vincula el método editar_evento
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 14),
            corner_radius=15,
            height=40,
            width=150
        ).pack(side="left", padx=5)

        # Botón para eliminar evento
        ctk.CTkButton(
            button_frame,
            text="🗑 Eliminar Evento",
            command=self.eliminar_evento,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 14),
            corner_radius=15,
            height=40,
            width=150
        ).pack(side="left", padx=5)

        # Tabla de eventos
        self.evento_tree = self.create_treeview(["ID", "Nombre", "Fecha", "Precio", "Aforo"])
        self.evento_tree.bind("<<TreeviewSelect>>", self.cargar_evento_seleccionado)
        self.actualizar_lista_eventos()

    def abrir_calendario_evento(self):
        """Abre una ventana para seleccionar fecha y hora del evento"""
        ventana_calendario = ctk.CTkToplevel()
        ventana_calendario.title("Seleccionar Fecha y Hora del Evento")
        ventana_calendario.geometry("500x500")
        ventana_calendario.configure(fg_color="#1e1e2d")
        
        # Hacer que la ventana sea modal
        ventana_calendario.grab_set()
        ventana_calendario.focus()

        # Título
        ctk.CTkLabel(
            ventana_calendario, 
            text="Seleccione la fecha y hora del evento",
            font=("Arial", 16, "bold"),
            text_color="#7209b7"
        ).pack(pady=10)

        # Frame para el calendario
        calendario_frame = ctk.CTkFrame(ventana_calendario, fg_color="#25253a")
        calendario_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Calendario
        ctk.CTkLabel(
            calendario_frame, 
            text="Fecha:",
            font=("Arial", 14)
        ).pack(pady=(10,5))
        
        calendario_evento = Calendar(
            calendario_frame,
            date_pattern="yyyy-mm-dd",
            font=("Arial", 12),
            selectmode="day",
            background="#7209b7",
            foreground="white",
            selectbackground="#9d4dc7",
            selectforeground="white",
            mindate=datetime.now().date()
        )
        calendario_evento.pack(pady=5)

        # Frame para hora
        hora_frame = ctk.CTkFrame(calendario_frame, fg_color="#1e1e2d")
        hora_frame.pack(pady=20)

        ctk.CTkLabel(
            hora_frame, 
            text="Hora:",
            font=("Arial", 14)
        ).pack()

        # Frame interno para los spinboxes
        spinbox_frame = ctk.CTkFrame(hora_frame, fg_color="transparent")
        spinbox_frame.pack(pady=10)

        # Spinbox para horas
        hora_spinbox = ttk.Spinbox(
            spinbox_frame, 
            from_=0, 
            to=23, 
            width=3, 
            format="%02.0f",
            font=("Arial", 12)
        )
        hora_spinbox.pack(side="left", padx=5)
        hora_spinbox.set("20")

        ctk.CTkLabel(
            spinbox_frame, 
            text=":",
            font=("Arial", 14)
        ).pack(side="left")

        # Spinbox para minutos
        minuto_spinbox = ttk.Spinbox(
            spinbox_frame, 
            from_=0, 
            to=59, 
            width=3, 
            format="%02.0f",
            font=("Arial", 12)
        )
        minuto_spinbox.pack(side="left", padx=5)
        minuto_spinbox.set("00")

        # Frame para botones
        botones_frame = ctk.CTkFrame(ventana_calendario, fg_color="transparent")
        botones_frame.pack(pady=20)

        def confirmar_fecha_hora():
            try:
                fecha_str = calendario_evento.get_date()
                hora = int(hora_spinbox.get())
                minuto = int(minuto_spinbox.get())
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                fecha_hora_evento = datetime(
                    year=fecha.year,
                    month=fecha.month,
                    day=fecha.day,
                    hour=hora,
                    minute=minuto
                )
                # Validar fecha y hora futura
                if fecha_hora_evento < datetime.now():
                    messagebox.showerror("Error", "No puedes seleccionar una fecha y hora anterior a la actual.")
                    return
                
                # Actualizar el entry con la fecha y hora seleccionada
                fecha_formateada = fecha_hora_evento.strftime("%Y-%m-%d %H:%M")
                self.fecha_evento_entry.delete(0, "end")
                self.fecha_evento_entry.insert(0, fecha_formateada)
                
                # Guardar la fecha_hora para uso posterior
                self.fecha_hora_seleccionada = fecha_hora_evento
                
                ventana_calendario.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al seleccionar fecha y hora: {str(e)}")

        def cancelar():
            ventana_calendario.destroy()

        # Botón Confirmar
        ctk.CTkButton(
            botones_frame,
            text="✅ Confirmar",
            command=confirmar_fecha_hora,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 14),
            width=120
        ).pack(side="left", padx=10)

        # Botón Cancelar
        ctk.CTkButton(
            botones_frame,
            text="❌ Cancelar",
            command=cancelar,
            fg_color="#666666",
            hover_color="#777777",
            font=("Arial", 14),
            width=120
        ).pack(side="left", padx=10)

    def registrar_evento(self):
        try:
            # Verificar que se haya seleccionado una fecha y hora
            if not hasattr(self, 'fecha_hora_seleccionada') or not self.fecha_hora_seleccionada:
                messagebox.showerror("Error", "Por favor seleccione una fecha y hora para el evento")
                return
            
            evento_data = {
                "nombre": self.evento_nombre.get(),
                "descripcion": self.evento_descripcion.get(),
                "fecha": self.fecha_hora_seleccionada,
                "precio_entrada": float(self.evento_precio.get()),
                "aforo_maximo": int(self.evento_aforo.get())
            }
            
            self.facade.registrar_evento(evento_data)
            messagebox.showinfo("Éxito", "Evento registrado")
            self.actualizar_lista_eventos()
            
            # Limpiar campos
            self.evento_nombre.delete(0, "end")
            self.evento_descripcion.delete(0, "end")
            self.evento_precio.delete(0, "end")
            self.evento_aforo.delete(0, "end")
            self.fecha_evento_entry.delete(0, "end")
            self.fecha_hora_seleccionada = None
            
        except ValueError as ve:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para precio y aforo")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cargar_evento_seleccionado(self, event):
        selected_item = self.evento_tree.selection()
        if not selected_item:
            return
        
        evento_id = self.evento_tree.item(selected_item[0], "values")[0]
        evento = EventoCRUD.obtener_por_id(self.db, evento_id)
        
        if evento:
            # Limpiar campos
            self.evento_nombre.delete(0, "end")
            self.evento_descripcion.delete(0, "end")
            self.evento_precio.delete(0, "end")
            self.evento_aforo.delete(0, "end")
            self.fecha_evento_entry.delete(0, "end")
            
            # Llenar campos con datos del evento
            self.evento_nombre.insert(0, evento.nombre)
            self.evento_descripcion.insert(0, evento.descripcion or "")
            self.evento_precio.insert(0, str(evento.precio_entrada))
            self.evento_aforo.insert(0, str(evento.aforo_maximo))
            
            # Formatear y mostrar fecha y hora
            fecha_formateada = evento.fecha.strftime("%Y-%m-%d %H:%M")
            self.fecha_evento_entry.insert(0, fecha_formateada)
            
            # Guardar la fecha_hora para edición
            self.fecha_hora_seleccionada = evento.fecha

    def editar_evento(self):
        selected_item = self.evento_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un evento para editar")
            return
        
        try:
            evento_id = self.evento_tree.item(selected_item[0], "values")[0]
            
            # Verificar que se haya seleccionado una fecha y hora
            if not hasattr(self, 'fecha_hora_seleccionada') or not self.fecha_hora_seleccionada:
                messagebox.showerror("Error", "Por favor seleccione una fecha y hora para el evento")
                return
            
            nuevos_datos = {
                "nombre": self.evento_nombre.get(),
                "descripcion": self.evento_descripcion.get(),
                "fecha": self.fecha_hora_seleccionada,
                "precio_entrada": float(self.evento_precio.get()),
                "aforo_maximo": int(self.evento_aforo.get())
            }
            
            if self.facade.actualizar_evento(evento_id, nuevos_datos):
                messagebox.showinfo("Éxito", "Evento actualizado correctamente")
                self.actualizar_lista_eventos()
                
                # Limpiar campos después de editar
                self.evento_nombre.delete(0, "end")
                self.evento_descripcion.delete(0, "end")
                self.evento_precio.delete(0, "end")
                self.evento_aforo.delete(0, "end")
                self.fecha_evento_entry.delete(0, "end")
                self.fecha_hora_seleccionada = None
            else:
                messagebox.showerror("Error", "No se pudo actualizar el evento")
                
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para precio y aforo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar evento: {str(e)}")

    def eliminar_evento(self):
        selected_item = self.evento_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un evento para eliminar")
            return
        
        evento_id = self.evento_tree.item(selected_item[0], "values")[0]
        
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este evento? Esta acción no se puede deshacer."
        )
        
        if confirmacion:
            try:
                if self.facade.eliminar_evento(evento_id):
                    messagebox.showinfo("Éxito", "Evento eliminado correctamente")
                    self.actualizar_lista_eventos()
                    # Limpiar campos después de eliminar
                    self.evento_nombre.delete(0, "end")
                    self.evento_descripcion.delete(0, "end")
                    self.evento_precio.delete(0, "end")
                    self.evento_aforo.delete(0, "end")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el evento")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el evento: {str(e)}")

    def actualizar_lista_eventos(self):
        self.evento_tree.delete(*self.evento_tree.get_children())
        for e in self.facade.listar_eventos():
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
        form_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="#1e1e2d", 
            corner_radius=15)
        form_frame.pack(fill="x", padx=20, pady=10)

        # Campos del formulario organizados con grid()
        # Entry del Nombre
        ctk.CTkLabel(
            form_frame, 
            text="Nombre:", 
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.cliente_nombre = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.cliente_nombre.grid(row=1, column=0, padx=10, sticky="ew")
        # Entry del RUT (solo números)
        ctk.CTkLabel(
            form_frame, 
            text="RUT:", 
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")

        self.cliente_rut = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1,
            width=120
        )
        self.cliente_rut.grid(row=1, column=1, padx=(10,0), sticky="ew")

        # Caja dígito verificador
        ctk.CTkLabel(
            form_frame,
            text="-",
            font=("Arial", 14)
        ).grid(row=1, column=2, padx=(0, 0))
        self.cliente_rut_dv = ctk.CTkEntry(
            form_frame,
            width=25,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.cliente_rut_dv.grid(row=1, column=3, padx=(0,10))
        
        # Entry del Email
        ctk.CTkLabel(
            form_frame, 
            text="Email:", 
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=10, pady=(5,0), sticky="w")
        
        self.cliente_email = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.cliente_email.grid(row=3, column=0, padx=10, pady=(0,10), sticky="ew")
        
        # Entry del Teléfono
        ctk.CTkLabel(
            form_frame, 
            text="Teléfono:", 
            font=("Arial", 14)
        ).grid(row=2, column=1, padx=10, pady=(5,0), sticky="w")
        
        self.cliente_telefono = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.cliente_telefono.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="ew")

        # Configurar las columnas para que las entradas se expandan
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Frame para botones
        button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        button_frame.pack(pady=10)

        # Botón para registrar cliente
        ctk.CTkButton(
            button_frame,
            text="📄 Registrar Cliente",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            command=self.registrar_cliente,
            corner_radius=15,
            font=("Arial", 14),
            height=40,
            width=150
        ).pack(side="left", padx=5)

        # Botón para editar cliente
        ctk.CTkButton(
            button_frame,
            text="🖊 Editar Cliente",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            command=self.editar_cliente,
            corner_radius=15,
            font=("Arial", 14),
            height=40,
            width=150
        ).pack(side="left", padx=5)
        
        # Botón para eliminar cliente 
        ctk.CTkButton(
            button_frame,
            text="🗑 Eliminar Cliente",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            command=self.eliminar_cliente,
            corner_radius=15,
            font=("Arial", 14),
            height=40,
            width=150
        ).pack(side="left", padx=5)

        # Tabla de clientes
        self.cliente_tree = self.create_treeview(["ID", "Nombre", "RUT", "Email", "Teléfono"])
        self.cliente_tree.bind("<<TreeviewSelect>>", self.on_cliente_select)
        self.actualizar_lista_clientes()
    
    def on_cliente_select(self, event):
        selected_items = self.cliente_tree.selection()
        if selected_items:
            item = self.cliente_tree.item(selected_items[0])
            values = item["values"]

            self.cliente_nombre.delete(0, "end")
            self.cliente_nombre.insert(0, values[1])

            # SEPARA RUT Y DV DE FORMA ROBUSTA
            self.cliente_rut.delete(0, "end")
            self.cliente_rut_dv.delete(0, "end")
            rut_db = values[2]
            # Elimina puntos y espacios
            rut_db = str(rut_db).replace(".", "").replace(" ", "")
            if "-" in rut_db:
                rut_num, dv = rut_db.split("-")
            elif len(rut_db) > 1:
                rut_num, dv = rut_db[:-1], rut_db[-1]
            else:
                rut_num, dv = "", ""
            self.cliente_rut.insert(0, rut_num)
            self.cliente_rut_dv.insert(0, dv)

            self.cliente_email.delete(0, "end")
            self.cliente_email.insert(0, values[3])

            self.cliente_telefono.delete(0, "end")
            self.cliente_telefono.insert(0, values[4])

    def registrar_cliente(self):
        nombre = self.cliente_nombre.get()
        rut_numero = self.cliente_rut.get().strip()
        dv = self.cliente_rut_dv.get().strip().upper()
        rut = f"{rut_numero}{dv}"
        email = self.cliente_email.get()
        telefono = self.cliente_telefono.get()

        # --- VALIDACIONES ESTRUCTURALES ---
        if not validar_rut(rut_numero, dv):
            messagebox.showerror("Error", "El RUT ingresado no es válido. Debe tener formato chileno y dígito verificador correcto.")
            return
        if not validar_telefono(telefono):
            messagebox.showerror("Error", "El teléfono debe tener 9 dígitos y comenzar con 9.")
            return
        if not validar_email(email):
            messagebox.showerror("Error", "El email ingresado no es válido. Ejemplo: usuario@gmail.com")
            return

        cliente_data = {
            "nombre": nombre,
            "rut": rut,
            "email": email,
            "telefono": telefono
        }
        try:
            self.facade.registrar_cliente(cliente_data)
            messagebox.showinfo("Éxito", "Cliente registrado correctamente")
            self.actualizar_lista_clientes()
            self.cliente_nombre.delete(0, "end")
            self.cliente_rut.delete(0, "end")
            self.cliente_rut_dv.delete(0, "end")
            self.cliente_email.delete(0, "end")
            self.cliente_telefono.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def editar_cliente(self):
        selected_item = self.cliente_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return

        nombre = self.cliente_nombre.get()
        rut_numero = self.cliente_rut.get().strip()
        dv = self.cliente_rut_dv.get().strip().upper()
        rut = f"{rut_numero}{dv}"
        email = self.cliente_email.get()
        telefono = self.cliente_telefono.get()


        # --- VALIDACIONES ESTRUCTURALES ---
        if not validar_rut(rut_numero, dv):
            messagebox.showerror("Error", "El RUT ingresado no es válido. Debe tener formato chileno y dígito verificador correcto.")
            return
        if not validar_telefono(telefono):
            messagebox.showerror("Error", "El teléfono debe tener 9 dígitos y comenzar con 9.")
            return
        if not validar_email(email):
            messagebox.showerror("Error", "El email ingresado no es válido. Ejemplo: usuario@gmail.com")
            return

        try:
            cliente_id = self.cliente_tree.item(selected_item[0], "values")[0]
            nuevos_datos = {
                "nombre": nombre,
                "rut": rut,
                "email": email,
                "telefono": telefono
            }
            self.facade.actualizar_cliente(cliente_id, nuevos_datos)
            messagebox.showinfo("Éxito", "Cliente editado correctamente")
            self.actualizar_lista_clientes()
            self.cliente_nombre.delete(0, "end")
            self.cliente_rut.delete(0, "end")
            self.cliente_rut_dv.delete(0, "end")
            self.cliente_email.delete(0, "end")
            self.cliente_telefono.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_cliente(self):
        # Obtener el cliente seleccionado en el Treeview
        selected_item = self.cliente_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        # Obtener el ID del cliente
        cliente_id = self.cliente_tree.item(selected_item[0], "values")[0]
        
        # Confirmar eliminación
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este cliente? Esta acción no se puede deshacer."
        )
        
        if confirmacion:
            try:
                # Eliminar el cliente usando el CRUD
                if self.facade.eliminar_cliente(cliente_id):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.actualizar_lista_clientes()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {str(e)}")

    def actualizar_lista_clientes(self):
        # Limpia el treeview
        for item in self.cliente_tree.get_children():
            self.cliente_tree.delete(item)
        # Vuelve a cargar los clientes
        for cliente in self.facade.listar_clientes():
            self.cliente_tree.insert("", "end", values=(
                cliente.id, cliente.nombre, cliente.rut, cliente.email, cliente.telefono
            ))

    def create_treeview(self, columns):
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)  # Ajustar el ancho de la columna según sea necesario
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
            tabview = ctk.CTkTabview(
                self.main_frame, 
                fg_color="#1e1e2d", 
                corner_radius=15,
                segmented_button_fg_color="#1e1e2d",        # Color de fondo de los botones
                segmented_button_selected_color="#7209b7",   # Color cuando está seleccionado
                segmented_button_selected_hover_color="#9d4dc7"  # Color hover cuando está seleccionado
            )
            tabview.pack(fill="both", expand=True, padx=20, pady=10)
            
            tabview.add("Registro")
            tabview.add("Pedidos")
            
            # Pestaña de Registro
            self.setup_tragos_registro_tab(tabview.tab("Registro"))
            
            # Pestaña de Pedidos
            self.setup_tragos_pedidos_tab(tabview.tab("Pedidos"))

    def setup_tragos_pedidos_tab(self, tab):
        # --- Frame de cliente y búsqueda ---
        cliente_frame = ctk.CTkFrame(tab, fg_color="#23233a", corner_radius=15)
        cliente_frame.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(cliente_frame, text="Cliente:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.busqueda_cliente = ctk.CTkEntry(cliente_frame, width=160, fg_color="#25253a", border_color="#7209b7", border_width=1)
        self.busqueda_cliente.grid(row=0, column=1, padx=(0,10), pady=10)
        self.busqueda_cliente.bind("<KeyRelease>", self.filtrar_clientes)

        self.lista_clientes = ctk.CTkComboBox(cliente_frame, border_color="#7209b7", fg_color="#25253a", state="readonly", width=220)
        self.lista_clientes.grid(row=0, column=2, padx=10, pady=10)
        self.actualizar_lista_clientes_combo()
        self.lista_clientes.bind("<<ComboboxSelected>>", self.on_cliente_seleccionado)

        self.cliente_seleccionado_label = ctk.CTkLabel(cliente_frame, text="Seleccione un cliente.", font=("Arial", 12))
        self.cliente_seleccionado_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")

        # --- Frame de selección de trago y cantidad ---
        trago_frame = ctk.CTkFrame(tab, fg_color="#23233a", corner_radius=15)
        trago_frame.pack(fill="x", padx=20, pady=(5, 5))

        ctk.CTkLabel(trago_frame, text="Trago:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.busqueda_trago = ctk.CTkEntry(trago_frame, width=160, fg_color="#25253a", border_color="#7209b7", border_width=1)
        self.busqueda_trago.grid(row=0, column=1, padx=(0,10), pady=10)
        self.busqueda_trago.bind("<KeyRelease>", self.filtrar_tragos)

        self.lista_tragos = ctk.CTkComboBox(trago_frame, border_color="#7209b7", fg_color="#25253a", state="readonly", width=220)
        self.lista_tragos.grid(row=0, column=2, padx=10, pady=10)
        self.actualizar_lista_tragos_combo()

        ctk.CTkLabel(trago_frame, text="Cantidad:", font=("Arial", 14)).grid(row=0, column=3, padx=(10,2), pady=10, sticky="w")
        self.trago_cantidad = ctk.CTkEntry(trago_frame, width=50, fg_color="#25253a", border_color="#7209b7", border_width=1)
        self.trago_cantidad.grid(row=0, column=4, padx=(2,10), pady=10)
        self.trago_cantidad.insert(0, "1")

        ctk.CTkButton(trago_frame, text="➕ Agregar", fg_color="#7209b7", hover_color="#9d4dc7",
                    command=self.agregar_trago_pedido, font=("Arial", 13), width=100, height=35).grid(row=0, column=5, padx=(10,0), pady=10)

        # --- Tabla de pedido ---
        pedido_frame = ctk.CTkFrame(tab, fg_color="#23233a", corner_radius=15)
        pedido_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))

        columns = ("Trago", "Cantidad", "Precio Unitario", "Subtotal", "Eliminar")
        self.pedido_tree = ttk.Treeview(pedido_frame, columns=columns, show="headings", height=8)
        self.pedido_tree.bind("<Double-1>", self.on_pedido_tree_double_click)
        for col in columns:
            self.pedido_tree.heading(col, text=col)
            self.pedido_tree.column(col, anchor="center", width=120)
        self.pedido_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Total y Confirmar ---
        total_frame = ctk.CTkFrame(tab, fg_color="transparent")
        total_frame.pack(fill="x", padx=20, pady=(5, 15))

        self.pedido_total = ctk.CTkLabel(total_frame, text="Total: $0.00", font=("Arial", 16, "bold"), text_color="#7209b7")
        self.pedido_total.pack(side="left", padx=(10,20), pady=10)
        
        ctk.CTkButton(
            pedido_frame,
            text="🗑 Eliminar Trago Seleccionado",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 13),
            width=200,
            height=35,
            command=self.eliminar_trago_seleccionado_pedido
        ).pack(pady=(0, 10), padx=10, anchor="e")

        ctk.CTkButton(total_frame, text="✅ Confirmar Pedido", fg_color="#7209b7", hover_color="#9d4dc7",
                    command=self.confirmar_pedido_tragos, font=("Arial", 15), width=180, height=40).pack(side="right", padx=10, pady=10)

        # --- Limpieza de pedido al cambiar de pestaña ---
        self.limpiar_pedido()
    def eliminar_trago_seleccionado_pedido(self):
        selected = self.pedido_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una fila para eliminar")
            return
        for item in selected:
            self.pedido_tree.delete(item)
        self.actualizar_total_pedido()

    def on_pedido_tree_double_click(self, event):
        # Detecta la columna y el item
        region = self.pedido_tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.pedido_tree.identify_column(event.x)
            # Suponiendo que "Eliminar" es la última columna (por ejemplo, "#5" si tienes 5 columnas)
            if col == f"#{len(self.pedido_tree['columns'])}":
                row_id = self.pedido_tree.identify_row(event.y)
                if row_id:
                    self.pedido_tree.delete(row_id)
                    self.actualizar_total_pedido()

    def setup_tragos_registro_tab(self, tab):
        form_frame = ctk.CTkFrame(tab, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Combobox para seleccionar trago existente
        ctk.CTkLabel(
            form_frame, 
            text="Seleccionar Trago:", 
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")

        # Label de Precio (en la misma fila que el label de Seleccionar Trago)
        ctk.CTkLabel(
            form_frame, 
            text="Precio:", 
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")
        
        # Combobox debajo de su label
        self.trago_seleccionado = ctk.CTkComboBox(
            form_frame, 
            border_color="#7209b7", 
            fg_color="#25253a",
            state="readonly",
            border_width=1
        )
        self.trago_seleccionado.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")

        # Entry de precio debajo de su label
        self.trago_precio = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.trago_precio.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        # --- ELIMINADO: Checkbox para disponibilidad ---
        # self.trago_disponible = ctk.CTkCheckBox(...)
        # self.trago_disponible.grid(...)
        
        # Botones
        btn_frame = ctk.CTkFrame(tab, fg_color="#1e1e2d")
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            btn_frame, 
            text="🔄 Actualizar Precio",
            command=self.actualizar_precio_trago,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            corner_radius=15,
            font=("Arial", 14),
            height=40,
            width=150
        ).pack(side="left", padx=5)

        # --- ELIMINADO: Botón de cambiar disponibilidad ---
        # ctk.CTkButton(
        #     btn_frame, 
        #     text="↔ Cambiar Disponibilidad",
        #     command=self.cambiar_disponibilidad_trago,
        #     fg_color="#7209b7",
        #     hover_color="#9d4dc7",
        #     corner_radius=15,
        #     font=("Arial", 14),
        #     height=40,
        #     width=150
        # ).pack(side="left", padx=10)

        ctk.CTkButton(
        btn_frame, 
        text="📦 Actualizar Stock",
        command=self.actualizar_stock_trago,
        fg_color="#7209b7",
        hover_color="#9d4dc7",
        corner_radius=15,
        font=("Arial", 14),
        height=40,
        width=150
        ).pack(side="left", padx=5)

        # Actualizar lista de tragos
        self.actualizar_lista_tragos_combobox()
        self.trago_seleccionado.bind("<<ComboboxSelected>>", self.on_trago_selected)

        # Lista de tragos
        columns = ["ID", "Nombre", "Precio", "Categoría", "Disponible", "Stock"]
        self.trago_tree = ttk.Treeview(tab, columns=columns, show="headings")
        
        # Configurar encabezados
        self.trago_tree.heading("ID", text="ID")
        self.trago_tree.heading("Nombre", text="Nombre")
        self.trago_tree.heading("Precio", text="Precio")
        self.trago_tree.heading("Categoría", text="Categoría")
        self.trago_tree.heading("Disponible", text="Disponible")
        self.trago_tree.heading("Stock", text="Stock")
        
        # Configurar anchos de columna
        self.trago_tree.column("ID", width=50, anchor="center")
        self.trago_tree.column("Nombre", width=150, anchor="w")
        self.trago_tree.column("Precio", width=100, anchor="e")
        self.trago_tree.column("Categoría", width=100, anchor="w")
        self.trago_tree.column("Disponible", width=80, anchor="center")
        self.trago_tree.column("Stock", width=60, anchor="center")
        
        self.actualizar_lista_tragos()
        self.trago_tree.pack(fill="both", expand=True, padx=20, pady=10)

        # Vincular evento para seleccionar trago desde el treeview
        self.trago_tree.bind("<<TreeviewSelect>>", self.on_trago_tree_select)

        ctk.CTkLabel(
        form_frame, 
        text="Stock:",
        font=("Arial", 14)
        ).grid(row=5, column=0, padx=10, pady=(5,0), sticky="w")
    
        self.trago_stock = ctk.CTkEntry(
            form_frame, 
            fg_color="#25253a", 
            border_color="#7209b7", 
            border_width=1
        )
        self.trago_stock.grid(row=5, column=1, padx=10, pady=(5,10), sticky="ew")

    def on_trago_selected(self, event):
        trago_str = self.trago_seleccionado.get()
        if trago_str:
            trago_nombre = trago_str.split(" ($")[0]
            trago = self.facade.obtener_trago_por_nombre(trago_nombre)
            if trago:
                self.trago_precio.delete(0, "end")
                self.trago_precio.insert(0, str(trago.precio))
                self.trago_stock.delete(0, "end")
                self.trago_stock.insert(0, str(trago.stock))
                # --- ELIMINADO: Disponibilidad manual ---
                # self.trago_disponible.select() if trago.disponible else self.trago_disponible.deselect()

    def on_trago_tree_select(self, event):
        selected = self.trago_tree.selection()
        if selected:
            values = self.trago_tree.item(selected[0])["values"]
            trago_nombre = values[1]
            combobox_val = next((v for v in self.trago_seleccionado.cget("values") if v.startswith(trago_nombre)), None)
            if combobox_val:
                self.trago_seleccionado.set(combobox_val)
                self.on_trago_selected(None)

    def actualizar_stock_trago(self):
        try:
            trago_str = self.trago_seleccionado.get()
            nuevo_stock = int(self.trago_stock.get())

            if not trago_str:
                messagebox.showwarning("Advertencia", "Seleccione un trago primero")
                return

            # Validación: Stock no negativo
            if nuevo_stock < 0:
                messagebox.showerror("Error", "El stock no puede ser negativo.")
                return

            trago_nombre = trago_str.split(" ($")[0]
            trago = self.facade.obtener_trago_por_nombre(trago_nombre)

            if trago:
                trago_actualizado = self.facade.actualizar_stock_trago(trago.id, nuevo_stock)
                if trago_actualizado:
                    estado = "disponible" if trago_actualizado.stock > 0 else "no disponible"
                    messagebox.showinfo("Éxito", f"Stock actualizado a {nuevo_stock}, trago ahora {estado}")
                    self.actualizar_lista_tragos()
                    self.actualizar_lista_tragos_combobox()
                    self.actualizar_lista_tragos_combo()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el stock")
            else:
                messagebox.showerror("Error", "Trago no encontrado")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para el stock")

    def actualizar_lista_tragos(self):
        for item in self.trago_tree.get_children():
            self.trago_tree.delete(item)
        
        # Obtener todos los tragos y mostrarlos correctamente
        tragos = self.facade.listar_tragos()
        for trago in tragos:
            # DISPONIBILIDAD SOLO POR STOCK
            disponible = "Sí" if trago.stock > 0 else "No"
            self.trago_tree.insert("", "end", values=(
                trago.id,
                trago.nombre,
                f"${trago.precio:.2f}",
                trago.categoria or "",
                disponible,
                trago.stock  # Mostrar el stock
            ))

    # --- ELIMINADO: cambiar_disponibilidad_trago y referencias a self.trago_disponible ---


    def obtener_tragos_combobox(self):
        tragos = self.facade.listar_tragos()
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
            trago = self.facade.obtener_trago_por_nombre(trago_nombre)
            
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
            cliente_rut = cliente_str.split("(")[-1].rstrip(")")
            cliente = self.facade.obtener_cliente_por_rut(cliente_rut)

            if not cliente:
                messagebox.showerror("Error", "Cliente no encontrado")
                return

            builder = PedidoBuilder().set_cliente(cliente.id)

            for item in items:
                values = self.pedido_tree.item(item, "values")
                trago_nombre = values[0]
                cantidad = int(values[1])

                trago = self.facade.obtener_trago_por_nombre(trago_nombre)
                builder.add_detalle(trago.id, cantidad, trago.precio)

            pedido_data = builder.build()

            pedido = self.facade.crear_pedido(
                pedido_data["cliente_id"],
                pedido_data["total"],
                pedido_data["detalles"]
            )

            self.generar_boleta_tragos(pedido.id)

            messagebox.showinfo("Éxito", f"Pedido #{pedido.id} registrado\nBoleta generada: boleta_pedido_{pedido.id}.pdf")
            self.limpiar_pedido()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar el pedido: {str(e)}")


    def actualizar_lista_tragos_combobox(self):
        tragos = self.facade.listar_tragos()
        valores = [f"{t.nombre} (${t.precio:.2f})" for t in tragos]
        self.trago_seleccionado.configure(values=valores)

    def on_trago_selected(self, event):
        trago_str = self.trago_seleccionado.get()
        if trago_str:
            trago_nombre = trago_str.split(" ($")[0]
            trago = self.facade.obtener_trago_por_nombre(trago_nombre)
            if trago:
                self.trago_precio.delete(0, "end")
                self.trago_precio.insert(0, str(trago.precio))
                self.trago_stock.delete(0, "end")
                self.trago_stock.insert(0, str(trago.stock))
                self.trago_disponible.select() if trago.disponible else self.trago_disponible.deselect()

    def actualizar_precio_trago(self):
        try:
            trago_str = self.trago_seleccionado.get()
            nuevo_precio = float(self.trago_precio.get())
            
            if not trago_str:
                messagebox.showwarning("Advertencia", "Seleccione un trago primero")
                return

            # --- VALIDACIÓN: Precio no negativo ---
            if nuevo_precio < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo.")
                return

            trago_nombre = trago_str.split(" ($")[0]
            trago = self.facade.obtener_trago_por_nombre(trago_nombre)
            
            if trago:
                self.facade.actualizar_precio_trago(trago.id, nuevo_precio)
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
        trago = self.facade.obtener_trago_por_nombre(trago_nombre)
        
        if trago:
            nueva_disponibilidad = self.trago_disponible.get()
            self.facade.cambiar_disponibilidad_trago(trago.id, nueva_disponibilidad)
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
            text="Seleccione un cliente.",
            font=("Arial", 12)
        )

    def actualizar_lista_clientes_combo(self):
        clientes = self.facade.listar_clientes()
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
        tragos = self.facade.listar_tragos()
        valores = [f"{t.nombre} (${t.precio:.2f})" for t in tragos]
        self.lista_tragos.configure(values=valores)

    def filtrar_tragos(self, event):
        busqueda = self.busqueda_trago.get().lower()
        tragos = self.facade.listar_tragos()
        
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