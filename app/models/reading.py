from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base

class MeterReading(Base):
    __tablename__ = "meter_readings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), index=True)
    month = Column(String, index=True) # YYYY-MM
    reading = Column(Float, nullable=False) # Chỉ số mới
    image_url = Column(String, nullable=True)
    is_anomaly = Column(Boolean, default=False) # Cảnh báo bất thường
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint('customer_id', 'month', name='_customer_month_uc'),)
