from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from apps.api.app.core.database import get_db
from apps.api.app.core.security import verify_password, get_password_hash, create_access_token
from apps.api.app.models.entities import User, Organization
from apps.api.app.schemas.dto import LoginRequest, RegisterRequest, SocialLoginRequest, TokenResponse, UserResponse
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

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    org = db.query(Organization).first()
    if not org:
        org = Organization(name="Public Works Department", slug="pwd-state", status="ACTIVE")
        db.add(org)
        db.commit()
        db.refresh(org)

    role = req.role if req.role in ["SUBMITTER", "REVIEWER", "AUDITOR", "ADMIN"] else "SUBMITTER"
    new_user = User(
        organization_id=org.id,
        email=req.email,
        display_name=req.display_name,
        password_hash=get_password_hash(req.password),
        role=role,
        status="ACTIVE"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(subject=new_user.id, roles=[new_user.role])
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        role=new_user.role,
        display_name=new_user.display_name
    )

@router.post("/social-login", response_model=TokenResponse)
def social_login(req: SocialLoginRequest, db: Session = Depends(get_db)):
    # Federated OAuth resolver (Google & Facebook)
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="Public Works Department", slug="pwd-state", status="ACTIVE")
            db.add(org)
            db.commit()
            db.refresh(org)
        role = req.role if req.role in ["SUBMITTER", "REVIEWER", "AUDITOR", "ADMIN"] else "SUBMITTER"
        user = User(
            organization_id=org.id,
            email=req.email,
            display_name=req.display_name or f"{req.provider.capitalize()} User",
            password_hash=get_password_hash(f"oauth_{req.provider}_{req.email}"),
            role=role,
            status="ACTIVE"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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


