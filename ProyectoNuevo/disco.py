import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from sqlalchemy.orm import Session
from disco_database import get_db, engine, Base
from models import Evento, ClienteDiscoteca, Entrada, Mesa, ReservaMesa
from crud.evento_crud import EventoCRUD
from crud.cliente_disco_crud import ClienteDiscotecaCRUD

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DiscotecaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Discoteca")
        self.geometry("1200x700")
        self.db: Session = next(get_db())

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.menu_frame = ctk.CTkFrame(self, width=200)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.create_menu_button("Eventos", self.show_eventos)
        self.create_menu_button("Clientes", self.show_clientes)

        self.show_eventos()

    def on_closing(self):
        try:
            self.destroy()
        except Exception:
            pass

    def create_menu_button(self, text, command):
        btn = ctk.CTkButton(self.menu_frame, text=text, command=command)
        btn.pack(fill="x", padx=10, pady=5)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_form_entry(self, parent, label, row):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        ctk.CTkLabel(frame, text=label + ":").pack(side="left", padx=5)
        entry = ctk.CTkEntry(frame)
        entry.pack(side="right", fill="x", expand=True, padx=5)
        return entry

    # ===== EVENTOS =====
    def show_eventos(self):
        self.clear_main_frame()
        ctk.CTkLabel(self.main_frame, text="Gestión de Eventos", font=("Arial", 20)).pack(pady=10)
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=10)

        self.evento_nombre = self.create_form_entry(form_frame, "Nombre", 0)
        self.evento_descripcion = self.create_form_entry(form_frame, "Descripción", 1)
        self.evento_fecha = self.create_form_entry(form_frame, "Fecha (YYYY-MM-DD HH:MM)", 2)
        self.evento_precio = self.create_form_entry(form_frame, "Precio Entrada", 3)
        self.evento_aforo = self.create_form_entry(form_frame, "Aforo Máximo", 4)

        ctk.CTkButton(self.main_frame, text="Registrar Evento", command=self.registrar_evento).pack(pady=10)

        self.evento_tree = self.create_treeview(["ID", "Nombre", "Fecha", "Precio", "Aforo"])
        self.actualizar_lista_eventos()

    def registrar_evento(self):
        try:
            evento_data = {
                "nombre": self.evento_nombre.get(),
                "descripcion": self.evento_descripcion.get(),
                "fecha": datetime.strptime(self.evento_fecha.get(), "%Y-%m-%d %H:%M"),
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
        ctk.CTkLabel(self.main_frame, text="Gestión de Clientes", font=("Arial", 20)).pack(pady=10)
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=10)

        self.cliente_nombre = self.create_form_entry(form_frame, "Nombre", 0)
        self.cliente_rut = self.create_form_entry(form_frame, "RUT", 1)
        self.cliente_email = self.create_form_entry(form_frame, "Email", 2)
        self.cliente_telefono = self.create_form_entry(form_frame, "Teléfono", 3)

        ctk.CTkButton(self.main_frame, text="Registrar Cliente", command=self.registrar_cliente).pack(pady=10)

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

if __name__ == "__main__":
    app = DiscotecaApp()
    app.mainloop()