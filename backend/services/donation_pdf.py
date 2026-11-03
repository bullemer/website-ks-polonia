"""Unsigned single cash-donation certificate, based on the BMF association template."""
import datetime
from decimal import Decimal
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from services.certificate_pdf import _FONT_BOLD, _FONT_REGULAR, _LOGO_PATH
import os

_SMALL = ('null','eins','zwei','drei','vier','fünf','sechs','sieben','acht','neun',
          'zehn','elf','zwölf','dreizehn','vierzehn','fünfzehn','sechzehn','siebzehn','achtzehn','neunzehn')
_TENS = ('','','zwanzig','dreißig','vierzig','fünfzig','sechzig','siebzig','achtzig','neunzig')
def _number(n: int) -> str:
    if n < 20: return _SMALL[n]
    if n < 100: return (_SMALL[n % 10].replace('eins','ein') + 'und' if n % 10 else '') + _TENS[n // 10]
    if n < 1000: return ('ein' if n // 100 == 1 else _SMALL[n // 100]) + 'hundert' + (_number(n % 100) if n % 100 else '')
    if n < 1000000: return ('ein' if n // 1000 == 1 else _number(n // 1000)) + 'tausend' + (_number(n % 1000) if n % 1000 else '')
    raise ValueError('Betrag zu hoch')

def amount_in_words(amount: Decimal) -> str:
    cents = int(amount * 100)
    euros, rest = divmod(cents, 100)
    euro_words = 'ein' if euros == 1 else _number(euros)
    cent_words = 'ein' if rest == 1 else _number(rest)
    return f'{euro_words} Euro und {cent_words} Cent'

def generate_donation_pdf(data: dict) -> bytes:
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(22, 14, 22)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    if os.path.exists(_FONT_REGULAR) and os.path.exists(_FONT_BOLD):
        pdf.add_font('DejaVu', '', _FONT_REGULAR)
        pdf.add_font('DejaVu', 'B', _FONT_BOLD)
        font='DejaVu'
    else:
        font='Helvetica'
    def text(value, size=9, bold=False, height=4.4):
        pdf.set_font(font, 'B' if bold else '', size)
        pdf.set_x(22)
        pdf.multi_cell(166, height, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(180, 20, 55)
    text('K.S. Polonia Hamburg e.V.', 13, True, 6)
    pdf.set_text_color(60,60,60)
    text('Finkenau 38 · 22081 Hamburg', 8, height=4)
    logo = _LOGO_PATH if os.path.exists(_LOGO_PATH) else '/usr/home/trusteei/public_html/ks-polonia/logo.png'
    if os.path.exists(logo): pdf.image(logo, x=165, y=12, w=22)
    pdf.ln(5)
    pdf.set_draw_color(180,20,55); pdf.line(22,pdf.get_y(),188,pdf.get_y()); pdf.ln(3)
    text('Bestätigung über Geldzuwendungen', 13, True, 6)
    text('im Sinne des § 10b des Einkommensteuergesetzes an eine der in § 5 Abs. 1 Nr. 9 des Körperschaftsteuergesetzes bezeichneten Körperschaften, Personenvereinigungen oder Vermögensmassen', 8, height=4)
    pdf.ln(3)
    text('Name und Anschrift des Zuwendenden:', 9, True)
    text(data['donor_name'] + '\n' + data['address'] + '\n' + data['postal_city'], 9, height=4.5)
    pdf.ln(2)
    amount=data['amount']
    text(f"Betrag der Zuwendung in Ziffern: {amount:.2f} EUR".replace('.', ','), 9, True)
    text('Betrag in Buchstaben: ' + amount_in_words(amount), 9)
    text('Tag der Zuwendung: ' + data['donation_date'].strftime('%d.%m.%Y'), 9)
    text('Es handelt sich um den Verzicht auf Erstattung von Aufwendungen: Nein', 9)
    pdf.ln(3)
    text('Wir sind wegen Förderung ' + data['purpose'] + ' nach dem Freistellungsbescheid bzw. nach der Anlage zum Körperschaftsteuerbescheid des Finanzamtes ' + data['tax_office'] + ', StNr. ' + data['tax_number'] + ', vom ' + data['notice_date'].strftime('%d.%m.%Y') + ' für den letzten Veranlagungszeitraum ' + data['tax_period'] + ' nach § 5 Abs. 1 Nr. 9 des Körperschaftsteuergesetzes von der Körperschaftsteuer und nach § 3 Nr. 6 des Gewerbesteuergesetzes von der Gewerbesteuer befreit.', 8.5, height=4.4)
    pdf.ln(2)
    text('Es wird bestätigt, dass die Zuwendung nur zur Förderung ' + data['purpose'] + ' verwendet wird.', 8.5, height=4.4)
    text('Es wird bestätigt, dass es sich nicht um einen Mitgliedsbeitrag handelt, dessen Abzug nach § 10b Abs. 1 des Einkommensteuergesetzes ausgeschlossen ist.', 8.5, height=4.4)
    pdf.ln(6)
    text('Hamburg, den ' + datetime.date.today().strftime('%d.%m.%Y') + '     ___________________________________', 9)
    text('                                                         Unterschrift des Zuwendungsempfängers', 8)
    pdf.ln(4)
    text('Hinweis:', 8, True, 4)
    text('Wer vorsätzlich oder grob fahrlässig eine unrichtige Zuwendungsbestätigung erstellt oder veranlasst, dass Zuwendungen nicht zu den in der Zuwendungsbestätigung angegebenen steuerbegünstigten Zwecken verwendet werden, haftet für die entgangene Steuer (§ 10b Abs. 4 EStG, § 9 Abs. 3 KStG, § 9 Nr. 5 GewStG).', 7.5, height=3.8)
    text('Diese Bestätigung wird nicht als Nachweis für die steuerliche Berücksichtigung der Zuwendung anerkannt, wenn das Datum des Freistellungsbescheides länger als 5 Jahre bzw. das Datum der Feststellung der Einhaltung der satzungsmäßigen Voraussetzungen nach § 60a Abs. 1 AO länger als 3 Jahre seit Ausstellung des Bescheides zurückliegt (§ 63 Abs. 5 AO).', 7.5, height=3.8)
    return bytes(pdf.output())
