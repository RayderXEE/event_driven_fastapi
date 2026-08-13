export interface Order {
    id: number;
    user_id: number;
    status: string;
    amount: number;
    currency: string;
    created_at: string;
    updated_at: string;
}

export interface OrderCreate {
    user_id: number;
    amount: number;
    currency?: string;
}

export interface User {
    id: number;
    email: string;
    name: string;
    balance: number;
    created_at: string;
    updated_at: string;
}

export interface UserCreate {
    name: string;
    email: string;
}

export interface Notification {
    id: number;
    event_type: string;
    message: string;
    status: string;
    created_at: string;
}

export interface ServiceHealth {
    status: string;
    service: string;
    version: string;
}

// ─── Workflow types ───────────────────────────────────────────────

export interface WorkflowStepConfig {
    step_number: number;
    step_name: string;
    assignee_role?: string;
    assignee_id?: number;
}

export interface Workflow {
    id: number;
    name: string;
    description: string | null;
    status: string;
    steps_config: WorkflowStepConfig[] | null;
    created_at: string;
    updated_at: string | null;
}

export interface WorkflowCreate {
    name: string;
    description?: string;
    status?: string;
    steps_config?: WorkflowStepConfig[];
}

export interface StepInstance {
    id: number;
    submission_id: number;
    step_number: number;
    step_name: string;
    assignee_id: number | null;
    status: string;
    comment: string | null;
    step_data: any;
    started_at: string | null;
    completed_at: string | null;
    created_at: string;
}

export interface Submission {
    id: number;
    workflow_id: number;
    user_id: number;
    title: string;
    description: string | null;
    status: string;
    current_step: number;
    step_data: any;
    created_at: string;
    updated_at: string | null;
}

export interface SubmissionDetail extends Submission {
    steps: StepInstance[];
}

export interface SubmissionCreate {
    workflow_id: number;
    user_id: number;
    title: string;
    description?: string;
    step_data?: any;
}
