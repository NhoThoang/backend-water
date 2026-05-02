from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.customer import CustomerType, CustomerStatus

class CustomerBase(BaseModel):
    customer_id: Optional[str] = None
    name: str
    phone_number: Optional[str] = None
    address: str
    meter_serial: Optional[str] = None
    customer_type: CustomerType = CustomerType.RESIDENTIAL
    status: CustomerStatus = CustomerStatus.ACTIVE
    email: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    installation_date: Optional[datetime] = None

class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None
    password: Optional[str] = None # Mật khẩu tùy chọn khi tạo

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    meter_serial: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    status: Optional[CustomerStatus] = None
    email: Optional[str] = None
    area: Optional[str] = None
    password: Optional[str] = None # Mật khẩu tùy chọn khi cập nhật

class CustomerInDBBase(CustomerBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Customer(CustomerInDBBase):
    pass
