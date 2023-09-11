import os
import ssl
import smtplib
import datetime
from dotenv import load_dotenv
from fastapi import HTTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auth.jwt import create_access_token_with_expiration

load_dotenv()

SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_APP_PASSWORD = os.getenv('SMTP_APP_PASSWORD')
RESET_PASSWORD_URL = os.getenv('RESET_PASSWORD_URL')

def generate_reset_link(email):
    # Create the data dictionary for the token
    data = {"sub": email}

    # Set the expiration time for the token
    expires_delta = datetime.timedelta(minutes=10)

    # Generate the JWT token
    token = create_access_token_with_expiration(data, expires_delta)

    # Create the reset link with the token
    reset_link = f"{RESET_PASSWORD_URL}?reset_token={token}"
    return reset_link

def send_email(email, reset_link):
    # Define email parameters
    sender_email = SMTP_USERNAME
    receiver_email = email
    subject = "Reset Your Password"
    message = f"""
    <html>
        <body>
            <p>Dear User,</p>
            <p>Click the following <a href="{reset_link}" style="text-decoration:underline; color:blue">link</a> to reset your password:</p>
            <span>Regards,</span> <br/> <span>Your Application Team</span>
        </body>
    </html>
    """

    # Create a MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the HTML message
    msg.attach(MIMEText(message, 'html'))

    # Configure SSL context
    context = ssl.create_default_context()

    # Send the email
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USERNAME, SMTP_APP_PASSWORD)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")