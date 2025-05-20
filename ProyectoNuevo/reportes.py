import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from database import get_db, engine
from models_folder.models_reporte import ReporteError
from report_database import get_report_db, init_report_db

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------- Dominio ----------
class Reporte:
    def __init__(self, titulo, modulo, urgencia, descripcion, reportado_por, estado="Abierto"):
        self.titulo = titulo
        self.modulo = modulo
        self.urgencia = urgencia
        self.descripcion = descripcion
        self.estado = estado
        self.reportado_por = reportado_por

# ---------- Infraestructura ----------
class IReporteRepository(ABC):
    @abstractmethod
    def crear(self, reporte: Reporte) -> int:
        pass
        
    @abstractmethod
    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        pass
        
    @abstractmethod
    def obtener_por_filtros(self, filtros: dict) -> list:
        pass

class SQLAlchemyReporteRepository(IReporteRepository):
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def crear(self, reporte: Reporte) -> int:
        entidad = ReporteError(
            titulo=reporte.titulo,
            modulo=reporte.modulo,
            urgencia=reporte.urgencia,
            descripcion=reporte.descripcion,
            estado=reporte.estado,
            reportado_por=reporte.reportado_por
        )
        self.db.add(entidad)
        self.db.commit()
        return entidad.id
        
    def actualizar_estado(self, id_reporte: int, nuevo_estado: str) -> bool:
        reporte = self.db.query(ReporteError).get(id_reporte)
        if reporte:
            reporte.estado = nuevo_estado
            self.db.commit()
            return True
        return False
        
    def obtener_por_filtros(self, filtros: dict) -> list:
        query = self.db.query(ReporteError)
        
        if filtros.get('modulo') and filtros['modulo'] != "Todos":
            query = query.filter(ReporteError.modulo == filtros['modulo'])
            
        if filtros.get('urgencia') and filtros['urgencia'] != "Todos":
            query = query.filter(ReporteError.urgencia == filtros['urgencia'])
            
        if filtros.get('estado') and filtros['estado'] != "Todos":
            query = query.filter(ReporteError.estado == filtros['estado'])
            
        if filtros.get('usuario') and filtros['usuario'] != "Todos":
            query = query.filter(ReporteError.reportado_por == filtros['usuario'])
            
        return query.order_by(ReporteError.fecha_reporte.desc()).all()

# ---------- Aplicación ----------
class ReporteService:
    def __init__(self, repository: IReporteRepository):
        self.repository = repository
        
    def crear_reporte(self, datos: dict) -> tuple[bool, str]:
        if not all(datos.values()):
            return False, "Todos los campos son obligatorios"
            
        try:
            reporte = Reporte(
                titulo=datos['titulo'],
                modulo=datos['modulo'],
                urgencia=datos['urgencia'],
                descripcion=datos['descripcion'],
                reportado_por=datos['usuario']
            )
            id_reporte = self.repository.crear(reporte)
            return True, f"Reporte {id_reporte} creado exitosamente"
        except Exception as e:
            return False, f"Error al crear reporte: {str(e)}"
            
    def actualizar_estados(self, ids: list[int], nuevo_estado: str) -> tuple[bool, str]:
        if not ids:
            return False, "No hay reportes seleccionados"
            
        try:
            success_count = 0
            for id_reporte in ids:
                if self.repository.actualizar_estado(id_reporte, nuevo_estado):
                    success_count += 1
            
            if success_count == 0:
                return False, "No se actualizó ningún reporte"
                
            return True, f"Se actualizaron {success_count} reportes a '{nuevo_estado}'"
        except Exception as e:
            return False, f"Error al actualizar estados: {str(e)}"
            
    def obtener_reportes(self, filtros: dict) -> list:
        return self.repository.obtener_por_filtros(filtros)

# ---------- Interfaz ----------
class ReportesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dormilon Admin APP - Reportes de Errores")
        self.geometry("1100x750")
        self.configure(fg_color="#1e1e2d")
        
        # Configuración de dependencias
        init_report_db()
        db_session = next(get_report_db())
        repository = SQLAlchemyReporteRepository(db_session)
        self.reporte_service = ReporteService(repository)
        
        # Datos de la interfaz
        self.usuarios_disponibles = ["Admin", "Manager", "Recepcionista", "Cocina", "Limpieza", "Seguridad", "Otro"]
        self.reportes_seleccionados = {}
        
        # Inicializar interfaz
        self.create_widgets()
    
    # [Métodos de creación de widgets se mantienen iguales hasta enviar_reporte]
    
    def enviar_reporte(self):
        datos = {
            'titulo': self.reporte_titulo.get(),
            'modulo': self.reporte_modulo.get(),
            'urgencia': self.reporte_urgencia.get(),
            'descripcion': self.reporte_descripcion.get("1.0", "end-1c"),
            'usuario': self.reporte_usuario.get()
        }
        
        success, msg = self.reporte_service.crear_reporte(datos)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.limpiar_formulario()
            self.cargar_reportes()
        else:
            messagebox.showerror("Error", msg)
    
    def cargar_reportes(self):
        filtros = {
            'modulo': self.filtro_modulo.get(),
            'urgencia': self.filtro_urgencia.get(),
            'estado': self.filtro_estado.get(),
            'usuario': self.filtro_usuario.get()
        }
        
        try:
            reportes = self.reporte_service.obtener_reportes(filtros)
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
            
            success, msg = self.reporte_service.actualizar_estados(ids_seleccionados, nuevo_estado)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.cargar_reportes()
            else:
                messagebox.showerror("Error", msg)
        
        ctk.CTkButton(dialog, text="Aplicar", command=aplicar_cambios).pack(pady=10)

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
        self.reporte_usuario = ctk.CTkComboBox(form_frame, values=self.usuarios_disponibles)
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
        self.filtro_estado.set("Todos")
        
        self.filtro_usuario = ctk.CTkComboBox(
            filter_frame,
            values=["Todos"] + self.usuarios_disponibles,
            width=120
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
        anchos = [50, 200, 100, 80, 100, 120, 150, 100]
        
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
            
            # Botón de selección para cambiar estado
            seleccionado = ctk.CTkCheckBox(frame_fila, text="", width=30)
            seleccionado.grid(row=0, column=7, padx=5, sticky="e")
            self.reportes_seleccionados[reporte[0]] = seleccionado
    
    def enviar_reporte(self):
        usuario = self.reporte_usuario.get()
        titulo = self.reporte_titulo.get()
        modulo = self.reporte_modulo.get()
        urgencia = self.reporte_urgencia.get()
        descripcion = self.reporte_descripcion.get("1.0", "end-1c")
        
        if not usuario or not titulo or not descripcion:
            messagebox.showwarning("Campos incompletos", "Por favor complete todos los campos obligatorios")
            return
        
        try:
            nuevo_reporte = ReporteError(
                titulo=titulo,
                modulo=modulo,
                urgencia=urgencia,
                descripcion=descripcion,
                estado="Abierto",  # Estado por defecto
                reportado_por=usuario
            )
            
            self.db.add(nuevo_reporte)
            self.db.commit()
            
            messagebox.showinfo("Éxito", "Reporte enviado correctamente")
            self.limpiar_formulario()
            self.cargar_reportes()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"No se pudo enviar el reporte: {str(e)}")
        finally:
            self.db.close()
    
    def limpiar_formulario(self):
        self.reporte_usuario.set("")
        self.reporte_titulo.delete(0, "end")
        self.reporte_modulo.set("Restaurante")
        self.reporte_urgencia.set("Baja")
        self.reporte_descripcion.delete("1.0", "end")
    
    def cargar_reportes(self):
        try:
            db = next(get_report_db())
            
            modulo = self.filtro_modulo.get()
            urgencia = self.filtro_urgencia.get()
            estado = self.filtro_estado.get()
            usuario = self.filtro_usuario.get()
            
            query = db.query(ReporteError)
            
            if modulo != "Todos":
                query = query.filter(ReporteError.modulo == modulo)
            
            if urgencia != "Todos":
                query = query.filter(ReporteError.urgencia == urgencia)
            
            if estado != "Todos":
                query = query.filter(ReporteError.estado == estado)
            
            if usuario != "Todos":
                query = query.filter(ReporteError.reportado_por == usuario)
            
            reportes = query.order_by(ReporteError.fecha_reporte.desc()).all()
            
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
        finally:
            db.close()
    
    def actualizar_estado_reportes(self):
        try:
            db = next(get_report_db())
            
            ids_seleccionados = [id_reporte for id_reporte, checkbox in self.reportes_seleccionados.items() if checkbox.get()]
            
            if not ids_seleccionados:
                messagebox.showwarning("Nada seleccionado", "Por favor seleccione al menos un reporte para actualizar")
                return
            
            # Crear ventana de diálogo personalizada
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
                
                try:
                    for id_reporte in ids_seleccionados:
                        reporte = db.query(ReporteError).filter(ReporteError.id == int(id_reporte)).first()
                        if reporte:
                            reporte.estado = nuevo_estado
                    
                    db.commit()
                    messagebox.showinfo("Éxito", f"Se actualizaron {len(ids_seleccionados)} reportes a '{nuevo_estado}'")
                    self.cargar_reportes()
                    
                except Exception as e:
                    db.rollback()
                    messagebox.showerror("Error", f"No se pudieron actualizar los reportes: {str(e)}")
                finally:
                    db.close()
            
            ctk.CTkButton(
                dialog,
                text="Aplicar",
                command=aplicar_cambios
            ).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el diálogo: {str(e)}")
    
if __name__ == "__main__":
    app = ReportesApp()
    app.mainloop()