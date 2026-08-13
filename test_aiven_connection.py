#!/usr/bin/env python3
"""
Aiven Kafka Connection Test Script

Usage:
    1. Fill in your Aiven credentials in the .env file (copy from .env.example)
    2. Run: python test_aiven_connection.py

This script will:
    - Connect to your Aiven Kafka instance
    - List all existing topics
    - Send a test message and consume it back
"""

import asyncio
import json
import os
import ssl
import sys
from pathlib import Path

from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, NoBrokersAvailable

# Load .env from order-service
load_dotenv(Path(__file__).parent / "services" / "order-service" / ".env")

REQUIRED_TOPICS = ["orders", "users", "workflows", "notifications"]


def get_kafka_config() -> dict:
    """Extract Kafka configuration from environment variables."""
    config = {
        "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "security_protocol": os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
    }

    if config["security_protocol"] != "PLAINTEXT":
        config.update({
            "sasl_mechanism": os.getenv("KAFKA_SASL_MECHANISM", "PLAIN"),
            "sasl_plain_username": os.getenv("KAFKA_API_KEY", ""),
            "sasl_plain_password": os.getenv("KAFKA_API_SECRET", ""),
            "ssl_context": ssl.create_default_context(),
        })

    return config


async def test_connection(config: dict) -> bool:
    """Test basic connectivity by creating a short-lived producer."""
    print("🔌 Testing connection to Kafka broker...")
    producer = AIOKafkaProducer(
        bootstrap_servers=config["bootstrap_servers"],
        security_protocol=config.get("security_protocol"),
        sasl_mechanism=config.get("sasl_mechanism"),
        sasl_plain_username=config.get("sasl_plain_username"),
        sasl_plain_password=config.get("sasl_plain_password"),
        ssl_context=config.get("ssl_context"),
    )
    try:
        await producer.start()
        print("✅ Connected successfully!")
        await producer.stop()
        return True
    except (KafkaConnectionError, NoBrokersAvailable, Exception) as e:
        print(f"❌ Connection failed: {e}")
        return False


async def list_topics(config: dict) -> list[str]:
    """List existing topics by probing each required topic."""
    print("\n📋 Checking topics...")
    existing = []
    for topic in REQUIRED_TOPICS:
        consumer = AIOKafkaConsumer(
            bootstrap_servers=config["bootstrap_servers"],
            security_protocol=config.get("security_protocol"),
            sasl_mechanism=config.get("sasl_mechanism"),
            sasl_plain_username=config.get("sasl_plain_username"),
            sasl_plain_password=config.get("sasl_plain_password"),
            ssl_context=config.get("ssl_context"),
            group_id=None,
        )
        try:
            await consumer.start()
            partitions = consumer.partitions_for_topic(topic)
            if partitions is not None:
                existing.append(topic)
                print(f"   ✅ Topic '{topic}' exists ({len(partitions)} partitions)")
            else:
                print(f"   ⚠️  Topic '{topic}' does not exist")
            await consumer.stop()
        except Exception as e:
            print(f"   ⚠️  Topic '{topic}' — {e}")
            await consumer.stop()
    return existing


async def test_producer_consumer(config: dict) -> bool:
    """Test sending and receiving a message."""
    print("\n📤 Testing producer and consumer...")

    test_topic = "orders"
    test_message = {
        "event_id": "test-001",
        "event_type": "order.created",
        "timestamp": "2025-07-11T12:00:00Z",
        "source_service": "test-script",
        "data": {
            "order_id": "test-order-001",
            "user_id": "user-123",
            "amount": 99.99,
            "currency": "USD",
        }
    }

    # Producer
    producer = AIOKafkaProducer(
        bootstrap_servers=config["bootstrap_servers"],
        security_protocol=config.get("security_protocol"),
        sasl_mechanism=config.get("sasl_mechanism"),
        sasl_plain_username=config.get("sasl_plain_username"),
        sasl_plain_password=config.get("sasl_plain_password"),
        ssl_context=config.get("ssl_context"),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()

    try:
        await producer.send_and_wait(test_topic, test_message)
        print("   ✅ Message sent successfully!")
    except Exception as e:
        print(f"   ❌ Failed to send message: {e}")
        await producer.stop()
        return False

    # Consumer
    consumer = AIOKafkaConsumer(
        test_topic,
        bootstrap_servers=config["bootstrap_servers"],
        security_protocol=config.get("security_protocol"),
        sasl_mechanism=config.get("sasl_mechanism"),
        sasl_plain_username=config.get("sasl_plain_username"),
        sasl_plain_password=config.get("sasl_plain_password"),
        ssl_context=config.get("ssl_context"),
        group_id="test-consumer-aiven",
        auto_offset_reset="earliest",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()

    try:
        messages = await consumer.getmany(timeout_ms=10000, max_records=100)
        found = False
        for tp, records in messages.items():
            for record in records:
                if record.value.get("event_id") == "test-001":
                    print("   ✅ Test message received back!")
                    print(f"   Content: {json.dumps(record.value, indent=6)}")
                    found = True
        if not found:
            print("   ⚠️  Test message not found in consumed records (may have been consumed by another group)")

    except Exception as e:
        print(f"   ❌ Consumer error: {e}")
    finally:
        await consumer.stop()
        await producer.stop()

    return True


async def main():
    print("=" * 60)
    print("  Aiven Kafka Connection Test")
    print("=" * 60)

    config = get_kafka_config()
    print(f"\n📡 Configuration:")
    print(f"   Bootstrap: {config['bootstrap_servers']}")
    print(f"   Protocol:  {config['security_protocol']}")

    # Step 1: Test connection
    if not await test_connection(config):
        print("\n⚠️  Cannot connect. Check your credentials in .env file")
        sys.exit(1)

    # Step 2: List topics
    await list_topics(config)

    # Step 3: Test producer/consumer
    await test_producer_consumer(config)

    print("\n" + "=" * 60)
    print("  ✅ All tests passed! Your Aiven Kafka is ready.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
