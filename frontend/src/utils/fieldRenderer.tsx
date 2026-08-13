import { Input, Select } from 'antd';
import type { FieldConfig } from '../types/index.ts';

export const renderFieldForType = (field: FieldConfig) => {
    switch (field.field_type) {
        case 'textarea':
            return <Input.TextArea rows={4} placeholder={field.placeholder} />;
        case 'number':
            return <Input type="number" placeholder={field.placeholder} />;
        case 'email':
            return <Input type="email" placeholder={field.placeholder} />;
        case 'date':
            return <Input type="date" />;
        case 'datetime':
            return <Input type="datetime-local" />;
        case 'boolean':
            return (
                <Select options={[
                    { value: true, label: 'Yes' },
                    { value: false, label: 'No' },
                ]} />
            );
        case 'choice': {
            const choices = field.choices
                .split(',')
                .filter(c => c.includes('|'))
                .map(c => {
                    const [value, label] = c.split('|');
                    return { value: value.trim(), label: label.trim() };
                });
            return <Select options={choices} />;
        }
        default:
            return <Input placeholder={field.placeholder} />;
    }
};
