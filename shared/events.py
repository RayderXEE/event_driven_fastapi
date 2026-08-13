"""
Shared Kafka event schemas.

All microservices import event types from this module to ensure
consistent, validated event contracts across the system.

Usage (producer):
    event = UserCreatedEvent.from_user(user_id=1, email="a@b.com", name="Alice")
    await send_event(topic="users", event=event.model_dump(), key="1")

Usage (consumer):
    raw = json.loads(message.value.decode("utf-8"))
    event = UserCreatedEvent.model_validate(raw)
    print(event.data.user_id, event.data.email)
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Base event envelope — every Kafka message wraps into this structure
# ---------------------------------------------------------------------------

class KafkaEvent(BaseModel):
    """Base structure for all Kafka events."""
    schema_version: str = "1.0.0"
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str
    data: Any


# ---------------------------------------------------------------------------
# User events
# ---------------------------------------------------------------------------

class UserCreatedData(BaseModel):
    """Payload for user.created events."""
    user_id: int
    email: str
    name: str


class UserCreatedEvent(KafkaEvent):
    event_type: str = "user.created"
    source_service: str = "user-service"
    data: UserCreatedData

    @classmethod
    def from_user(cls, user_id: int, email: str, name: str) -> "UserCreatedEvent":
        return cls(data=UserCreatedData(user_id=user_id, email=email, name=name))


# ---------------------------------------------------------------------------
# Order events
# ---------------------------------------------------------------------------

class OrderStatus(str, Enum):
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"


class OrderCreatedData(BaseModel):
    """Payload for order.created events."""
    order_id: int
    user_id: int
    amount: float
    currency: str


class OrderCreatedEvent(KafkaEvent):
    event_type: str = "order.created"
    source_service: str = "order-service"
    data: OrderCreatedData

    @classmethod
    def from_order(
        cls, order_id: int, user_id: int, amount: float, currency: str
    ) -> "OrderCreatedEvent":
        return cls(data=OrderCreatedData(order_id=order_id, user_id=user_id, amount=amount, currency=currency))


class OrderUpdatedData(BaseModel):
    """Payload for order.updated events."""
    order_id: int
    user_id: int
    status: OrderStatus
    amount: float
    currency: str


class OrderUpdatedEvent(KafkaEvent):
    event_type: str = "order.updated"
    source_service: str = "order-service"
    data: OrderUpdatedData


class OrderCancelledData(BaseModel):
    """Payload for order.cancelled events."""
    order_id: int
    user_id: int


class OrderCancelledEvent(KafkaEvent):
    event_type: str = "order.cancelled"
    source_service: str = "order-service"
    data: OrderCancelledData


# ---------------------------------------------------------------------------
# Payment events (produced by external payment system)
# ---------------------------------------------------------------------------

class PaymentCompletedData(BaseModel):
    """Payload for payment.completed events."""
    order_id: int
    payment_id: str
    amount: float
    currency: str


class PaymentCompletedEvent(KafkaEvent):
    event_type: str = "payment.completed"
    source_service: str = "payment-service"
    data: PaymentCompletedData


class PaymentFailedData(BaseModel):
    """Payload for payment.failed events."""
    order_id: int
    payment_id: str
    reason: str


class PaymentFailedEvent(KafkaEvent):
    event_type: str = "payment.failed"
    source_service: str = "payment-service"
    data: PaymentFailedData


# ---------------------------------------------------------------------------
# Workflow events
# ---------------------------------------------------------------------------

class WorkflowCreatedData(BaseModel):
    """Payload for workflow.created events."""
    workflow_id: int
    name: str


class WorkflowCreatedEvent(KafkaEvent):
    event_type: str = "workflow.created"
    source_service: str = "workflow-service"
    data: WorkflowCreatedData

    @classmethod
    def from_workflow(cls, workflow_id: int, name: str) -> "WorkflowCreatedEvent":
        return cls(data=WorkflowCreatedData(workflow_id=workflow_id, name=name))


class SubmissionCreatedData(BaseModel):
    """Payload for submission.created events."""
    submission_id: int
    workflow_id: int
    user_id: int


class SubmissionCreatedEvent(KafkaEvent):
    event_type: str = "submission.created"
    source_service: str = "workflow-service"
    data: SubmissionCreatedData

    @classmethod
    def from_submission(cls, submission_id: int, workflow_id: int, user_id: int) -> "SubmissionCreatedEvent":
        return cls(data=SubmissionCreatedData(submission_id=submission_id, workflow_id=workflow_id, user_id=user_id))


class StepCompletedData(BaseModel):
    """Payload for step.completed events."""
    submission_id: int
    step_id: int
    user_id: int


class StepCompletedEvent(KafkaEvent):
    event_type: str = "step.completed"
    source_service: str = "workflow-service"
    data: StepCompletedData

    @classmethod
    def from_step_completed(cls, submission_id: int, step_id: int, user_id: int) -> "StepCompletedEvent":
        return cls(data=StepCompletedData(submission_id=submission_id, step_id=step_id, user_id=user_id))


class StepRejectedData(BaseModel):
    """Payload for step.rejected events."""
    submission_id: int
    step_id: int
    user_id: int
    comment: str


class StepRejectedEvent(KafkaEvent):
    event_type: str = "step.rejected"
    source_service: str = "workflow-service"
    data: StepRejectedData

    @classmethod
    def from_step_rejected(cls, submission_id: int, step_id: int, user_id: int, comment: str) -> "StepRejectedEvent":
        return cls(data=StepRejectedData(submission_id=submission_id, step_id=step_id, user_id=user_id, comment=comment))


# ---------------------------------------------------------------------------
# Registry — map event_type string -> concrete event class
# ---------------------------------------------------------------------------

EVENT_TYPE_MAP: dict[str, type[KafkaEvent]] = {
    "user.created": UserCreatedEvent,
    "order.created": OrderCreatedEvent,
    "order.updated": OrderUpdatedEvent,
    "order.cancelled": OrderCancelledEvent,
    "payment.completed": PaymentCompletedEvent,
    "payment.failed": PaymentFailedEvent,
    "workflow.created": WorkflowCreatedEvent,
    "submission.created": SubmissionCreatedEvent,
    "step.completed": StepCompletedEvent,
    "step.rejected": StepRejectedEvent,
}


def parse_event(raw: dict) -> KafkaEvent:
    """
    Deserialize a raw Kafka message into the correct typed event.

    Raises ValueError if event_type is unknown.
    Raises ValidationError if payload does not match the schema.
    """
    event_type = raw.get("event_type")
    cls = EVENT_TYPE_MAP.get(event_type)
    if cls is None:
        raise ValueError(f"Unknown event_type: {event_type}")
    return cls.model_validate(raw)
