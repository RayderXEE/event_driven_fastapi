from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.config import get_settings
from app.api.v1.router import api_router
from app.kafka.consumer import kafka_consumer
from app.kafka.producer import close_kafka_producer
from app.db.session import engine
from app.db.base import Base
from app.models.workflow import Workflow, Submission, StepInstance  # noqa: F401
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
    # Startup
    logger.info("Starting Workflow Service", extra={"service": settings.APP_NAME})
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified", extra={"service": settings.APP_NAME})
    task = asyncio.create_task(kafka_consumer())
    app.state.kafka_task = task
    yield
    # Shutdown
    logger.info("Shutting down Workflow Service", extra={"service": settings.APP_NAME})
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

Event-driven business process management service.

## Features
- **Workflow Templates**: Create multi-step approval workflows
- **Submissions**: Track and manage business process submissions
- **Step Management**: Approve/reject individual steps
- **Event Sourcing**: All changes published to Kafka
- **Async PostgreSQL**: Persistent storage with SQLAlchemy 2.0

## API Endpoints
- **Workflows**: Create, read, update, delete workflow templates
- **Submissions**: Start new submissions, track progress
- **Steps**: Submit or reject individual workflow steps
- **Health Check**: `/health` endpoint for monitoring
- **Metrics**: `/metrics` for Prometheus scraping

## Event Schema
All Kafka events follow this structure:
```json
{{
    "schema_version": "1.0.0",
    "event_type": "workflow.created",
    "timestamp": "2024-01-01T00:00:00Z",
    "source_service": "workflow-service",
    "data": {{...}}
}}
```
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
            "name": "workflows",
            "description": "Workflow template management",
        },
        {
            "name": "submissions",
            "description": "Submission and step management",
        }
    ],
)

# CORS middleware - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.openapi = custom_openapi
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": "1.0.0",
    }

# Prometheus metrics
Instrumentator().instrument(app).expose(app)
