import customtkinter as ctk

def create_report_button(parent, current_window=None, module_name=None):
    """
    Crea un botón estandarizado para reportar errores.
    
    Args:
        parent: Widget padre donde se colocará el botón
        current_window: Ventana actual que se pasará al launcher
        module_name: Nombre del módulo para volver ('restaurant', 'hotel', 'disco')
    """
    from utils.module_launcher import launch_reports_module
    
    button = ctk.CTkButton(
        parent,
        text="⚠ Reportar Error",
        command=lambda: launch_reports_module(current_window, return_to=module_name),
        fg_color="#ff4757",  # Color rojo original
        hover_color="#ff6b81",  # Hover original
        font=("Arial", 14),    # Tamaño de fuente original
        height=35,             # Altura original
        corner_radius=10,      # Bordes redondeados originales
        width=150             # Ancho original
    )
    
    return button