from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services.auth_service import AuthService
from app.schemas.token import Token, TokenRefresh
from app.schemas.user import UserLogin, User as UserSchema, UserUpdate
from app.core import security
from app.models.user import User
from app.models.customer import Customer
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    login_data: UserLogin,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Login with JSON body and set tokens in HttpOnly cookies.
    """
    user = await AuthService.authenticate(db, login_data.username, login_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    tokens = await AuthService.create_session(db, user.id)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False, # Đặt True nếu dùng HTTPS
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
    )
    
    logger.info(f"User logged in: {login_data.username}")
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
    body: TokenRefresh = None
):
    """
    Refresh access token using a refresh token from cookie or body.
    """
    refresh_token = (body.refresh_token if body else None) or request.cookies.get("refresh_token")
    
    if not refresh_token:
         raise HTTPException(status_code=400, detail="Refresh token required")
         
    new_tokens = await AuthService.refresh_access_token(db, refresh_token)
    if not new_tokens:
        logger.warning("Invalid or expired refresh token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Update access token cookie
    response.set_cookie(
        key="access_token",
        value=new_tokens["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,
    )
    
    return {
        **new_tokens,
        "refresh_token": refresh_token
    }

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
    body: TokenRefresh = None
):
    """
    Revoke a refresh token and clear cookies.
    """
    refresh_token = (body.refresh_token if body else None) or request.cookies.get("refresh_token")
         
    if refresh_token:
        await AuthService.revoke_refresh_token(db, refresh_token)
    
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    logger.info("User logged out and cookies cleared")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get current logged in user information.
    """
    return current_user

@router.patch("/me", response_model=UserSchema)
async def update_user_me(
    user_in: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update current user profile.
    """
    if user_in.password:
        current_user.password_hash = security.get_password_hash(user_in.password)
        current_user.password_set = 1
    if user_in.phone_number is not None:
        current_user.phone_number = user_in.phone_number
    if user_in.address is not None:
        current_user.address = user_in.address
        
    # Nếu là khách hàng, cập nhật thông tin trong bảng Customer
    if current_user.role == "user":
        stmt = select(Customer).where(Customer.user_id == current_user.id)
        result = await db.execute(stmt)
        customer = result.scalars().first()
        if customer:
            if user_in.name: customer.name = user_in.name
            if user_in.email: customer.email = user_in.email
            if user_in.phone_number: customer.phone_number = user_in.phone_number
            if user_in.address: customer.address = user_in.address
            db.add(customer)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

