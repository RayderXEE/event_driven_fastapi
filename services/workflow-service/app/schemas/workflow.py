from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

# Workflow schemas
class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    steps_config: Optional[list[dict[str, Any]]] = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    steps_config: Optional[list[dict[str, Any]]] = None

class WorkflowResponse(WorkflowBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class WorkflowDetail(WorkflowResponse):
    submissions_count: int = 0

# Submission schemas
class SubmissionBase(BaseModel):
    workflow_id: int
    user_id: int
    title: str
    description: Optional[str] = None

class SubmissionCreate(BaseModel):
    workflow_id: int
    user_id: int
    title: str
    description: Optional[str] = None
    step_data: dict[str, Any] = {}

class SubmissionResponse(BaseModel):
    id: int
    workflow_id: int
    user_id: int
    title: str
    description: Optional[str] = None
    status: str
    current_step: int
    step_data: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class SubmissionDetail(SubmissionResponse):
    steps: list[dict[str, Any]] = []

# Step schemas
class StepSubmit(BaseModel):
    step_data: dict[str, Any] = {}
    comment: str = ""

class StepInstanceResponse(BaseModel):
    id: int
    submission_id: int
    step_number: int
    step_name: str
    assignee_id: Optional[int] = None
    status: str
    comment: Optional[str] = None
    step_data: Optional[dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
