from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.services.reading_service import ReadingService
from app.schemas.reading import MeterReading, MeterReadingCreate, ReadingResponse
from app.models.reading import MeterReading as MeterReadingModel
from app.utils.logger import logger

router = APIRouter()

@router.post("/", response_model=ReadingResponse)
def create_reading(
    *,
    db: Session = Depends(deps.get_db),
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
        reading, bill = ReadingService.add_reading(
            db, 
            customer_id=reading_in.customer_id,
            reading_value=reading_in.reading,
            month=reading_in.month,
            worker_id=current_user.id
        )
        
        if reading.is_anomaly:
            logger.warning(f"Anomaly detected for customer {reading.customer_id} in month {reading.month}")
            
        return {"reading": reading, "bill": bill}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/anomalies", response_model=List[MeterReading])
def get_anomalies(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Lấy danh sách các chỉ số nước bất thường (Admin only).
    """
    anomalies = db.query(MeterReadingModel).filter(MeterReadingModel.is_anomaly == True).all()
    return anomalies

@router.get("/customer/{customer_id}", response_model=List[MeterReading])
def get_customer_readings(
    customer_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Xem lịch sử ghi chỉ số của một hộ dân.
    """
    readings = db.query(MeterReadingModel).filter(MeterReadingModel.customer_id == customer_id).all()
    return readings
