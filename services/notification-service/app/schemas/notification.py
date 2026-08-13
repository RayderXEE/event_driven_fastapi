from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    USER_CREATED = "user.created"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class NotificationResponse(BaseModel):
    id: int
    event_type: str
    status: NotificationStatus
    created_at: datetime
