import os
import re
import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from core.config import get_settings  

# Carrega as configurações centralizadas
settings = get_settings()

# Usa a chave diretamente do objeto settings
JWT_SECRET_KEY = settings.secret_key 

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Optional
from backend.repositories.user_repository import user
from sqlalchemy.ext.asyncio import AsyncSession



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


bearer_scheme = HTTPBearer()

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash armazenado.
    
    O hash armazenado está no formato: salt:hash_hexadecimal
    """
    try:
        salt, password_hash = hashed_password.split(":")
        plain_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            bytes.fromhex(salt),
            100_000,
        ).hex()
        return plain_hash == password_hash
    except (ValueError, IndexError):
        return False


def create_access_token(user: dict) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": user.email,
        "user_id": user.id,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(db: AsyncSession, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as error:
        raise HTTPException(status_code=401, detail="Token expirado.") from error
    except jwt.InvalidTokenError as error:
        raise HTTPException(status_code=401, detail="Token invalido.") from error

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token invalido.")

    user = user.get_by_email(db,email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado.")

    return user

def validate_email(email: str):
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
        raise HTTPException(status_code=400, detail="Informe um e-mail valido.")