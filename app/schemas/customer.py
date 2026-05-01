from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.customer import CustomerType, CustomerStatus

class CustomerBase(BaseModel):
    name: str
    address: str
    customer_type: CustomerType = CustomerType.RESIDENTIAL
    status: CustomerStatus = CustomerStatus.ACTIVE

class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    status: Optional[CustomerStatus] = None

class CustomerInDBBase(CustomerBase):
    id: int
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class Customer(CustomerInDBBase):
    pass
