from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import get_settings
from app.kafka.consumer import kafka_consumer, close_kafka
from app.api.notifications import router as notifications_router
import asyncio
import sys
import os

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
try:
    from shared.logging_config import setup_logging
except ImportError:
    import logging
    def setup_logging(level="INFO", log_format="json", service_name="service"):
        logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO),
                          format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        return logging.getLogger(service_name)

settings = get_settings()
logger = setup_logging(
    level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
    service_name=settings.APP_NAME,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting service", extra={"service": settings.APP_NAME})
    task = asyncio.create_task(kafka_consumer())
    app.state.kafka_task = task
    yield
    logger.info("Shutting down service", extra={"service": settings.APP_NAME})
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await close_kafka()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description=f"""
# {settings.APP_NAME}

Event-driven notification service that consumes Kafka events and sends notifications.

## Features
- **Kafka Consumer**: Listens to order and user events
- **Email Notifications**: Via SMTP (MailHog for testing)
- **Structured JSON logging** for observability
- **Prometheus metrics** at `/metrics`

## API Endpoints
- **Notifications**: List delivered notifications
- **Health Check**: `/health` endpoint for monitoring
- **Metrics**: `/metrics` for Prometheus scraping
        """,
        contact={
            "name": "API Support",
            "email": "support@example.com",
        },
        license_info={
            "name": "MIT",
        },
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return openapi_schema


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "notifications",
            "description": "Notification management operations",
        }
    ],
)

app.openapi = custom_openapi
app.include_router(notifications_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }


Instrumentator().instrument(app).expose(app)
