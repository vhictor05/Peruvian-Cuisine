import customtkinter as ctk
from tkinter import ttk

def create_form_entry(parent, label, row, column=0, columnspan=1):
    frame = ctk.CTkFrame(parent, fg_color="#1e1e2d")
    frame.grid(row=row, column=column, columnspan=columnspan, sticky="ew", pady=5)
    
    ctk.CTkLabel(
        frame,
        text=f"{label}:",
        fg_color="#1e1e2d",
        font=("Arial", 14)
    ).pack(side="left", padx=5)
    
    entry = ctk.CTkEntry(
        frame,
        fg_color="#25253a",
        border_color="#7209b7",
        border_width=1
    )
    entry.pack(side="right", fill="x", expand=True, padx=5)
    
    return entry

def create_treeview(parent, columns):
    # Configurar el estilo
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
        background="#1e1e2d",
        foreground="white",
        fieldbackground="#1e1e2d",
        bordercolor="#3b3b3b",
        borderwidth=0
    )
    style.configure("Treeview.Heading",
        background="#1e1e2d",
        foreground="white",
        borderwidth=1
    )
    style.map('Treeview',
        background=[('selected', '#7209b7')],
        foreground=[('selected', 'white')]
    )
    
    # Crear y configurar el Treeview
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(fill="both", expand=True, padx=20, pady=10)
    return tree

def create_button(parent, text, command, width=150, height=40):
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="#7209b7",
        hover_color="#9d4dc7",
        font=("Arial", 14),
        corner_radius=15,
        width=width,
        height=height
    )