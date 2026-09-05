"""
KS Polonia – Official Membership Certificate (Mitgliedsbescheinigung) PDF Generator.
Generates DIN A4 letterhead PDF with official logo, Manfred Wolny signature, and club footer.
"""
import os
import datetime
from typing import Optional, List, Dict, Any
from fpdf import FPDF
from fpdf.enums import XPos, YPos

_BASE = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.join(_BASE, "..", "..", "public", "logo.png")
_SIG_PATH = os.path.join(_BASE, "..", "assets", "signature_manfred_wolny.png")
_FOOTER_PATH = os.path.join(_BASE, "..", "assets", "letter_footer.png")

_FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _format_date(d: Any) -> str:
    """Safely format date to TT.MM.JJJJ."""
    if not d:
        return "—"
    if isinstance(d, (datetime.date, datetime.datetime)):
        return d.strftime("%d.%m.%Y")
    if isinstance(d, str):
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.datetime.strptime(d[:10], fmt).strftime("%d.%m.%Y")
            except ValueError:
                continue
    return str(d)


class PoloniaLetterPDF(FPDF):
    """A4 letter with KS Polonia layout."""
    pass


def generate_membership_certificate(
    member: Dict[str, Any],
    divisions: Optional[List[Dict[str, Any]]] = None,
    purpose: str = "",
    paid_current_year: bool = True,
) -> bytes:
    """
    Generate an official Mitgliedsbescheinigung as DIN A4 PDF.
    Returns the PDF raw bytes.
    """
    pdf = PoloniaLetterPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(25, 20, 25)
    pdf.add_page()

    # Load Unicode fonts
    if os.path.exists(_FONT_REGULAR) and os.path.exists(_FONT_BOLD):
        pdf.add_font("DejaVu", "", _FONT_REGULAR)
        pdf.add_font("DejaVu", "B", _FONT_BOLD)
        font_family = "DejaVu"
    else:
        font_family = "Helvetica"

    # ═══════════════════════════════════════
    # 1. BRIEFKOPF (Header with Logo)
    # ═══════════════════════════════════════
    pdf.set_font(font_family, "B", 14)
    pdf.set_text_color(220, 20, 60) # Polonia Crimson
    pdf.set_xy(25, 20)
    pdf.cell(110, 7, "K.S. Polonia Hamburg e.V.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font(font_family, "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.set_x(25)
    pdf.cell(110, 4.5, "Finkenau 38 · 22081 Hamburg", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(25)
    pdf.cell(110, 4.5, "Telefon: 0173-8236287 · E-Mail: info@ks-polonia.de", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(25)
    pdf.cell(110, 4.5, "Web: www.ks-polonia.de · Amtsgericht Hamburg", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Right: Club Logo
    if os.path.exists(_LOGO_PATH):
        pdf.image(_LOGO_PATH, x=155, y=17, w=28)

    # Crimson dividing rule
    pdf.set_draw_color(220, 20, 60)
    pdf.set_line_width(0.6)
    pdf.line(25, 42, 185, 42)

    # ═══════════════════════════════════════
    # 2. ANSCHRIFTFELD & DATUM
    # ═══════════════════════════════════════
    # Return line for window envelope (Rücksendezeile)
    pdf.set_font(font_family, "", 7.5)
    pdf.set_text_color(140, 140, 140)
    pdf.set_xy(25, 47)
    pdf.cell(100, 3.5, "K.S. Polonia Hamburg e.V. · Finkenau 38 · 22081 Hamburg", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Member Address
    vorname = member.get("vorname", "")
    nachname = member.get("nachname", "")
    strasse = member.get("strasse", "")
    plz = member.get("plz", "")
    ort = member.get("ort", "Hamburg")

    pdf.set_font(font_family, "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.set_xy(25, 53)
    pdf.cell(100, 5, f"{vorname} {nachname}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(25)
    pdf.cell(100, 5, strasse or "—", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_x(25)
    pdf.cell(100, 5, f"{plz} {ort}".strip() or "—", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Place & Date (Right-aligned)
    today_str = datetime.date.today().strftime("%d.%m.%Y")
    pdf.set_xy(105, 73)
    pdf.cell(80, 5, f"Hamburg, den {today_str}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ═══════════════════════════════════════
    # 3. TITEL & MITGLIEDSNUMMER
    # ═══════════════════════════════════════
    pdf.set_xy(25, 86)
    pdf.set_font(font_family, "B", 15)
    pdf.set_text_color(220, 20, 60)
    pdf.cell(160, 7, "Mitgliedsbescheinigung", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    nr = member.get("mitgliedsnummer") or "POL-2026-XXXX"
    pdf.set_font(font_family, "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.set_x(25)
    pdf.cell(160, 5, f"Mitgliedsnummer: {nr}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ═══════════════════════════════════════
    # 4. BESCHEINIGUNGSTEXT & DATENFELD
    # ═══════════════════════════════════════
    pdf.set_xy(25, 104)
    pdf.set_font(font_family, "", 10.5)
    pdf.set_text_color(30, 30, 30)
    pdf.multi_cell(160, 6.5, "Hiermit wird bestätigt, dass")
    pdf.ln(2)

    # Box with member details
    box_start_y = pdf.get_y()
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(225, 228, 234)
    pdf.rect(25, box_start_y, 160, 27, "DF")

    inner_y = box_start_y + 3.5
    pdf.set_xy(30, inner_y)
    pdf.set_font(font_family, "B", 10)
    pdf.cell(36, 6, "Name:")
    pdf.set_font(font_family, "", 10)
    pdf.cell(110, 6, f"{vorname} {nachname}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    geb_date = _format_date(member.get("geburtsdatum"))
    pdf.set_x(30)
    pdf.set_font(font_family, "B", 10)
    pdf.cell(36, 6, "Geburtsdatum:")
    pdf.set_font(font_family, "", 10)
    pdf.cell(110, 6, geb_date, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    addr_full = f"{strasse}, {plz} {ort}".strip(", ")
    pdf.set_x(30)
    pdf.set_font(font_family, "B", 10)
    pdf.cell(36, 6, "Anschrift:")
    pdf.set_font(font_family, "", 10)
    pdf.cell(110, 6, addr_full or "—", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Continue text below the box
    pdf.set_y(box_start_y + 32)
    pdf.set_font(font_family, "", 10.5)

    ein_date = _format_date(member.get("eintrittsdatum"))
    pdf.set_x(25)
    pdf.multi_cell(
        160,
        6.5,
        f"seit dem {ein_date} ordentliches Mitglied in unserem Sportverein K.S. Polonia Hamburg e.V. ist.",
    )
    pdf.ln(3)

    # Division text
    div_names = [d["name"] for d in (divisions or []) if d.get("name")]
    is_passive = member.get("membership_level") == "passive" or "Passive Mitglieder" in div_names

    pdf.set_x(25)
    if is_passive:
        pdf.multi_cell(
            160,
            6.5,
            "Die Person unterstützt den Verein als Fördermitglied / passives Mitglied in der Abteilung Passive Mitglieder.",
        )
    elif div_names:
        div_str = ", ".join(div_names)
        pdf.multi_cell(
            160,
            6.5,
            f"Die Person ist aktiv in der Abteilung / Sportgruppe: {div_str}.",
        )
    else:
        pdf.multi_cell(
            160,
            6.5,
            "Die Person ist ordentlich geführtes Mitglied des Vereins.",
        )
    pdf.ln(3)

    # Payment / dues text
    current_year = datetime.date.today().year
    pdf.set_x(25)
    if paid_current_year:
        pdf.multi_cell(
            160,
            6.5,
            f"Der Mitgliedsbeitrag für das laufende Jahr ({current_year}) ist bezahlt.",
        )
    else:
        pdf.multi_cell(
            160,
            6.5,
            f"Die Mitgliedschaft besteht für das laufende Jahr ({current_year}).",
        )
    pdf.ln(3)

    # Purpose text
    clean_purpose = purpose.strip() if purpose else "Vorlage bei der Krankenkasse / Behörde"
    pdf.set_x(25)
    pdf.multi_cell(
        160,
        6.5,
        f"Diese Bescheinigung wird auf Wunsch des Mitglieds für {clean_purpose} ausgestellt.",
    )

    # ═══════════════════════════════════════
    # 5. UNTERSCHRIFT & GRUSSFORMEL
    # ═══════════════════════════════════════
    pdf.set_xy(25, pdf.get_y() + 6)
    pdf.cell(160, 6, "Mit sportlichen Grüßen,", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    sig_y = pdf.get_y() + 2
    if os.path.exists(_SIG_PATH):
        # 60mm width maintains natural signature proportions
        pdf.image(_SIG_PATH, x=25, y=sig_y, w=65)

    # ═══════════════════════════════════════
    # 6. BRIEFFUSS (Footer with Bank & Board)
    # ═══════════════════════════════════════
    if os.path.exists(_FOOTER_PATH):
        pdf.image(_FOOTER_PATH, x=25, y=262, w=160)

    return bytes(pdf.output())
