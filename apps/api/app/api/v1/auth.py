from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from apps.api.app.core.database import get_db
from apps.api.app.core.security import verify_password, create_access_token
from apps.api.app.models.entities import User, Organization
from apps.api.app.schemas.dto import LoginRequest, TokenResponse, UserResponse
from apps.api.app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    token = create_access_token(subject=user.id, roles=[user.role])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
        display_name=user.display_name
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

