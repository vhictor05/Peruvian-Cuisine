import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime

class CalendarioVista(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.fecha_actual = datetime.now()
        self.inicializar_ui()
        
    def inicializar_ui(self):
        # Controles de navegación
        frame_nav = ttk.Frame(self)
        frame_nav.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(frame_nav, text="<", command=self.mes_anterior).pack(side='left')
        self.lbl_mes = ttk.Label(frame_nav, text=self.obtener_texto_mes())
        self.lbl_mes.pack(side='left', expand=True)
        ttk.Button(frame_nav, text=">", command=self.mes_siguiente).pack(side='right')
        
        # Calendario
        self.frame_calendario = ttk.Frame(self)
        self.frame_calendario.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.actualizar_calendario()
        
    def obtener_texto_mes(self):
        return f"{calendar.month_name[self.fecha_actual.month]} {self.fecha_actual.year}"
        
    def actualizar_calendario(self):
        # Limpiar calendario existente
        for widget in self.frame_calendario.winfo_children():
            widget.destroy()
            
        # Crear cabecera con días de la semana
        for i, dia in enumerate(calendar.day_abbr):
            ttk.Label(self.frame_calendario, text=dia).grid(row=0, column=i, padx=2, pady=2)
            
        # Obtener calendario del mes
        cal = calendar.monthcalendar(self.fecha_actual.year, self.fecha_actual.month)
        
        # Crear botones para cada día
        for semana in range(len(cal)):
            for dia in range(7):
                if cal[semana][dia] != 0:
                    btn = ttk.Button(self.frame_calendario, 
                                   text=str(cal[semana][dia]),
                                   command=lambda d=cal[semana][dia]: self.seleccionar_dia(d))
                    btn.grid(row=semana+1, column=dia, padx=2, pady=2)
                    
    def mes_anterior(self):
        if self.fecha_actual.month == 1:
            self.fecha_actual = self.fecha_actual.replace(year=self.fecha_actual.year-1, month=12)
        else:
            self.fecha_actual = self.fecha_actual.replace(month=self.fecha_actual.month-1)
        self.lbl_mes.config(text=self.obtener_texto_mes())
        self.actualizar_calendario()
        
    def mes_siguiente(self):
        if self.fecha_actual.month == 12:
            self.fecha_actual = self.fecha_actual.replace(year=self.fecha_actual.year+1, month=1)
        else:
            self.fecha_actual = self.fecha_actual.replace(month=self.fecha_actual.month+1)
        self.lbl_mes.config(text=self.obtener_texto_mes())
        self.actualizar_calendario()
        
    def seleccionar_dia(self, dia):
        fecha = self.fecha_actual.replace(day=dia)
        # Aquí puedes implementar la lógica para cuando se selecciona un día
        print(f"Día seleccionado: {fecha.strftime('%Y-%m-%d')}")