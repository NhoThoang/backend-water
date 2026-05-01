from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.USER
    customer_id: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[UserRole] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
