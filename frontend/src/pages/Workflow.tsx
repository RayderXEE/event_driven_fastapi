import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Tag, Popconfirm, message, Space, Select } from 'antd';
import {
    PlusOutlined,
    DeleteOutlined,
    FileTextOutlined,
    EditOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Workflow, WorkflowCreate, WorkflowStepConfig } from '../types';
import { workflowService } from '../api/workflows';

const { TextArea } = Input;

const WorkflowPage: React.FC = () => {
    const [workflows, setWorkflows] = useState<Workflow[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [form] = Form.useForm();

    const fetchWorkflows = async () => {
        setLoading(true);
        try {
            const res = await workflowService.getAll();
            setWorkflows(res.data || []);
        } catch {
            message.error('Failed to fetch workflows');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchWorkflows(); }, []);

    const handleCreate = async (values: any) => {
        // Parse steps_config from JSON string to array
        if (typeof values.steps_config === 'string') {
            try {
                values.steps_config = JSON.parse(values.steps_config);
            } catch {
                message.error('Invalid JSON in steps_config');
                return;
            }
        }
        try {
            if (editingId) {
                await workflowService.update(editingId, values);
                message.success('Workflow updated');
            } else {
                await workflowService.create(values);
                message.success('Workflow created');
            }
            setModalOpen(false);
            setEditingId(null);
            form.resetFields();
            fetchWorkflows();
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Operation failed');
        }
    };

    const handleEdit = (wf: Workflow) => {
        setEditingId(wf.id);
        form.setFieldsValue(wf);
        setModalOpen(true);
    };

    const handleDelete = async (id: number) => {
        try {
            await workflowService.delete(id);
            message.success('Workflow deleted');
            fetchWorkflows();
        } catch {
            message.error('Failed to delete');
        }
    };

    const statusColor: Record<string, string> = {
        draft: 'default',
        active: 'green',
        archived: 'error',
    };

    const columns: ColumnsType<Workflow> = [
        { title: 'ID', dataIndex: 'id', key: 'id', width: 70 },
        { title: 'Name', dataIndex: 'name', key: 'name', ellipsis: true },
        {
            title: 'Description',
            dataIndex: 'description',
            key: 'description',
            ellipsis: { showTitle: false },
            render: (t: string) => t || '—',
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            width: 120,
            render: (s: string) => <Tag color={statusColor[s] || 'orange'}>{s}</Tag>,
        },
        {
            title: 'Steps',
            dataIndex: 'steps_config',
            key: 'steps_config',
            width: 120,
            render: (steps: WorkflowStepConfig[]) => steps?.length || 0,
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
            width: 150,
            render: (_, r) => (
                <Space>
                    <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(r)} />
                    <Popconfirm title="Delete?" onConfirm={() => handleDelete(r.id)} okText="Yes" cancelText="No">
                        <Button type="link" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ margin: 0 }}>
                    <FileTextOutlined /> Workflow Templates
                </h1>
                <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => { setEditingId(null); form.resetFields(); setModalOpen(true); }}
                >
                    New Workflow
                </Button>
            </div>

            <Card>
                <Table
                    columns={columns}
                    dataSource={workflows}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                />
            </Card>

            <Modal
                title={editingId ? 'Edit Workflow' : 'Create Workflow'}
                open={modalOpen}
                onCancel={() => { setModalOpen(false); setEditingId(null); form.resetFields(); }}
                onOk={() => form.submit()}
                destroyOnClose
            >
                <Form form={form} layout="vertical" onFinish={handleCreate}>
                    <Form.Item name="name" label="Name" rules={[{ required: true, message: 'Required' }]}>
                        <Input placeholder="e.g. Leave Request" />
                    </Form.Item>
                    <Form.Item name="description" label="Description">
                        <TextArea rows={2} placeholder="Short description..." />
                    </Form.Item>
                    <Form.Item name="status" label="Status">
                        <Select options={[
                            { label: 'Draft', value: 'draft' },
                            { label: 'Active', value: 'active' },
                            { label: 'Archived', value: 'archived' },
                        ]} />
                    </Form.Item>
                    <Form.Item name="steps_config" label="Steps (JSON array)">
                        <TextArea
                            rows={5}
                            placeholder='[{"step_number":1,"step_name":"Manager Review","assignee_role":"manager"},{"step_number":2,"step_name":"HR Approval","assignee_role":"hr"}]'
                        />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default WorkflowPage;
