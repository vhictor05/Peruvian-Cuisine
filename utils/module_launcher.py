import subprocess
import sys
import os
from tkinter import messagebox

def launch_reports_module(current_window=None, return_to=None):
    """
    Abre el módulo de reportes y retorna al módulo original.
    
    Args:
        current_window: Ventana actual que se cerrará antes de abrir reportes
        return_to: String que indica a qué módulo volver ('restaurant', 'hotel', 'disco')
    """
    reports_path = os.path.join(".", "reportes.py")
    
    if not os.path.exists(reports_path):
        messagebox.showerror(
            "Error", 
            f"No se encontró reportes.py en:\n{os.path.abspath(reports_path)}"
        )
        return
        
    try:
        if current_window:
            current_window.destroy()
            
        subprocess.run([sys.executable, reports_path], check=True)
        
        # Volver al módulo original
        if return_to:
            module_path = os.path.join(".", f"{return_to}.py")
            if os.path.exists(module_path):
                subprocess.run([sys.executable, module_path], check=True)
                
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar el módulo de reportes:\n{str(e)}")