import { healthApi } from './client';
import type { ServiceHealth } from '../types';

export const healthService = {
    check: () => 
        healthApi.get<ServiceHealth>('/'),
};
