from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class CustomerType(str, enum.Enum):
    RESIDENTIAL = "residential"  # Sinh hoạt
    BUSINESS = "business"        # Kinh doanh

class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    customer_type = Column(String, default=CustomerType.RESIDENTIAL)
    status = Column(String, default=CustomerStatus.ACTIVE)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
