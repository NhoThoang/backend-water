from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment, PaymentLog
from app.models.bill import Bill, BillStatus
from app.utils.logger import logger
from datetime import datetime

class PaymentService:
    @staticmethod
    async def process_webhook_payment(db: AsyncSession, transaction_ref: str, amount: float, method: str, raw_data: dict):
        # 1. Log lại request raw
        log = PaymentLog(raw_request=raw_data, status="received")
        db.add(log)
        await db.flush()

        # 2. Tìm Bill tương ứng qua transaction_ref
        bill_id_str = "".join(filter(str.isdigit, transaction_ref))
        if not bill_id_str:
            log.status = "failed_no_bill_id"
            await db.commit()
            return None
            
        bill_id = int(bill_id_str)
        stmt = select(Bill).where(Bill.id == bill_id, Bill.status != BillStatus.PAID)
        result = await db.execute(stmt)
        bill = result.scalars().first()
        
        if not bill:
            log.status = "failed_bill_not_found"
            await db.commit()
            return None

        # 3. Kiểm tra số tiền
        if amount < bill.total_amount:
             bill.status = BillStatus.PARTIAL
        else:
             bill.status = BillStatus.PAID
             bill.paid_at = datetime.utcnow()

        # 4. Tạo bản ghi Payment
        payment = Payment(
            bill_id=bill.id,
            amount=amount,
            method=method,
            status="success",
            transaction_ref=transaction_ref,
            paid_at=datetime.utcnow()
        )
        db.add(payment)
        await db.flush()
        
        log.payment_id = payment.id
        log.status = "success"
        
        await db.commit()
        logger.info(f"Payment success for Bill ID {bill.id}, Amount: {amount}")
        return payment
