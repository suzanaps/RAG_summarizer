from models.user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Iterable, Optional
from sqlalchemy import select
import hashlib
import hmac
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional



class UserRepository:
    def get_hash_password(self,password: str, salt: Optional[str] = None) -> str:
        salt = salt or os.urandom(16).hex()
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            100_000,
        ).hex()
        return f"{salt}:{password_hash}"


    async def create(self,session:AsyncSession, user: User )->User:
        normalized_email = user.email.strip().lower()
        hash_password = self.get_hash_password(user.password)
        new_user = User(username=user.username,description=user.description, name=user.name, profile_picture=user.profile_picture,email=normalized_email, password=hash_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user


    async def update(self,session:AsyncSession,
     user:User, 
     *, 
     email: Optional[str]=None, 
     password: Optional[str]=None,
     username: Optional[str]=None,
     description: Optional[str]=None,
     name: Optional[str]=None,
     profile_picture: Optional[str]=None,
     )-> User:

        if email is not None:
            user.email = email
        if password is not None:
            user.password = password
        if username is not None:
            user.username = username
        if description is not None:
            user.description = description
        if name is not None:
            user.name = name
        if profile_picture is not None:
            user.profile_picture = profile_picture
    
        await session.commit()
        await session.refresh(user)
        return user
    

    async def delete(self,session:AsyncSession, user:User)->User:
        await session.delete(user)
        await session.commit()


    async def get(self,session:AsyncSession, user_id: int)->Optional[User]:
        return await session.get(User, user_id)
        
    async def get_by_email(self,session:AsyncSession, email:str)->Optional[User]:
        normalized_email = email.strip().lower()
        query = select(User).where(User.email == normalized_email)
        result = session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self,session:AsyncSession, username:str)->Optional[User]:
        query = select(User).where(User.username == username)
        result = session.execute(query)
        return result.scalar_one_or_none()


    async def list(self,session:AsyncSession, *,skip: int =0, limit: int = 50,) -> Iterable[User]:
        query = select(User)
        query = query.offset(skip).limit(limit)
        result = session.execute(query)
        return result.scalars().all()


user = UserRepository()