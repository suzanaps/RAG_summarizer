from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth_service import validate_email, create_access_token

from db.database import get_db
from schemas.user_schema import UserCreate, UserPublic, UserUpdate, AuthResponse
from services.user_service import (
    adicionar_usuario,
    listar_usuarios,
    get_usuario,
    atualizar_usuario,
    remover_usuario,
)

from models.user_model import User

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    user = await adicionar_usuario(db, payload)

    access_token = create_access_token(user)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic(id=user.id, email=user.email, username=user.username, name=user.name, description=user.description),
    )


@router.get("", response_model=list[UserPublic])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> list[UserPublic]:
    users = await listar_usuarios(db, skip, limit)
   # return [UserPublic.model_validate(u) for u in users]
    return users


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    user = await get_usuario(db, user_id)
    return user


@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(
    payload: UserUpdate,
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    user = await atualizar_usuario(db, user_id, payload)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    await remover_usuario(db, user_id)
    return None