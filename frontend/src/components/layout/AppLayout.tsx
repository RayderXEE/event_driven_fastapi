import React from 'react';
import { Layout, Menu } from 'antd';
import {
    DashboardOutlined,
    UnorderedListOutlined,
    UserOutlined,
    FileTextOutlined,
    PlayCircleOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

const AppLayout: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
        { key: '/orders', icon: <UnorderedListOutlined />, label: 'Orders' },
        { key: '/users', icon: <UserOutlined />, label: 'Users' },
        { key: '/workflows', icon: <FileTextOutlined />, label: 'Workflows' },
        { key: '/submissions', icon: <PlayCircleOutlined />, label: 'Submissions' },
    ];

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider breakpoint="lg" collapsedWidth="80">
                <div style={{
                    height: 64,
                    margin: 16,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 18,
                    fontWeight: 'bold',
                }}>
                    ⚡ Event Driven API
                </div>
                <Menu
                    theme="dark"
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={({ key }) => navigate(key)}
                />
            </Sider>
            <Layout>
                <Header style={{
                    background: '#fff',
                    padding: '0 24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'flex-end',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                }}>
                    <span style={{ color: '#666' }}>Microservices Frontend</span>
                </Header>
                <Content style={{ margin: 24, padding: 24, background: '#f0f2f5', minHeight: 400, borderRadius: 8 }}>
                    <Outlet />
                </Content>
            </Layout>
        </Layout>
    );
};

export default AppLayout;
