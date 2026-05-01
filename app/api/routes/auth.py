from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api import deps
from app.services.auth_service import AuthService
from app.schemas.token import Token, TokenRefresh
from app.utils.logger import logger

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = AuthService.authenticate(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    logger.info(f"User logged in: {form_data.username}")
    return AuthService.create_session(db, user.id)

@router.post("/refresh", response_model=Token)
def refresh_token(
    db: Session = Depends(deps.get_db),
    body: TokenRefresh = None
):
    """
    Refresh access token using a refresh token.
    """
    if not body:
         raise HTTPException(status_code=400, detail="Refresh token required")
         
    new_tokens = AuthService.refresh_access_token(db, body.refresh_token)
    if not new_tokens:
        logger.warning("Invalid or expired refresh token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    # Ở đây chúng ta chỉ trả về access token mới, hoặc có thể rotate refresh token nếu muốn
    # Để đơn giản, ta trả về cả 2 (giữ nguyên refresh token cũ)
    return {
        **new_tokens,
        "refresh_token": body.refresh_token
    }

@router.post("/logout")
def logout(
    db: Session = Depends(deps.get_db),
    body: TokenRefresh = None
):
    """
    Revoke a refresh token.
    """
    if not body:
         raise HTTPException(status_code=400, detail="Refresh token required")
         
    AuthService.revoke_refresh_token(db, body.refresh_token)
    logger.info("User logged out and refresh token revoked")
    return {"message": "Successfully logged out"}
