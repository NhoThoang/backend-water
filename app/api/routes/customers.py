from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.customer import Customer as CustomerModel
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.utils.logger import logger

router = APIRouter()

@router.get("/", response_model=List[Customer])
def read_customers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user)
):
    """
    Retrieve customers. Accessible by Admin and Worker.
    """
    customers = db.query(CustomerModel).offset(skip).limit(limit).all()
    return customers

@router.post("/", response_model=Customer)
def create_customer(
    *,
    db: Session = Depends(deps.get_db),
    customer_in: CustomerCreate,
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Create new customer. Admin only.
    """
    customer = CustomerModel(**customer_in.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    logger.info(f"Admin {current_user.username} created customer: {customer.name}")
    return customer

@router.get("/{id}", response_model=Customer)
def read_customer(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Get customer by ID.
    """
    customer = db.query(CustomerModel).filter(CustomerModel.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.patch("/{id}", response_model=Customer)
def update_customer(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    customer_in: CustomerUpdate,
    current_user = Depends(deps.get_current_active_admin)
):
    """
    Update a customer. Admin only.
    """
    customer = db.query(CustomerModel).filter(CustomerModel.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
        
    db.add(customer)
    db.commit()
    db.refresh(customer)
    logger.info(f"Admin {current_user.username} updated customer ID: {id}")
    return customer
