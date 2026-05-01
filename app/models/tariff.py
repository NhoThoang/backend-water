from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.base import Base

class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    customer_type = Column(String, index=True) # residential / business
    step_number = Column(Integer) # Bậc 1, 2, 3...
    from_m3 = Column(Float) # Từ bao nhiêu khối
    to_m3 = Column(Float, nullable=True) # Đến bao nhiêu khối (null là vô tận)
    price_per_m3 = Column(Float) # Đơn giá
