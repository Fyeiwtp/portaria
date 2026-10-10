from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit

CAMPOS = {
    "Check-in": ["Nome", "Chave", "Entrada", "Quarto", "Hora"],
    "Check-out": ["Nome", "Chave", "Saída", "Quarto", "Hora"],
    "Visitantes": [
        "Nome", "Identificação", "Visitado",
        "Quarto", "Entrada", "Saída",
    ],
}


def criar_ficha_pdf(tipo, valores=None, vigilante="", data=""):
    valores = valores or {}
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    c.setTitle("Portaria - " + tipo)
    c.setFillColor(colors.HexColor("#12213a"))
    c.rect(0, altura - 108, largura, 108, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, altura - 55, "PORTARIA RESIDENCIAL")
    c.setFont("Helvetica", 14)
    c.drawString(40, altura - 82, "Ficha de " + tipo)

    c.setFillColor(colors.HexColor("#12213a"))
    c.setFont("Helvetica", 10)
    c.drawString(
        40,
        altura - 137,
        "Data: " + (data or "____ / ____ / ________"),
    )

    y = altura - 190

    for i, campo in enumerate(CAMPOS[tipo]):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y + 12, campo)

        if not valores:
            c.acroForm.textfield(
                name=f"campo_{i}",
                tooltip=campo,
                x=40,
                y=y - 31,
                width=largura - 80,
                height=34,
                borderWidth=1,
                borderStyle="solid",
                forceBorder=True,
                borderColor=colors.HexColor("#cbd5e1"),
                fillColor=colors.HexColor("#f8fafc"),
                fontSize=11,
                maxlen=200,
            )
        else:
            c.setStrokeColor(colors.HexColor("#cbd5e1"))
            c.roundRect(
                40, y - 31, largura - 80, 34,
                4, stroke=1, fill=0,
            )
            c.setFont("Helvetica", 10)
            linhas = simpleSplit(
                str(valores.get(campo, "")),
                "Helvetica",
                10,
                largura - 100,
            )
            for j, linha in enumerate(linhas[:2]):
                c.drawString(50, y - 10 - j * 12, linha)

        y -= 78

    c.setFont("Helvetica", 10)
    c.drawString(40, 100, "Vigilante: " + vigilante)
    c.drawString(
        40, 70,
        "Assinatura: __________________________________________",
    )
    c.setFont("Helvetica", 8)
    c.drawString(
        40, 35,
        "Ficha de portaria | Guarde uma cópia após o preenchimento.",
    )
    c.save()
    return buffer.getvalue()
