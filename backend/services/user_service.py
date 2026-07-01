from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from repositories.user_repository import user
from models.user_model import User

from schemas.user_schema import (
    UserCreate,
    UserUpdate,
)


async def adicionar_usuario(
    session: AsyncSession,
    payload: UserCreate,
):
    existing_user = await user.get_by_email(session, payload.email)
    existing_username = await user.get_by_username(session, payload.username)
    #print(existing_user.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já registrado"
        )
    
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nome de usuário já registrado"
        )

    return await user.create(session, payload)
       


async def listar_usuarios(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
):
    return await user.list(session,skip=skip, limit=limit)


async def get_usuario(
    session: AsyncSession,
    usuario_id: int,
):
    found_user = await user.get(session, usuario_id)
    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return found_user


async def atualizar_usuario(
    session: AsyncSession,
    usuario_id: int,
    payload: UserUpdate,
):
    user = await user.get(session, usuario_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return await user.update(session, user, email=payload.email, password=payload.password)
   


async def remover_usuario(
    session: AsyncSession,
    usuario_id: int,
):
    user = await user.get(session, usuario_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return await user.delete(session=session, user=user)