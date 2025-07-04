from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: bool = False

class User(UserBase):
    id: str
    hashed_password: str
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    # REMOVA COMPLETAMENTE A REFERÊNCIA AO HISTÓRICO