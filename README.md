# Event-Driven Architecture with FastAPI + Kafka

A microservices project demonstrating event-driven architecture using FastAPI, Apache Kafka, PostgreSQL, Redis, React frontend, and comprehensive monitoring.

## Architecture

```
Order Service (:8001) ──┐
                        ├──→ Kafka ──→ Notification Service (:8003)
User Service (:8002) ───┘
Workflow Service (:8004) ──→ Kafka ──→ Notification Service (:8003)

Frontend (:3001) ──→ Nginx (:8080) ──→ All Services
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Order Service | 8001 | Order CRUD, publishes `order.created` events |
| User Service | 8002 | User CRUD, publishes `user.created` events |
| Notification Service | 8003 | Consumes events, sends notifications |
| Workflow Service | 8004 | Workflow & submissions management, publishes `workflow.*` events |
| Frontend | 3001 | React SPA with nginx, proxies API requests to backend services |
| Nginx (proxy) | 8080 | Reverse proxy for all backend services |

## Infrastructure

| Component | Port | Purpose |
|-----------|------|---------|
| PostgreSQL (orders) | 5432 | Order database |
| PostgreSQL (users) | 5433 | User database |
| PostgreSQL (workflows) | 5434 | Workflow database |
| Redis | 6379 | Caching |
| Kafka | 9092 | Event bus |
| Zookeeper | 2181 | Kafka coordination |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Dashboards |
| Jaeger | 16686 | Distributed tracing |
| MailHog | 8025 | Email testing UI |

## Quick Start

```bash
docker-compose up --build -d
docker-compose ps
docker-compose logs -f order-service
```

## API Endpoints

### Order Service (http://localhost:8001)
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/orders/{id}` - Get order
- `/docs` - Swagger UI

### User Service (http://localhost:8002)
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}` - Get user
- `/docs` - Swagger UI

### Notification Service (http://localhost:8003)
- `GET /api/v1/notifications/` - List notifications
- `/docs` - Swagger UI

### Workflow Service (http://localhost:8004)
- `GET /api/workflows/` - List workflows
- `GET /api/workflows/{id}` - Get workflow
- `GET /api/submissions/` - List submissions
- `GET /api/submissions/{id}` - Get submission
- `POST /api/submissions/` - Create submission
- `/docs` - Swagger UI

### Frontend (http://localhost:3001)
- React SPA with workflow management UI
- Proxies API requests to backend services via nginx

### Nginx Reverse Proxy (http://localhost:8080)
- `/api/orders/` → Order Service
- `/api/users/` → User Service
- `/api/notifications/` → Notification Service
- `/api/workflows/` → Workflow Service

## Monitoring

- **Frontend**: http://localhost:3001
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686
- **MailHog**: http://localhost:8025

## Kafka Topics

| Topic | Produced By | Consumed By |
|-------|-------------|-------------|
| `orders` | Order Service | User Service, Notification Service |
| `users` | User Service | Notification Service |
| `payments` | External | Order Service |
| `workflows` | Workflow Service | Notification Service |

## Event Schemas

All event types, data models and the `parse_event()` dispatcher are defined in a single shared module:

**[`shared/events.py`](shared/events.py)**

It contains:
- `KafkaEvent` — base envelope with `schema_version`, `event_type`, `timestamp`, `source_service`, `data`
- Typed event data models: `OrderCreatedData`, `OrderUpdatedData`, `UserCreatedData`, `WorkflowCreatedData`, `SubmissionCreatedData`, `StepCompletedData`, `StepRejectedData`
- Typed event classes: `OrderCreatedEvent`, `OrderUpdatedEvent`, `UserCreatedEvent`, `WorkflowCreatedEvent`, `SubmissionCreatedEvent`, `StepCompletedEvent`, `StepRejectedEvent`
- `EVENT_TYPE_MAP` — maps `event_type` string → event class
- `parse_event(raw_dict)` — validates and deserializes any raw Kafka message into the correct typed event

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues and solutions:
- CORS / 307 Redirect issues with trailing slashes
- Nginx proxy configuration for port preservation
- Frontend build and Docker image rebuild steps
