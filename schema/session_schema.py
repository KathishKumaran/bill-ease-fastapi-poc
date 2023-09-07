from pydantic import BaseModel, EmailStr

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse(BaseModel):
    id:int
    first_name:str
    last_name:str
    role:str

class UserLogoutResponse(BaseModel):
    message:str