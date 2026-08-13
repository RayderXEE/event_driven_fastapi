from fastapi import APIRouter
from app.api.v1.orders import router as orders_router

api_router = APIRouter()
api_router.include_router(orders_router)
