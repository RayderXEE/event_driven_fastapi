from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class KafkaEvent(BaseModel):
    """Base structure for all Kafka events"""
    schema_version: str = "1.0.0"
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "order-service"

class OrderCreatedEvent(KafkaEvent):
    event_type: str = "order.created"
    data: dict

    @classmethod
    def from_order(cls, order_id: int, user_id: int, amount: float, currency: str):
        return cls(
            data={
                "order_id": order_id,
                "user_id": user_id,
                "amount": amount,
                "currency": currency,
            }
        )

class OrderUpdatedEvent(KafkaEvent):
    event_type: str = "order.updated"
    data: dict

class OrderCancelledEvent(KafkaEvent):
    event_type: str = "order.cancelled"
    data: dict
