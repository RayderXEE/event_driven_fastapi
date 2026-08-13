import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import AppLayout from './components/layout/AppLayout.tsx';
import Dashboard from './pages/Dashboard.tsx';
import Orders from './pages/Orders.tsx';
import Users from './pages/Users.tsx';
import WorkflowPage from './pages/Workflow.tsx';
import SubmissionsPage from './pages/Submissions.tsx';
import './style.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ConfigProvider theme={{
            token: {
                colorPrimary: '#1890ff',
                borderRadius: 6,
            },
        }}>
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<AppLayout />}>
                        <Route index element={<Dashboard />} />
                        <Route path="orders" element={<Orders />} />
                        <Route path="users" element={<Users />} />
                        <Route path="workflows" element={<WorkflowPage />} />
                        <Route path="submissions" element={<SubmissionsPage />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </ConfigProvider>
    </React.StrictMode>
);
