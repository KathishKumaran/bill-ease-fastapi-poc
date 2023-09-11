from models.models import User
from schema.dependencies import get_current_user, get_db
from schema.image_schema import ExtractedImageResponse, ImageUploadResponse
from fastapi import APIRouter, Depends, File, UploadFile, Header, HTTPException

from services.image import (
    upload_image,
    extract_text_from_image,
)

image_router = APIRouter()

@image_router.post("/file_upload", tags=["Image"], response_model=ImageUploadResponse)
async def image_upload(file: UploadFile = File(...), authorization: str = Header(None), current_user: User = Depends(get_current_user)):
    try:
        return upload_image(file, authorization, current_user)
    except HTTPException as e:
        raise e

@image_router.get("/extract_text", tags=["Image"], response_model=ExtractedImageResponse)
async def extract_text(user: User = Depends(get_current_user), authorization: str = Header(None), db=Depends(get_db)):
    try:
        return extract_text_from_image(user, authorization, db)
    except HTTPException as e:
        raise e
