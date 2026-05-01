from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import RefreshToken
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from datetime import datetime, timedelta
from app.core.config import settings

class AuthService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        # Cho phép đăng nhập bằng username HOẶC mã khách hàng
        user = db.query(User).filter(
            (User.username == username) | (User.customer_id == username)
        ).first()
        
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_session(db: Session, user_id: int):
        access_token = create_access_token(subject=user_id)
        refresh_token_str = create_refresh_token(subject=user_id)
        
        # Lưu refresh token vào DB
        expires_at = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        db_refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(db_refresh_token)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "bearer"
        }

    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str):
        # 1. Decode và verify token
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            return None
        
        # 2. Kiểm tra trong DB
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.is_revoked == False
        ).first()
        
        if not db_token or db_token.expires_at < datetime.utcnow():
            return None
            
        # 3. Cấp access token mới
        new_access_token = create_access_token(subject=db_token.user_id)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    @staticmethod
    def revoke_refresh_token(db: Session, refresh_token_str: str):
        db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_str).first()
        if db_token:
            db_token.is_revoked = True
            db.commit()
            return True
        return False
