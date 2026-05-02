from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core import security
from app.models.user import User
from app.schemas.token import TokenPayload
from app.db.session import AsyncSessionLocal

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False # Don't raise error if header is missing
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    request: Request = None,
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    # 1. Lấy token từ header hoặc cookie
    actual_token = token or request.cookies.get("access_token")
    
    if not actual_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
        
    try:
        payload = jwt.decode(
            actual_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(User).filter(User.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_active_staff(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in ["admin", "worker"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_user
