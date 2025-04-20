import customtkinter as ctk
import subprocess
import sys
import os
from tkinter import messagebox
from PIL import Image

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModuleLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Selección de Módulo")
        self.geometry("400x300")
        self.configure(fg_color="#1c1c1c")

        # Carga imágenes desde la carpeta icons
        icons_path = os.path.join("ProyectoNuevo", "icons")
        self.restaurant_icon = ctk.CTkImage(Image.open(os.path.join(icons_path, "restaurant.png")), size=(30, 30))
        self.disco_icon = ctk.CTkImage(Image.open(os.path.join(icons_path, "disco.png")), size=(30, 30))
        self.hotel_icon = ctk.CTkImage(Image.open(os.path.join(icons_path, "hotel.png")), size= (30, 30))

        # Título
        self.label_title = ctk.CTkLabel(self, text="¡Bienvenido! Elige una opción.", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        # Botones y sus iconos
        self.create_module_button("Restaurante", "restaurant.py", self.restaurant_icon)
        self.create_module_button("Disco", "disco.py", self.disco_icon)
        self.create_module_button("Hotel", "hotel.py", self.hotel_icon)

    def create_module_button(self, text, module_file, icon):
        button = ctk.CTkButton(
            self,
            text=text,
            image=icon,  # Asigna la imagen al botón
            compound="left",  # Posición de la imagen respecto al texto
            command=lambda: self.launch_module(module_file),
            font=("Arial", 16, "bold"),
            height=40,
            fg_color="#5d3fd3",
            hover_color="#3f00ff",
            border_color="#eaddca",
            border_width=2,
            corner_radius=43,
        )
        button.pack(pady=10)

    def launch_module(self, module_file):
    # Ruta relativa a la subcarpeta ProyectoNuevo
        module_path = os.path.join("ProyectoNuevo", module_file)
    
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