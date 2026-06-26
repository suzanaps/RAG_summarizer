from fastapi import APIRouter

from routes import (
    auth_router,
    document_router
)


api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(document_router.router)
