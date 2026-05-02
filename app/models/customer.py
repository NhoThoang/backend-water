from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Float
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
    customer_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=False)
    meter_serial = Column(String, nullable=True)
    customer_type = Column(String, default=CustomerType.RESIDENTIAL)
    status = Column(String, default=CustomerStatus.ACTIVE)
    
    # New Fields
    email = Column(String, nullable=True)
    area = Column(String, nullable=True, index=True) # Khu vực / Tuyến đọc
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    installation_date = Column(DateTime(timezone=True), nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
