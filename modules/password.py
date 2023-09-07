import os
import ssl
import bcrypt
import smtplib
import datetime

from models.models import User
from dotenv import load_dotenv
from .dependencies import get_db
from sqlalchemy.orm import Session
from email.mime.text import MIMEText
from config.database import SessionLocal
from passlib.context import CryptContext
from modules.dependencies import get_current_user
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, Depends, HTTPException, Header, status
from auth.jwt import create_access_token_with_expiration, decode_access_token
from schema.password_schema import EmailRequest, PasswordResetRequest, PasswordChangeRequest, PasswordResponse

load_dotenv()

password_router= APIRouter()

SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_USERNAME =os.getenv('SMTP_USERNAME')
SMTP_APP_PASSWORD =os.getenv('SMTP_APP_PASSWORD')
RESET_PASSWORD_URL=os.getenv('RESET_PASSWORD_URL')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_function(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

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

    msg = MIMEMultipart()
    msg['From'] = os.getenv('FROM_EMAIL')
    msg['To'] = email
    msg['Subject'] = 'Reset Your Password'

    # Create HTML content for the email body
    html = f"""
    <html>
        <body>
            <p>Dear User,</p>
            <p>Click the following <a href="{reset_link}" style="text-decoration:underline; color:blue">link</a> to reset your password:</p>
            <span>Regards,</span> <br/> <span>Portal Team</span>
        </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))  # Specify 'html' as the content type

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USERNAME, SMTP_APP_PASSWORD)
        server.sendmail(msg['From'], msg['To'], msg.as_string())

@password_router.post("/send_resend_password_link",tags=["Password"],response_model=PasswordResponse)
async def send_reset_password_link(email_data: EmailRequest):
    email = email_data.email

    # Check if email exists in the database
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if user is None:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate reset password link
    reset_link = generate_reset_link(email)

    # Send the email with the reset link
    try:
        send_email(email, reset_link)
        return {"message": "Reset password link sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send reset password link")

@password_router.post("/reset_password", tags=["Password"],response_model=PasswordResponse)
async def reset_password(
    new_password_data: PasswordResetRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    # Ensure Authorization Header is Present
    if not authorization:
        raise HTTPException(status_code=401, detail="You are not allowed to perform this action")

    # Extract Bearer Token
    try:
        token_type, token = authorization.split()
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    # Validate and Decode Bearer Token
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Validate and Update Password
    if new_password_data.new_password != new_password_data.confirm_new_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = db.query(User).filter_by(email=email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's password in the database
    user.encrypted_password = hash_function(new_password_data.new_password)
    db.commit()

    return {"message": "Password reset successfully"}

@password_router.post("/change_password",tags=["Password"],response_model=PasswordResponse)
def change_password(
    password_data: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_password = password_data.current_password
    new_password = password_data.new_password

    if not verify_password(current_password, user.encrypted_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password")

    # Hash the new password before storing it
    hashed_new_password = pwd_context.hash(new_password)

    # Update the user's hashed password in the database
    user.encrypted_password = hashed_new_password
    db.commit()

    return {"message":"Password changed successfully"}
