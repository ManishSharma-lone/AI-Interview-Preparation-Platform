from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.models.database_models import User, Progress, Leaderboard
from backend.app.schemas.api_schemas import UserRegister, UserLogin, Token
from backend.app.auth.auth_service import get_password_hash, verify_password, create_access_token
from backend.app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash the password and create user
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize Progress and Leaderboard records
    user_progress = Progress(
        user_id=new_user.id,
        total_interviews=0,
        average_score=0.0,
        best_score=0.0,
        weak_topics="[]",
        strong_topics="[]",
        streak_count=0
    )
    user_leaderboard = Leaderboard(
        user_id=new_user.id,
        username=new_user.username,
        score=0.0
    )
    db.add(user_progress)
    db.add(user_leaderboard)
    db.commit()

    # Generate token
    access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": new_user.username,
        "email": new_user.email
    }

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check remember me for different token lifespan
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    if login_data.remember_me:
        expire_minutes = 1440 * 7  # 7 days

    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=expire_minutes)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email
    }

# FastAPI spec standard form-login support (for automatic OpenAPI doc authentication)
@router.post("/login-form", response_model=Token, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form_data.username) | (User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "email": user.email
    }
