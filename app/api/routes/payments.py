from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentResponse, SePayWebhookData
from app.models.payment import Payment
from app.models.bill import Bill
from app.models.customer import Customer
from app.utils.logger import logger

router = APIRouter()

@router.post("/webhook/sepay")
async def sepay_webhook(
    data: SePayWebhookData,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Webhook tiếp nhận thông báo chuyển khoản từ SePay.
    """
    logger.info(f"Received SePay Webhook: {data.id} - Content: {data.content}")
    
    # SePay gửi content là nội dung chuyển khoản
    payment = await PaymentService.process_webhook_payment(
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
async def get_payment_history(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Xem lịch sử thanh toán (Admin xem tất cả, User chỉ xem của mình).
    """
    stmt = select(Payment).join(Bill)
    
    if current_user.role not in ["admin", "worker"]:
        # Tìm customer_id từ user_id
        stmt_customer = select(Customer).where(Customer.user_id == current_user.id)
        res_customer = await db.execute(stmt_customer)
        customer = res_customer.scalars().first()
        if not customer:
            return []
        stmt = stmt.where(Bill.customer_id == customer.id)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/me", response_model=List[PaymentResponse])
async def get_my_payments(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Khách hàng tự xem lịch sử thanh toán của mình.
    """
    stmt_customer = select(Customer).where(Customer.user_id == current_user.id)
    res_customer = await db.execute(stmt_customer)
    customer = res_customer.scalars().first()
    
    if not customer:
        return []
        
    stmt = select(Payment).join(Bill).where(Bill.customer_id == customer.id)
    result = await db.execute(stmt)
    return result.scalars().all()

