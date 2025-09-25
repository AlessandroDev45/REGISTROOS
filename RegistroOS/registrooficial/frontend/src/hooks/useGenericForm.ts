import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify'; // Assuming react-toastify is used

interface UseGenericFormProps<T> {
    initialData?: Partial<T>;
    validate: (data: T) => { [key in keyof T]?: string }; // Validation function
}

export function useGenericForm<T extends object>({ initialData, validate }: UseGenericFormProps<T>) {
    const [formData, setFormData] = useState<T>(initialData as T);
    const [errors, setErrors] = useState<{ [key in keyof T]?: string }>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        // Only merge initialData if it's different to prevent unnecessary re-renders
        if (initialData) {
            setFormData(initialData as T); // Directly set initialData to reset form properly
            setErrors({}); // Clear errors on initialData change
        }
    }, [initialData]);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        const processedValue: any = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

        setFormData(prev => ({
            ...prev,
            [name]: processedValue
        }));

        // Clear error for this field as user types
        setErrors(prev => {
            if (prev && prev[name as keyof T]) {
                const newErrors = { ...prev };
                delete newErrors[name as keyof T];
                return newErrors;
            }
            return prev;
        });
    }, []);

    const handleSubmit = useCallback(async (
        e: React.FormEvent,
        onSubmitCallback: (data: T, isEdit: boolean) => Promise<void> | void,
        isEdit: boolean
    ) => {
        e.preventDefault();
        setIsSubmitting(true);
        const validationErrors = validate(formData);

        if (Object.keys(validationErrors).length > 0) {
            setErrors(validationErrors);
            toast.error('Por favor, corrija os erros no formulário.');
            setIsSubmitting(false);
            return;
        }

        try {
            await onSubmitCallback(formData, isEdit);
            toast.success('Operação realizada com sucesso!');
        } catch (error: any) {
            console.error('Submission error:', error);
            toast.error(error.message || 'Erro ao salvar os dados.');
            setErrors(prev => ({ ...prev, general: error.message || 'Erro ao salvar' } as { [key in keyof T]?: string }));
        } finally {
            setIsSubmitting(false);
        }
    }, [formData, validate]);

    const getFieldError = useCallback((fieldName: keyof T): string | undefined => {
        return errors[fieldName];
    }, [errors]);

    return {
        formData,
        setFormData,
        errors,
        handleChange,
        handleSubmit,
        isSubmitting,
        getFieldError
    };
}