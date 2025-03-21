import smtplib
import os

from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()


def send_email(receivent, subject, message):
    sender = os.getenv("EMAIL_SENDER")
    email_password = os.getenv("EMAIL_PASSWORD")
    smtp_port = os.getenv("SMTP_PORT")
    
    server = smtplib.SMTP("smtp.gmail.com", smtp_port)
    server.starttls()
    
    try:
        server.login(sender, email_password)
        
        msg_to_send = MIMEText(message)
        msg_to_send["Subject"] = subject
        
        server.sendmail(sender, receivent, msg_to_send.as_string())
    except Exception as ex:
        return False
    
    return True
