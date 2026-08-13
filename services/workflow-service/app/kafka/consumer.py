import json
import logging
from aiokafka import AIOKafkaConsumer
from app.config import get_settings
from shared.events import (
    parse_event,
    WorkflowCreatedEvent,
    SubmissionCreatedEvent,
    StepCompletedEvent,
    StepRejectedEvent,
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
    """Consume workflow events from Kafka with typed event parsing"""
    consumer = _build_consumer([settings.KAFKA_TOPIC_WORKFLOWS])
    await consumer.start()
    logger.info("Workflow consumer started on topic: %s (protocol=%s)",
                settings.KAFKA_TOPIC_WORKFLOWS, settings.KAFKA_SECURITY_PROTOCOL)

    try:
        async for message in consumer:
            raw = message.value
            try:
                event = parse_event(raw)
            except (ValueError, ValidationError) as exc:
                logger.error("Failed to parse event: %s | raw=%s", exc, raw)
                continue

            logger.info("Received event: %s from %s", event.event_type, event.source_service)

            if isinstance(event, WorkflowCreatedEvent):
                await handle_workflow_created(event.data)
            elif isinstance(event, SubmissionCreatedEvent):
                await handle_submission_created(event.data)
            elif isinstance(event, StepCompletedEvent):
                await handle_step_completed(event.data)
            elif isinstance(event, StepRejectedEvent):
                await handle_step_rejected(event.data)

    finally:
        await consumer.stop()
        logger.info("Workflow consumer stopped")


async def handle_workflow_created(data):
    logger.info("[WORKFLOW] Workflow #%s '%s' created", data.workflow_id, data.name)


async def handle_submission_created(data):
    logger.info(
        "[SUBMISSION] Submission #%s created for workflow #%s by user #%s",
        data.submission_id, data.workflow_id, data.user_id,
    )


async def handle_step_completed(data):
    logger.info(
        "[STEP] Step #%s completed for submission #%s by user #%s",
        data.step_id, data.submission_id, data.user_id,
    )


async def handle_step_rejected(data):
    logger.info(
        "[STEP] Step #%s rejected for submission #%s by user #%s: %s",
        data.step_id, data.submission_id, data.user_id, data.comment,
    )


async def close_kafka():
    pass
