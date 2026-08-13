from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: str = Field(..., description="User email")
    name: str = Field(..., min_length=1, max_length=255)
    balance: float = Field(default=0.0, ge=0)

class UserUpdate(BaseModel):
    name: str | None = None
    balance: float | None = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    balance: float
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
