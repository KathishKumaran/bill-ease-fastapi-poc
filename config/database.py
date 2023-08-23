import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load variables from .env into the environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
