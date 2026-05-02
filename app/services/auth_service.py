from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.user import User
from app.models.token import RefreshToken
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta, timezone
from app.core.config import settings

class AuthService:
    @staticmethod
    async def authenticate(db: AsyncSession, username: str, password: str):
        # Cho phép đăng nhập bằng username HOẶC mã khách hàng
        stmt = select(User).where(
            or_(User.username == username, User.customer_id == username)
        )
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return None
            
        # 1. Nếu đã đổi mật khẩu (password_set == 1), CHỈ kiểm tra password trong DB
        if user.password_set == 1:
            if verify_password(password, user.password_hash):
                return user
            return None # Sai pass là tạch luôn, không check fallback
            
        # 2. Nếu chưa đổi mật khẩu (password_set == 0), kiểm tra theo thứ tự ưu tiên
        if user.role == "user":
            # Ưu tiên 1: Kiểm tra Số điện thoại (nếu có)
            if user.phone_number:
                if password == user.phone_number:
                    return user
                return None # Có SĐT mà nhập sai thì không check cái mặc định nữa
            
            # Ưu tiên 2: Mật khẩu mặc định (chỉ dùng khi không có SĐT)
            if password == "zxcvbnm12345":
                return user
                
        # 3. Fallback cuối cùng cho Admin/Worker (nếu họ chưa đổi pass - ít xảy ra)
        if verify_password(password, user.password_hash):
            return user
            
        return None

    @staticmethod
    async def create_session(db: AsyncSession, user_id: int):
        access_token = create_access_token(subject=user_id)
        refresh_token_str = create_refresh_token(subject=user_id)
        
        # Lưu refresh token vào DB
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        db_refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(db_refresh_token)
        await db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer"
        }

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token_str: str):
        # 1. Decode và verify token
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            return None
        
        # 2. Kiểm tra trong DB
        stmt = select(RefreshToken).where(
            RefreshToken.token == refresh_token_str,
            RefreshToken.is_revoked == False
        )
        result = await db.execute(stmt)
        db_token = result.scalars().first()
        
        if not db_token or db_token.expires_at < datetime.now(timezone.utc):
            return None
            
        # 3. Cấp access token mới
        new_access_token = create_access_token(subject=db_token.user_id)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def revoke_refresh_token(db: AsyncSession, refresh_token_str: str):
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        result = await db.execute(stmt)
        db_token = result.scalars().first()
        
        if db_token:
            db_token.is_revoked = True
            await db.commit()
            return True
        return False
