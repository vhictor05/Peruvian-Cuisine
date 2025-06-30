# generar_boleta.py
from fpdf import FPDF
from estructura.models_folder.models_restaurente import Cliente, Menu
from datetime import datetime

class Generarboleta:
    def __init__(self, pedido, db):
        self.pedido = pedido
        self.db = db

    def generar_boleta(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        cliente = self.db.query(Cliente).filter(Cliente.rut == self.pedido.cliente_rut).first()

        pdf.cell(200, 10, txt="BOLETA DE COMPRA", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Fecha: {self.pedido.fecha.strftime('%d-%m-%Y %H:%M')}", ln=True)
        pdf.cell(200, 10, txt=f"Cliente: {cliente.nombre} - RUT: {cliente.rut}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, txt="Detalle del Pedido:", ln=True)

        for item in self.pedido.menus:
            menu = self.db.query(Menu).filter(Menu.id == item["id"]).first()
            if menu:
                total = menu.precio * item["cantidad"]
                pdf.cell(200, 10, txt=f"{menu.nombre} x{item['cantidad']} - ${total:.2f}", ln=True)

        pdf.ln(10)
        pdf.cell(200, 10, txt=f"TOTAL: ${self.pedido.total:.2f}", ln=True, align="R")

        filename = f"boleta_{self.pedido.id}.pdf"
        pdf.output(filename)