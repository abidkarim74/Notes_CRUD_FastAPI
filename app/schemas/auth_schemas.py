from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: str
    
    
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenPayload(BaseModel):
    id: str


