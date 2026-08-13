from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order, OrderStatus
from app.schemas.order import OrderCreate
from app.kafka.producer import send_event
from shared.events import OrderCreatedEvent
from app.config import get_settings

settings = get_settings()

class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, data: OrderCreate) -> Order:
        order = Order(
            user_id=data.user_id,
            amount=data.amount,
            currency=data.currency,
            status=OrderStatus.CREATED,
        )
        self.db.add(order)
        await self.db.flush()

        # Publish event to Kafka
        event = OrderCreatedEvent.from_order(
            order_id=order.id,
            user_id=data.user_id,
            amount=data.amount,
            currency=data.currency,
        )
        await send_event(
            topic=settings.KAFKA_TOPIC_ORDERS,
            event=event.model_dump(),
            key=str(order.id),
        )

        await self.db.refresh(order)
        return order

    async def get_order(self, order_id: int) -> Order | None:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_orders(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def cancel_order(self, order_id: int) -> Order | None:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if order and order.status == OrderStatus.CREATED:
            order.status = OrderStatus.CANCELLED
            await self.db.flush()
            await self.db.refresh(order)
        return order
