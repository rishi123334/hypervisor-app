import os
import bcrypt
from sqlalchemy.orm import Session
from app.db.db_schema import User
from app.schemas.user import UserCreate
from fastapi import HTTPException, Header
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "my_secret_key")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def hash_password(password: str):
    """
    Hash a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    """
    Verify if a plain password matches the hashed password.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """
    To verify the given token is valid or not
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


def create_user(db: Session, user: UserCreate):
    """
    Create a new user with the hashed password and associate them with the organization.
    """
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")

    # Hash the password and store the user
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, organization_id=None)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user by checking if the username exists and the password matches.
    """
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Generate JWT token
    access_token = create_access_token(data={"sub": db_user.username})
    return {"id": db_user.id, "username": db_user.username, "access_token": access_token, "token_type": "bearer"}


def validate_user_access(token: str, db: Session):
    """
    Validate whether the given token corresponds to a user and return the user if exists
    """
    payload = verify_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user

def get_token(authorization: str = Header(...)):
    """
    Fetch the required token from the headers
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Token must be a Bearer token")
    token = authorization[len("Bearer "):]  # Extract the token from the "Bearer " prefix
    return token