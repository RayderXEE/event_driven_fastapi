from pydantic import BaseModel, Field
from datetime import datetime
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    user_id: int = Field(..., ge=1, description="User ID")
    amount: float = Field(..., gt=0, description="Order amount")
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$", description="ISO 4217 currency code")

class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    amount: float | None = None
    currency: str | None = None

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    amount: float
    currency: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
