import smtplib
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, TARGET_EMAIL, FROM_EMAIL


def _sanitize_header_value(value: str) -> str:
    """Strip newlines and special characters that could enable header injection."""
    return re.sub(r'[\r\n\x00-\x1f]+', ' ', value).strip()


def send_email(subject: str, text_body: str, reply_to_email: str = None, reply_to_name: str = None, attachments: list = None, to_email: str = None):
    """
    Sends a plain text email and optional attachments via the configured SMTP server.
    If to_email is provided, sends to that address; otherwise sends to TARGET_EMAIL.
    """
    msg = MIMEMultipart()
    
    # Use standard UTF-8 text part
    part1 = MIMEText(text_body, 'plain', "utf-8")
    msg.attach(part1)

    recipient = to_email or TARGET_EMAIL

    msg['Subject'] = subject
    msg['From'] = f"KS Polonia Website <{FROM_EMAIL}>"
    msg['To'] = recipient
    
    if reply_to_email:
        name = _sanitize_header_value(reply_to_name) if reply_to_name else reply_to_email
        msg['Reply-To'] = f"{name} <{reply_to_email}>"

    # Process Attachments
    if attachments:
        for file_path in attachments:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)

    try:
        # Start SMTP TLS connection
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)
