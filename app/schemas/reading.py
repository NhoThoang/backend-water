from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class MeterReadingBase(BaseModel):
    customer_id: int
    reading: float
    month: str # YYYY-MM
    image_url: Optional[str] = None
    note: Optional[str] = None

class MeterReadingCreate(MeterReadingBase):
    pass

class MeterReading(MeterReadingBase):
    id: int
    previous_reading: float
    consumption: float
    is_anomaly: bool
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True

class BillResponse(BaseModel):
    id: int
    bill_number: Optional[str] = None
    month: str
    consumption: float
    water_amount: float
    vat_amount: float
    env_fee_amount: float
    previous_debt: float
    total_amount: float
    status: str
    due_date: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReadingResponse(BaseModel):
    reading: MeterReading
    bill: BillResponse
