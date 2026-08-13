from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowDetail,
    SubmissionCreate, SubmissionResponse, SubmissionDetail,
    StepSubmit, StepInstanceResponse,
)
from app.service.workflow import WorkflowService, SubmissionService
from app.kafka.producer import publish_workflow_event
from shared.events import WorkflowCreatedEvent, SubmissionCreatedEvent

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new workflow template"""
    service = WorkflowService(db)
    workflow = await service.create_workflow(data)
    await publish_workflow_event(
        WorkflowCreatedEvent.from_workflow(workflow_id=workflow.id, name=workflow.name),
        key=str(workflow.id),
    )
    return workflow

@router.get("/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get workflow by ID"""
    service = WorkflowService(db)
    workflow = await service.get_workflow_detail(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """List all workflows"""
    service = WorkflowService(db)
    return await service.list_workflows(skip, limit)

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update workflow"""
    service = WorkflowService(db)
    workflow = await service.update_workflow(workflow_id, data)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete workflow"""
    service = WorkflowService(db)
    deleted = await service.delete_workflow(workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")

@router.post("/{workflow_id}/start", response_model=SubmissionResponse)
async def start_workflow(
    workflow_id: int,
    data: SubmissionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Start a new submission for a workflow"""
    # Override workflow_id from path
    data.workflow_id = workflow_id
    service = SubmissionService(db)
    submission = await service.create_submission(user_id=data.user_id, data=data)
    await publish_workflow_event(
        SubmissionCreatedEvent.from_submission(
            submission_id=submission.id,
            workflow_id=workflow_id,
            user_id=data.user_id,
        ),
        key=str(submission.id),
    )
    return submission
