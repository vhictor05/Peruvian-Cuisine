import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from sqlalchemy.orm import Session
from hotel_database import get_db, Base
from models import Huesped, Habitacion, Reserva
from crud.huesped_crud import HuespedCRUD
from crud.habitacion_crud import HabitacionCRUD
from crud.reserva_crud import ReservaCRUD
from datetime import datetime, timedelta
from tkcalendar import DateEntry

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Hotel")
        self.geometry("1200x700")
        self.db = next(get_db())
        
        # Menú lateral
        self.menu_frame = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        # Contenido principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
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
            font=("Arial", 14),
            height=40,
            corner_radius=8
        )
        btn.pack(fill="x", padx=10, pady=5)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ===== PANEL HUÉSPEDES =====
    def show_huespedes(self):
        self.clear_main_frame()
        
        # Título
        ctk.CTkLabel(self.main_frame, text="Gestión de Huéspedes", font=("Arial", 20)).pack(pady=10)
        
        # Formulario
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        self.huesped_nombre = self.create_form_entry(form_frame, "Nombre", 0)
        self.huesped_rut = self.create_form_entry(form_frame, "RUT", 1)
        self.huesped_email = self.create_form_entry(form_frame, "Email", 2)
        self.huesped_telefono = self.create_form_entry(form_frame, "Teléfono", 3)
        
        # Botones
        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Registrar", command=self.registrar_huesped).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Buscar", command=self.buscar_huesped).pack(side="left", padx=5)
        
        # Lista de huéspedes
        columns = ["ID", "Nombre", "RUT", "Email", "Teléfono"]
        self.huesped_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.huesped_tree.heading(col, text=col)
            self.huesped_tree.column(col, width=120)
        
        self.huesped_tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.actualizar_lista_huespedes()

    # ===== PANEL HABITACIONES =====
    def show_habitaciones(self):
        self.clear_main_frame()
        
        # Título
        ctk.CTkLabel(self.main_frame, text="Gestión de Habitaciones", font=("Arial", 20)).pack(pady=10)
        
        # Formulario
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        self.habitacion_numero = self.create_form_entry(form_frame, "Número", 0)
        self.habitacion_tipo = self.create_form_entry(form_frame, "Tipo", 1)
        self.habitacion_precio = self.create_form_entry(form_frame, "Precio", 2)
        
        # Botones
        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Registrar", command=self.registrar_habitacion).pack(side="left", padx=5)
        
        # Lista de habitaciones
        columns = ["ID", "Número", "Tipo", "Precio", "Disponible"]
        self.habitacion_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.habitacion_tree.heading(col, text=col)
        
        self.habitacion_tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.actualizar_lista_habitaciones()

    # ===== PANEL RESERVAS =====
    def show_reservas(self):
        self.clear_main_frame()
    
        # Título
        ctk.CTkLabel(self.main_frame, text="Gestión de Reservas", font=("Arial", 20)).pack(pady=10)
        
        # Formulario
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Combobox para huéspedes
        ctk.CTkLabel(form_frame, text="Huésped:").grid(row=0, column=0, padx=5, pady=5)
        self.reserva_huesped = ctk.CTkComboBox(form_frame, values=self.obtener_huespedes_combobox())
        self.reserva_huesped.grid(row=0, column=1, padx=5, pady=5)
        
        # Combobox para habitaciones disponibles
        ctk.CTkLabel(form_frame, text="Habitación:").grid(row=1, column=0, padx=5, pady=5)
        self.reserva_habitacion = ctk.CTkComboBox(form_frame, values=self.obtener_habitaciones_disponibles_combobox())
        self.reserva_habitacion.grid(row=1, column=1, padx=5, pady=5)
        
        # Fechas
        ctk.CTkLabel(form_frame, text="Fecha Entrada:").grid(row=2, column=0, padx=5, pady=5)
        self.reserva_fecha_entrada = ctk.CTkEntry(form_frame)
        self.reserva_fecha_entrada.grid(row=2, column=1, padx=5, pady=5)
        self.reserva_fecha_entrada.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ctk.CTkLabel(form_frame, text="Fecha Salida:").grid(row=3, column=0, padx=5, pady=5)
        self.reserva_fecha_salida = ctk.CTkEntry(form_frame)
        self.reserva_fecha_salida.grid(row=3, column=1, padx=5, pady=5)
        self.reserva_fecha_salida.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        
        # Botón de reserva
        btn_frame = ctk.CTkFrame(self.main_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Crear Reserva", command=self.crear_reserva).pack(side="left", padx=5)
        
        # Lista de reservas
        columns = ["ID", "Huésped", "Habitación", "Entrada", "Salida", "Estado"]
        self.reserva_tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        for col in columns:
            self.reserva_tree.heading(col, text=col)
        
        self.reserva_tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.actualizar_lista_reservas()
    
    def obtener_huespedes_combobox(self):
        huespedes = self.db.query(Huesped).all()
        return [f"{h.nombre} ({h.rut})" for h in huespedes]

    def obtener_habitaciones_disponibles_combobox(self):
        habitaciones = self.db.query(Habitacion).filter(Habitacion.disponible == True).all()
        return [f"{h.numero} - {h.tipo}" for h in habitaciones]

    def actualizar_lista_reservas(self):
        for item in self.reserva_tree.get_children():
            self.reserva_tree.delete(item)
            
        reservas = self.db.query(Reserva).all()
        for res in reservas:
            self.reserva_tree.insert("", "end", values=(
                res.id,
                res.huesped.nombre,
                res.habitacion.numero,
                res.fecha_entrada.strftime("%Y-%m-%d"),
                res.fecha_salida.strftime("%Y-%m-%d"),
                res.estado
            ))

    def crear_reserva(self):
        try:
            # Obtener IDs de los combobox
            huesped_rut = self.reserva_huesped.get().split("(")[-1].rstrip(")")
            habitacion_num = self.reserva_habitacion.get().split(" - ")[0]
            
            huesped = self.db.query(Huesped).filter(Huesped.rut == huesped_rut).first()
            habitacion = self.db.query(Habitacion).filter(Habitacion.numero == habitacion_num).first()
            
            self.reserva_fecha_entrada = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
            self.reserva_fecha_salida = DateEntry(form_frame, date_pattern="yyyy-mm-dd")


            
            ReservaCRUD.crear_reserva(
                self.db,
                huesped_id=huesped.id,
                habitacion_id=habitacion.id,
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida
            )
            
            messagebox.showinfo("Éxito", "Reserva creada correctamente")
            self.actualizar_lista_reservas()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la reserva: {str(e)}")


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
        tipo = self.habitacion_tipo.get()
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
            messagebox.showerror("Error", "Precio debe ser un número")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()