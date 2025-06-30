import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from estructura.models_folder.models_hotel import Reserva, Habitacion, Huesped
from estructura.estrategy.hotel_estrategy import PrecioStrategyFactory, CalculadoraPrecio
from estructura.builder.hotel_builder import HotelBuilder

class ReservasVista(ctk.CTkFrame):
    def __init__(self, parent, hotel_facade):
        super().__init__(parent)
        self.facade = hotel_facade
        self.configure(fg_color="#25253a")
        self.inicializar_ui()

    def inicializar_ui(self):
        # Título
        ctk.CTkLabel(
            self,
            text="Gestión de Reservas",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=10)

        # Huésped y Tipo de Habitación
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

        # Fechas
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

        # Botón Calendario
        boton_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        boton_frame.grid(row=4, column=0, columnspan=2, pady=(5,10), sticky="ew")
        boton_frame.columnconfigure(1, weight=1)

        ctk.CTkButton(
            boton_frame,
            text="Seleccionar Fechas",
            command=self.abrir_calendario,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 14),
            corner_radius=10,
            width=200
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

        # Frame para botones
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
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
        self.reserva_tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.reserva_tree.heading(col, text=col)
            if col == "ID":
                self.reserva_tree.column(col, width=50)
            else:
                self.reserva_tree.column(col, width=130)

        self.reserva_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Actualizar lista de reservas
        self.actualizar_lista_reservas()

    def abrir_calendario(self):
        ventana_calendario = ctk.CTkToplevel()
        ventana_calendario.title("Seleccionar Fechas")
        ventana_calendario.geometry("750x350")

        ctk.CTkLabel(
            ventana_calendario, 
            text="Fecha Entrada:"
        ).grid(row=0, column=0, padx=10, pady=10)

        calendario_entrada = Calendar(
            ventana_calendario,
            date_pattern="yyyy-mm-dd",
            font=("Arial", 14),
            selectmode="day"
        )
        calendario_entrada.grid(row=1, column=0, padx=10, pady=5)

        ctk.CTkLabel(
            ventana_calendario, 
            text="Fecha Salida:"
        ).grid(row=0, column=1, padx=10, pady=10)

        calendario_salida = Calendar(
            ventana_calendario,
            date_pattern="yyyy-mm-dd",
            font=("Arial", 14),
            selectmode="day"
        )
        calendario_salida.grid(row=1, column=1, padx=10, pady=5)

        def confirmar_fechas():
            fecha_entrada = calendario_entrada.get_date()
            fecha_salida = calendario_salida.get_date()
            self.fecha_entrada_entry.delete(0, 'end')
            self.fecha_entrada_entry.insert(0, fecha_entrada)
            self.fecha_salida_entry.delete(0, 'end')
            self.fecha_salida_entry.insert(0, fecha_salida)
            ventana_calendario.destroy()

        ctk.CTkButton(
            ventana_calendario, 
            text="Confirmar",
            command=confirmar_fechas,
            fg_color="#f72585",
            hover_color="#fa5c9c"
        ).grid(row=2, column=0, columnspan=2, pady=10)

    def obtener_huespedes_combobox(self):
        huespedes = self.facade.db.query(Huesped).all()
        return [f"{h.nombre} ({h.rut})" for h in huespedes]

    def obtener_habitaciones_disponibles_combobox(self):
        habitaciones = self.facade.db.query(Habitacion).filter(Habitacion.disponible == True).all()
        return [f"{h.numero} - {h.tipo}" for h in habitaciones]

    def crear_reserva(self):
        try:
            # Obtener huésped
            huesped_info = self.reserva_huesped.get()
            huesped_rut = huesped_info.split("(")[-1].rstrip(")")
            huesped = self.facade.obtener_huesped_por_rut(huesped_rut)
            if not huesped:
                raise ValueError(f"El huésped con RUT {huesped_rut} no existe")

            # Validar fechas
            fecha_entrada = datetime.strptime(self.fecha_entrada_entry.get(), "%Y-%m-%d")
            fecha_salida = datetime.strptime(self.fecha_salida_entry.get(), "%Y-%m-%d")
            if fecha_entrada >= fecha_salida:
                raise ValueError("La fecha de salida debe ser posterior a la fecha de entrada")

            # Buscar habitación disponible
            habitacion_tipo = self.habitacion_tipo.get()
            habitacion = self.facade.db.query(Habitacion).filter(
                Habitacion.tipo == habitacion_tipo,
                Habitacion.disponible == True
            ).first()
            
            if not habitacion:
                habitacion = self.facade.db.query(Habitacion).filter(
                    Habitacion.disponible == True
                ).first()
            
            if not habitacion:
                raise ValueError("No hay habitaciones disponibles")

            # Calcular precio usando Strategy
            tipo = self.tipo_precio.get()
            estrategia = PrecioStrategyFactory.obtener_estrategia(tipo)
            calculadora = CalculadoraPrecio(estrategia)
            precio_final = calculadora.calcular(habitacion.precio)

            # Mostrar precio final
            if messagebox.askyesno("Confirmar Precio", 
                                 f"Precio final de la habitación: ${precio_final:.2f}\n\n¿Desea continuar?"):
                
                # Usar Builder para crear la reserva
                builder = HotelBuilder()
                reserva_data = builder.set_reserva(
                    huesped=huesped,
                    habitacion=habitacion,
                    fecha_entrada=fecha_entrada,
                    fecha_salida=fecha_salida,
                    precio_final=precio_final
                ).set_estado("Confirmada").get_result()

                # Guardar la reserva
                reserva_obj = reserva_data["reserva"]
                self.facade.guardar_reserva(reserva_obj)

                messagebox.showinfo("Éxito", "Reserva creada correctamente")
                self.actualizar_lista_reservas()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la reserva: {str(e)}")

    def modificar_reserva(self):
        selected_item = self.reserva_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para modificar")
            return

        reserva_id = int(self.reserva_tree.item(selected_item[0])['values'][0])

        try:
            # Obtener reserva actual
            reserva = self.facade.db.query(Reserva).get(reserva_id)
            if not reserva:
                raise ValueError("Reserva no encontrada")

            # Obtener nuevos datos
            huesped_info = self.reserva_huesped.get()
            huesped_rut = huesped_info.split("(")[-1].rstrip(")")
            huesped = self.facade.obtener_huesped_por_rut(huesped_rut)
            
            fecha_entrada = datetime.strptime(self.fecha_entrada_entry.get(), "%Y-%m-%d")
            fecha_salida = datetime.strptime(self.fecha_salida_entry.get(), "%Y-%m-%d")
            
            habitacion_tipo = self.habitacion_tipo.get()
            nueva_habitacion = self.facade.db.query(Habitacion).filter(
                Habitacion.tipo == habitacion_tipo
            ).first()

            tipo_precio = self.tipo_precio.get()
            
            # Calcular nuevo precio
            estrategia = PrecioStrategyFactory.obtener_estrategia(tipo_precio)
            calculadora = CalculadoraPrecio(estrategia)
            nuevo_precio = calculadora.calcular(nueva_habitacion.precio)

            # Confirmar modificación
            if messagebox.askyesno("Confirmar Modificación", 
                                 f"Nuevo precio: ${nuevo_precio:.2f}\n\n¿Desea continuar?"):
                
                # Actualizar reserva
                self.facade.actualizar_reserva(
                    reserva_id,
                    huesped_id=huesped.id,
                    habitacion_id=nueva_habitacion.id,
                    fecha_entrada=fecha_entrada,
                    fecha_salida=fecha_salida,
                    tipo_precio=tipo_precio,
                    precio_final=nuevo_precio
                )

                messagebox.showinfo("Éxito", "Reserva modificada correctamente")
                self.actualizar_lista_reservas()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar la reserva: {str(e)}")

    def eliminar_reserva(self):
        selected_item = self.reserva_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una reserva para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta reserva?"):
            reserva_id = int(self.reserva_tree.item(selected_item[0])['values'][0])
            try:
                self.facade.eliminar_reserva(reserva_id)
                messagebox.showinfo("Éxito", "Reserva eliminada correctamente")
                self.actualizar_lista_reservas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la reserva: {str(e)}")

    def actualizar_lista_reservas(self):
        for item in self.reserva_tree.get_children():
            self.reserva_tree.delete(item)
            
        reservas = self.facade.obtener_todas_reservas()
        
        for res in reservas:
            self.reserva_tree.insert('', 'end', values=(
                res.id,
                res.huesped.nombre if res.huesped else "",
                res.habitacion.numero if res.habitacion else "",
                res.habitacion.tipo if res.habitacion else "",
                f"${res.precio_final:.2f}" if res.precio_final else "",
                res.fecha_entrada.strftime("%Y-%m-%d"),
                res.fecha_salida.strftime("%Y-%m-%d"),
                res.estado
            ))