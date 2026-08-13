from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.workflow import (
    SubmissionResponse, SubmissionDetail, SubmissionCreate,
    StepSubmit, StepInstanceResponse,
)
from app.service.workflow import SubmissionService
from app.kafka.producer import publish_workflow_event
from shared.events import SubmissionCreatedEvent, StepCompletedEvent, StepRejectedEvent

router = APIRouter(prefix="/submissions", tags=["submissions"])

@router.get("/", response_model=list[SubmissionResponse])
async def list_submissions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all submissions"""
    service = SubmissionService(db)
    return await service.list_submissions(skip, limit)

@router.post("/", response_model=SubmissionResponse)
async def create_submission(
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new submission"""
    service = SubmissionService(db)
    submission = await service.create_submission(data)
    await publish_workflow_event(
        SubmissionCreatedEvent.from_submission(
            submission_id=submission.id,
            workflow_id=submission.workflow_id,
            user_id=submission.user_id,
        ),
        key=str(submission.id),
    )
    return submission

@router.get("/my/", response_model=list[SubmissionResponse])
async def get_my_submissions(
    user_id: int = Query(..., description="User ID"),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get user's submissions"""
    service = SubmissionService(db)
    return await service.get_user_submissions(user_id, skip, limit)

@router.get("/{submission_id}", response_model=SubmissionDetail)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get submission by ID"""
    service = SubmissionService(db)
    submission = await service.get_submission_detail(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.post("/{submission_id}/steps/{step_id}/submit/", response_model=StepInstanceResponse)
async def submit_step(
    submission_id: int,
    step_id: int,
    data: StepSubmit,
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Submit a step in the workflow"""
    service = SubmissionService(db)
    try:
        step = await service.submit_step(submission_id, step_id, data, user_id)
        if not step:
            raise HTTPException(status_code=404, detail="Step not found")
        await publish_workflow_event(
            StepCompletedEvent.from_step_completed(
                submission_id=submission_id,
                step_id=step_id,
                user_id=user_id,
            ),
            key=f"{submission_id}-{step_id}",
        )
        return step
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{submission_id}/steps/{step_id}/reject/", response_model=StepInstanceResponse)
async def reject_step(
    submission_id: int,
    step_id: int,
    comment: str = Query(..., description="Rejection comment"),
    user_id: int = Query(..., description="User ID"),
    db: AsyncSession = Depends(get_db),
):
    """Reject a step in the workflow"""
    service = SubmissionService(db)
    step = await service.reject_step(submission_id, step_id, comment, user_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    await publish_workflow_event(
        StepRejectedEvent.from_step_rejected(
            submission_id=submission_id,
            step_id=step_id,
            user_id=user_id,
            comment=comment,
        ),
        key=f"{submission_id}-{step_id}",
    )
    return step
