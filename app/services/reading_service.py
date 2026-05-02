from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models.reading import MeterReading
from app.models.bill import Bill, BillStatus
from app.models.customer import Customer
from app.services.tariff_service import TariffService
from datetime import datetime, timedelta

class ReadingService:
    @staticmethod
    async def add_reading(db: AsyncSession, customer_id: int, reading_value: float, month: str, worker_id: int):
        # 1. Lấy chỉ số tháng trước
        stmt = select(MeterReading).where(
            MeterReading.customer_id == customer_id,
            MeterReading.month < month
        ).order_by(desc(MeterReading.month)).limit(1)
        result = await db.execute(stmt)
        last_reading = result.scalars().first()
        
        last_value = last_reading.reading if last_reading else 0
        
        if reading_value < last_value:
            raise ValueError("Chỉ số mới không được nhỏ hơn chỉ số cũ")
            
        consumption = reading_value - last_value
        
        # 2. Kiểm tra bất thường (Anomaly Detection)
        is_anomaly = False
        if last_reading:
            # Nếu tăng > 50% so với tháng trước
            stmt_prev = select(MeterReading).where(
                MeterReading.customer_id == customer_id,
                MeterReading.month < last_reading.month
            ).order_by(desc(MeterReading.month)).limit(1)
            result_prev = await db.execute(stmt_prev)
            prev_reading = result_prev.scalars().first()
            
            prev_value_of_last = prev_reading.reading if prev_reading else 0
            prev_consumption = last_value - prev_value_of_last
            
            if consumption > prev_consumption * 1.5:
                is_anomaly = True
        
        # 3. Lưu reading
        new_reading = MeterReading(
            customer_id=customer_id,
            reading=reading_value,
            previous_reading=last_value,
            consumption=consumption,
            month=month,
            is_anomaly=is_anomaly,
            created_by=worker_id
        )
        db.add(new_reading)
        await db.flush() # Để lấy ID
        
        # 4. Tính toán tiền và tạo Bill
        customer_stmt = select(Customer).where(Customer.id == customer_id)
        customer_result = await db.execute(customer_stmt)
        customer = customer_result.scalars().first()
        
        water_amount = await TariffService.calculate_water_amount(db, customer.customer_type, consumption)
        
        # Tìm nợ cũ
        debt_stmt = select(Bill).where(
            Bill.customer_id == customer_id,
            Bill.status == BillStatus.UNPAID
        )
        debt_result = await db.execute(debt_stmt)
        unpaid_bills = debt_result.scalars().all()
        previous_debt = sum(b.total_amount for b in unpaid_bills)
        
        bill_details = TariffService.get_full_bill_details(water_amount, previous_debt)
        
        new_bill = Bill(
            customer_id=customer_id,
            reading_id=new_reading.id,
            month=month,
            bill_number=f"HD{month.replace('-', '')}{customer_id:04d}",
            consumption=consumption,
            **bill_details,
            due_date=datetime.now() + timedelta(days=15)
        )
        db.add(new_bill)
        await db.commit()
        
        return new_reading, new_bill
