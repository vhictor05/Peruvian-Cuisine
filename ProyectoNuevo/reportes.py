import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db, engine
from models_folder.models_reporte import ReporteError
from report_database import get_report_db, init_report_db
from models_folder.models_reporte import ReporteError

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ReportesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dormilon Admin APP - Reportes de Errores")
        self.geometry("1000x700")
        self.configure(fg_color="#1e1e2d")
        
        init_report_db()
        # Conexión a la base de datos de reportes
        self.db = next(get_report_db())
        # Crear estructura de la interfaz
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
        ctk.CTkLabel(form_frame, text="Título del Reporte:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.reporte_titulo = ctk.CTkEntry(form_frame, width=400)
        self.reporte_titulo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Módulo afectado:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.reporte_modulo = ctk.CTkComboBox(form_frame, values=["Restaurante", "Discoteca", "Hotel", "General"])
        self.reporte_modulo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Nivel de urgencia:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.reporte_urgencia = ctk.CTkComboBox(form_frame, values=["Baja", "Media", "Alta", "Crítica"])
        self.reporte_urgencia.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Descripción detallada:").grid(row=3, column=0, padx=10, pady=10, sticky="nw")
        self.reporte_descripcion = ctk.CTkTextbox(form_frame, width=400, height=200)
        self.reporte_descripcion.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        
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
        
        self.filtro_modulo = ctk.CTkComboBox(
            filter_frame, 
            values=["Todos", "Restaurante", "Discoteca", "Hotel", "General"],
            width=120
        )
        self.filtro_modulo.pack(side="left", padx=5)
        self.filtro_modulo.set("Todos")
        
        self.filtro_urgencia = ctk.CTkComboBox(
            filter_frame, 
            values=["Todos", "Baja", "Media", "Alta", "Crítica"],
            width=100
        )
        self.filtro_urgencia.pack(side="left", padx=5)
        self.filtro_urgencia.set("Todos")
        
        self.filtro_estado = ctk.CTkComboBox(
            filter_frame, 
            values=["Todos", "Abierto", "En progreso", "Resuelto"],
            width=120
        )
        self.filtro_estado.pack(side="left", padx=5)
        self.filtro_estado.set("Abierto")
        
        ctk.CTkButton(
            filter_frame,
            text="Aplicar Filtros",
            command=self.cargar_reportes,
            width=100
        ).pack(side="left", padx=10)
        
        # Contenedor para la tabla
        self.tabla_container = ctk.CTkScrollableFrame(tab)
        self.tabla_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Encabezados de la tabla
        self.crear_encabezados_tabla()
        
        # Frame para los datos
        self.tabla_datos_frame = ctk.CTkFrame(self.tabla_container, fg_color="transparent")
        self.tabla_datos_frame.pack(fill="both", expand=True)
        
        # Cargar datos iniciales
        self.cargar_reportes()
    
    def crear_encabezados_tabla(self):
        # Frame para los encabezados
        encabezados_frame = ctk.CTkFrame(self.tabla_container, fg_color="#4cc9f0", height=40)
        encabezados_frame.pack(fill="x", pady=(0, 5))
        
        # Columnas
        columnas = ["ID", "Título", "Módulo", "Urgencia", "Estado", "Fecha", "Reportado por"]
        anchos = [50, 200, 100, 80, 100, 120, 150]
        
        for i, (columna, ancho) in enumerate(zip(columnas, anchos)):
            ctk.CTkLabel(
                encabezados_frame,
                text=columna,
                text_color="white",
                font=("Arial", 12, "bold"),
                width=ancho
            ).grid(row=0, column=i, padx=2, sticky="w")
    
    def mostrar_datos_tabla(self, datos):
        # Limpiar datos anteriores
        for widget in self.tabla_datos_frame.winfo_children():
            widget.destroy()
        
        # Mostrar nuevos datos
        for i, fila in enumerate(datos):
            frame_fila = ctk.CTkFrame(self.tabla_datos_frame, fg_color="#2a2a3a" if i % 2 == 0 else "#1e1e2d")
            frame_fila.pack(fill="x", pady=1)
            
            for j, valor in enumerate(fila):
                ctk.CTkLabel(
                    frame_fila,
                    text=valor,
                    text_color="white",
                    font=("Arial", 12),
                    anchor="w",
                    width=50 if j == 0 else 200 if j == 1 else 100 if j == 2 else 80 if j == 3 else 100 if j == 4 else 120 if j == 5 else 150
                ).grid(row=0, column=j, padx=2, sticky="w")
    
    def enviar_reporte(self):
        titulo = self.reporte_titulo.get()
        modulo = self.reporte_modulo.get()
        urgencia = self.reporte_urgencia.get()
        descripcion = self.reporte_descripcion.get("1.0", "end-1c")
        
        if not titulo or not descripcion:
            messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos obligatorios")
            return
        
        try:
            # Crear nuevo reporte
            nuevo_reporte = ReporteError(
                titulo=titulo,
                modulo=modulo,
                urgencia=urgencia,
                descripcion=descripcion,
                estado="Abierto",
                reportado_por="Usuario Actual"  # En un sistema real, obtendrías esto del auth
            )
            
            # Guardar en base de datos
            self.db.add(nuevo_reporte)
            self.db.commit()
            
            messagebox.showinfo("Éxito", "Reporte enviado correctamente")
            self.limpiar_formulario()
            self.cargar_reportes()  # Actualizar la tabla
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"No se pudo enviar el reporte: {str(e)}")
        finally:
            self.db.close()
    
    def limpiar_formulario(self):
        self.reporte_titulo.delete(0, "end")
        self.reporte_modulo.set("")
        self.reporte_urgencia.set("Baja")
        self.reporte_descripcion.delete("1.0", "end")
    
    def cargar_reportes(self):
        try:
            # Obtener nueva conexión a la base de datos
            db = next(get_report_db())
            
            # Obtener filtros
            modulo = self.filtro_modulo.get()
            urgencia = self.filtro_urgencia.get()
            estado = self.filtro_estado.get()
            
            # Construir query
            query = db.query(ReporteError)
            
            if modulo != "Todos":
                query = query.filter(ReporteError.modulo == modulo)
            
            if urgencia != "Todos":
                query = query.filter(ReporteError.urgencia == urgencia)
            
            if estado != "Todos":
                query = query.filter(ReporteError.estado == estado)
            
            # Ordenar por fecha descendente
            reportes = query.order_by(ReporteError.fecha_reporte.desc()).all()
            
            # Preparar datos para la tabla
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
            
            # Mostrar datos en la tabla
            if datos_tabla:
                self.mostrar_datos_tabla(datos_tabla)
            else:
                self.mostrar_datos_tabla([["No hay datos coincidentes"] * 7])
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los reportes: {str(e)}")
        finally:
            db.close()

if __name__ == "__main__":
    app = ReportesApp()
    app.mainloop()