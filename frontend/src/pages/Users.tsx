import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, message } from 'antd';
import { 
    PlusOutlined, 
    UserOutlined, 
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { User, UserCreate } from '../types';
import { userService } from '../api/users';

const Users: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [form] = Form.useForm();

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const res = await userService.getAll();
            setUsers(res.data || []);
        } catch (err: any) {
            message.error('Failed to fetch users');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleCreate = async (values: UserCreate) => {
        try {
            await userService.create(values);
            message.success('User created successfully');
            setModalOpen(false);
            form.resetFields();
            fetchUsers();
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Failed to create user');
        }
    };

    const columns: ColumnsType<User> = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: 80,
        },
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
        },
        {
            title: 'Email',
            dataIndex: 'email',
            key: 'email',
        },
        {
            title: 'Balance',
            dataIndex: 'balance',
            key: 'balance',
            width: 120,
            render: (balance: number) => `$${balance.toFixed(2)}`,
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 200,
            render: (date: string) => new Date(date).toLocaleString(),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ margin: 0 }}>
                    <UserOutlined /> Users
                </h1>
                <Button 
                    type="primary" 
                    icon={<PlusOutlined />} 
                    onClick={() => setModalOpen(true)}
                >
                    New User
                </Button>
            </div>

            <Card>
                <Table 
                    columns={columns} 
                    dataSource={users} 
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                />
            </Card>

            <Modal
                title="Create New User"
                open={modalOpen}
                onCancel={() => {
                    setModalOpen(false);
                    form.resetFields();
                }}
                onOk={() => form.submit()}
                destroyOnClose
            >
                <Form form={form} layout="vertical" onFinish={handleCreate}>
                    <Form.Item
                        name="name"
                        label="Name"
                        rules={[{ required: true, message: 'Please enter name' }]}
                    >
                        <Input placeholder="Enter full name" />
                    </Form.Item>
                    <Form.Item
                        name="email"
                        label="Email"
                        rules={[
                            { required: true, message: 'Please enter email' },
                            { type: 'email', message: 'Please enter a valid email' }
                        ]}
                    >
                        <Input placeholder="Enter email address" />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default Users;
