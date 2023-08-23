# modules/routers.py
from fastapi import APIRouter
from .session import auth_router
from .password import password_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(password_router)
