from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io

def generar_pdf_comprobante(usuario, pago):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFillColor(colors.hexColor("#003366")) # Azul Oscuro
    c.rect(0, 750, 612, 50, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 765, "RECIBO DE PAGO - WOLF TEAM")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(50, 710, f"Usuario: {usuario.nombre_completo}")
    c.drawString(50, 690, f"Monto: ${pago.monto} ({pago.metodo})")
    c.drawString(50, 670, f"Mes: {pago.mes_correspondiente}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer