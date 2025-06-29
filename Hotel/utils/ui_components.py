import tkinter as tk
from tkinter import ttk

def crear_tabla(parent, columnas):
    """Crea una tabla (Treeview) con las columnas especificadas"""
    tabla = ttk.Treeview(parent, columns=columnas, show='headings')
    
    # Configurar columnas
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=100)  # Ancho por defecto
        
    # Agregar scrollbars
    scrolly = ttk.Scrollbar(parent, orient='vertical', command=tabla.yview)
    scrollx = ttk.Scrollbar(parent, orient='horizontal', command=tabla.xview)
    tabla.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
    
    # Posicionar scrollbars
    scrolly.pack(side='right', fill='y')
    scrollx.pack(side='bottom', fill='x')
    
    return tabla

def crear_botones_crud(parent, comando_nuevo, comando_editar, comando_eliminar):
    """Crea los botones estándar para operaciones CRUD"""
    ttk.Button(parent, text="Nuevo", command=comando_nuevo).pack(side='left', padx=5)
    ttk.Button(parent, text="Editar", command=comando_editar).pack(side='left', padx=5)
    ttk.Button(parent, text="Eliminar", command=comando_eliminar).pack(side='left', padx=5)