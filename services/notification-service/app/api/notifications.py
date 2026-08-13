from fastapi import APIRouter, HTTPException
from app.schemas.notification import NotificationStatus, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])

_in_memory_notifications: list = []

@router.get("/", response_model=list[NotificationResponse])
async def list_notifications():
    return _in_memory_notifications

@router.post("/test")
async def test_notification():
    return {"message": "Notification service is running"}
