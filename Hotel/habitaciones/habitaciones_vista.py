import customtkinter as ctk
from tkinter import ttk, messagebox
from models_folder.models_hotel import Habitacion

class HabitacionesVista(ctk.CTkFrame):
    def __init__(self, parent, hotel_facade):
        super().__init__(parent)
        self.facade = hotel_facade
        self.configure(fg_color="#25253a")
        self.inicializar_ui()

    def inicializar_ui(self):
        # Título
        ctk.CTkLabel(
            self,
            text="Gestión de Habitaciones",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=10)

        # Campos del formulario organizados con grid()
        # Número y Tipo
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
            values=["Penthouse", "Grande", "Mediana", "Pequeña"],
            fg_color="#25253a",
            border_color="#f72585",
            border_width=1
        )
        self.habitacion_tipo.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        # Precio
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

        # Configurar las columnas del formulario
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Frame para botones
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
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
        self.habitacion_tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.habitacion_tree.heading(col, text=col)
            if col == "ID":
                self.habitacion_tree.column(col, width=50)
            else:
                self.habitacion_tree.column(col, width=150)

        self.habitacion_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Vincular evento de selección
        self.habitacion_tree.bind("<<TreeviewSelect>>", self.cargar_datos_habitacion)
        
        # Actualizar lista de habitaciones
        self.actualizar_lista_habitaciones()

    def registrar_habitacion(self):
        numero = self.habitacion_numero.get().strip()
        tipo = self.habitacion_tipo.get().strip()
        precio = self.habitacion_precio.get().strip()

        if not all([numero, tipo, precio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            self.facade.crear_habitacion(numero, tipo, precio)
            messagebox.showinfo("Éxito", "Habitación registrada correctamente")
            self.actualizar_lista_habitaciones()
            # Limpiar campos
            self.habitacion_numero.delete(0, 'end')
            self.habitacion_tipo.set("Penthouse")
            self.habitacion_precio.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la habitación: {str(e)}")

    def modificar_habitacion(self):
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para modificar")
            return

        habitacion_id = self.habitacion_tree.item(selected_item[0])['values'][0]
        numero = self.habitacion_numero.get().strip()
        tipo = self.habitacion_tipo.get().strip()
        precio = self.habitacion_precio.get().strip()
        disponible = messagebox.askyesno("Disponibilidad", "¿Está disponible esta habitación?")

        if not all([numero, tipo, precio]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = float(precio)
            self.facade.modificar_habitacion(
                habitacion_id=habitacion_id,
                numero=numero,
                tipo=tipo,
                precio=precio,
                disponible=disponible
            )
            messagebox.showinfo("Éxito", "Habitación modificada correctamente")
            self.actualizar_lista_habitaciones()
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar la habitación: {str(e)}")

    def eliminar_habitacion(self):
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione una habitación para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta habitación?"):
            habitacion_id = self.habitacion_tree.item(selected_item[0])['values'][0]
            try:
                self.facade.eliminar_habitacion(habitacion_id)
                messagebox.showinfo("Éxito", "Habitación eliminada correctamente")
                self.actualizar_lista_habitaciones()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la habitación: {str(e)}")

    def cargar_datos_habitacion(self, event=None):
        selected_item = self.habitacion_tree.selection()
        if not selected_item:
            return

        valores = self.habitacion_tree.item(selected_item[0])['values']
        
        self.habitacion_numero.delete(0, 'end')
        self.habitacion_numero.insert(0, valores[1])
        
        self.habitacion_tipo.set(valores[2])
        
        precio = str(valores[3]).replace('$', '').replace(',', '')
        self.habitacion_precio.delete(0, 'end')
        self.habitacion_precio.insert(0, precio)

    def actualizar_lista_habitaciones(self):
        for item in self.habitacion_tree.get_children():
            self.habitacion_tree.delete(item)
            
        habitaciones = self.facade.db.query(Habitacion).all()
        
        for hab in habitaciones:
            self.habitacion_tree.insert('', 'end', values=(
                hab.id,
                hab.numero,
                hab.tipo,
                f"${hab.precio:.2f}",
                "Sí" if hab.disponible else "No"
            ))