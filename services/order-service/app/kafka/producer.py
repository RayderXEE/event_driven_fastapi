import json
import logging
from aiokafka import AIOKafkaProducer
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_kafka_producer: AIOKafkaProducer | None = None


def _build_producer() -> AIOKafkaProducer:
    """Build AIOKafkaProducer with security config for Aiven/Confluent/Local."""
    kwargs = {
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "value_serializer": lambda v: json.dumps(v, default=str).encode("utf-8"),
        "acks": "all",
    }

    # Add SASL_SSL config for cloud Kafka (Aiven, Confluent, etc.)
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
        logger.info("Kafka producer started (protocol=%s)", settings.KAFKA_SECURITY_PROTOCOL)
    return _kafka_producer


async def send_event(topic: str, event: dict, key: str | None = None):
    producer = await get_kafka_producer()
    future = await producer.send_and_wait(
        topic=topic,
        value=event,
        key=key.encode() if key else None,
    )
    logger.info(
        "Event sent: topic=%s, partition=%s, offset=%s",
        future.topic, future.partition, future.offset,
    )
    return future


async def close_kafka_producer():
    global _kafka_producer
    if _kafka_producer:
        await _kafka_producer.stop()
        _kafka_producer = None
        logger.info("Kafka producer stopped")
