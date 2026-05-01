from sqlalchemy.orm import Session
from app.models.reading import MeterReading
from app.models.bill import Bill, BillStatus
from app.models.customer import Customer
from app.services.tariff_service import TariffService
from datetime import datetime, timedelta

class ReadingService:
    @staticmethod
    def add_reading(db: Session, customer_id: int, reading_value: float, month: str, worker_id: int):
        # 1. Lấy chỉ số tháng trước
        last_reading = db.query(MeterReading).filter(
            MeterReading.customer_id == customer_id,
            MeterReading.month < month
        ).order_by(MeterReading.month.desc()).first()
        
        last_value = last_reading.reading if last_reading else 0
        
        if reading_value < last_value:
            raise ValueError("Chỉ số mới không được nhỏ hơn chỉ số cũ")
            
        consumption = reading_value - last_value
        
        # 2. Kiểm tra bất thường (Anomaly Detection)
        is_anomaly = False
        if last_reading:
            # Nếu tăng > 50% so với tháng trước
            prev_consumption = last_value - (db.query(MeterReading).filter(
                MeterReading.customer_id == customer_id,
                MeterReading.month < last_reading.month
            ).order_by(MeterReading.month.desc()).first().reading if db.query(MeterReading).filter(
                MeterReading.customer_id == customer_id,
                MeterReading.month < last_reading.month
            ).first() else 0)
            
            if consumption > prev_consumption * 1.5:
                is_anomaly = True
        
        # 3. Lưu reading
        new_reading = MeterReading(
            customer_id=customer_id,
            reading=reading_value,
            month=month,
            is_anomaly=is_anomaly,
            created_by=worker_id
        )
        db.add(new_reading)
        db.flush() # Để lấy ID
        
        # 4. Tính toán tiền và tạo Bill
        customer = db.query(Customer).get(customer_id)
        water_amount = TariffService.calculate_water_amount(db, customer.customer_type, consumption)
        
        # Tìm nợ cũ
        unpaid_bills = db.query(Bill).filter(
            Bill.customer_id == customer_id,
            Bill.status == BillStatus.UNPAID
        ).all()
        previous_debt = sum(b.total_amount for b in unpaid_bills)
        
        bill_details = TariffService.get_full_bill_details(water_amount, previous_debt)
        
        new_bill = Bill(
            customer_id=customer_id,
            reading_id=new_reading.id,
            month=month,
            consumption=consumption,
            **bill_details,
            due_date=datetime.now() + timedelta(days=15)
        )
        db.add(new_bill)
        db.commit()
        
        return new_reading, new_bill
