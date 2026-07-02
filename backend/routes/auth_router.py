from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus

from db.database import get_db
from schemas.user_schema import AuthResponse, LoginRequest, UserPublic
from services.auth_service import validate_email, create_access_token, verify_password
from repositories.user_repository import user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    validate_email(request.email)

    if not request.password:
        raise HTTPException(status_code=400, detail="Informe sua senha.")

    user_login = await user.get_by_email(db, request.email)
    if not user_login:
        raise HTTPException(status_code=401, detail="E-mail incorreto.")

    if not verify_password(request.password, user_login.password):
        raise HTTPException(status_code=401, detail="Senha incorreta.")

    access_token = create_access_token(user_login)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic(id=user_login.id, email=user_login.email, username=user_login.username, name=user_login.name, description=user_login.description),
    )
