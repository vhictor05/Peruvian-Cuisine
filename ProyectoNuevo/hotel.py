import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from sqlalchemy.orm import Session
from hotel_database import get_db, Base, recreate_db
from models import Huesped, Habitacion, Reserva
from crud.huesped_crud import HuespedCRUD
from crud.habitacion_crud import HabitacionCRUD
from crud.reserva_crud import ReservaCRUD
from datetime import datetime, timedelta
from tkcalendar import DateEntry

# recreate_db()  # Recreate the database with the new schema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Hotel")
        self.geometry("1200x700")
        self.db = next(get_db())
        self.configure(fg_color="#25253e", corner_radius=15)
        
        # Menú lateral
        self.menu_frame = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="#1e1e2d")
        self.menu_frame.pack(side="top", fill="x")
        
        # Contenido principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e2d")
        self.main_frame.pack(side="bottom", fill="both", expand=True, padx=30, pady=30)
        
        # Botones del menú
        self.create_menu_button("Huéspedes", self.show_huespedes)
        self.create_menu_button("Habitaciones", self.show_habitaciones)
        self.create_menu_button("Reservas", self.show_reservas)
        
        # Mostrar panel de huéspedes por defecto
        self.show_huespedes()

    def create_menu_button(self, text, command):
        btn = ctk.CTkButton(
            self.menu_frame,
            text=text,
            command=command,
            font=("Arial", 14, "bold"),
            height=40,
            width=150,
            corner_radius=50,
            fg_color="#f72585",  # Color principal
            hover_color="#fa5c9c"
        )
        btn.pack(side="left", padx=10, pady=20)

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
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#25253e", corner_radius=15)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Campos del formulario organizados con grid()
        ctk.CTkLabel(form_frame, text="Nombre:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.huesped_nombre = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.huesped_nombre.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="RUT:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.huesped_rut = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.huesped_rut.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Email:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.huesped_email = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.huesped_email.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Teléfono:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.huesped_telefono = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.huesped_telefono.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Configurar las columnas del formulario para que las entradas se expandan
        form_frame.columnconfigure(1, weight=1)

        # Botones debajo del formulario
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        btn_frame.grid(row=2, column=0, pady=5, sticky="n")

        ctk.CTkButton(
            btn_frame,
            text="Registrar",
            command=self.registrar_huesped,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16, "bold"),
            height=50,
            width=150,
            corner_radius=50
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Buscar",
            command=self.buscar_huesped,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16, "bold"),
            height=50,
            width=150,
            corner_radius=50
        ).pack(side="left", padx=10)

        # Tabla de huéspedes
        columns = ["ID", "Nombre", "RUT", "Email", "Teléfono"]
        self.huesped_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.huesped_tree.heading(col, text=col)
            self.huesped_tree.column(col, width=120)

        self.huesped_tree.grid(row=1, column=1, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Configurar las columnas del main_frame para que la tabla se expanda
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    # ===== PANEL HABITACIONES =====
    def show_habitaciones(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Habitaciones",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#25253e", corner_radius=15)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Campos del formulario organizados con grid()
        ctk.CTkLabel(form_frame, text="Número:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.habitacion_numero = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.habitacion_numero.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Tipo:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.habitacion_tipo = ctk.CTkComboBox(
            form_frame,
            values=["VIP", "Penthouse", "Grande", "Mediana", "Pequeña"],
            fg_color="#f72585"
        )
        self.habitacion_tipo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Precio:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.habitacion_precio = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.habitacion_precio.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Configurar las columnas del formulario para que las entradas se expandan
        form_frame.columnconfigure(1, weight=1)

        # Botones debajo del formulario
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        btn_frame.grid(row=2, column=0, pady=5, sticky="n")

        ctk.CTkButton(
            btn_frame,
            text="Registrar",
            command=self.registrar_habitacion,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16, "bold"),
            height=50,
            width=150,
            corner_radius=50
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Modificar",
            command=self.modificar_habitacion,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16, "bold"),
            height=50,
            width=150,
            corner_radius=50
        ).pack(side="left", padx=10)

        # Tabla de habitaciones
        columns = ["ID", "Número", "Tipo", "Precio", "Disponible"]
        self.habitacion_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.habitacion_tree.heading(col, text=col)
            self.habitacion_tree.column(col, width=120)

        self.habitacion_tree.grid(row=1, column=1, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Configurar las columnas del main_frame para que la tabla se expanda
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    # ===== PANEL RESERVAS =====
    def show_reservas(self):
        self.clear_main_frame()

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="Gestión de Reservas",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).grid(row=0, column=0, columnspan=2, pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="#25253e", corner_radius=15)
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        # Campos del formulario organizados con grid()
        ctk.CTkLabel(form_frame, text="Huésped:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.reserva_huesped = ctk.CTkComboBox(
            form_frame,
            values=self.obtener_huespedes_combobox(),
            fg_color="#f72585"
        )
        self.reserva_huesped.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Tipo de Habitación:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.habitacion_tipo = ctk.CTkComboBox(
            form_frame,
            values=["VIP", "Penthouse", "Grande", "Mediana", "Pequeña"],
            fg_color="#f72585"
        )
        self.habitacion_tipo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Fecha Entrada:", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.reserva_fecha_entrada = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.reserva_fecha_entrada.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Fecha Salida:", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.reserva_fecha_salida = ctk.CTkEntry(form_frame, fg_color="#1e1e2d", border_color="#f72585", border_width=2)
        self.reserva_fecha_salida.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Configurar las columnas del formulario para que las entradas se expandan
        form_frame.columnconfigure(1, weight=1)

        # Botones debajo del formulario
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e2d", corner_radius=15)
        btn_frame.grid(row=2, column=0, pady=5, sticky="n")

        ctk.CTkButton(
            btn_frame,
            text="Crear Reserva",
            command=self.crear_reserva,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16, "bold"),
            height=50,
            width=200,
            corner_radius=50
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Eliminar Reserva",
            command=self.eliminar_reserva,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16, "bold"),
            height=50,
            width=200,
            corner_radius=50
        ).pack(side="left", padx=10)

        # Tabla de reservas
        columns = ["ID", "Huésped", "Habitación", "Entrada", "Salida", "Estado"]
        self.reserva_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.reserva_tree.heading(col, text=col)
            self.reserva_tree.column(col, width=120)

        self.reserva_tree.grid(row=1, column=1, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Configurar las columnas del main_frame para que la tabla se expanda
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
    
    # Función que obtiene los huéspedes para el combobox, asegurándonos de que devuelvan tanto el nombre como el rut
    def obtener_huespedes_combobox(self):
        huespedes = self.db.query(Huesped).all()  # Obtener todos los huéspedes de la base de datos
        return [f"{huesped.nombre} ({huesped.rut})" for huesped in huespedes]  # Formato: Nombre (Rut)

    def obtener_habitaciones_disponibles_combobox(self):
        habitaciones = self.db.query(Habitacion).filter(Habitacion.disponible == True).all()
        return [f"{h.numero} - {h.tipo}" for h in habitaciones]

    def actualizar_lista_reservas(self):
        # Verificar si el TreeView está disponible
        if not hasattr(self, 'reserva_tree') or not self.reserva_tree.winfo_exists():
            print("El TreeView no está disponible o ha sido destruido.")
            return  # Evita errores si el TreeView no existe
        
        # Limpiar los elementos del TreeView
        for item in self.reserva_tree.get_children():
            self.reserva_tree.delete(item)
        
        # Obtener todas las reservas de la base de datos
        reservas = self.db.query(Reserva).all()
        if not reservas:
            print("No se encontraron reservas en la base de datos.")
        
        # Insertar cada reserva en el TreeView
        for res in reservas:
            print(f"Insertando reserva: {res.id}, {res.huesped.nombre}, {res.habitacion.numero}")
            self.reserva_tree.insert("", "end", values=(
                res.id,
                res.huesped.nombre,
                res.habitacion.numero,
                res.fecha_entrada.strftime("%Y-%m-%d"),
                res.fecha_salida.strftime("%Y-%m-%d"),
                res.estado
            ))

    # Al momento de crear la reserva, extraemos el rut
    def crear_reserva(self):
        try:
            # Obtener el tipo de habitación seleccionado desde el combobox
            habitacion_tipo = self.habitacion_tipo.get()  # Aquí obtenemos el tipo de habitación seleccionado
            print(f"Tipo de habitación seleccionado: '{habitacion_tipo}'")  # Imprimir para verificar

            # Obtener el huésped seleccionado desde el combobox
            huesped_info = self.reserva_huesped.get()  # Obtener el valor completo (Nombre (Rut))
            print(f"Huésped completo: {huesped_info}")  # Imprimir para verificar

            # Extraer el rut del huésped del formato "Nombre (Rut)"
            huesped_rut = huesped_info.split("(")[-1].rstrip(")")  # Extraemos solo el rut
            print(f"Huésped seleccionado: {huesped_rut}")  # Imprimir para verificar

            # Buscar el huésped en la base de datos utilizando el rut
            huesped = self.db.query(Huesped).filter(Huesped.rut == huesped_rut).first()
            if not huesped:
                raise ValueError(f"El huésped con rut {huesped_rut} no existe")
            
            # Obtener las fechas
            fecha_entrada = datetime.strptime(self.reserva_fecha_entrada.get(), "%Y-%m-%d")
            fecha_salida = datetime.strptime(self.reserva_fecha_salida.get(), "%Y-%m-%d")
            
            if fecha_entrada >= fecha_salida:
                raise ValueError("La fecha de salida debe ser posterior a la fecha de entrada")
            
            # Buscar habitaciones disponibles del tipo seleccionado
            habitaciones_disponibles = self.db.query(Habitacion).filter(
                Habitacion.tipo == habitacion_tipo,
                Habitacion.disponible == True
            ).first()  # Obtener solo la primera habitación disponible

            # Si no se encuentra una habitación disponible de ese tipo, buscar una habitación de cualquier tipo
            if not habitaciones_disponibles:
                habitaciones_disponibles = self.db.query(Habitacion).filter(
                    Habitacion.disponible == True
                ).first()  # Buscar cualquier habitación disponible

            # Si no hay habitaciones disponibles en general, lanzar error
            if not habitaciones_disponibles:
                raise ValueError("No hay habitaciones disponibles en este momento")

            # Crear la reserva
            ReservaCRUD.crear_reserva(
                self.db,
                huesped_id=huesped.id,  # Aquí usamos el ID del huésped correctamente
                habitacion_id=habitaciones_disponibles.id,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida
            )
            
            # Actualizar disponibilidad de la habitación
            habitaciones_disponibles.disponible = False
            self.db.commit()
            
            messagebox.showinfo("Éxito", "Reserva creada correctamente")
            self.actualizar_lista_reservas()
            self.actualizar_lista_habitaciones()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la reserva: {str(e)}")

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
            ReservaCRUD.eliminar_reserva(self.db, reserva_id=int(reserva_id))
            messagebox.showinfo("Éxito", "Reserva eliminada correctamente")
            self.actualizar_lista_reservas()
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
            HuespedCRUD.crear_huesped(
                self.db,
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
            
        huesped = HuespedCRUD.obtener_huesped_por_rut(self.db, rut)
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
            precio = float(precio)
            HabitacionCRUD.crear_habitacion(
                self.db,
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
            HabitacionCRUD.modificar_habitacion(
                self.db,
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

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()