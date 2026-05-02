from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    WORKER = "worker"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, index=True, default=UserRole.USER)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_active = Column(Integer, default=1) # 1: Active, 0: Disabled
    password_set = Column(Integer, default=0) # 0: Default, 1: User changed it
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
