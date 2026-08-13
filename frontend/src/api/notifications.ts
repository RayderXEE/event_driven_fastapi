import { notificationApi } from './client';
import type { Notification } from '../types';

export const notificationService = {
    getAll: () => 
        notificationApi.get<Notification[]>('/'),
};
