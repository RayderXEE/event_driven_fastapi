from fastapi import APIRouter
from app.api.v1.workflows import router as workflows_router
from app.api.v1.submissions import router as submissions_router

api_router = APIRouter()
api_router.include_router(workflows_router)
api_router.include_router(submissions_router)
