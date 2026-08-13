from pydantic import BaseModel, Field
from datetime import datetime

class KafkaEvent(BaseModel):
    schema_version: str = "1.0.0"
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "user-service"

class UserCreatedEvent(KafkaEvent):
    event_type: str = "user.created"
    data: dict

    @classmethod
    def from_user(cls, user_id: int, email: str, name: str):
        return cls(
            data={
                "user_id": user_id,
                "email": email,
                "name": name,
            }
        )
