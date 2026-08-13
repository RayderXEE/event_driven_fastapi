import { userApi } from './client';
import type { User, UserCreate } from '../types';

export const userService = {
    getAll: (skip: number = 0, limit: number = 100) => 
        userApi.get<User[]>('/', { params: { skip, limit } }),
    
    getById: (id: number) => 
        userApi.get<User>(`${id}/`),
    
    create: (data: UserCreate) => 
        userApi.post<User>('/', data),
};
