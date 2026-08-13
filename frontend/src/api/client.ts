import axios from 'axios';

// API client for Order Service
const orderApi = axios.create({
    baseURL: '/api/orders/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// API client for User Service
const userApi = axios.create({
    baseURL: '/api/users/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// API client for Notification Service
const notificationApi = axios.create({
    baseURL: '/api/notifications/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Health check client
const healthApi = axios.create({
    baseURL: '/api/health/',
    headers: {
        'Content-Type': 'application/json',
    },
});

export { orderApi, userApi, notificationApi, healthApi };
export default { orderApi, userApi, notificationApi, healthApi };
