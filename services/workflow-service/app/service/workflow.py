from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import Optional
from app.models.workflow import Workflow, Submission, StepInstance, WorkflowStatus, SubmissionStatus, StepStatus
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, SubmissionCreate, StepSubmit

class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(self, data: WorkflowCreate) -> Workflow:
        workflow = Workflow(**data.model_dump())
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def list_workflows(self, skip: int = 0, limit: int = 100) -> list[Workflow]:
        result = await self.db.execute(
            select(Workflow).offset(skip).limit(limit).order_by(Workflow.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_workflow(self, workflow_id: int, data: WorkflowUpdate) -> Optional[Workflow]:
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(workflow, key, value)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete_workflow(self, workflow_id: int) -> bool:
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return False
        await self.db.delete(workflow)
        await self.db.commit()
        return True

    async def get_workflow_detail(self, workflow_id: int) -> Optional[dict]:
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        result = await self.db.execute(
            select(func.count(Submission.id)).where(Submission.workflow_id == workflow_id)
        )
        count = result.scalar()
        
        return {
            **workflow.__dict__,
            "submissions_count": count,
        }

class SubmissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_submission(self, data: SubmissionCreate) -> Submission:
        # Get workflow
        result = await self.db.execute(
            select(Workflow).where(Workflow.id == data.workflow_id)
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {data.workflow_id} not found")

        # Create submission
        submission = Submission(
            workflow_id=data.workflow_id,
            user_id=data.user_id,
            title=data.title,
            description=data.description if hasattr(data, 'description') else None,
            step_data=data.step_data,
            status=SubmissionStatus.PENDING,
            current_step=1,
        )
        self.db.add(submission)
        await self.db.flush()

        # Create step instances from workflow config
        if workflow.steps_config:
            for i, step_config in enumerate(workflow.steps_config, 1):
                step = StepInstance(
                    submission_id=submission.id,
                    step_number=i,
                    step_name=step_config.get("name", f"Step {i}"),
                    assignee_id=step_config.get("assignee_id"),
                    status=StepStatus.PENDING if i == 1 else StepStatus.PENDING,
                )
                if i == 1:
                    step.status = StepStatus.PENDING
                self.db.add(step)

        await self.db.commit()
        await self.db.refresh(submission)
        return submission

    async def list_submissions(self, skip: int = 0, limit: int = 100) -> list[Submission]:
        result = await self.db.execute(
            select(Submission)
            .offset(skip)
            .limit(limit)
            .order_by(Submission.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_submission(self, submission_id: int) -> Optional[Submission]:
        result = await self.db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_submission_detail(self, submission_id: int) -> Optional[dict]:
        submission = await self.get_submission(submission_id)
        if not submission:
            return None

        result = await self.db.execute(
            select(StepInstance)
            .where(StepInstance.submission_id == submission_id)
            .order_by(StepInstance.step_number)
        )
        steps = list(result.scalars().all())

        return {
            "id": submission.id,
            "workflow_id": submission.workflow_id,
            "user_id": submission.user_id,
            "title": submission.title,
            "description": submission.description,
            "status": submission.status.value if submission.status else str(submission.status),
            "current_step": submission.current_step,
            "step_data": submission.step_data,
            "created_at": submission.created_at.isoformat() if submission.created_at else None,
            "updated_at": submission.updated_at.isoformat() if submission.updated_at else None,
            "steps": [
                {
                    "id": step.id,
                    "submission_id": step.submission_id,
                    "step_number": step.step_number,
                    "step_name": step.step_name,
                    "assignee_id": step.assignee_id,
                    "status": step.status.value if step.status else str(step.status),
                    "comment": step.comment,
                    "step_data": step.step_data,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "created_at": step.created_at.isoformat() if step.created_at else None,
                }
                for step in steps
            ],
        }

    async def get_user_submissions(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Submission]:
        result = await self.db.execute(
            select(Submission)
            .where(Submission.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Submission.created_at.desc())
        )
        return list(result.scalars().all())

    async def submit_step(self, submission_id: int, step_id: int, data: StepSubmit, user_id: int) -> Optional[StepInstance]:
        step = await self.get_step(step_id)
        if not step or step.submission_id != submission_id:
            return None
        if step.status != StepStatus.PENDING:
            raise ValueError("Step is not pending")

        step.status = StepStatus.COMPLETED
        step.comment = data.comment
        step.step_data = data.step_data
        step.completed_at = datetime.utcnow()
        step.assignee_id = user_id

        # Move to next step
        submission = await self.get_submission(submission_id)
        if submission:
            next_step = step.step_number + 1
            result = await self.db.execute(
                select(StepInstance)
                .where(
                    StepInstance.submission_id == submission_id,
                    StepInstance.step_number == next_step
                )
            )
            next_step_instance = result.scalar_one_or_none()
            
            if next_step_instance:
                submission.current_step = next_step
                submission.status = SubmissionStatus.IN_PROGRESS
            else:
                submission.status = SubmissionStatus.APPROVED

        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def reject_step(self, submission_id: int, step_id: int, comment: str, user_id: int) -> Optional[StepInstance]:
        step = await self.get_step(step_id)
        if not step or step.submission_id != submission_id:
            return None

        step.status = StepStatus.REJECTED
        step.comment = comment
        step.completed_at = datetime.utcnow()

        submission = await self.get_submission(submission_id)
        if submission:
            submission.status = SubmissionStatus.REJECTED

        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def get_step(self, step_id: int) -> Optional[StepInstance]:
        result = await self.db.execute(
            select(StepInstance).where(StepInstance.id == step_id)
        )
        return result.scalar_one_or_none()
