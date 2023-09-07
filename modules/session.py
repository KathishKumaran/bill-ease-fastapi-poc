import os
import bcrypt
import datetime

from fastapi import Request
from models.models import User
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from jose import ExpiredSignatureError
from jsonschema import ValidationError
from auth.jwt import create_access_token
from fastapi.responses import JSONResponse
from .dependencies import get_current_user, get_db
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import APIRouter, Depends,  HTTPException, Header, status
from schema.session_schema import UserLoginRequest, UserLoginResponse, UserLogoutResponse

# Load variables from .env into the environment
load_dotenv()

ALGORITHM=os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

auth_router = APIRouter()

@auth_router.post("/login",response_model=UserLoginResponse, tags=["Session"])
async def login(user_login: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == user_login.email).first()
        if not user or not bcrypt.checkpw(user_login.password.encode('utf-8'), user.encrypted_password.encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.email})

        # Update user information
        user.access_token = access_token
        user.is_currently_logged_in = True
        user.last_sign_in_at = user.current_sign_in_at
        user.current_sign_in_at = datetime.datetime.now()
        user.last_sign_in_ip = user.current_sign_in_ip
        user.current_sign_in_ip = request.client.host
        db.commit()

        # Create a response object
        response_model = UserLoginResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
        response = JSONResponse(content=response_model.dict())
        response.headers["Authorization"] = f"Bearer {access_token}"

        return response

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

@auth_router.delete("/logout", tags=["Session"],response_model=UserLogoutResponse)
async def logout(authorization: str = Header(None),current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

            response = JSONResponse(content={"message": "Logged out successfully"})
            return response
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