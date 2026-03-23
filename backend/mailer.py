import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Hardcoded server configs (as previously found in PHPMailer scripts)
SMTP_HOST = "mail.your-server.de"
SMTP_PORT = 587
SMTP_USER = "info@ks-polonia.de"
SMTP_PASSWORD = "C4XOidAid08XX7U6"
TARGET_EMAIL = "info@ks-polonia.de"
FROM_EMAIL = "info@ks-polonia.de"

def send_email(subject: str, text_body: str, reply_to_email: str = None, reply_to_name: str = None, attachments: list = None):
    """
    Sends a plain text email and optional attachments via the configured SMTP server.
    """
    msg = MIMEMultipart()
    
    # Use standard UTF-8 text part
    part1 = MIMEText(text_body, 'plain', "utf-8")
    msg.attach(part1)

    msg['Subject'] = subject
    msg['From'] = f"KS Polonia Website <{FROM_EMAIL}>"
    msg['To'] = TARGET_EMAIL
    
    if reply_to_email:
        name = reply_to_name if reply_to_name else reply_to_email
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

