from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import get_settings
from app.api.v1.router import api_router
from app.kafka.consumer import kafka_consumer
from app.kafka.producer import close_kafka_producer
from app.db.session import engine
from app.db.base import Base
from app.models.user import User  # noqa: F401 - needed for Base.metadata
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
    # Create database tables if they don't exist (dev mode)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified", extra={"service": settings.APP_NAME})
    task = asyncio.create_task(kafka_consumer())
    app.state.kafka_task = task
    yield
    logger.info("Shutting down service", extra={"service": settings.APP_NAME})
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await close_kafka_producer()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description=f"""
# {settings.APP_NAME}

Event-driven microservice for user management.

## Features
- **RESTful API** with full OpenAPI documentation
- **Event sourcing** via Apache Kafka
- **Async PostgreSQL** persistence with SQLAlchemy 2.0
- **Structured JSON logging** for observability
- **Prometheus metrics** at `/metrics`

## API Endpoints
- **Users Management**: Create, read, and list users
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
            "name": "users",
            "description": "User management operations",
        }
    ],
)

app.openapi = custom_openapi
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }


Instrumentator().instrument(app).expose(app)
