import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from tkcalendar import Calendar
from apps.disco.utils.ui_components import create_form_entry, create_treeview, create_button

class EventosVista:
    def __init__(self, parent, facade):
        self.parent = parent
        self.facade = facade
        self.fecha_hora_seleccionada = None
        
    def show(self):
        self.setup_title()
        self.setup_form()
        self.setup_buttons()
        self.setup_treeview()
        
    def setup_title(self):
        ctk.CTkLabel(
            self.parent,
            text="Gestión de Eventos",
            text_color="#7209b7",
            font=("Arial", 28, "bold")
        ).pack(pady=20)
        
    def setup_form(self):
        self.form_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#1e1e2d",
            corner_radius=15
        )
        self.form_frame.pack(fill="x", padx=30, pady=20)
        
        # Configurar grid
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Campos del formulario
        self.evento_nombre = create_form_entry(self.form_frame, "Nombre", 0, columnspan=2)
        self.evento_descripcion = create_form_entry(self.form_frame, "Descripción", 2, columnspan=2)
        self.evento_precio = create_form_entry(self.form_frame, "Precio Entrada", 4)
        self.evento_aforo = create_form_entry(self.form_frame, "Aforo Máximo", 4, column=1)
        
        # Campo de fecha
        self.setup_fecha_field()
        
    def setup_fecha_field(self):
        ctk.CTkLabel(
            self.form_frame,
            text="Fecha del Evento:",
            font=("Arial", 14)
        ).grid(row=6, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.fecha_evento_entry = ctk.CTkEntry(
            self.form_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1,
            placeholder_text="Seleccione fecha y hora"
        )
        self.fecha_evento_entry.grid(row=7, column=0, padx=10, pady=(5,10), sticky="ew")
        
        boton_fecha_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        boton_fecha_frame.grid(row=7, column=1, pady=(5,10), padx=10, sticky="ew")
        
        ctk.CTkButton(
            boton_fecha_frame,
            text="📅 Seleccionar Fecha y Hora",
            command=self.abrir_calendario_evento,
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            font=("Arial", 14),
            corner_radius=10,
            width=200
        ).pack()

    def setup_buttons(self):
        button_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        button_frame.pack(pady=10)
        
        create_button(
            button_frame,
            "📄 Registrar Evento",
            self.registrar_evento
        ).pack(side="left", padx=5)
        
        create_button(
            button_frame,
            "🖊 Editar Evento",
            self.editar_evento
        ).pack(side="left", padx=5)
        
        create_button(
            button_frame,
            "🗑 Eliminar Evento",
            self.eliminar_evento
        ).pack(side="left", padx=5)

    def setup_treeview(self):
        self.evento_tree = create_treeview(
            self.parent,
            ["ID", "Nombre", "Fecha", "Precio", "Aforo"]
        )
        self.evento_tree.bind("<<TreeviewSelect>>", self.cargar_evento_seleccionado)
        self.actualizar_lista_eventos()

    def abrir_calendario_evento(self):
        ventana_calendario = ctk.CTkToplevel()
        ventana_calendario.title("Seleccionar Fecha y Hora del Evento")
        ventana_calendario.geometry("500x500")
        ventana_calendario.configure(fg_color="#1e1e2d")
        ventana_calendario.grab_set()
        
        # ... [resto del código del calendario, igual que en el original]
        
    def registrar_evento(self):
        try:
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
            self.limpiar_campos()
            
        except ValueError as ve:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos para precio y aforo")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def editar_evento(self):
        selected_item = self.evento_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un evento para editar")
            return
            
        try:
            evento_id = self.evento_tree.item(selected_item[0], "values")[0]
            
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
                self.limpiar_campos()
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
                    self.limpiar_campos()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el evento")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el evento: {str(e)}")

    def cargar_evento_seleccionado(self, event):
        selected_item = self.evento_tree.selection()
        if not selected_item:
            return
            
        evento_id = self.evento_tree.item(selected_item[0], "values")[0]
        evento = self.facade.obtener_evento_por_id(evento_id)
        
        if evento:
            self.limpiar_campos()
            self.evento_nombre.insert(0, evento.nombre)
            self.evento_descripcion.insert(0, evento.descripcion or "")
            self.evento_precio.insert(0, str(evento.precio_entrada))
            self.evento_aforo.insert(0, str(evento.aforo_maximo))
            
            fecha_formateada = evento.fecha.strftime("%Y-%m-%d %H:%M")
            self.fecha_evento_entry.insert(0, fecha_formateada)
            self.fecha_hora_seleccionada = evento.fecha

    def actualizar_lista_eventos(self):
        self.evento_tree.delete(*self.evento_tree.get_children())
        for e in self.facade.listar_eventos():
            self.evento_tree.insert("", "end", values=(
                e.id, e.nombre, e.fecha, e.precio_entrada, e.aforo_maximo
            ))
            
    def limpiar_campos(self):
        self.evento_nombre.delete(0, "end")
        self.evento_descripcion.delete(0, "end")
        self.evento_precio.delete(0, "end")
        self.evento_aforo.delete(0, "end")
        self.fecha_evento_entry.delete(0, "end")
        self.fecha_hora_seleccionada = None

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