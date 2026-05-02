from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class BillStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    PARTIAL = "partial"

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    reading_id = Column(Integer, ForeignKey("meter_readings.id"), unique=True)
    month = Column(String, index=True) # YYYY-MM
    bill_number = Column(String, unique=True, index=True) # Mã hóa đơn (Vd: HD2026050001)
    
    consumption = Column(Float) # Số khối tiêu thụ (current - last)
    water_amount = Column(Float) # Tiền nước trước thuế
    vat_amount = Column(Float) # 5% VAT
    env_fee_amount = Column(Float) # 10% Phí BVMT
    previous_debt = Column(Float, default=0) # Nợ cũ cộng dồn
    total_amount = Column(Float) # Tổng cộng cần thanh toán
    
    calculation_details = Column(JSON, nullable=True) # Chi tiết tính tiền (các bậc)
    status = Column(String, default=BillStatus.UNPAID)
    due_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
