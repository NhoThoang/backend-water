from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.api import deps
from app.models.bill import Bill, BillStatus
from app.models.customer import Customer
from app.models.reading import MeterReading
from app.schemas.reading import BillResponse
from app.schemas.report import DashboardSummary, DashboardStat, RecentActivity
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/unpaid", response_model=List[BillResponse])
async def get_unpaid_bills(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Lấy danh sách các hóa đơn chưa thanh toán. 
    Staff xem toàn bộ, Customer chỉ xem của mình.
    """
    stmt = select(Bill).where(Bill.status != BillStatus.PAID)
    
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

@router.get("/revenue-stats")
async def get_revenue_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_staff)
):
    """
    Thống kê doanh thu theo tháng.
    """
    stmt = select(
        Bill.month,
        func.sum(Bill.total_amount).label("total_billed"),
        func.sum(case((Bill.status == BillStatus.PAID, Bill.total_amount), else_=0)).label("total_collected")
    ).group_by(Bill.month)
    
    result = await db.execute(stmt)
    stats = result.all()
    
    return [
        {"month": s.month, "total_billed": s.total_billed, "total_collected": s.total_collected}
        for s in stats
    ]

@router.get("/high-consumption")
async def get_high_consumption_customers(
    threshold: float = 50.0,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_staff)
):
    """
    Lọc các hộ tiêu thụ nước nhiều (trên ngưỡng threshold m3).
    """
    stmt = select(Customer.name, Customer.address, Bill.consumption, Bill.month)\
        .join(Bill, Customer.id == Bill.customer_id)\
        .where(Bill.consumption >= threshold)
        
    result = await db.execute(stmt)
    results = result.all()
        
    return [
        {"name": r.name, "address": r.address, "consumption": r.consumption, "month": r.month}
        for r in results
    ]

@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Tổng hợp thông tin cho Dashboard và các trang quản lý.
    """
    # Phân quyền: Admin/Worker xem toàn bộ, Customer xem cá nhân
    if current_user.role in ["admin", "worker"]:
        # 1. Tổng khách hàng
        total_customers = await db.scalar(select(func.count(Customer.id)))
        
        # 2. Sản lượng & Doanh thu tháng này
        current_month = datetime.now().strftime("%Y-%m")
        
        stmt_month = select(
            func.sum(Bill.consumption).label("total_consumption"),
            func.sum(Bill.total_amount).label("total_revenue"),
            func.sum(case((Bill.status == BillStatus.PAID, Bill.total_amount), else_=0)).label("collected_revenue"),
            func.sum(case((Bill.status != BillStatus.PAID, Bill.total_amount), else_=0)).label("unpaid_revenue"),
            func.count(case((Bill.status != BillStatus.PAID, Bill.id), else_=None)).label("unpaid_count")
        ).where(Bill.month == current_month)
        
        month_data = (await db.execute(stmt_month)).first()
        total_consumption = month_data.total_consumption or 0
        total_revenue = month_data.total_revenue or 0
        collected_revenue = month_data.collected_revenue or 0
        unpaid_revenue = month_data.unpaid_revenue or 0
        unpaid_count = month_data.unpaid_count or 0
        
        # 3. Cảnh báo rò rỉ (Anomalies)
        stmt_anomalies = select(MeterReading, Customer.name)\
            .join(Customer, MeterReading.customer_id == Customer.id)\
            .where(MeterReading.is_anomaly == True)\
            .order_by(MeterReading.created_at.desc())\
            .limit(10)
        
        anomalies_result = await db.execute(stmt_anomalies)
        anomalies = []
        for reading, customer_name in anomalies_result:
            anomalies.append({
                "id": reading.id,
                "customer_name": customer_name,
                "month": reading.month,
                "consumption": float(reading.consumption or 0),
                "time_ago": "Vừa xong"
            })
        
        stats = [
            {"title": "Tổng khách hàng", "value": f"{total_customers:,}", "change": "+0%", "trend": "up", "icon_type": "users", "color": "bg-blue-500/20 text-blue-500"},
            {"title": "Sản lượng tháng này", "value": f"{total_consumption:,.1f} m³", "change": "+0%", "trend": "up", "icon_type": "droplets", "color": "bg-cyan-500/20 text-cyan-500"},
            {"title": "Doanh thu dự kiến", "value": f"{total_revenue:,.0f}đ", "change": "+0%", "trend": "up", "icon_type": "dollar", "color": "bg-emerald-500/20 text-emerald-500"},
            {"title": "Cảnh báo rò rỉ", "value": str(len(anomalies)), "change": "+0", "trend": "up", "icon_type": "alert", "color": "bg-amber-500/20 text-amber-500"}
        ]
        
        # 4. Hoạt động gần đây
        stmt_recent = select(Bill, Customer.name)\
            .join(Customer, Bill.customer_id == Customer.id)\
            .order_by(Bill.created_at.desc())\
            .limit(5)
        
        recent_results = await db.execute(stmt_recent)
        recent_activities = []
        for bill, customer_name in recent_results:
            recent_activities.append({
                "id": bill.id,
                "description": f"Hóa đơn {customer_name} tháng {bill.month} đã được tạo",
                "time_ago": "Vừa xong",
                "type": "bill"
            })
            
        # 5. Lịch sử tiêu thụ (6 tháng gần nhất)
        stmt_history = select(
            MeterReading.month,
            func.sum(MeterReading.consumption).label("consumption")
        ).group_by(MeterReading.month).order_by(MeterReading.month.desc()).limit(6)
        
        history_results = (await db.execute(stmt_history)).all()
        consumption_history = [
            {"month": h.month, "consumption": float(h.consumption or 0)}
            for h in reversed(history_results)
        ]
            
        return {
            "stats": stats,
            "recent_activities": recent_activities,
            "bill_overview": {"total_unpaid": unpaid_revenue, "unpaid_count": unpaid_count, "total_collected": collected_revenue},
            "anomalies": anomalies,
            "consumption_history": consumption_history
        }
    else:
        # LOGIC CHO CUSTOMER (Người dùng cuối)
        # 1. Tìm thông tin khách hàng liên kết với user này
        stmt_cust = select(Customer).where(Customer.user_id == current_user.id)
        customer = (await db.execute(stmt_cust)).scalars().first()
        
        if not customer:
            return {
                "stats": [], "recent_activities": [], 
                "bill_overview": {"total_unpaid": 0, "unpaid_count": 0, "total_collected": 0},
                "anomalies": []
            }

        # 2. Thống kê hóa đơn của riêng khách hàng này
        stmt_bills = select(
            func.sum(Bill.consumption).label("total_consumption"),
            func.sum(case((Bill.status != BillStatus.PAID, Bill.total_amount), else_=0)).label("unpaid_revenue"),
            func.count(case((Bill.status != BillStatus.PAID, Bill.id), else_=None)).label("unpaid_count"),
            func.sum(case((Bill.status == BillStatus.PAID, Bill.total_amount), else_=0)).label("collected_revenue")
        ).where(Bill.customer_id == customer.id)
        
        cust_data = (await db.execute(stmt_bills)).first()
        
        # 3. Lấy chỉ số mới nhất
        stmt_last_reading = select(MeterReading).where(MeterReading.customer_id == customer.id).order_by(MeterReading.created_at.desc()).limit(1)
        last_reading = (await db.execute(stmt_last_reading)).scalars().first()
        
        stats = [
            {"title": "Mã khách hàng", "value": customer.customer_id, "change": "Đang hoạt động", "trend": "up", "icon_type": "users", "color": "bg-blue-500/20 text-blue-500"},
            {"title": "Chỉ số mới nhất", "value": f"{last_reading.reading if last_reading else 0:,.1f}", "change": last_reading.month if last_reading else "-", "trend": "up", "icon_type": "droplets", "color": "bg-cyan-500/20 text-cyan-500"},
            {"title": "Tổng nợ hiện tại", "value": f"{cust_data.unpaid_revenue or 0:,.0f}đ", "change": f"{cust_data.unpaid_count or 0} hóa đơn", "trend": "down", "icon_type": "dollar", "color": "bg-destructive/20 text-destructive"},
            {"title": "Tiêu thụ (Lũy kế)", "value": f"{cust_data.total_consumption or 0:,.1f} m³", "change": "Tổng cộng", "trend": "up", "icon_type": "alert", "color": "bg-emerald-500/20 text-emerald-500"}
        ]
        
        # 4. Lịch sử tiêu thụ cá nhân (6 tháng gần nhất)
        stmt_cust_history = select(
            MeterReading.month,
            MeterReading.consumption
        ).where(MeterReading.customer_id == customer.id).order_by(MeterReading.month.desc()).limit(6)
        
        cust_history_results = (await db.execute(stmt_cust_history)).all()
        consumption_history = [
            {"month": h.month, "consumption": float(h.consumption or 0)}
            for h in reversed(cust_history_results)
        ]

        # 5. Lịch sử hóa đơn gần đây
        stmt_recent_bills = select(Bill).where(Bill.customer_id == customer.id).order_by(Bill.month.desc()).limit(5)
        recent_bills = (await db.execute(stmt_recent_bills)).scalars().all()
        recent_activities = [
            {"id": b.id, "description": f"Hóa đơn tháng {b.month}: {b.total_amount:,.0f}đ ({'Đã trả' if b.status == BillStatus.PAID else 'Chưa trả'})", "time_ago": "Hóa đơn", "type": "bill"}
            for b in recent_bills
        ]

        return {
            "stats": stats,
            "recent_activities": recent_activities,
            "bill_overview": {"total_unpaid": cust_data.unpaid_revenue or 0, "unpaid_count": cust_data.unpaid_count or 0, "total_collected": cust_data.collected_revenue or 0},
            "anomalies": [],
            "consumption_history": consumption_history
        }
