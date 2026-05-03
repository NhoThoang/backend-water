from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.services.reading_service import ReadingService
from app.schemas.reading import MeterReading, MeterReadingCreate, ReadingResponse
from app.models.reading import MeterReading as MeterReadingModel
from app.models.customer import Customer
from app.utils.logger import logger

router = APIRouter()

@router.post("/", response_model=ReadingResponse)
async def create_reading(
    *,
    db: AsyncSession = Depends(deps.get_db),
    reading_in: MeterReadingCreate,
    current_user = Depends(deps.get_current_user)
):
    """
    Submit a new water meter reading. Tự động tính tiền và tạo hóa đơn.
    Accessible by Admin and Worker.
    """
    if current_user.role not in ["admin", "worker"]:
        raise HTTPException(status_code=403, detail="Not enough privileges")
        
    try:
        reading, bill = await ReadingService.add_reading(
            db, 
            customer_id=reading_in.customer_id,
            reading_value=reading_in.reading,
            month=reading_in.month,
            worker_id=current_user.id,
            image_url=reading_in.image_url,
            note=reading_in.note
        )
        
        if reading.is_anomaly:
            logger.warning(f"Anomaly detected for customer {reading.customer_id} in month {reading.month}")
            
        return {"reading": reading, "bill": bill}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/anomalies", response_model=List[MeterReading])
async def get_anomalies(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Lấy danh sách các chỉ số nước bất thường (Admin only).
    """
    stmt = select(MeterReadingModel).where(MeterReadingModel.is_anomaly == True)
    result = await db.execute(stmt)
    anomalies = result.scalars().all()
    return anomalies

@router.get("/customer/{customer_id}", response_model=List[MeterReading])
async def get_customer_readings(
    customer_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Xem lịch sử ghi chỉ số của một hộ dân.
    """
    stmt = select(MeterReadingModel).where(MeterReadingModel.customer_id == customer_id)
    result = await db.execute(stmt)
    readings = result.scalars().all()
    return readings

@router.get("/me", response_model=List[MeterReading])
async def get_my_readings(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Khách hàng tự xem lịch sử ghi chỉ số của mình.
    """
    # Tìm customer liên kết với user này
    stmt_customer = select(Customer).where(Customer.user_id == current_user.id)
    result_customer = await db.execute(stmt_customer)
    customer = result_customer.scalars().first()
    
    if not customer:
        return []
        
    stmt = select(MeterReadingModel).where(MeterReadingModel.customer_id == customer.id)
    result = await db.execute(stmt)
    return result.scalars().all()

