from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.service.order import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new order and publish order.created event to Kafka."""
    service = OrderService(db)
    order = await service.create_order(data)
    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get order by ID."""
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all orders with pagination."""
    service = OrderService(db)
    return await service.list_orders(skip, limit)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Cancel an order (only if status is CREATED)."""
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderService.__module__.split(".")[-1]:  # Check status
        if order.status.value != "created":
            raise HTTPException(status_code=400, detail="Only created orders can be cancelled")
    order = await service.cancel_order(order_id)
    return order
