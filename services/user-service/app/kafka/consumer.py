import json
import logging
from aiokafka import AIOKafkaConsumer
from app.config import get_settings
from shared.events import parse_event, OrderCreatedEvent
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
    """Listens to orders topic for order events"""
    consumer = _build_consumer([settings.KAFKA_TOPIC_ORDERS])
    await consumer.start()
    logger.info("Kafka consumer started on topic: %s (protocol=%s)",
                settings.KAFKA_TOPIC_ORDERS, settings.KAFKA_SECURITY_PROTOCOL)

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

    finally:
        await consumer.stop()
        logger.info("Kafka consumer stopped")


async def handle_order_created(data):
    logger.info("Order created for user %s (order #%s, amount=%s %s)",
                data.user_id, data.order_id, data.amount, data.currency)
