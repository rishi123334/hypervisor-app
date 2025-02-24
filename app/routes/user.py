from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.auth import authenticate_user, create_user
from app.db.base import get_db

router = APIRouter()

@router.post("/register/", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    API to create a new user
    """
    return create_user(db=db, user=user)

@router.post("/login/", response_model=TokenResponse)
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    API to authenticate the registered user
    """
    db_user = authenticate_user(db=db, username=user.username, password=user.password)
    return db_user
