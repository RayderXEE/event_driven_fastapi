import axios from 'axios';
import type {
    Workflow,
    WorkflowCreate,
    Submission,
    SubmissionDetail,
    SubmissionCreate,
    StepInstance,
} from '../types';

const workflowApi = axios.create({
    baseURL: '/api/workflows/',
    headers: { 'Content-Type': 'application/json' },
});

const submissionApi = axios.create({
    baseURL: '/api/submissions/',
    headers: { 'Content-Type': 'application/json' },
});

export const workflowService = {
    getAll: (skip = 0, limit = 100) =>
        workflowApi.get<Workflow[]>('/', { params: { skip, limit } }),

    getById: (id: number) =>
        workflowApi.get<Workflow>(`${id}/`),

    create: (data: WorkflowCreate) =>
        workflowApi.post<Workflow>('/', data),

    update: (id: number, data: Partial<WorkflowCreate>) =>
        workflowApi.put<Workflow>(`${id}/`, data),

    delete: (id: number) =>
        workflowApi.delete(`${id}/`),
};

export const submissionService = {
    getAll: (skip = 0, limit = 100) =>
        submissionApi.get<Submission[]>('/', { params: { skip, limit } }),

    getById: (id: number) =>
        submissionApi.get<SubmissionDetail>(`${id}`),

    create: (data: SubmissionCreate) =>
        submissionApi.post<Submission>('/', data),

    submitStep: (submissionId: number, stepId: number, stepData: any, comment: string, userId: number) =>
        submissionApi.post<StepInstance>(
            `${submissionId}/steps/${stepId}/submit/`,
            { step_data: stepData, comment },
            { params: { user_id: userId } }
        ),

    rejectStep: (submissionId: number, stepId: number, comment: string, userId: number) =>
        submissionApi.post<StepInstance>(
            `${submissionId}/steps/${stepId}/reject/`,
            {},
            { params: { comment, user_id: userId } }
        ),
};
