from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Notification Service"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Kafka (Aiven / Confluent / Local)
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_TOPIC_ORDERS: str = "orders"
    KAFKA_TOPIC_USERS: str = "users"
    KAFKA_TOPIC_WORKFLOWS: str = "workflows"
    KAFKA_TOPIC_NOTIFICATIONS: str = "notifications"
    KAFKA_GROUP_ID: str = "notification-service"

    # Kafka Security (for Aiven/Confluent Cloud)
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISM: str = "PLAIN"
    KAFKA_API_KEY: str = ""
    KAFKA_API_SECRET: str = ""

    REDIS_URL: str = "redis://redis:6379/2"

    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025

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
