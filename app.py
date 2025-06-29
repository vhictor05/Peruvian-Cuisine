import customtkinter as ctk
import subprocess
import sys
import os
from tkinter import messagebox
from PIL import Image, ImageTk

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
      
class ModuleLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title("Dormilon Admin APP - Sistema de Gestión")
        self.geometry("800x600")
        self.configure(fg_color="#1e1e2d")
        
        # Crear estructura de la interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Encabezado con logo y título
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Logo (puedes reemplazar con tu propio logo)
        try:
            logo_img = ctk.CTkImage(light_image=Image.open("logo.png"),
                                  dark_image=Image.open("logo.png"),
                                  size=(80, 80))
            logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
            logo_label.pack(side="left", padx=(0, 20))
        except:
            pass  # Si no hay imagen, continuar sin logo
        
        # Título principal
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            title_frame, 
            text="Dormilon Admin App", 
            font=("Arial", 28, "bold"),
            text_color="#4cc9f0"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame, 
            text="Sistema Integrado de Gestión", 
            font=("Arial", 16),
            text_color="#a5a8b3"
        ).pack(anchor="w")
        
        # Botón de cerrar
        close_btn = ctk.CTkButton(
            header_frame,
            text="✕",
            command=self.destroy,
            width=40,
            height=40,
            fg_color="transparent",
            hover_color="#ff4757",
            font=("Arial", 18),
            text_color="#ffffff"
        )
        close_btn.pack(side="right")
        
        # Mensaje de bienvenida
        welcome_frame = ctk.CTkFrame(main_frame, fg_color="#25253a", corner_radius=15)
        welcome_frame.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(
            welcome_frame,
            text="¡Bienvenido al sistema de gestión de Dormilon Industries!",
            font=("Arial", 14),
            text_color="#f8f9fa",
            wraplength=700
        ).pack(padx=20, pady=15)
        
        # Tarjetas de módulos
        modules_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        modules_frame.pack(fill="both", expand=True)
        
        # Configuración de las tarjetas
        modules = [
            {
                "name": "Restaurante",
                "file": "restaurant.py",
                "color": "#4361ee",
                "desc": "Gestión de menús, pedidos y clientes del restaurante"
            },
            {
                "name": "Discoteca",
                "file": "disco.py",
                "color": "#7209b7",
                "desc": "Control de eventos, tragos y reservas en la discoteca"
            },
            {
                "name": "Hotel",
                "file": "hotel.py",
                "color": "#f72585",
                "desc": "Administración de habitaciones, huéspedes y reservas"
            },
            {
                "name": "Reportes de Errores",
                "file": "reportes.py",
                "color": "#4cc9f0",
                "desc": "Sistema de reporte y seguimiento de incidencias"
            }

        ]
        
        # Crear tarjetas en una cuadrícula
        for i, module in enumerate(modules):
            card = ctk.CTkFrame(
                modules_frame,
                border_width=2,
                border_color=module["color"],
                corner_radius=15,
                fg_color="#25253a"
            )
            card.grid(
                row=i//2, 
                column=i%2, 
                padx=15, 
                pady=15, 
                sticky="nsew"
            )
            
            # Configurar expansión uniforme
            modules_frame.grid_columnconfigure(i%2, weight=1)
            modules_frame.grid_rowconfigure(i//2, weight=1)
            
            # Contenido de la tarjeta
            ctk.CTkLabel(
                card,
                text=module["name"],
                font=("Arial", 20, "bold"),
                text_color=module["color"]
            ).pack(pady=(15, 5), padx=20)
            
            ctk.CTkLabel(
                card,
                text=module["desc"],
                font=("Arial", 12),
                text_color="#adb5bd",
                wraplength=300
            ).pack(pady=(0, 15), padx=20)
            
            ctk.CTkButton(
                card,
                text="Abrir Módulo",
                command=lambda m=module: self.launch_module(m["file"]),
                fg_color=module["color"],
                hover_color=module["color"],  # ✅ corregido
                font=("Arial", 14),
                height=40,
                corner_radius=10
            ).pack(pady=(0, 15), padx=20, fill="x")     
        
    def launch_module(self, module_file):
        # Ruta relativa a la subcarpeta ProyectoNuevo
        module_path = os.path.join(".", module_file)
        
        if not os.path.exists(module_path):
            messagebox.showerror("Error", 
                               f"No se encontró {module_file} en:\n{os.path.abspath(module_path)}")
            return

        try:
            self.destroy()
            subprocess.run([sys.executable, module_path], check=True)
            ModuleLauncherApp().mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el módulo:\n{str(e)}")

if __name__ == "__main__":
    app = ModuleLauncherApp()
    app.mainloop()