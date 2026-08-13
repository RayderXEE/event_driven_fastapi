import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Spin, Alert, Button } from 'antd';
import {
    UnorderedListOutlined,
    UserOutlined,
    CheckCircleOutlined,
    WarningOutlined,
    ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Order, User, ServiceHealth } from '../types';
import { orderService } from '../api/orders';
import { userService } from '../api/users';
import { healthService } from '../api/health';

const Dashboard: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [orders, setOrders] = useState<Order[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [health, setHealth] = useState<ServiceHealth | null>(null);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [ordersRes, usersRes, healthRes] = await Promise.all([
                orderService.getAll(0, 5).catch(() => ({ data: [] })),
                userService.getAll(0, 5).catch(() => ({ data: [] })),
                healthService.check().catch(() => null),
            ]);
            
            setOrders(ordersRes.data || []);
            setUsers(usersRes.data || []);
            setHealth(healthRes?.data || null);
        } catch (err: any) {
            setError(err.message || 'Failed to fetch data');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const ordersColumns: ColumnsType<Order> = [
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
            width: 120,
            render: (amount: number, record: Order) => `$${amount.toFixed(2)} ${record.currency}`,
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            width: 150,
            render: (status: string) => {
                const color = status === 'created' ? 'green' : status === 'cancelled' ? 'red' : 'orange';
                return <Tag color={color}>{status}</Tag>;
            },
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            key: 'created_at',
            width: 180,
            render: (date: string) => new Date(date).toLocaleString(),
        },
    ];

    const usersColumns: ColumnsType<User> = [
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
    ];

    const createdOrders = orders.filter(o => o.status === 'created').length;
    const cancelledOrders = orders.filter(o => o.status === 'cancelled').length;

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h1 style={{ margin: 0 }}>Dashboard</h1>
                <Button 
                    type="default"
                    icon={<ReloadOutlined />} 
                    onClick={fetchData}
                >
                    Refresh
                </Button>
            </div>

            {error && (
                <Alert 
                    message="Connection Error" 
                    description={error} 
                    type="error" 
                    showIcon 
                    style={{ marginBottom: 24 }}
                />
            )}

            <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Total Orders"
                            value={orders.length}
                            prefix={<UnorderedListOutlined />}
                            valueStyle={{ color: '#1890ff' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Total Users"
                            value={users.length}
                            prefix={<UserOutlined />}
                            valueStyle={{ color: '#722ed1' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Active Orders"
                            value={createdOrders}
                            prefix={<CheckCircleOutlined />}
                            valueStyle={{ color: '#3f8600' }}
                        />
                    </Card>
                </Col>
                <Col xs={24} sm={12} lg={6}>
                    <Card>
                        <Statistic
                            title="Service Status"
                            value={health ? 'UP' : 'DOWN'}
                            prefix={health ? <CheckCircleOutlined /> : <WarningOutlined />}
                            valueStyle={{ color: health ? '#3f8600' : '#cf1322' }}
                        />
                    </Card>
                </Col>
            </Row>

            {loading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <Spin size="large" tip="Loading data..." />
                </div>
            ) : (
                <>
                    <Card 
                        style={{ marginTop: 24 }} 
                        title={
                            <span>
                                <UnorderedListOutlined /> 
                                Recent Orders
                            </span>
                        }
                    >
                        <Table 
                            columns={ordersColumns} 
                            dataSource={orders} 
                            rowKey="id"
                            pagination={false}
                            size="small"
                        />
                    </Card>

                    <Card 
                        style={{ marginTop: 16 }} 
                        title={
                            <span>
                                <UserOutlined /> 
                                Recent Users
                            </span>
                        }
                    >
                        <Table 
                            columns={usersColumns} 
                            dataSource={users} 
                            rowKey="id"
                            pagination={false}
                            size="small"
                        />
                    </Card>
                </>
            )}
        </div>
    );
};

export default Dashboard;
