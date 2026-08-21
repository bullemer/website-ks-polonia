"""
KS Polonia – Season Ticket PDF Generator.
Creates a branded PDF ticket with QR code for email attachment.
"""
import io
import json
import os
import tempfile
from fpdf import FPDF
import qrcode

# Logo path (resolved at import time)
_BASE = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.join(_BASE, "..", "..", "public", "logo.png")


class TicketPDF(FPDF):
    """Custom PDF with Polonia branding for season tickets."""
    pass


def generate_ticket_pdf(
    vorname: str,
    nachname: str,
    ticket_code: str,
    season: str,
    seat_info: str = "",
) -> bytes:
    """
    Generate a branded season ticket PDF and return the raw bytes.
    The ticket is a landscape A6-ish card (148×105mm) on an A4 page.
    """
    pdf = TicketPDF(orientation="L", unit="mm", format=(110, 160))
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # ── Background gradient (solid crimson) ──
    pdf.set_fill_color(220, 20, 60)
    pdf.rect(0, 0, 160, 110, "F")

    # Darker bottom section
    pdf.set_fill_color(139, 0, 0)
    pdf.rect(0, 55, 160, 55, "F")

    # ── White decorative elements ──
    pdf.set_draw_color(255, 255, 255)
    pdf.set_line_width(0.3)
    # Perforated line
    dash_y = 55
    x = 5
    while x < 155:
        pdf.line(x, dash_y, x + 3, dash_y)
        x += 5

    # ── Logo ──
    logo = _LOGO_PATH
    if os.path.exists(logo):
        pdf.image(logo, x=8, y=8, w=20, h=20)

    # ── Title block ──
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_xy(95, 8)
    pdf.cell(60, 5, "DAUERKARTE", align="R")

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_xy(60, 14)
    pdf.cell(95, 6, "K.S. Polonia Hamburg e.V.", align="R")

    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(95, 21)
    pdf.cell(60, 5, f"Saison {season}", align="R")

    # ── Holder name (large) ──
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(8, 33)
    full_name = f"{vorname} {nachname}"
    pdf.cell(144, 8, full_name)

    # ── Ticket code ──
    pdf.set_font("Courier", "", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(8, 43)
    pdf.cell(100, 6, ticket_code)

    # ── Info fields (below perf line) ──
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(200, 200, 200)

    pdf.set_xy(8, 60)
    pdf.cell(30, 4, "SAISON")
    pdf.set_xy(45, 60)
    pdf.cell(30, 4, "TICKET-NR.")
    if seat_info:
        pdf.set_xy(90, 60)
        pdf.cell(30, 4, "PLATZ")

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(255, 255, 255)

    pdf.set_xy(8, 64)
    pdf.cell(30, 5, season)
    pdf.set_xy(45, 64)
    pdf.cell(40, 5, ticket_code)
    if seat_info:
        pdf.set_xy(90, 64)
        pdf.cell(40, 5, seat_info)

    # ── Valid for ──
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(200, 200, 200)
    pdf.set_xy(8, 75)
    pdf.cell(100, 4, "Gültig für alle Pflichtspiel-Heimspiele")

    # ── Club info ──
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(180, 180, 180)
    pdf.set_xy(8, 100)
    pdf.cell(100, 4, "Finkenau 38, 22081 Hamburg · www.ks-polonia.de")

    # ── QR Code ──
    qr_data = json.dumps({
        "type": "season_ticket",
        "code": ticket_code,
        "holder": full_name,
        "season": season,
    })
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Save QR to temp file for fpdf
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        qr_img.save(tmp.name)
        qr_path = tmp.name

    # White background for QR
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(120, 60, 34, 34, "F")
    # Round corners effect (small white rect)
    pdf.image(qr_path, x=122, y=62, w=30, h=30)

    # Clean up temp file
    try:
        os.unlink(qr_path)
    except OSError:
        pass

    # Return PDF bytes
    return pdf.output()
