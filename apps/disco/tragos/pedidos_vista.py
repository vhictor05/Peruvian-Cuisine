import customtkinter as ctk
from tkinter import messagebox, ttk
from apps.disco.utils.ui_components import create_treeview
from estructura.builder.pedido_builder import PedidoBuilder
from fpdf import FPDF

class PedidosTragosVista:
    def __init__(self, parent, facade):
        self.parent = parent
        self.facade = facade
        
    def show(self):
        self.setup_cliente_frame()
        self.setup_trago_frame()
        self.setup_pedido_frame()
        self.setup_total_frame()
        
    def setup_cliente_frame(self):
        cliente_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#23233a",
            corner_radius=15
        )
        cliente_frame.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            cliente_frame,
            text="Cliente:",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.busqueda_cliente = ctk.CTkEntry(
            cliente_frame,
            width=160,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.busqueda_cliente.grid(row=0, column=1, padx=(0,10), pady=10)
        self.busqueda_cliente.bind("<KeyRelease>", self.filtrar_clientes)

        self.lista_clientes = ctk.CTkComboBox(
            cliente_frame,
            border_color="#7209b7",
            fg_color="#25253a",
            state="readonly",
            width=220
        )
        self.lista_clientes.grid(row=0, column=2, padx=10, pady=10)
        self.actualizar_lista_clientes_combo()
        self.lista_clientes.bind("<<ComboboxSelected>>", self.on_cliente_seleccionado)

        self.cliente_seleccionado_label = ctk.CTkLabel(
            cliente_frame,
            text="Seleccione un cliente.",
            font=("Arial", 12)
        )
        self.cliente_seleccionado_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 5), sticky="w")
        
    def setup_trago_frame(self):
        trago_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#23233a",
            corner_radius=15
        )
        trago_frame.pack(fill="x", padx=20, pady=(5, 5))

        ctk.CTkLabel(
            trago_frame,
            text="Trago:",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.busqueda_trago = ctk.CTkEntry(
            trago_frame,
            width=160,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.busqueda_trago.grid(row=0, column=1, padx=(0,10), pady=10)
        self.busqueda_trago.bind("<KeyRelease>", self.filtrar_tragos)

        self.lista_tragos = ctk.CTkComboBox(
            trago_frame,
            border_color="#7209b7",
            fg_color="#25253a",
            state="readonly",
            width=220
        )
        self.lista_tragos.grid(row=0, column=2, padx=10, pady=10)
        self.actualizar_lista_tragos_combo()

        ctk.CTkLabel(
            trago_frame,
            text="Cantidad:",
            font=("Arial", 14)
        ).grid(row=0, column=3, padx=(10,2), pady=10, sticky="w")

        self.trago_cantidad = ctk.CTkEntry(
            trago_frame,
            width=50,
            fg_color="#25253a",
            border_color="#7209b7",
            border_width=1
        )
        self.trago_cantidad.grid(row=0, column=4, padx=(2,10), pady=10)
        self.trago_cantidad.insert(0, "1")

        ctk.CTkButton(
            trago_frame,
            text="➕ Agregar",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            command=self.agregar_trago_pedido,
            font=("Arial", 13),
            width=100,
            height=35
        ).grid(row=0, column=5, padx=(10,0), pady=10)
        
    def setup_pedido_frame(self):
        pedido_frame = ctk.CTkFrame(
            self.parent,
            fg_color="#23233a",
            corner_radius=15
        )
        pedido_frame.pack(fill="both", expand=True, padx=20, pady=(5, 5))

        columns = ("Trago", "Cantidad", "Precio Unitario", "Subtotal", "Eliminar")
        self.pedido_tree = create_treeview(pedido_frame, columns)
        
        for col in columns:
            self.pedido_tree.column(col, anchor="center", width=120)
            
        self.pedido_tree.bind("<Double-1>", self.on_pedido_tree_double_click)

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
        
    def setup_total_frame(self):
        total_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )
        total_frame.pack(fill="x", padx=20, pady=(5, 15))

        self.pedido_total = ctk.CTkLabel(
            total_frame,
            text="Total: $0.00",
            font=("Arial", 16, "bold"),
            text_color="#7209b7"
        )
        self.pedido_total.pack(side="left", padx=(10,20), pady=10)

        ctk.CTkButton(
            total_frame,
            text="✅ Confirmar Pedido",
            fg_color="#7209b7",
            hover_color="#9d4dc7",
            command=self.confirmar_pedido_tragos,
            font=("Arial", 15),
            width=180,
            height=40
        ).pack(side="right", padx=10, pady=10)

        # Limpiar pedido al iniciar
        self.limpiar_pedido()

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
            
            self.actualizar_total_pedido()
            self.trago_cantidad.delete(0, "end")
            self.trago_cantidad.insert(0, "1")
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número entero")

    def eliminar_trago_seleccionado_pedido(self):
        selected = self.pedido_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una fila para eliminar")
            return
        for item in selected:
            self.pedido_tree.delete(item)
        self.actualizar_total_pedido()

    def on_pedido_tree_double_click(self, event):
        region = self.pedido_tree.identify("region", event.x, event.y)
        if region == "cell":
            col = self.pedido_tree.identify_column(event.x)
            if col == f"#{len(self.pedido_tree['columns'])}":
                row_id = self.pedido_tree.identify_row(event.y)
                if row_id:
                    self.pedido_tree.delete(row_id)
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

    def generar_boleta_tragos(self, pedido_id):
        pedido = self.facade.obtener_pedido_por_id(pedido_id)
        cliente = self.facade.obtener_cliente_por_id(pedido.cliente_id)
        
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
            trago = self.facade.obtener_trago_por_id(trago_id)
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
        clientes = self.facade.listar_clientes()
        
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