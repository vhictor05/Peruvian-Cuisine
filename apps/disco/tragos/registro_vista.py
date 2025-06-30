import customtkinter as ctk
from tkinter import messagebox
from apps.disco.utils.ui_components import create_treeview, create_button

class RegistroTragosVista:
    def __init__(self, parent, facade):
        self.parent = parent
        self.facade = facade
        
    def show(self):
        self.setup_form()
        self.setup_buttons()
        self.setup_treeview()
        
    def setup_form(self):
        form_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#1e1e2d",
            corner_radius=15
        )
        form_frame.pack(fill="x", padx=10, pady=10)

        # Combobox para seleccionar trago
        ctk.CTkLabel(
            form_frame,
            text="Seleccionar Trago:",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=(10,0), sticky="w")

        ctk.CTkLabel(
            form_frame,
            text="Precio:",
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=10, pady=(10,0), sticky="w")
        
        self.trago_seleccionado = ctk.CTkComboBox(
            form_frame,
            border_color="#7209b7",
            fg_color="#25253a",
            state="readonly",
            border_width=1
        )
        self.trago_seleccionado.grid(row=1, column=0, padx=10, pady=(5,10), sticky="ew")

        self.trago_precio = ctk.CTkEntry(
            form_frame,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.trago_precio.grid(row=1, column=1, padx=10, pady=(5,10), sticky="ew")

        # Campo Stock
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

        # Configurar el peso de las columnas
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # Actualizar lista de tragos
        self.actualizar_lista_tragos_combobox()
        self.trago_seleccionado.bind("<<ComboboxSelected>>", self.on_trago_selected)
        
    def setup_buttons(self):
        btn_frame = ctk.CTkFrame(self.parent, fg_color="#1e1e2d")
        btn_frame.pack(fill="x", padx=10, pady=10)

        create_button(
            btn_frame,
            "🔄 Actualizar Precio",
            self.actualizar_precio_trago
        ).pack(side="left", padx=5)

        create_button(
            btn_frame,
            "📦 Actualizar Stock",
            self.actualizar_stock_trago
        ).pack(side="left", padx=5)
        
    def setup_treeview(self):
        columns = ["ID", "Nombre", "Precio", "Categoría", "Disponible", "Stock"]
        self.trago_tree = create_treeview(self.parent, columns)
        
        # Configurar anchos de columna
        self.trago_tree.column("ID", width=50, anchor="center")
        self.trago_tree.column("Nombre", width=150, anchor="w")
        self.trago_tree.column("Precio", width=100, anchor="e")
        self.trago_tree.column("Categoría", width=100, anchor="w")
        self.trago_tree.column("Disponible", width=80, anchor="center")
        self.trago_tree.column("Stock", width=60, anchor="center")
        
        self.trago_tree.bind("<<TreeviewSelect>>", self.on_trago_tree_select)
        self.actualizar_lista_tragos()
        
    def actualizar_precio_trago(self):
        try:
            trago_str = self.trago_seleccionado.get()
            nuevo_precio = float(self.trago_precio.get())
            
            if not trago_str:
                messagebox.showwarning("Advertencia", "Seleccione un trago primero")
                return

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
        except ValueError:
            messagebox.showerror("Error", "Ingrese un precio válido")
            
    def actualizar_stock_trago(self):
        try:
            trago_str = self.trago_seleccionado.get()
            nuevo_stock = int(self.trago_stock.get())

            if not trago_str:
                messagebox.showwarning("Advertencia", "Seleccione un trago primero")
                return

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
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el stock")
            else:
                messagebox.showerror("Error", "Trago no encontrado")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido para el stock")
            
    def actualizar_lista_tragos(self):
        for item in self.trago_tree.get_children():
            self.trago_tree.delete(item)
            
        tragos = self.facade.listar_tragos()
        for trago in tragos:
            disponible = "Sí" if trago.stock > 0 else "No"
            self.trago_tree.insert("", "end", values=(
                trago.id,
                trago.nombre,
                f"${trago.precio:.2f}",
                trago.categoria or "",
                disponible,
                trago.stock
            ))
            
    def actualizar_lista_tragos_combobox(self):
        tragos = self.facade.listar_tragos()
        valores = [f"{t.nombre} (${t.precio:.2f})" for t in tragos]
        self.trago_seleccionado.configure(values=valores)
        
    def on_trago_selected(self, event=None):
        trago_str = self.trago_seleccionado.get()
        if trago_str:
            trago_nombre = trago_str.split(" ($")[0]
            trago = self.facade.obtener_trago_por_nombre(trago_nombre)
            if trago:
                self.trago_precio.delete(0, "end")
                self.trago_precio.insert(0, str(trago.precio))
                self.trago_stock.delete(0, "end")
                self.trago_stock.insert(0, str(trago.stock))
                
    def on_trago_tree_select(self, event):
        selected = self.trago_tree.selection()
        if selected:
            values = self.trago_tree.item(selected[0])["values"]
            trago_nombre = values[1]
            combobox_val = next((v for v in self.trago_seleccionado.cget("values") 
                               if v.startswith(trago_nombre)), None)
            if combobox_val:
                self.trago_seleccionado.set(combobox_val)
                self.on_trago_selected(None)