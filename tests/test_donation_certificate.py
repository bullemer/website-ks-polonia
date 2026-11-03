import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import date
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi.testclient import TestClient
from pypdf import PdfReader
from app import app
from auth import create_access_token
from services.donation_pdf import amount_in_words

DATA = dict(donor_name='Max Beispiel', address='Musterstraße 1', postal_city='12345 Musterstadt',
            amount='300.00', donation_date='2025-01-01', purpose='des Sports',
            notice_date='2025-01-01', tax_office='Hamburg-Mitte', tax_number='00/000/00000',
            tax_period='2024', confirmed='yes')
class DonationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    def login_as(self, role):
        self.client.cookies.set('session_token', create_access_token(1, 'test@example.org', role=role))
    def test_only_superadmin_can_access_and_create(self):
        self.assertEqual(self.client.get('/admin/donations/certificate').status_code, 401)
        self.login_as('admin')
        self.assertEqual(self.client.post('/admin/donations/certificate', data=DATA).status_code, 403)
        self.assertEqual(self.client.get('/admin/donations/certificate').status_code, 403)
    def test_generate_and_archive(self):
        self.login_as('superadmin')
        with tempfile.TemporaryDirectory() as d, patch('config.UPLOAD_DIR', d):
            r = self.client.post('/admin/donations/certificate', data=DATA)
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.headers['content-type'], 'application/pdf')
            saved = list((Path(d) / 'donation_certificates').glob('*.pdf'))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0].read_bytes(), r.content)
            self.assertIn(saved[0].stem, self.client.get('/admin/donations/certificates').text)
            self.assertEqual(self.client.get('/admin/donations/certificates/' + saved[0].stem).content, r.content)
            pdf = PdfReader(io.BytesIO(r.content))
            text = '\n'.join(p.extract_text() for p in pdf.pages)
            self.assertIn('300,00 EUR', text)
            self.assertIn('dreihundert Euro und null Cent', text)
            self.assertIn('Unterschrift des Zuwendungsempfängers', text)
    def test_rejects_missing_or_bad_inputs_and_cross_origin(self):
        self.login_as('superadmin')
        for changes in ({'amount':'-3'}, {'amount':'1.001'}, {'confirmed':''}, {'donor_name':''}, {'donation_date':'2999-01-01'}):
            self.assertEqual(self.client.post('/admin/donations/certificate',data={**DATA, **changes}).status_code,422)
        self.assertEqual(self.client.post('/admin/donations/certificate',data=DATA,headers={'Origin':'https://evil.example'}).status_code,403)
    def test_amount_words(self):
        self.assertEqual(amount_in_words(Decimal('21.03')), 'einundzwanzig Euro und drei Cent')
        self.assertEqual(amount_in_words(Decimal('1000.01')), 'eintausend Euro und ein Cent')
if __name__ == '__main__': unittest.main()
