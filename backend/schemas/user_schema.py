from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator



class UserBase(BaseModel):
    email: str
    password: str

    @field_validator('email', mode='before')
    @classmethod
    def normalize_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email:Optional[str] = None
    password:Optional[str] = None

class UserPublic(BaseModel):
    id:int
    email:str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic
   
  

    class Config:
        from_attributes=True