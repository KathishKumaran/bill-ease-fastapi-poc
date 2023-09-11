from models.models import User
from sqlalchemy.orm import Session
from schema.dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, Header, HTTPException
from schema.password_schema import EmailRequest, PasswordResetRequest, PasswordChangeRequest, PasswordResponse

from services.password import (
    send_reset_password_link,
    reset_password,
    change_password,
)

password_router = APIRouter()

@password_router.post("/send_resend_password_link", tags=["Password"], response_model=PasswordResponse)
async def send_reset_link(email_data: EmailRequest):
    try:
        return send_reset_password_link(email_data)
    except HTTPException as e:
        raise e

@password_router.post("/reset_password", tags=["Password"], response_model=PasswordResponse)
async def password_reset(
    new_password_data: PasswordResetRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    try:
        return reset_password(new_password_data, authorization, db)
    except HTTPException as e:
        raise e

@password_router.post("/change_password", tags=["Password"], response_model=PasswordResponse)
async def password_change(
    password_data: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return change_password(password_data, user, db)
    except HTTPException as e:
        raise e
