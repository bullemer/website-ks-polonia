import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Hardcoded server configs (as previously found in PHPMailer scripts)
SMTP_HOST = "mail.your-server.de"
SMTP_PORT = 587
SMTP_USER = "info@ks-polonia.de"
SMTP_PASSWORD = "C4XOidAid08XX7U6"
TARGET_EMAIL = "info@ks-polonia.de"
FROM_EMAIL = "info@ks-polonia.de"

def send_email(subject: str, text_body: str, reply_to_email: str = None, reply_to_name: str = None):
    """
    Sends a plain text email via the configured SMTP server.
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
