"""Exercise both contact-form transports without sending email."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import os
os.environ.setdefault("JWT_SECRET", "local-tests-only-not-a-production-secret-12345")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
DATA = {"name": "Test Name", "email": "test@gmail.com", "subject": "allgemein",
        "message": "Test message", "website_url": "", "captcha_answer": "8", "captcha_expected": "8"}

class ContactTest(unittest.TestCase):
    @patch('app.send_email', return_value=(True, None))
    def test_json_and_form_submit(self, send):
        for params in ({'json': DATA}, {'data': DATA}):
            response = client.post('/contact', **params)
            self.assertEqual(response.status_code, 200)
            self.assertIn('erfolgreich gesendet', response.text)
        self.assertEqual(send.call_count, 2)

    @patch('app.send_email')
    def test_wrong_captcha_and_invalid_email_do_not_send(self, send):
        for params in ({'json': {**DATA, 'captcha_answer': '1'}},
                       {'data': {**DATA, 'email': 'invalid'}}):
            response = client.post('/contact', **params)
            self.assertIn(response.status_code, (400, 422))
            self.assertIn('Bitte', response.text) if response.status_code == 422 else self.assertIn('Sicherheitsfrage', response.text)
        send.assert_not_called()

    @patch('app.send_email', return_value=(False, 'internal SMTP details'))
    def test_delivery_failure_is_clear_and_does_not_expose_details(self, send):
        for params in ({'json': DATA}, {'data': DATA}):
            response = client.post('/contact', **params)
            self.assertEqual(response.status_code, 500)
            self.assertIn('info@ks-polonia.de', response.text)
            self.assertNotIn('internal SMTP details', response.text)

if __name__ == '__main__':
    unittest.main()
