from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Order Service"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://order_user:order_pass@postgres_orders:5432/orders"

    # Kafka (Aiven / Confluent / Local)
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_TOPIC_ORDERS: str = "orders"
    KAFKA_TOPIC_PAYMENTS: str = "payments"
    KAFKA_GROUP_ID: str = "order-service"

    # Kafka Security (for Aiven/Confluent Cloud)
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"  # PLAINTEXT | SASL_SSL
    KAFKA_SASL_MECHANISM: str = "PLAIN"
    KAFKA_API_KEY: str = ""
    KAFKA_API_SECRET: str = ""

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # OpenTelemetry
    OTEL_ENABLED: bool = True
    OTEL_ENDPOINT: str = "jaeger:4317"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
