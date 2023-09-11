import os
import io
import time
import base64
import logging
import easyocr
from models.models import  Image
from sqlalchemy.orm import Session
from config.database import SessionLocal
from fastapi import HTTPException,status

# Suppress easyocr warnings by setting its logging level to a higher level
logging.getLogger('easyocr').setLevel(logging.ERROR)

reader = easyocr.Reader(['en'])

def upload_image(file, authorization, current_user):
    # Ensure Authorization Header is Present
    if authorization != f"Bearer {current_user.access_token}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    valid_formats = [".jpeg", ".jpg", ".png"]

    filename = file.filename
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension not in valid_formats:
        raise HTTPException(status_code=422, detail="Invalid file format. Only JPEG, JPG, and PNG formats are allowed.")

    max_file_size = 2 * 1024 * 1024  # 20MB in bytes
    file_content = file.file.read()
    if len(file_content) > max_file_size:
        raise HTTPException(status_code=413, detail="File size exceeds the limit of 20MB.")

    db: Session = SessionLocal()

    # Query the database for the user's existing image
    existing_image = db.query(Image).filter_by(user_id=current_user.id).first()

    if existing_image:
        # Delete the old image file from storage
        if os.path.exists(existing_image.image_url):
            os.remove(existing_image.image_url)
        # Update the existing image record in the database
        existing_image.image_url = None  # Remove the old URL

    image_folder = "assets"  # Choose an appropriate folder name
    uploaded_image_name = file.filename + "_" + str(time.time()) + file_extension
    uploaded_image_path = os.path.join(image_folder, uploaded_image_name)

    with open(uploaded_image_path, "wb") as image_file:
        image_file.write(file_content)

    if existing_image:
        # Update the existing image record with the new URL
        existing_image.image_url = uploaded_image_path
    else:
        # Create a new image record
        db_image = Image(user_id=current_user.id, image_url=uploaded_image_path)
        db.add(db_image)

    db.commit()
    db.close()

    return {"message": "Image uploaded successfully"}

def extract_text_from_image(user, authorization, db):
    # Ensure Authorization Header is Present
    if authorization != f"Bearer {user.access_token}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Query the database for the user's image
    user_image = db.query(Image).filter_by(user_id=user.id).first()

    if not user_image or not user_image.image_url:
        raise HTTPException(status_code=404, detail="Image not found for the user")

    image_path = user_image.image_url

    # Perform text extraction using EasyOCR
    try:
        results = reader.readtext(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error extracting text from image")

    image_binary = get_image_binary(image_path)

    # Encode the image data using Base64
    image_base64 = base64.b64encode(image_binary).decode('utf-8')

    extracted_text = []
    for result in results:
        text, coord, _ = result  # Unpack the tuple
        extracted_text.append({
            "coordinates": str(text),
            "text": coord
        })

    response_content = {
        "extracted_text": extracted_text,
        "image_data": image_base64,
    }

    return response_content

def get_image_binary(image_path):
    # Open the image file
    try:
        with open(image_path, "rb") as f:
            image = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading image")

    # Create a BytesIO object
    try:
        with io.BytesIO() as b:
            b.write(image)
            b.seek(0)
            image_data = b.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing image")

    return image_data
