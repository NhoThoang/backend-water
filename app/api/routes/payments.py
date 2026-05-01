from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.api import deps
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentResponse, SePayWebhookData
from app.utils.logger import logger

router = APIRouter()

@router.post("/webhook/sepay")
async def sepay_webhook(
    data: SePayWebhookData,
    db: Session = Depends(deps.get_db)
):
    """
    Webhook tiếp nhận thông báo chuyển khoản từ SePay.
    """
    logger.info(f"Received SePay Webhook: {data.id} - Content: {data.content}")
    
    # SePay gửi content là nội dung chuyển khoản
    payment = PaymentService.process_webhook_payment(
        db, 
        transaction_ref=data.content, 
        amount=data.transferAmount, 
        method="sepay",
        raw_data=data.dict()
    )
    
    if not payment:
        return {"status": "error", "message": "Bill not found or processed"}
        
    return {"status": "success", "payment_id": payment.id}

@router.get("/history", response_model=List[PaymentResponse])
def get_payment_history(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Xem lịch sử thanh toán của cá nhân (hoặc tất cả nếu là Admin).
    """
    from app.models.payment import Payment
    from app.models.bill import Bill
    
    query = db.query(Payment).join(Bill)
    
    if current_user.role != "admin":
        query = query.filter(Bill.customer_id == current_user.id) # Giả sử user_id trùng với customer_id cho đơn giản hoặc join thêm
        
    return query.all()
