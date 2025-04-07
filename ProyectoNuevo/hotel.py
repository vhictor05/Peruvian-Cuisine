# hotel.py (ejemplo básico)
import customtkinter as ctk
from tkinter import messagebox

class HotelApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Hotel")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        
        label = ctk.CTkLabel(self, text="Módulo Hotel en desarrollo", font=("Arial", 24))
        label.pack(pady=50)

if __name__ == "__main__":
    app = HotelApp()
    app.mainloop()