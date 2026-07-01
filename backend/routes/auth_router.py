from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from schemas.user_schema import AuthResponse, LoginRequest, UserPublic, UserCreate
from services.auth_service import validate_email, create_access_token, verify_password
from repositories.user_repository import user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserCreate, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    validate_email(request.email)

    if not request.password or len(request.password) < 6:
        raise HTTPException(status_code=400, detail="A senha deve ter pelo menos 6 caracteres.")

    existing_user = await user.get_by_email(db, request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Este e-mail ja esta cadastrado.")

    new_user = await user.create(db, email=request.email, password=request.password)

    access_token = create_access_token(new_user)
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserPublic(id=new_user.id, email=new_user.email),
    )


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
