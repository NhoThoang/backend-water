import io
import pandas as pd
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.utils.logger import logger

router = APIRouter()

@router.post("/upload", status_code=201)
async def upload_users_excel(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    Upload Excel file to create multiple customer accounts.
    Excel should have columns: 'mã khách hàng', 'số điện thoại', 'địa chỉ'
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")

    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    
    # Normalize column names
    df.columns = [str(c).strip().lower() for c in df.columns]
    
    required_cols = ['mã khách hàng']
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

    created_count = 0
    skipped_count = 0
    
    for _, row in df.iterrows():
        # 1. Mã khách hàng (Bắt buộc)
        c_id = str(row.get('mã khách hàng', '')).strip()
        if not c_id or c_id == 'nan':
            continue
            
        # Kiểm tra trùng mã khách hàng (phải khác nhau)
        existing_user = db.query(User).filter(User.customer_id == c_id).first()
        if existing_user:
            skipped_count += 1
            continue
            
        # 2. Tên đăng nhập (Có thể có hoặc không)
        # Vì username không còn là duy nhất trong DB, ta lấy theo Excel hoặc mặc định là c_id
        u_name = str(row.get('tên đăng nhập', '')).strip()
        if not u_name or u_name == 'nan':
            u_name = c_id
            
        # 3. Các thông tin khác (Có hoặc không)
        phone = str(row.get('số điện thoại', '')).strip()
        if not phone or phone == 'nan': phone = None
            
        address = str(row.get('địa chỉ', '')).strip()
        if not address or address == 'nan': address = None
            
        role = str(row.get('vai trò', 'user')).strip().lower()
        if role not in [UserRole.ADMIN, UserRole.WORKER, UserRole.USER]:
            role = UserRole.USER
            
        password_raw = str(row.get('mật khẩu', '')).strip()
        if not password_raw or password_raw == 'nan':
            password = phone if phone else "zxcvbnm12345"
        else:
            password = password_raw
        
        new_user = User(
            username=u_name,
            customer_id=c_id,
            password_hash=get_password_hash(password),
            phone_number=phone,
            address=address,
            role=role
        )
        
        db.add(new_user)
        created_count += 1
        
    db.commit()
    logger.info(f"Admin {current_admin.username} uploaded Excel. Created: {created_count}, Skipped: {skipped_count}")
    
    return {
        "message": "Processing complete",
        "created": created_count,
        "skipped": skipped_count
    }

@router.get("/export")
def export_users_excel(
    db: Session = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    Export all customer accounts to Excel.
    """
    users = db.query(User).filter(User.role == UserRole.USER).all()
    
    data = []
    for user in users:
        data.append({
            "Mã khách hàng": user.customer_id,
            "Tên đăng nhập": user.username,
            "Vai trò": user.role,
            "Số điện thoại": user.phone_number,
            "Địa chỉ": user.address,
            "Ngày tạo": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else ""
        })
        
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Customers')
    
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="customers_export.xlsx"'
    }
    
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
