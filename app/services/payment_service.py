from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentLog
from app.models.bill import Bill, BillStatus
from app.utils.logger import logger
from datetime import datetime

class PaymentService:
    @staticmethod
    def process_webhook_payment(db: Session, transaction_ref: str, amount: float, method: str, raw_data: dict):
        # 1. Log lại request raw
        log = PaymentLog(raw_request=raw_data, status="received")
        db.add(log)
        db.flush()

        # 2. Tìm Payment record hoặc Bill tương ứng qua transaction_ref
        # Thường transaction_ref sẽ chứa mã hóa đơn (vd: BILL123)
        # Ở đây giả sử mã thanh toán được gửi trong nội dung chuyển khoản
        
        # Tìm Bill chưa thanh toán có ID khớp với mã trong transaction_ref hoặc content
        # Giả sử nội dung là "BILL ID"
        bill_id_str = "".join(filter(str.isdigit, transaction_ref))
        if not bill_id_str:
            log.status = "failed_no_bill_id"
            db.commit()
            return None
            
        bill_id = int(bill_id_str)
        bill = db.query(Bill).filter(Bill.id == bill_id, Bill.status != BillStatus.PAID).first()
        
        if not bill:
            log.status = "failed_bill_not_found"
            db.commit()
            return None

        # 3. Kiểm tra số tiền (Cho phép thanh toán dư hoặc đủ)
        if amount < bill.total_amount:
             # Có thể xử lý thanh toán một phần ở đây
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
        
        log.payment_id = payment.id
        log.status = "success"
        
        db.commit()
        logger.info(f"Payment success for Bill ID {bill.id}, Amount: {amount}")
        return payment
