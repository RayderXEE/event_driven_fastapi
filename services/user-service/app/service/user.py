from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.kafka.producer import send_event
from shared.events import UserCreatedEvent
from app.config import get_settings

settings = get_settings()

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        user = User(
            email=data.email,
            name=data.name,
            balance=data.balance,
        )
        self.db.add(user)
        await self.db.flush()

        event = UserCreatedEvent.from_user(
            user_id=user.id,
            email=data.email,
            name=data.name,
        )
        await send_event(
            topic=settings.KAFKA_TOPIC_USERS,
            event=event.model_dump(),
            key=str(user.id),
        )

        await self.db.refresh(user)
        return user

    async def get_user(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def list_users(self, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()
