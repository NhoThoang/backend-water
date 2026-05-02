import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.customer import Customer, CustomerType, CustomerStatus
from app.models.reading import MeterReading
from app.models.bill import Bill, BillStatus
from app.core.security import get_password_hash
from app.db.init_db import init_db

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal

async def seed_data():
    async with engine.begin() as conn:
        print("Dropping all tables (CASCADE)...")
        # Lấy danh sách các bảng hiện có
        from sqlalchemy import text
        await conn.execute(text("DROP TABLE IF EXISTS payments, bills, meter_readings, tariffs, customers, users, tokens CASCADE"))
        
        print("Recreating all tables...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        print("Initializing basic data (Admin, Tariffs)...")
        await init_db(db)
        
        print("Starting sample data seed...")

        # 2. Tạo một số khách hàng mẫu
        customers_data = [
            {"name": "Nguyễn Văn An", "address": "123 Đường Lê Lợi, TP. Đà Nẵng", "phone": "0905123456", "type": CustomerType.RESIDENTIAL, "cid": "KH001", "meter": "SN-8801"},
            {"name": "Trần Thị Bình", "address": "456 Đường Hùng Vương, TP. Đà Nẵng", "phone": "0905234567", "type": CustomerType.RESIDENTIAL, "cid": "KH002", "meter": "SN-8802"},
            {"name": "Lê Văn Cường", "address": "789 Đường Nguyễn Tất Thành, TP. Đà Nẵng", "phone": "0905345678", "type": CustomerType.RESIDENTIAL, "cid": "KH003", "meter": "SN-8803"},
            {"name": "Phạm Minh Đức", "address": "101 Đường Điện Biên Phủ, TP. Đà Nẵng", "phone": "0905456789", "type": CustomerType.RESIDENTIAL, "cid": "KH004", "meter": "SN-8804"},
            {"name": "Công ty TNHH Giải Pháp Nước", "address": "Khu Công nghiệp Hòa Khánh", "phone": "02363123456", "type": CustomerType.BUSINESS, "cid": "KH005", "meter": "SN-9901"},
        ]

        customers = []
        for data in customers_data:
            # Tạo User trước
            user = User(
                username=data["cid"], # Dùng mã KH làm tên đăng nhập
                password_hash=get_password_hash("placeholder_not_used"),
                role=UserRole.USER,
                customer_id=data["cid"],
                phone_number=data["phone"],
                address=data["address"],
                password_set=0 # Sẽ kiểm tra fallback: SĐT hoặc zxcvbnm12345
            )
            db.add(user)
            await db.flush() # Để lấy user.id

            customer = Customer(
                customer_id=data["cid"],
                name=data["name"],
                phone_number=data["phone"],
                address=data["address"],
                meter_serial=data["meter"],
                customer_type=data["type"],
                status=CustomerStatus.ACTIVE,
                user_id=user.id # Liên kết với user
            )
            db.add(customer)
            customers.append(customer)
        
        await db.commit()
        for c in customers:
            await db.refresh(c)

        # 2.5 Tạo tài khoản Worker
        print("Creating sample worker...")
        worker = User(
            username="worker1",
            password_hash=get_password_hash("worker1"),
            role=UserRole.WORKER,
            phone_number="0911222333",
            password_set=1
        )
        db.add(worker)
        await db.commit()
        await db.refresh(worker)

        # 3. Tạo chỉ số nước và hóa đơn cho 3 tháng gần nhất
        months = ["2026-03", "2026-04", "2026-05"]
        
        for customer in customers:
            last_reading = random.randint(100, 500)
            
            for month in months:
                # Tạo chỉ số nước
                consumption = random.randint(15, 35)
                # Giả lập rò rỉ cho khách hàng 3 vào tháng 5
                if customer.customer_id == "KH003" and month == "2026-05":
                    consumption = 85
                    is_anomaly = True
                else:
                    is_anomaly = False
                
                current_reading_val = last_reading + consumption
                
                reading = MeterReading(
                    customer_id=customer.id,
                    month=month,
                    reading=current_reading_val,
                    previous_reading=float(last_reading),
                    consumption=float(consumption),
                    is_anomaly=is_anomaly,
                    created_by=worker.id # Ghi bởi worker1
                )
                db.add(reading)
                await db.commit()
                await db.refresh(reading)

                # Tạo hóa đơn
                # Logic tính tiền đơn giản (giả sử 10k/m3)
                water_amount = consumption * 10000
                vat = water_amount * 0.05
                env_fee = water_amount * 0.1
                total = water_amount + vat + env_fee
                
                # Trạng thái thanh toán: tháng 3, 4 đã trả, tháng 5 chưa trả
                status = BillStatus.PAID if month != "2026-05" else BillStatus.UNPAID
                paid_at = datetime.now() if status == BillStatus.PAID else None
                
                bill = Bill(
                    customer_id=customer.id,
                    reading_id=reading.id,
                    month=month,
                    bill_number=f"HD{month.replace('-', '')}{customer.id:04d}",
                    consumption=float(consumption),
                    water_amount=float(water_amount),
                    vat_amount=float(vat),
                    env_fee_amount=float(env_fee),
                    total_amount=float(total),
                    status=status,
                    due_date=datetime.now() + timedelta(days=15),
                    paid_at=paid_at,
                    calculation_details={"tiers": [{"m3": consumption, "price": 10000}]}
                )
                db.add(bill)
                
                last_reading = current_reading_val
        
        await db.commit()
        print("Seed data completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
