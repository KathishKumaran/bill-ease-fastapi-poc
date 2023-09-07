from pydantic import BaseModel
from typing import List

class ExtractedTextItem(BaseModel):
    text: str
    coordinates: str

class ExtractedImageResponse(BaseModel):
    extracted_text: List[ExtractedTextItem]
    image_data: str

class ImageUploadResponse(BaseModel):
    message:str