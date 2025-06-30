import customtkinter as ctk
from tkinter import messagebox
from apps.disco.utils.ui_components import create_form_entry, create_treeview, create_button
from apps.disco.utils.validadores import validar_rut, validar_telefono, validar_email

class ClientesVista:
    def __init__(self, parent, facade):
        self.parent = parent
        self.facade = facade
        
    def show(self):
        self.setup_title()
        self.setup_form()
        self.setup_buttons()
        self.setup_treeview()
        
    def setup_title(self):
        ctk.CTkLabel(
            self.parent,
            text="Gestión de Clientes",
            font=("Arial", 28, "bold"),
            text_color="#7209b7"
        ).pack(pady=10)
        
    def setup_form(self):
        self.form_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#1e1e2d",
            corner_radius=15
        )
        self.form_frame.pack(fill="x", padx=20, pady=10)
        
        # Configurar grid
        self.form_frame.columnconfigure(0, weight=1)
        self.form_frame.columnconfigure(1, weight=1)
        
        # Entry del Nombre
        ctk.CTkLabel(
            self.form_frame,
            text="Nombre:",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")
        
        self.cliente_nombre = ctk.CTkEntry(
            self.form_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.cliente_nombre.grid(row=1, column=0, padx=10, sticky="ew")
        
        # RUT y DV
        ctk.CTkLabel(
            self.form_frame,
            text="RUT:",
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")
        
        rut_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        rut_frame.grid(row=1, column=1, sticky="ew")
        
        self.cliente_rut = ctk.CTkEntry(
            rut_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1,
            width=120
        )
        self.cliente_rut.pack(side="left")
        
        ctk.CTkLabel(
            rut_frame,
            text="-",
            font=("Arial", 14)
        ).pack(side="left")
        
        self.cliente_rut_dv = ctk.CTkEntry(
            rut_frame,
            width=25,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.cliente_rut_dv.pack(side="left")
        
        # Email
        ctk.CTkLabel(
            self.form_frame,
            text="Email:",
            font=("Arial", 14)
        ).grid(row=2, column=0, padx=10, pady=(5,0), sticky="w")
        
        self.cliente_email = ctk.CTkEntry(
            self.form_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.cliente_email.grid(row=3, column=0, padx=10, pady=(0,10), sticky="ew")
        
        # Teléfono
        ctk.CTkLabel(
            self.form_frame,
            text="Teléfono:",
            font=("Arial", 14)
        ).grid(row=2, column=1, padx=10, pady=(5,0), sticky="w")
        
        self.cliente_telefono = ctk.CTkEntry(
            self.form_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.cliente_telefono.grid(row=3, column=1, padx=10, pady=(0,10), sticky="ew")
        
    def setup_buttons(self):
        button_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        button_frame.pack(pady=10)
        
        create_button(
            button_frame,
            "📄 Registrar Cliente",
            self.registrar_cliente
        ).pack(side="left", padx=5)
        
        create_button(
            button_frame,
            "🖊 Editar Cliente",
            self.editar_cliente
        ).pack(side="left", padx=5)
        
        create_button(
            button_frame,
            "🗑 Eliminar Cliente",
            self.eliminar_cliente
        ).pack(side="left", padx=5)
        
    def setup_treeview(self):
        self.cliente_tree = create_treeview(
            self.parent,
            ["ID", "Nombre", "RUT", "Email", "Teléfono"]
        )
        self.cliente_tree.bind("<<TreeviewSelect>>", self.on_cliente_select)
        self.actualizar_lista_clientes()
        
    def registrar_cliente(self):
        nombre = self.cliente_nombre.get()
        rut_numero = self.cliente_rut.get().strip()
        dv = self.cliente_rut_dv.get().strip().upper()
        rut = f"{rut_numero}{dv}"
        email = self.cliente_email.get()
        telefono = self.cliente_telefono.get()

        # Validaciones
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
            self.limpiar_campos()
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

        # Validaciones
        if not validar_rut(rut_numero, dv):
            messagebox.showerror("Error", "El RUT ingresado no es válido.")
            return
        if not validar_telefono(telefono):
            messagebox.showerror("Error", "El teléfono debe tener 9 dígitos y comenzar con 9.")
            return
        if not validar_email(email):
            messagebox.showerror("Error", "El email ingresado no es válido.")
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
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def eliminar_cliente(self):
        selected_item = self.cliente_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        cliente_id = self.cliente_tree.item(selected_item[0], "values")[0]
        
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            "¿Está seguro que desea eliminar este cliente? Esta acción no se puede deshacer."
        )
        
        if confirmacion:
            try:
                if self.facade.eliminar_cliente(cliente_id):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.actualizar_lista_clientes()
                    self.limpiar_campos()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {str(e)}")
                
    def on_cliente_select(self, event):
        selected_items = self.cliente_tree.selection()
        if selected_items:
            item = self.cliente_tree.item(selected_items[0])
            values = item["values"]

            self.cliente_nombre.delete(0, "end")
            self.cliente_nombre.insert(0, values[1])

            # Separar RUT y DV
            self.cliente_rut.delete(0, "end")
            self.cliente_rut_dv.delete(0, "end")
            rut_db = values[2]
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
            
    def actualizar_lista_clientes(self):
        for item in self.cliente_tree.get_children():
            self.cliente_tree.delete(item)
        for cliente in self.facade.listar_clientes():
            self.cliente_tree.insert("", "end", values=(
                cliente.id,
                cliente.nombre,
                cliente.rut,
                cliente.email,
                cliente.telefono
            ))
            
    def limpiar_campos(self):
        self.cliente_nombre.delete(0, "end")
        self.cliente_rut.delete(0, "end")
        self.cliente_rut_dv.delete(0, "end")
        self.cliente_email.delete(0, "end")
        self.cliente_telefono.delete(0, "end")