import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.config import get_settings
from shared.events import (
    parse_event,
    UserCreatedEvent,
    OrderCreatedEvent,
    OrderUpdatedEvent,
    WorkflowCreatedEvent,
    SubmissionCreatedEvent,
    StepCompletedEvent,
    StepRejectedEvent,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)
settings = get_settings()

_kafka_producer: AIOKafkaProducer | None = None


def _build_consumer(topics: list[str]) -> AIOKafkaConsumer:
    """Build AIOKafkaConsumer with security config for Aiven/Confluent/Local."""
    kwargs = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group_id": settings.KAFKA_GROUP_ID,
        "value_deserializer": lambda m: json.loads(m.decode("utf-8")),
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
    }

    if settings.KAFKA_SECURITY_PROTOCOL != "PLAINTEXT":
        kwargs.update({
            "security_protocol": settings.KAFKA_SECURITY_PROTOCOL,
            "sasl_mechanism": settings.KAFKA_SASL_MECHANISM,
            "sasl_plain_username": settings.KAFKA_API_KEY,
            "sasl_plain_password": settings.KAFKA_API_SECRET,
        })

    return AIOKafkaConsumer(*topics, **kwargs)


def _build_producer() -> AIOKafkaProducer:
    """Build AIOKafkaProducer with security config for Aiven/Confluent/Local."""
    kwargs = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "value_serializer": lambda v: json.dumps(v, default=str).encode("utf-8"),
        "acks": "all",
    }

    if settings.KAFKA_SECURITY_PROTOCOL != "PLAINTEXT":
        kwargs.update({
            "security_protocol": settings.KAFKA_SECURITY_PROTOCOL,
            "sasl_mechanism": settings.KAFKA_SASL_MECHANISM,
            "sasl_plain_username": settings.KAFKA_API_KEY,
            "sasl_plain_password": settings.KAFKA_API_SECRET,
        })

    return AIOKafkaProducer(**kwargs)


async def get_kafka_producer() -> AIOKafkaProducer:
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = _build_producer()
        await _kafka_producer.start()
    return _kafka_producer


async def kafka_consumer():
    """Listens to orders, users and workflows topics for notification events"""
    topics = [
        settings.KAFKA_TOPIC_ORDERS,
        settings.KAFKA_TOPIC_USERS,
        settings.KAFKA_TOPIC_WORKFLOWS,
    ]

    consumer = _build_consumer(topics)
    await consumer.start()
    logger.info("Notification consumer started on topics: %s (protocol=%s)",
                topics, settings.KAFKA_SECURITY_PROTOCOL)

    try:
        async for message in consumer:
            raw = message.value
            try:
                event = parse_event(raw)
            except (ValueError, ValidationError) as exc:
                logger.error("Failed to parse event: %s | raw=%s", exc, raw)
                continue

            logger.info("Received event: %s from %s", event.event_type, event.source_service)

            if isinstance(event, OrderCreatedEvent):
                await handle_order_created(event.data)
            elif isinstance(event, OrderUpdatedEvent):
                await handle_order_updated(event.data)
            elif isinstance(event, UserCreatedEvent):
                await handle_user_created(event.data)
            elif isinstance(event, WorkflowCreatedEvent):
                await handle_workflow_created(event.data)
            elif isinstance(event, SubmissionCreatedEvent):
                await handle_submission_created(event.data)
            elif isinstance(event, StepCompletedEvent):
                await handle_step_completed(event.data)
            elif isinstance(event, StepRejectedEvent):
                await handle_step_rejected(event.data)

    finally:
        await consumer.stop()
        logger.info("Notification consumer stopped")


async def handle_order_created(data):
    logger.info(
        "[EMAIL] To user %s: Your order #%s for $%s %s has been created!",
        data.user_id, data.order_id, data.amount, data.currency,
    )


async def handle_order_updated(data):
    logger.info("[EMAIL] Order #%s status updated to %s", data.order_id, data.status)


async def handle_user_created(data):
    logger.info("[EMAIL] To user %s (%s <%s>): Welcome!",
                data.user_id, data.name, data.email)


async def handle_workflow_created(data):
    logger.info("[EMAIL] Workflow #%s '%s' has been created", data.workflow_id, data.name)


async def handle_submission_created(data):
    logger.info(
        "[EMAIL] To user %s: Submission #%s for workflow #%s has been created",
        data.user_id, data.submission_id, data.workflow_id,
    )


async def handle_step_completed(data):
    logger.info(
        "[EMAIL] Step #%s completed for submission #%s by user #%s",
        data.step_id, data.submission_id, data.user_id,
    )


async def handle_step_rejected(data):
    logger.info(
        "[EMAIL] Step #%s rejected for submission #%s by user #%s: %s",
        data.step_id, data.submission_id, data.user_id, data.comment,
    )


async def close_kafka():
    global _kafka_producer
    if _kafka_producer:
        await _kafka_producer.stop()
        _kafka_producer = None
