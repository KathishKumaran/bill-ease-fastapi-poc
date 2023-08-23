from pydantic import BaseModel

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class EmailRequest(BaseModel):
    email: str

class PasswordResetRequest(BaseModel):
    new_password: str
    confirm_new_password: str