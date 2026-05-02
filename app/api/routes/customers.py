from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.customer import Customer as CustomerModel
from app.models.user import User, UserRole
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.core.security import get_password_hash
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[Customer])
async def read_customers(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user)
):
    """
    Retrieve customers. Accessible by Admin and Worker.
    """
    stmt = select(CustomerModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    customers = result.scalars().all()
    return customers

@router.post("/", response_model=Customer)
async def create_customer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    customer_in: CustomerCreate,
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Create new customer and its associated user account. Admin only.
    """
    # 1. Tạo tài khoản User trước
    username = customer_in.customer_id or customer_in.phone_number or f"user_{customer_in.name.replace(' ', '').lower()}"
    password = customer_in.password or "zxcvbnm12345"
    
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        role=UserRole.USER,
        customer_id=customer_in.customer_id,
        phone_number=customer_in.phone_number,
        address=customer_in.address,
        password_set=1 if customer_in.password else 0
    )
    db.add(user)
    await db.flush() # Để lấy user.id
    
    # 2. Tạo Customer
    customer_data = customer_in.dict(exclude={"password"})
    customer = CustomerModel(**customer_data, user_id=user.id)
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    
    logger.info(f"Admin {current_user.username} created customer: {customer.name} with user_id: {user.id}")
    return customer

@router.get("/{id}", response_model=Customer)
async def read_customer(
    id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Get customer by ID.
    """
    stmt = select(CustomerModel).where(CustomerModel.id == id)
    result = await db.execute(stmt)
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.patch("/{id}", response_model=Customer)
async def update_customer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    customer_in: CustomerUpdate,
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Update a customer. Admin only.
    """
    stmt = select(CustomerModel).where(CustomerModel.id == id)
    result = await db.execute(stmt)
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 1. Nếu có password, cập nhật cho User liên kết
    if customer_in.password:
        stmt_user = select(User).where(User.id == customer.user_id)
        result_user = await db.execute(stmt_user)
        user = result_user.scalars().first()
        if user:
            user.password_hash = get_password_hash(customer_in.password)
            user.password_set = 1
            db.add(user)

    # 2. Cập nhật thông tin Customer
    update_data = customer_in.dict(exclude_unset=True, exclude={"password"})
    for field, value in update_data.items():
        setattr(customer, field, value)
        
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    logger.info(f"Admin {current_user.username} updated customer ID: {id}")
    return customer

@router.delete("/{id}")
async def delete_customer(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Delete a customer and their associated user account. Admin only.
    """
    stmt = select(CustomerModel).where(CustomerModel.id == id)
    result = await db.execute(stmt)
    customer = result.scalars().first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Delete associated user if exists
    if customer.user_id:
        stmt_user = select(User).where(User.id == customer.user_id)
        result_user = await db.execute(stmt_user)
        user = result_user.scalars().first()
        if user:
            await db.delete(user)
            
    await db.delete(customer)
    await db.commit()
    
    logger.info(f"Admin {current_user.username} deleted customer ID: {id}")
    return {"message": "Customer deleted successfully"}
