import io
import pandas as pd
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema
from app.core.security import get_password_hash
from app.utils.logger import logger

router = APIRouter()

@router.post("/upload", status_code=201)
async def upload_users_excel(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db),
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
        stmt = select(User).where(User.customer_id == c_id)
        result = await db.execute(stmt)
        existing_user = result.scalars().first()
        
        if existing_user:
            skipped_count += 1
            continue
            
        # 2. Tên đăng nhập (Có thể có hoặc không)
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
        
    await db.commit()
    logger.info(f"Admin {current_admin.username} uploaded Excel. Created: {created_count}, Skipped: {skipped_count}")
    
    return {
        "message": "Processing complete",
        "created": created_count,
        "skipped": skipped_count
    }

@router.get("/export")
async def export_users_excel(
    db: AsyncSession = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    Export all customer accounts to Excel.
    """
    stmt = select(User).where(User.role == UserRole.USER)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
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

@router.get("/", response_model=List[UserSchema])
async def list_users(
    role: str = None,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    List users, optionally filtered by role (Admin only).
    """
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", status_code=201, response_model=UserSchema)
async def create_user_manual(
    user_in: dict,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    Create a user manually (Worker or Admin).
    """
    username = user_in.get("username")
    password = user_in.get("password")
    role = user_in.get("role", UserRole.USER)
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")
    
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")
        
    new_user = User(
        username=username,
        password_hash=get_password_hash(password),
        role=role,
        phone_number=user_in.get("phone_number"),
        address=user_in.get("address"),
        customer_id=user_in.get("customer_id")
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: dict,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    Update a user's information.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update fields
    if "password" in user_in and user_in["password"]:
        user.password_hash = get_password_hash(user_in["password"])
    
    if "role" in user_in:
        user.role = user_in["role"]
        
    if "phone_number" in user_in:
        user.phone_number = user_in["phone_number"]
        
    if "address" in user_in:
        user.address = user_in["address"]
        
    if "is_active" in user_in:
        user.is_active = user_in["is_active"]

    if "username" in user_in:
        # Check if username is already taken by another user
        stmt_check = select(User).where(User.username == user_in["username"], User.id != user_id)
        res_check = await db.execute(stmt_check)
        if res_check.scalars().first():
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = user_in["username"]
        
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: User = Depends(deps.get_current_active_admin)
):
    """
    Delete a user.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
