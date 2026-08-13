import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Tag, Popconfirm, message } from 'antd';
import { 
    PlusOutlined, 
    UnorderedListOutlined, 
    DeleteOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Order, OrderCreate } from '../types';
import { orderService } from '../api/orders';

const Orders: React.FC = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [form] = Form.useForm();

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const res = await orderService.getAll();
            setOrders(res.data || []);
        } catch (err: any) {
            message.error('Failed to fetch orders');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const handleCreate = async (values: OrderCreate) => {
        try {
            await orderService.create(values);
            message.success('Order created successfully');
            setModalOpen(false);
            form.resetFields();
            fetchOrders();
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Failed to create order');
        }
    };

    const handleCancel = async (id: number) => {
        try {
            await orderService.cancel(id);
            message.success('Order cancelled');
            fetchOrders();
        } catch (err: any) {
            message.error(err.response?.data?.detail || 'Failed to cancel order');
        }
    };

    const columns: ColumnsType<Order> = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: 80,
        },
        {
            title: 'User ID',
            dataIndex: 'user_id',
            key: 'user_id',
            width: 100,
        },
        {
            title: 'Amount',
            dataIndex: 'amount',
            key: 'amount',
            width: 150,
            render: (amount: number, record: Order) => `$${amount.toFixed(2)} ${record.currency}`,
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            width: 150,
            render: (status: string) => {
                const config: Record<string, { color: string; icon: React.ReactNode }> = {
                    created: { color: 'green', icon: <CheckCircleOutlined /> },
                    cancelled: { color: 'red', icon: <CloseCircleOutlined /> },
                };
                const { color, icon } = config[status] || { color: 'orange', icon: null };
                return <Tag color={color} icon={icon}>{status}</Tag>;
            },
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 200,
            render: (date: string) => new Date(date).toLocaleString(),
        },
        {
            title: 'Actions',
            key: 'actions',
            width: 120,
            render: (_, record) => (
                <Popconfirm
                    title="Cancel this order?"
                    description="Only created orders can be cancelled."
                    onConfirm={() => handleCancel(record.id)}
                    disabled={record.status !== 'created'}
                    okText="Yes"
                    cancelText="No"
                >
                    <Button 
                        type="link" 
                        danger 
                        icon={<DeleteOutlined />}
                        disabled={record.status !== 'created'}
                    >
                        Cancel
                    </Button>
                </Popconfirm>
            ),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ margin: 0 }}>
                    <UnorderedListOutlined /> Orders
                </h1>
                <Button 
                    type="primary" 
                    icon={<PlusOutlined />} 
                    onClick={() => setModalOpen(true)}
                >
                    New Order
                </Button>
            </div>

            <Card>
                <Table 
                    columns={columns} 
                    dataSource={orders} 
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                />
            </Card>

            <Modal
                title="Create New Order"
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
                        name="user_id"
                        label="User ID"
                        rules={[{ required: true, message: 'Please enter User ID' }]}
                    >
                        <InputNumber style={{ width: '100%' }} min={1} />
                    </Form.Item>
                    <Form.Item
                        name="amount"
                        label="Amount ($)"
                        rules={[{ required: true, message: 'Please enter amount' }]}
                    >
                        <InputNumber style={{ width: '100%' }} min={0} step={0.01} />
                    </Form.Item>
                    <Form.Item
                        name="currency"
                        label="Currency"
                        initialValue="USD"
                    >
                        <Input placeholder="USD" />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default Orders;
