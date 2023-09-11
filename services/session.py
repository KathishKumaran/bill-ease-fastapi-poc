import os
import bcrypt
import datetime
from fastapi import Request
from models.models import User
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from auth.jwt import create_access_token
from fastapi import HTTPException,status
from schema.session_schema import UserLoginRequest
from jose import jwt, ExpiredSignatureError, JWTError

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

def login_user(db: Session, user_login: UserLoginRequest, request: Request):
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user or not bcrypt.checkpw(user_login.password.encode('utf-8'), user.encrypted_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})

    user.access_token = access_token
    user.is_currently_logged_in = True
    user.last_sign_in_at = user.current_sign_in_at
    user.current_sign_in_at = datetime.datetime.now()
    user.last_sign_in_ip = user.current_sign_in_ip
    user.current_sign_in_ip = request.client.host
    db.commit()

    return user, access_token

def logout_user(db: Session, authorization: str, current_user: User):
    if authorization != f"Bearer {current_user.access_token}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Find the user and update user information
        user = db.query(User).filter(User.email == decoded_token['sub']).first()
        if user:
            user.access_token = None
            user.is_currently_logged_in = False
            db.commit()
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
