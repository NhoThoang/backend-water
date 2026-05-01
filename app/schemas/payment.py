from typing import Optional, Any
from pydantic import BaseModel
from datetime import datetime

class PaymentBase(BaseModel):
    bill_id: int
    amount: float
    method: str
    transaction_ref: str

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    status: str
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True

class SePayWebhookData(BaseModel):
    id: int
    content: str
    transferType: str
    transferAmount: float
    accumulated: float
    code: Optional[str]
    transactionDate: str
    referenceCode: str
    description: str
    gateway: str
