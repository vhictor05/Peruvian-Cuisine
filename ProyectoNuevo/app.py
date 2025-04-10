import customtkinter as ctk
import subprocess
import sys
import os
from tkinter import messagebox

# Configuración de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModuleLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Selección de Módulo")
        self.geometry("400x300")
        self.configure(fg_color="#1c1c1c")

        # Título
        self.label_title = ctk.CTkLabel(self, text="Selecciona un módulo", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        # Botones
        self.create_module_button("Restaurant", "restaurant.py", 1)
        self.create_module_button("Disco", "disco.py", 2)
        self.create_module_button("Hotel", "hotel.py", 3)

    def create_module_button(self, text, module_file, row):
        button = ctk.CTkButton(
            self,
            text=text,
            command=lambda: self.launch_module(module_file),
            font=("Arial", 16, "bold"),
            height=40,
            fg_color="#3c99dc",
            hover_color="#4da9eb",
            corner_radius=10
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