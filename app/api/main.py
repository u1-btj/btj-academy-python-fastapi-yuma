from fastapi import APIRouter

from .user.views import router as user_router
from .auth.views import router as auth_router
from .base.views import router as base_router

router = APIRouter()
router.include_router(user_router)
router.include_router(auth_router)
router.include_router(base_router)