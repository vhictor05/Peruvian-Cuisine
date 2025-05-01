import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sqlite3
from sqlalchemy.orm import Session
from database import get_db,Base,engine
from models_folder.models_reporte import Base, ReporteError

Base.metadata.create_all(bind=engine)

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ReportesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PRIVITAIN CUISINE - Reportes de Errores")
        self.geometry("1000x700")
        self.configure(fg_color="#1e1e2d")
        
        # Conexión a la base de datos
        self.db: Session = next(get_db())
        
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
        
        # Tabla de reportes
        self.reportes_tree = ctk.CTkFrame(tab)
        self.reportes_tree.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Aquí iría la implementación de la tabla real usando CTkTable o similar
        # Por ahora es un placeholder
        ctk.CTkLabel(
            self.reportes_tree, 
            text="Tabla de reportes aparecerá aquí\n(En desarrollo)",
            font=("Arial", 16),
            text_color="#a5a8b3"
        ).pack(expand=True)
    
    def enviar_reporte(self):
        titulo = self.reporte_titulo.get()
        modulo = self.reporte_modulo.get()
        urgencia = self.reporte_urgencia.get()
        descripcion = self.reporte_descripcion.get("1.0", "end-1c")
        
        if not titulo or not descripcion:
            messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos obligatorios")
            return
        
        try:
            # Aquí iría la lógica para guardar en la base de datos
            # Por ahora es solo un mock
            reporte_data = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "titulo": titulo,
                "modulo": modulo,
                "urgencia": urgencia,
                "descripcion": descripcion,
                "estado": "Abierto",
                "reportado_por": "Usuario Actual"  # Debería obtenerse del sistema de autenticación
            }
            
            # Guardar en base de datos (implementación pendiente)
            # self.guardar_reporte_en_db(reporte_data)
            
            messagebox.showinfo("Éxito", "Reporte enviado correctamente")
            self.limpiar_formulario()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el reporte: {str(e)}")
    
    def limpiar_formulario(self):
        self.reporte_titulo.delete(0, "end")
        self.reporte_modulo.set("")
        self.reporte_urgencia.set("Baja")
        self.reporte_descripcion.delete("1.0", "end")
    
    def cargar_reportes(self):
        # Implementación pendiente para cargar reportes filtrados
        pass

if __name__ == "__main__":
    app = ReportesApp()
    app.mainloop()