import customtkinter as ctk
from tkinter import messagebox, ttk
from apps.disco.utils.ui_components import create_treeview
from estructura.builder.pedido_builder import PedidoBuilder
from fpdf import FPDF
import requests
import threading

API_TRAGOS_URL = "http://localhost:8000/api/v1/disco/tragos"

class PedidosTragosVista:
    def __init__(self, parent, facade=None):
        self.parent = parent
        # self.facade = facade  # Ya no se usa
        
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
            # Obtener trago desde la API
            response = requests.get(f"{API_TRAGOS_URL}?nombre={trago_nombre}")
            if response.status_code == 200 and response.json():
                trago = response.json()[0]  # Suponiendo que la API devuelve una lista
            else:
                messagebox.showerror("Error", "Trago no encontrado")
                return
            subtotal = trago['precio'] * cantidad
            # Insertar con botón de eliminar
            item_id = self.pedido_tree.insert("", "end", values=(
                trago['nombre'],
                cantidad,
                f"${trago['precio']:.2f}",
                f"${subtotal:.2f}",
                "✖"
            ))
            
            self.actualizar_total_pedido()
            self.trago_cantidad.delete(0, "end")
            self.trago_cantidad.insert(0, "1")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el trago: {str(e)}")

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
            # Obtener cliente desde la API
            r = requests.get(f"http://localhost:8000/api/v1/disco/clientes?rut={cliente_rut}")
            if r.status_code == 200 and r.json():
                cliente = r.json()[0]
            else:
                messagebox.showerror("Error", "Cliente no encontrado")
                return

            builder = PedidoBuilder().set_cliente(cliente['id'])
            detalles_list = []

            for item in items:
                values = self.pedido_tree.item(item, "values")
                trago_nombre = values[0]
                cantidad = int(values[1])
                # Obtener trago desde la API
                resp = requests.get(f"http://localhost:8000/api/v1/disco/tragos?nombre={trago_nombre}")
                if resp.status_code == 200 and resp.json():
                    trago = resp.json()[0]
                else:
                    messagebox.showerror("Error", f"Trago '{trago_nombre}' no encontrado")
                    return
                builder.add_detalle(trago['id'], cantidad, trago['precio'])
                detalles_list.append({
                    "trago_id": trago['id'],
                    "cantidad": cantidad,
                    "precio_unitario": trago['precio']
                })

            pedido_data = builder.build()

            payload = {
                "cliente_id": pedido_data["cliente_id"],
                "total": pedido_data["total"],
                "detalles": detalles_list
            }
            resp = requests.post("http://localhost:8000/api/v1/disco/pedidos", json=payload)
            if resp.status_code == 201:
                messagebox.showinfo("Éxito", f"Pedido registrado correctamente")
                self.limpiar_pedido()
            else:
                messagebox.showerror("Error", f"No se pudo registrar el pedido: {resp.text}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo completar el pedido: {str(e)}")

    def generar_boleta_tragos(self, pedido_id):
        # Aquí deberías obtener el pedido y cliente desde la API si existe endpoint
        messagebox.showinfo("Info", "Generación de boleta pendiente de integración con la API de pedidos.")

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
        def task():
            try:
                r = requests.get("http://localhost:8000/api/v1/disco/clientes?limit=1000&offset=0")
                if r.status_code == 200:
                    clientes = r.json()
                    valores = [f"{c['nombre']} ({c['rut']})" for c in clientes]
                    self.parent.after(0, lambda: self.lista_clientes.configure(values=valores))
                else:
                    self.parent.after(0, lambda: self.lista_clientes.configure(values=[]))
            except Exception:
                self.parent.after(0, lambda: self.lista_clientes.configure(values=[]))
        threading.Thread(target=task).start()

    def filtrar_clientes(self, event):
        def task():
            busqueda = self.busqueda_cliente.get().lower()
            try:
                r = requests.get("http://localhost:8000/api/v1/disco/clientes?limit=1000&offset=0")
                if r.status_code == 200:
                    clientes = r.json()
                    if busqueda:
                        filtrados = [f"{c['nombre']} ({c['rut']})" for c in clientes if busqueda in c['nombre'].lower() or busqueda in c['rut']]
                    else:
                        filtrados = [f"{c['nombre']} ({c['rut']})" for c in clientes]
                    self.parent.after(0, lambda: [self.lista_clientes.configure(values=filtrados), self.lista_clientes.set("")])
                else:
                    self.parent.after(0, lambda: [self.lista_clientes.configure(values=[]), self.lista_clientes.set("")])
            except Exception:
                self.parent.after(0, lambda: [self.lista_clientes.configure(values=[]), self.lista_clientes.set("")])
        threading.Thread(target=task).start()

    def actualizar_lista_tragos_combo(self):
        def task():
            try:
                r = requests.get(f"{API_TRAGOS_URL}?limit=1000&offset=0")
                if r.status_code == 200:
                    tragos = r.json()
                    valores = [f"{t['nombre']} (${t['precio']:.2f})" for t in tragos]
                    self.parent.after(0, lambda: self.lista_tragos.configure(values=valores))
                else:
                    self.parent.after(0, lambda: self.lista_tragos.configure(values=[]))
            except Exception:
                self.parent.after(0, lambda: self.lista_tragos.configure(values=[]))
        threading.Thread(target=task).start()

    def filtrar_tragos(self, event):
        def task():
            busqueda = self.busqueda_trago.get().lower()
            try:
                r = requests.get(f"{API_TRAGOS_URL}?limit=1000&offset=0")
                if r.status_code == 200:
                    tragos = r.json()
                    if busqueda:
                        filtrados = [f"{t['nombre']} (${t['precio']:.2f})" for t in tragos if busqueda in t['nombre'].lower() or (t.get('categoria','').lower() if t.get('categoria') else "")]
                    else:
                        filtrados = [f"{t['nombre']} (${t['precio']:.2f})" for t in tragos]
                    self.parent.after(0, lambda: [self.lista_tragos.configure(values=filtrados), self.lista_tragos.set("")])
                else:
                    self.parent.after(0, lambda: [self.lista_tragos.configure(values=[]), self.lista_tragos.set("")])
            except Exception:
                self.parent.after(0, lambda: [self.lista_tragos.configure(values=[]), self.lista_tragos.set("")])
        threading.Thread(target=task).start()

    def obtener_trago_por_nombre(self, nombre, callback):
        def task():
            try:
                r = requests.get(f"{API_TRAGOS_URL}?limit=1000&offset=0")
                if r.status_code == 200:
                    tragos = r.json()
                    trago = next((t for t in tragos if t['nombre'] == nombre), None)
                    self.parent.after(0, lambda: callback(trago))
                else:
                    self.parent.after(0, lambda: callback(None))
            except Exception:
                self.parent.after(0, lambda: callback(None))
        threading.Thread(target=task).start()

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