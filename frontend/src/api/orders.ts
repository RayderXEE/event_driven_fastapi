import { orderApi } from './client';
import type { Order, OrderCreate } from '../types';

export const orderService = {
    getAll: (skip: number = 0, limit: number = 100) => 
        orderApi.get<Order[]>('/', { params: { skip, limit } }),
    
    getById: (id: number) => 
        orderApi.get<Order>(`${id}/`),
    
    create: (data: OrderCreate) => 
        orderApi.post<Order>('/', data),
    
    cancel: (id: number) => 
        orderApi.post<Order>(`${id}/cancel/`),
};
