import customtkinter as ctk
from tkinter import messagebox
from estructura.facade.reporte_facade import ReporteFacade
from apps.Reportes.dominio import Reporte

class ReportesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dormilon Admin APP - Reportes de Errores")
        self.geometry("1100x750")
        self.configure(fg_color="#1e1e2d")
        self.facade = ReporteFacade()
        self.reportes_seleccionados = {}
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezado
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            header_frame,
            text="Reportes de Errores",
            font=("Arial", 24, "bold"),
            text_color="#4cc9f0"
        ).pack(side="left")

        # Botón de cerrar
        close_btn = ctk.CTkButton(
            header_frame,
            text="Cerrar Módulo",
            command=self.destroy,
            width=100,
            height=30,
            fg_color="#ff4757",
            hover_color="#ff6b81",
            font=("Arial", 12)
        )
        close_btn.pack(side="right")

        # Pestañas
        tabview = ctk.CTkTabview(main_frame)
        tabview.pack(fill="both", expand=True)

        tabview.add("Nuevo Reporte")
        tabview.add("Reportes Existentes")

        # Pestaña de Nuevo Reporte
        self.setup_nuevo_reporte_tab(tabview.tab("Nuevo Reporte"))

        # Pestaña de Reportes Existentes
        self.setup_reportes_tab(tabview.tab("Reportes Existentes"))

    def setup_nuevo_reporte_tab(self, tab):
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=20, pady=20)

        # Campos del formulario
        ctk.CTkLabel(form_frame, text="Reportado por:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.reporte_usuario = ctk.CTkComboBox(form_frame, values=self.facade.obtener_usuarios())
        self.reporte_usuario.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Título del Reporte:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.reporte_titulo = ctk.CTkEntry(form_frame, width=400)
        self.reporte_titulo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Módulo afectado:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.reporte_modulo = ctk.CTkComboBox(form_frame, values=["Restaurante", "Discoteca", "Hotel", "General"])
        self.reporte_modulo.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Nivel de urgencia:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.reporte_urgencia = ctk.CTkComboBox(form_frame, values=["Baja", "Media", "Alta", "Crítica"])
        self.reporte_urgencia.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Descripción detallada:").grid(row=4, column=0, padx=10, pady=10, sticky="nw")
        self.reporte_descripcion = ctk.CTkTextbox(form_frame, width=400, height=200)
        self.reporte_descripcion.grid(row=4, column=1, padx=10, pady=10, sticky="nsew")

        # Botón de enviar
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Enviar Reporte",
            command=self.enviar_reporte,
            fg_color="#4cc9f0",
            hover_color="#3aa8d9",
            font=("Arial", 14),
            height=40
        ).pack(pady=10)

    def setup_reportes_tab(self, tab):
        # Frame de filtros
        filter_frame = ctk.CTkFrame(tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(filter_frame, text="Filtrar por:").pack(side="left", padx=(0, 10))

        opciones_filtro = self.facade.get_opciones_filtro()

        self.filtro_modulo = ctk.CTkComboBox(
            filter_frame, values=opciones_filtro['modulo'], width=120
        )
        self.filtro_modulo.pack(side="left", padx=5)
        self.filtro_modulo.set("Todos")

        self.filtro_urgencia = ctk.CTkComboBox(
            filter_frame, values=opciones_filtro['urgencia'], width=100
        )
        self.filtro_urgencia.pack(side="left", padx=5)
        self.filtro_urgencia.set("Todos")

        self.filtro_estado = ctk.CTkComboBox(
            filter_frame, values=opciones_filtro['estado'], width=120
        )
        self.filtro_estado.pack(side="left", padx=5)
        self.filtro_estado.set("Todos")

        self.filtro_usuario = ctk.CTkComboBox(
            filter_frame, values=opciones_filtro['usuario'], width=120
        )
        self.filtro_usuario.pack(side="left", padx=5)
        self.filtro_usuario.set("Todos")

        ctk.CTkButton(
            filter_frame,
            text="Aplicar Filtros",
            command=self.cargar_reportes,
            width=100
        ).pack(side="left", padx=10)

        # Botón para actualizar estado
        self.actualizar_btn = ctk.CTkButton(
            filter_frame,
            text="Cambiar Estado",
            command=self.actualizar_estado_reportes,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=120
        )
        self.actualizar_btn.pack(side="right", padx=10)

        # Botón para eliminar
        self.eliminar_btn = ctk.CTkButton(
            filter_frame,
            text="Eliminar",
            command=self.eliminar_reportes,
            fg_color="#ff4757",
            hover_color="#ff6b81",
            width=100
        )
        self.eliminar_btn.pack(side="right", padx=10)

        # Contenedor para la tabla
        self.tabla_container = ctk.CTkScrollableFrame(tab)
        self.tabla_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Encabezados de la tabla
        self.crear_encabezados_tabla()

        # Frame para los datos
        self.tabla_datos_frame = ctk.CTkFrame(self.tabla_container, fg_color="transparent")
        self.tabla_datos_frame.pack(fill="both", expand=True)

        # Diccionario para checkboxes
        self.reportes_seleccionados = {}

        # Cargar datos iniciales
        self.cargar_reportes()

    def crear_encabezados_tabla(self):
        encabezados_frame = ctk.CTkFrame(self.tabla_container, fg_color="#4cc9f0", height=40)
        encabezados_frame.pack(fill="x", pady=(0, 5))

        columnas = ["ID", "Título", "Módulo", "Urgencia", "Estado", "Fecha", "Reportado por", "Acciones"]
        anchos = [50, 200, 100, 80, 100, 120, 150, 150]

        for i, (columna, ancho) in enumerate(zip(columnas, anchos)):
            ctk.CTkLabel(
                encabezados_frame,
                text=columna,
                text_color="white",
                font=("Arial", 12, "bold"),
                width=ancho
            ).grid(row=0, column=i, padx=2, sticky="w")

    def mostrar_datos_tabla(self, datos):
        for widget in self.tabla_datos_frame.winfo_children():
            widget.destroy()

        self.reportes_seleccionados = {}

        for i, reporte in enumerate(datos):
            frame_fila = ctk.CTkFrame(self.tabla_datos_frame, fg_color="#2a2a3a" if i % 2 == 0 else "#1e1e2d")
            frame_fila.pack(fill="x", pady=1)

            # Mostrar datos en columnas
            for j, valor in enumerate(reporte):
                ctk.CTkLabel(
                    frame_fila,
                    text=valor,
                    text_color="white",
                    font=("Arial", 12),
                    anchor="w",
                    width=50 if j == 0 else 200 if j == 1 else 100 if j == 2 else 80 if j == 3 else 100 if j == 4 else 120 if j == 5 else 150
                ).grid(row=0, column=j, padx=2, sticky="w")

            # Frame para los botones de acción
            acciones_frame = ctk.CTkFrame(frame_fila, fg_color="transparent")
            acciones_frame.grid(row=0, column=7, padx=5, sticky="e")

            # Checkbox de selección
            seleccionado = ctk.CTkCheckBox(acciones_frame, text="", width=30)
            seleccionado.pack(side="left", padx=5)
            self.reportes_seleccionados[reporte[0]] = seleccionado

    def enviar_reporte(self):
        try:
            builder = (Reporte.builder()
                .con_titulo(self.reporte_titulo.get())
                .en_modulo(self.reporte_modulo.get())
                .con_urgencia(self.reporte_urgencia.get())
                .con_descripcion(self.reporte_descripcion.get("1.0", "end-1c"))
                .reportado_por(self.reporte_usuario.get()))

            reporte = builder.build()  # First build the reporte object
            datos = {
                'titulo': reporte.titulo,
                'modulo': reporte.modulo,
                'urgencia': reporte.urgencia,
                'descripcion': reporte.descripcion,
                'usuario': reporte.reportado_por  # Note: use reportado_por, not usuario_reporte
            }

            success, msg = self.facade.crear_reporte(datos)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.limpiar_formulario()
                self.cargar_reportes()
            else:
                messagebox.showerror("Error", msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}")

    def limpiar_formulario(self):
        self.reporte_usuario.set("")
        self.reporte_titulo.delete(0, "end")
        self.reporte_modulo.set("Restaurante")
        self.reporte_urgencia.set("Baja")
        self.reporte_descripcion.delete("1.0", "end")

    def cargar_reportes(self):
        filtros = {
            'modulo': self.filtro_modulo.get(),
            'urgencia': self.filtro_urgencia.get(),
            'estado': self.filtro_estado.get(),
            'usuario': self.filtro_usuario.get()
        }

        try:
            reportes = self.facade.obtener_reportes_filtrados(filtros)
            datos_tabla = []
            for reporte in reportes:
                datos_tabla.append([
                    str(reporte.id),
                    reporte.titulo[:30] + "..." if len(reporte.titulo) > 30 else reporte.titulo,
                    reporte.modulo,
                    reporte.urgencia,
                    reporte.estado,
                    reporte.fecha_reporte.strftime("%Y-%m-%d %H:%M"),
                    reporte.reportado_por
                ])
            if datos_tabla:
                self.mostrar_datos_tabla(datos_tabla)
            else:
                self.mostrar_datos_tabla([["", "No hay datos coincidentes", "", "", "", "", "", ""]])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los reportes: {str(e)}")

    def actualizar_estado_reportes(self):
        ids_seleccionados = [int(id_reporte) for id_reporte, checkbox in self.reportes_seleccionados.items() if checkbox.get()]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Seleccionar nuevo estado")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Seleccione el nuevo estado:").pack(pady=10)

        estado_var = ctk.StringVar(value="Abierto")
        opciones = ["Abierto", "En progreso", "Resuelto"]

        for opcion in opciones:
            ctk.CTkRadioButton(
                dialog,
                text=opcion,
                variable=estado_var,
                value=opcion
            ).pack(anchor="w", padx=20)

        def aplicar_cambios():
            nuevo_estado = estado_var.get()
            dialog.destroy()

            success, msg = self.facade.actualizar_estados(ids_seleccionados, nuevo_estado)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.cargar_reportes()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(dialog, text="Aplicar", command=aplicar_cambios).pack(pady=10)

    def eliminar_reportes(self):
        ids_seleccionados = [int(id_reporte) for id_reporte, checkbox in self.reportes_seleccionados.items() if checkbox.get()]

        if not ids_seleccionados:
            messagebox.showwarning("Advertencia", "No hay reportes seleccionados para eliminar")
            return

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar {len(ids_seleccionados)} reporte(s)? Esta acción no se puede deshacer."
        )

        if confirmacion:
            success, msg = self.facade.eliminar_reporte(ids_seleccionados)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.cargar_reportes()
            else:
                messagebox.showerror("Error", msg)