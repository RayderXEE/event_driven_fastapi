import json
import logging
from aiokafka import AIOKafkaConsumer
from app.config import get_settings
from shared.events import (
    parse_event,
    PaymentCompletedEvent,
    PaymentFailedEvent,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)
settings = get_settings()


def _build_consumer(topics: list[str]) -> AIOKafkaConsumer:
    """Build AIOKafkaConsumer with security config for Aiven/Confluent/Local."""
    kwargs = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group_id": settings.KAFKA_GROUP_ID,
        "value_deserializer": lambda m: json.loads(m.decode("utf-8")),
        "auto_offset_reset": "earliest",
        "enable_auto_commit": True,
        "auto_commit_interval_ms": 5000,
    }

    if settings.KAFKA_SECURITY_PROTOCOL != "PLAINTEXT":
        kwargs.update({
            "security_protocol": settings.KAFKA_SECURITY_PROTOCOL,
            "sasl_mechanism": settings.KAFKA_SASL_MECHANISM,
            "sasl_plain_username": settings.KAFKA_API_KEY,
            "sasl_plain_password": settings.KAFKA_API_SECRET,
        })

    return AIOKafkaConsumer(*topics, **kwargs)


async def kafka_consumer():
    """Background task: listens to payments topic and updates order status"""
    consumer = _build_consumer([settings.KAFKA_TOPIC_PAYMENTS])
    await consumer.start()
    logger.info("Kafka consumer started on topic: %s (protocol=%s)",
                settings.KAFKA_TOPIC_PAYMENTS, settings.KAFKA_SECURITY_PROTOCOL)

    try:
        async for message in consumer:
            raw = message.value
            try:
                event = parse_event(raw)
            except (ValueError, ValidationError) as exc:
                logger.error("Failed to parse event: %s | raw=%s", exc, raw)
                continue

            logger.info("Received event: %s from %s", event.event_type, event.source_service)

            if isinstance(event, PaymentCompletedEvent):
                await handle_payment_completed(event.data)
            elif isinstance(event, PaymentFailedEvent):
                await handle_payment_failed(event.data)

    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def handle_payment_completed(data):
    """Updates order status to PAID"""
    from sqlalchemy import select
    from app.db.session import async_session_factory
    from app.models.order import Order, OrderStatus

    order_id = data.order_id
    async with async_session_factory() as session:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if order:
            order.status = OrderStatus.PAID
            await session.commit()
            logger.info("Order %s marked as PAID (payment=%s, amount=%s %s)",
                        order_id, data.payment_id, data.amount, data.currency)
        else:
            logger.warning("Order %s not found", order_id)


async def handle_payment_failed(data):
    logger.warning("Payment failed for order %s (payment=%s, reason=%s)",
                   data.order_id, data.payment_id, data.reason)
