import React, { useState, useEffect } from 'react';
import {
    Card, Table, Button, Modal, Form, Input, Tag, message, Space, Select,
    Descriptions, Timeline, Divider, Alert, Badge,
} from 'antd';
import {
    PlayCircleOutlined,
    FileTextOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    ClockCircleOutlined,
    EyeOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Submission, SubmissionDetail, SubmissionCreate, Workflow, StepInstance } from '../types';
import { submissionService, workflowService } from '../api/workflows';

const { TextArea } = Input;

const statusColor: Record<string, string> = {
    pending: 'blue',
    in_progress: 'orange',
    approved: 'green',
    rejected: 'red',
    cancelled: 'default',
};

const stepStatusIcon: Record<string, React.ReactNode> = {
    pending: <ClockCircleOutlined style={{ color: '#faad14' }} />,
    completed: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
    rejected: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
};

const SubmissionsPage: React.FC = () => {
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [workflows, setWorkflows] = useState<Workflow[]>([]);
    const [loading, setLoading] = useState(false);
    const [detailOpen, setDetailOpen] = useState(false);
    const [detailLoading, setDetailLoading] = useState(false);
    const [detail, setDetail] = useState<SubmissionDetail | null>(null);
    const [createOpen, setCreateOpen] = useState(false);
    const [form] = Form.useForm();
    const [userId, setUserId] = useState<number>(1);

    const fetchSubmissions = async () => {
        setLoading(true);
        try {
            const res = await submissionService.getAll();
            setSubmissions(res.data || []);
        } catch {
            message.error('Failed to fetch submissions');
        } finally {
            setLoading(false);
        }
    };

    const fetchWorkflows = async () => {
        try {
            const res = await workflowService.getAll();
            setWorkflows(res.data || []);
        } catch {
            message.error('Failed to fetch workflows');
        }
    };

    useEffect(() => {
        fetchSubmissions();
        fetchWorkflows();
    }, []);

    const handleCreate = async (values: SubmissionCreate) => {
        try {
            await submissionService.create({ ...values, user_id: userId });
            message.success('Submission created');
            setCreateOpen(false);
            form.resetFields();
            fetchSubmissions();
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Failed to create');
        }
    };

    const handleViewDetail = async (id: number) => {
        setDetailLoading(true);
        setDetailOpen(true);
        try {
            const res = await submissionService.getById(id);
            setDetail(res.data);
        } catch {
            message.error('Failed to load details');
        } finally {
            setDetailLoading(false);
        }
    };

    const handleApproveStep = async (submissionId: number, stepId: number) => {
        try {
            await submissionService.submitStep(submissionId, stepId, {}, 'Approved', userId);
            message.success('Step approved');
            const res = await submissionService.getById(submissionId);
            setDetail(res.data);
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Failed to approve');
        }
    };

    const handleRejectStep = async (submissionId: number, stepId: number) => {
        const comment = prompt('Rejection reason:');
        if (!comment) return;
        try {
            await submissionService.rejectStep(submissionId, stepId, comment, userId);
            message.success('Step rejected');
            const res = await submissionService.getById(submissionId);
            setDetail(res.data);
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Failed to reject');
        }
    };

    const columns: ColumnsType<Submission> = [
        { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
        {
            title: 'Workflow',
            dataIndex: 'workflow_id',
            key: 'workflow_id',
            width: 120,
            render: (wid: number) => workflows.find(w => w.id === wid)?.name || `#${wid}`,
        },
        { title: 'Title', dataIndex: 'title', key: 'title', ellipsis: true },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            width: 130,
            render: (s: string) => <Tag color={statusColor[s] || 'default'}>{s}</Tag>,
        },
        {
            title: 'Step',
            dataIndex: 'current_step',
            key: 'current_step',
            width: 80,
            render: (n: number) => `#${n}`,
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 200,
            render: (d: string) => new Date(d).toLocaleString(),
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 100,
            render: (_, r) => (
                <Button type="link" icon={<EyeOutlined />} onClick={() => handleViewDetail(r.id)}>
                    View
                </Button>
            ),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ margin: 0 }}>
                    <PlayCircleOutlined /> Business Process Submissions
                </h1>
                <Space>
                    <span style={{ color: '#666' }}>Act as user:</span>
                    <Select
                        value={userId}
                        onChange={setUserId}
                        style={{ width: 120 }}
                        options={[
                            { label: 'User #1', value: 1 },
                            { label: 'User #2', value: 2 },
                            { label: 'Manager', value: 3 },
                            { label: 'HR', value: 4 },
                        ]}
                    />
                    <Button
                        type="primary"
                        icon={<PlayCircleOutlined />}
                        onClick={() => setCreateOpen(true)}
                    >
                        New Submission
                    </Button>
                </Space>
            </div>

            <Card>
                <Table
                    columns={columns}
                    dataSource={submissions}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                />
            </Card>

            {/* ── Create Submission Modal ─────────────────────────── */}
            <Modal
                title="Create New Submission"
                open={createOpen}
                onCancel={() => { setCreateOpen(false); form.resetFields(); }}
                onOk={() => form.submit()}
                destroyOnClose
            >
                <Form form={form} layout="vertical" onFinish={handleCreate}>
                    <Form.Item name="workflow_id" label="Workflow Template" rules={[{ required: true, message: 'Select a workflow' }]}>
                        <Select
                            options={workflows.map(w => ({ label: `${w.name} (${w.status})`, value: w.id }))}
                            placeholder="Choose workflow..."
                        />
                    </Form.Item>
                    <Form.Item name="title" label="Title" rules={[{ required: true, message: 'Required' }]}>
                        <Input placeholder="e.g. Vacation - Sept 2026" />
                    </Form.Item>
                    <Form.Item name="description" label="Description">
                        <TextArea rows={2} placeholder="Details..." />
                    </Form.Item>
                </Form>
            </Modal>

            {/* ── Detail Modal ────────────────────────────────────── */}
            <Modal
                title={`Submission #${detail?.id} — ${detail?.title}`}
                open={detailOpen}
                onCancel={() => setDetailOpen(false)}
                footer={null}
                width={720}
                destroyOnClose
            >
                {detailLoading ? (
                    <div style={{ textAlign: 'center', padding: 40 }}>Loading...</div>
                ) : detail ? (
                    <div>
                        <Descriptions bordered column={2} size="small">
                            <Descriptions.Item label="Status">
                                <Tag color={statusColor[detail.status]}>{detail.status}</Tag>
                            </Descriptions.Item>
                            <Descriptions.Item label="Current Step">#{detail.current_step}</Descriptions.Item>
                            <Descriptions.Item label="User ID">{detail.user_id}</Descriptions.Item>
                            <Descriptions.Item label="Created">
                                {new Date(detail.created_at).toLocaleString()}
                            </Descriptions.Item>
                            <Descriptions.Item label="Title" span={2}>{detail.title}</Descriptions.Item>
                            {detail.description && (
                                <Descriptions.Item label="Description" span={2}>{detail.description}</Descriptions.Item>
                            )}
                        </Descriptions>

                        <Divider orientation="left">Process Steps</Divider>

                        <Timeline
                            items={(detail?.steps || []).map((step: StepInstance) => ({
                                color: step.status === 'completed' ? 'green' : step.status === 'rejected' ? 'red' : 'gray',
                                children: (
                                    <div key={step.id}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <strong>
                                                {stepStatusIcon[step.status]} Step {step.step_number}: {step.step_name}
                                            </strong>
                                            <Tag color={
                                                step.status === 'completed' ? 'green' :
                                                step.status === 'rejected' ? 'red' : 'blue'
                                            }>
                                                {step.status}
                                            </Tag>
                                        </div>
                                        {step.comment && <div style={{ color: '#888', fontSize: 12, marginTop: 4 }}>💬 {step.comment}</div>}
                                        {step.completed_at && (
                                            <div style={{ color: '#888', fontSize: 12 }}>
                                                Completed: {new Date(step.completed_at).toLocaleString()}
                                            </div>
                                        )}
                                        {/* Action buttons for current pending step */}
                                        {step.status === 'pending' && detail.current_step === step.step_number && (
                                            <div style={{ marginTop: 8 }}>
                                                <Space>
                                                    <Button
                                                        type="primary"
                                                        size="small"
                                                        icon={<CheckCircleOutlined />}
                                                        onClick={() => handleApproveStep(detail.id, step.id)}
                                                    >
                                                        Approve
                                                    </Button>
                                                    <Button
                                                        danger
                                                        size="small"
                                                        icon={<CloseCircleOutlined />}
                                                        onClick={() => handleRejectStep(detail.id, step.id)}
                                                    >
                                                        Reject
                                                    </Button>
                                                </Space>
                                            </div>
                                        )}
                                    </div>
                                ),
                            }))}
                        />

                        {(detail.status === 'approved' || detail.status === 'rejected') && (
                            <Alert
                                style={{ marginTop: 16 }}
                                type={detail.status === 'approved' ? 'success' : 'error'}
                                message={`Process ${detail.status === 'approved' ? 'approved' : 'rejected'} — no more steps`}
                            />
                        )}
                    </div>
                ) : null}
            </Modal>
        </div>
    );
};

export default SubmissionsPage;
