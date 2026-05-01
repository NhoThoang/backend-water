from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.bill import Bill, BillStatus
from app.models.customer import Customer
from app.schemas.reading import BillResponse

router = APIRouter()

@router.get("/unpaid", response_model=List[BillResponse])
def get_unpaid_bills(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Lấy danh sách các hóa đơn chưa thanh toán (Nợ đọng).
    """
    return db.query(Bill).filter(Bill.status != BillStatus.PAID).all()

@router.get("/revenue-stats")
def get_revenue_stats(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Thống kê doanh thu theo tháng.
    """
    stats = db.query(
        Bill.month,
        func.sum(Bill.total_amount).label("total_billed"),
        func.sum(func.case((Bill.status == BillStatus.PAID, Bill.total_amount), else_=0)).label("total_collected")
    ).group_by(Bill.month).all()
    
    return [
        {"month": s.month, "total_billed": s.total_billed, "total_collected": s.total_collected}
        for s in stats
    ]

@router.get("/high-consumption")
def get_high_consumption_customers(
    threshold: float = 50.0,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Lọc các hộ tiêu thụ nước nhiều (trên ngưỡng threshold m3).
    """
    results = db.query(Customer.name, Customer.address, Bill.consumption, Bill.month)\
        .join(Bill, Customer.id == Bill.customer_id)\
        .filter(Bill.consumption >= threshold).all()
        
    return [
        {"name": r.name, "address": r.address, "consumption": r.consumption, "month": r.month}
        for r in results
    ]
