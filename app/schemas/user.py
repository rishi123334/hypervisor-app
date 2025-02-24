from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    organization_id: Optional[int]


class TokenResponse(BaseModel):
    id: int
    username: str
    access_token: str
    token_type: str