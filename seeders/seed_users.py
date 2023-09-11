import os
import sys
import bcrypt
from datetime import datetime
from models.models import User
from config.database import SessionLocal

# Add the root directory of your project to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def seed_users():
    users = [
        User(
            first_name='xxxx1',
            last_name='xxxx1',
            email='xxxx1@yopmail.com',
            role='admin',
            encrypted_password=bcrypt.hashpw(b'xxxx@012', bcrypt.gensalt()).decode('utf-8'),
            confirmed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        User(
            first_name='xxxx2',
            last_name='xxxx2',
            email='xxxx2@yopmail.com',
            role='user',
            encrypted_password=bcrypt.hashpw(b'xxx@012', bcrypt.gensalt()).decode('utf-8'),
            confirmed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        # Add more user instances as needed
    ]
    with SessionLocal() as session:
        session.add_all(users)
        session.commit()

# Execute the seed_users function only when the script is run directly
if __name__ == '__main__':
    seed_users()
