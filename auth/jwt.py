import os
import datetime
from uuid import uuid4

from dotenv import load_dotenv

from jose import jwt, JWTError

# Load variables from .env into the environment
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")

# For no expiration
def create_access_token(data: dict):
    login_attempt_id = str(uuid4())
    to_encode = data.copy()
    to_encode.update({"login_attempt_id": login_attempt_id})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# For expiration
def create_access_token_with_expiration(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
