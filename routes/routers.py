from fastapi import APIRouter
from controllers.image import image_router
from controllers.session import auth_router
from controllers.password import password_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(password_router)
router.include_router(image_router)
