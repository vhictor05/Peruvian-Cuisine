import customtkinter as ctk
from tkinter import ttk, messagebox
from models_folder.models_hotel import Huesped

class HuespedesVista(ctk.CTkFrame):
    def __init__(self, parent, hotel_facade):
        super().__init__(parent)
        self.facade = hotel_facade
        self.configure(fg_color="#25253a")
        self.inicializar_ui()
        # Agregar binding para selección en la tabla
        self.huesped_tree.bind('<<TreeviewSelect>>', self.cargar_datos_huesped)
        
    def inicializar_ui(self):
        # Título
        ctk.CTkLabel(
            self,
            text="Gestión de Huéspedes",
            font=("Arial", 28, "bold"),
            text_color="#f72585"
        ).pack(pady=10)

        # Frame del formulario
        form_frame = ctk.CTkFrame(self, fg_color="#1e1e2d", corner_radius=15)
        form_frame.pack(fill="x", padx=30, pady=10)

        # Campos del formulario organizados con grid()
        # Nombre
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

        # RUT
        ctk.CTkLabel(
            form_frame, 
            text="RUT:", 
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")

        rut_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        rut_frame.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        self.huesped_rut = ctk.CTkEntry(
            rut_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1,
            width=120
        )
        self.huesped_rut.pack(side="left")

        ctk.CTkLabel(
            rut_frame, 
            text="-", 
            font=("Arial", 14)
        ).pack(side="left", padx=5)

        self.huesped_dv = ctk.CTkEntry(
            rut_frame, 
            fg_color="#25253a", 
            border_color="#f72585", 
            border_width=1,
            width=30
        )
        self.huesped_dv.pack(side="left")

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

        # Configurar las columnas del formulario
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        # Frame para botones
        btn_frame = ctk.CTkFrame(self, fg_color="#25253a", corner_radius=15)
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

        ctk.CTkButton(
            btn_frame,
            text="✏️ Editar",
            command=self.editar_huesped,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_huesped,
            fg_color="#f72585",
            hover_color="#fa5c9c",
            font=("Arial", 16),
            height=50,
            width=140,
            corner_radius=15
        ).pack(side="left", padx=10)

        # Tabla de huéspedes
        columns = ["ID", "Nombre", "RUT", "Email", "Teléfono"]
        self.huesped_tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.huesped_tree.heading(col, text=col)
            if col == "ID":
                self.huesped_tree.column(col, width=50)
            else:
                self.huesped_tree.column(col, width=150)

        self.huesped_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Actualizar lista de huéspedes
        self.actualizar_lista_huespedes()

    def registrar_huesped(self):
        nombre = self.huesped_nombre.get().strip()
        rut = self.huesped_rut.get().strip()
        dv = self.huesped_dv.get().strip()
        email = self.huesped_email.get().strip()
        telefono = self.huesped_telefono.get().strip()
        
        if not nombre or not rut or not dv:
            messagebox.showerror("Error", "Nombre y RUT son obligatorios")
            return
            
        try:
            # Validar formato de RUT
            if not rut.isdigit():
                raise ValueError("El RUT debe contener solo números")
            if not dv.isalnum() or len(dv) != 1:
                raise ValueError("El dígito verificador debe ser un solo carácter")
            
            # Formatear el RUT con puntos y guión
            rut_numero = int(rut)
            rut_formateado = f"{rut_numero:,}".replace(",", ".")
            rut_completo = f"{rut_formateado}-{dv}"
            
            self.facade.crear_huesped(
                nombre=nombre,
                rut=rut_completo,
                email=email if email else None,
                telefono=telefono if telefono else None
            )
            messagebox.showinfo("Éxito", "Huésped registrado correctamente")
            self.actualizar_lista_huespedes()
            # Limpiar campos
            self.huesped_nombre.delete(0, 'end')
            self.huesped_rut.delete(0, 'end')
            self.huesped_dv.delete(0, 'end')
            self.huesped_email.delete(0, 'end')
            self.huesped_telefono.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {str(e)}")

    def buscar_huesped(self):
        rut = self.huesped_rut.get().strip()
        dv = self.huesped_dv.get().strip()
        
        if not rut or not dv:
            messagebox.showwarning("Advertencia", "Ingrese un RUT completo para buscar")
            return

        try:
            # Formatear el RUT con puntos y guión
            rut_numero = int(rut)
            rut_formateado = f"{rut_numero:,}".replace(",", ".")
            rut_completo = f"{rut_formateado}-{dv}"
            
            huesped = self.facade.obtener_huesped_por_rut(rut_completo)
            
            if huesped:
                self.huesped_nombre.delete(0, 'end')
                self.huesped_nombre.insert(0, huesped.nombre)

                # Extraer el RUT sin formato para mostrar en los campos
                rut_parts = huesped.rut.split('-')
                rut_sin_puntos = rut_parts[0].replace(".", "")
                
                self.huesped_rut.delete(0, 'end')
                self.huesped_rut.insert(0, rut_sin_puntos)
                self.huesped_dv.delete(0, 'end')
                self.huesped_dv.insert(0, rut_parts[1])

                self.huesped_email.delete(0, 'end')
                if huesped.email:
                    self.huesped_email.insert(0, huesped.email)

                self.huesped_telefono.delete(0, 'end')
                if huesped.telefono:
                    self.huesped_telefono.insert(0, huesped.telefono)
            else:
                messagebox.showinfo("Información", "No se encontró el huésped")
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")

    def editar_huesped(self):
        selected_item = self.huesped_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un huésped para editar")
            return

        huesped_id = self.huesped_tree.item(selected_item[0])['values'][0]
        nombre = self.huesped_nombre.get().strip()
        rut = self.huesped_rut.get().strip()
        dv = self.huesped_dv.get().strip()
        email = self.huesped_email.get().strip()
        telefono = self.huesped_telefono.get().strip()

        if not nombre or not rut or not dv:
            messagebox.showerror("Error", "Nombre y RUT son obligatorios")
            return

        try:
            # Formatear el RUT con puntos y guión
            rut_numero = int(rut)
            rut_formateado = f"{rut_numero:,}".replace(",", ".")
            rut_completo = f"{rut_formateado}-{dv}"

            # Actualizar huésped
            self.facade.db.query(Huesped).filter_by(id=huesped_id).update({
                'nombre': nombre,
                'rut': rut_completo,
                'email': email if email else None,
                'telefono': telefono if telefono else None
            })
            self.facade.db.commit()

            messagebox.showinfo("Éxito", "Huésped actualizado correctamente")
            self.actualizar_lista_huespedes()
            
            # Limpiar campos
            self.huesped_nombre.delete(0, 'end')
            self.huesped_rut.delete(0, 'end')
            self.huesped_dv.delete(0, 'end')
            self.huesped_email.delete(0, 'end')
            self.huesped_telefono.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")

    def eliminar_huesped(self):
        selected_item = self.huesped_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un huésped para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este huésped?"):
            try:
                huesped_id = self.huesped_tree.item(selected_item[0])['values'][0]
                huesped = self.facade.db.query(Huesped).get(huesped_id)
                
                if huesped:
                    self.facade.db.delete(huesped)
                    self.facade.db.commit()
                    messagebox.showinfo("Éxito", "Huésped eliminado correctamente")
                    self.actualizar_lista_huespedes()
                    
                    # Limpiar campos
                    self.huesped_nombre.delete(0, 'end')
                    self.huesped_rut.delete(0, 'end')
                    self.huesped_dv.delete(0, 'end')
                    self.huesped_email.delete(0, 'end')
                    self.huesped_telefono.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def cargar_datos_huesped(self, event=None):
        selected_item = self.huesped_tree.selection()
        if not selected_item:
            return

        # Obtener valores del item seleccionado
        valores = self.huesped_tree.item(selected_item[0])['values']
        
        # Limpiar campos actuales
        self.huesped_nombre.delete(0, 'end')
        self.huesped_rut.delete(0, 'end')
        self.huesped_dv.delete(0, 'end')
        self.huesped_email.delete(0, 'end')
        self.huesped_telefono.delete(0, 'end')

        # Insertar valores en los campos
        self.huesped_nombre.insert(0, valores[1])
        
        # Separar RUT y DV
        rut_completo = valores[2]
        rut_parts = rut_completo.split('-')
        rut_sin_puntos = rut_parts[0].replace(".", "")
        
        self.huesped_rut.insert(0, rut_sin_puntos)
        self.huesped_dv.insert(0, rut_parts[1])
        
        if valores[3]:  # Email
            self.huesped_email.insert(0, valores[3])
        if valores[4]:  # Teléfono
            self.huesped_telefono.insert(0, valores[4])

    def actualizar_lista_huespedes(self):
        for item in self.huesped_tree.get_children():
            self.huesped_tree.delete(item)
            
        huespedes = self.facade.db.query(Huesped).all()
        for huesped in huespedes:
            self.huesped_tree.insert("", "end", values=(
                huesped.id,
                huesped.nombre,
                huesped.rut,  # Ya incluye el guión
                huesped.email or "",
                huesped.telefono or ""
            ))
        