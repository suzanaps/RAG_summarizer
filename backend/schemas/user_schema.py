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
    username: str
    description: Optional[str] = None
    profile_picture: Optional[str] = None
    name: str


class UserUpdate(BaseModel):
    email:Optional[str] = None
    password:Optional[str] = None
    username: Optional[str] = None
    description: Optional[str] = None
    profile_picture: Optional[str] = None
    name: Optional[str] = None


class UserPublic(BaseModel):
    id:int
    email:str
    username:str
    description:str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic
   
  
    class Config:
        from_attributes=True