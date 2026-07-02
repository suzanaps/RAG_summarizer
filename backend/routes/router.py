from fastapi import APIRouter

from routes import (
    auth_router,
    document_router,
    user_router,
    summarizer_router
)


api_router = APIRouter()
api_router.include_router(user_router.router)
api_router.include_router(auth_router.router)
api_router.include_router(document_router.router)
api_router.include_router(summarizer_router.router)
