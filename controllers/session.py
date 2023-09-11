from models.models import User
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from fastapi import APIRouter, Depends, Header
from services.session import login_user, logout_user
from schema.dependencies import get_current_user, get_db
from schema.session_schema import UserLoginRequest, UserLoginResponse, UserLogoutResponse

auth_router = APIRouter()

@auth_router.post("/login", response_model=UserLoginResponse, tags=["Session"])
async def login(user_login: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    try:
        user, access_token = login_user(db, user_login, request)
        response_model = UserLoginResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
        response = JSONResponse(content=response_model.dict())
        response.headers["Authorization"] = f"Bearer {access_token}"
        return response
    except HTTPException as e:
        raise e

@auth_router.delete("/logout", tags=["Session"], response_model=UserLogoutResponse)
async def logout(authorization: str = Header(None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        logout_user(db, authorization, current_user)
        response = JSONResponse(content={"message": "Logged out successfully"})
        return response
    except HTTPException as e:
        raise e
