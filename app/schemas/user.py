from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserLogin(BaseModel):
    username: str
    password: str

class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.USER
    customer_id: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[int] = None

class User(UserBase):
    id: int
    is_active: int = 1
    last_login: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
