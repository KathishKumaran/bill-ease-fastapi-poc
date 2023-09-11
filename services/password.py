import bcrypt
from models.models import User
from fastapi import HTTPException
from passlib.context import CryptContext
from config.database import SessionLocal
from auth.jwt import  decode_access_token
from schema.password_schema import EmailRequest
from jose import ExpiredSignatureError, JWTError
from services.mailer import generate_reset_link, send_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_function(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def send_reset_password_link(email_data: EmailRequest):
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

def reset_password(new_password_data, authorization, db):
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
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
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

def change_password(password_data, user, db):
    current_password = password_data.current_password
    new_password = password_data.new_password

    # Verify the current password
    if not verify_password(current_password, user.encrypted_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Hash the new password before storing it
    hashed_new_password = hash_function(new_password)

    # Update the user's hashed password in the database
    user.encrypted_password = hashed_new_password
    db.commit()

    return {"message": "Password changed successfully"}
