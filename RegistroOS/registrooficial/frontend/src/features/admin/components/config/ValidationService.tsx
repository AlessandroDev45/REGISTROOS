import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

// Tipos de erro de validação
export interface ValidationError {
    field: string;
    message: string;
}

// Opções de validação
export interface ValidationOptions {
    required?: boolean;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    custom?: (value: any) => boolean | string;
    email?: boolean;
    numeric?: boolean;
    minValue?: number;
    maxValue?: number;
}

// Schema de validação
export interface ValidationSchema {
    [key: string]: ValidationOptions | ValidationOptions[];
}

// Hook de validação
export const useValidation = (initialValues: any, schema: ValidationSchema) => {
    const [values, setValues] = useState(initialValues);
    const [errors, setErrors] = useState<ValidationError[]>([]);
    const [touched, setTouched] = useState<{ [key: string]: boolean }>({});
    const [isValid, setIsValid] = useState(false);

    // Validar um campo específico
    const validateField = (name: string, value: any): ValidationError | null => {
        const rules = schema[name];
        if (!rules) return null;

        const ruleArray = Array.isArray(rules) ? rules : [rules];

        for (const rule of ruleArray) {
            if (rule.required && (value === undefined || value === null || value === '')) {
                return { field: name, message: `O campo ${name} é obrigatório` };
            }

            if (rule.minLength && value.length < rule.minLength) {
                return { field: name, message: `O campo ${name} deve ter pelo menos ${rule.minLength} caracteres` };
            }

            if (rule.maxLength && value.length > rule.maxLength) {
                return { field: name, message: `O campo ${name} deve ter no máximo ${rule.maxLength} caracteres` };
            }

            if (rule.pattern && !rule.pattern.test(value)) {
                return { field: name, message: `O campo ${name} não está no formato correto` };
            }

            if (rule.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                return { field: name, message: `Por favor, insira um e-mail válido` };
            }

            if (rule.numeric && isNaN(Number(value))) {
                return { field: name, message: `O campo ${name} deve ser um número` };
            }

            if (rule.minValue !== undefined && Number(value) < rule.minValue) {
                return { field: name, message: `O campo ${name} deve ser no mínimo ${rule.minValue}` };
            }

            if (rule.maxValue !== undefined && Number(value) > rule.maxValue) {
                return { field: name, message: `O campo ${name} deve ser no máximo ${rule.maxValue}` };
            }

            if (rule.custom) {
                const customResult = rule.custom(value);
                if (customResult !== true) {
                    const message = typeof customResult === 'string' ? customResult : `O campo ${name} é inválido`;
                    return { field: name, message };
                }
            }
        }

        return null;
    };

    // Validar todos os campos
    const validateAll = (): boolean => {
        const newErrors: ValidationError[] = [];
        let isValid = true;

        Object.keys(schema).forEach(key => {
            const error = validateField(key, values[key]);
            if (error) {
                newErrors.push(error);
                isValid = false;
            }
        });

        setErrors(newErrors);
        return isValid;
    };

    // Atualizar valor e validar
    const handleChange = (name: string, value: any) => {
        setValues((prev: any) => ({ ...prev, [name]: value }));
        setTouched((prev: any) => ({ ...prev, [name]: true }));

        const error = validateField(name, value);
        if (error) {
            setErrors((prev: ValidationError[]) => [...prev.filter(e => e.field !== name), error]);
        } else {
            setErrors((prev: ValidationError[]) => prev.filter(e => e.field !== name));
        }
    };

    // Marcar campo como tocado
    const handleBlur = (name: string) => {
        setTouched((prev: any) => ({ ...prev, [name]: true }));
        const error = validateField(name, values[name]);
        if (error) {
            setErrors((prev: ValidationError[]) => [...prev.filter(e => e.field !== name), error]);
        } else {
            setErrors((prev: ValidationError[]) => prev.filter(e => e.field !== name));
        }
    };

    // Resetar validação
    const reset = () => {
        setValues(initialValues);
        setErrors([]);
        setTouched({});
        setIsValid(false);
    };

    // Verificar se o formulário é válido
    useEffect(() => {
        const formIsValid = validateAll();
        setIsValid(formIsValid);
    }, [values]);

    // Verificar se um campo foi tocado e tem erro
    const getFieldError = (name: string): string | null => {
        if (!touched[name]) return null;
        const error = errors.find(e => e.field === name);
        return error ? error.message : null;
    };

    return {
        values,
        errors,
        touched,
        isValid,
        handleChange,
        handleBlur,
        validateField,
        validateAll,
        reset,
        getFieldError
    };
};

// Validadores comuns
export const commonValidators = {
    required: (): ValidationOptions => ({ required: true }),
    email: (): ValidationOptions => ({ email: true }),
    minLength: (length: number): ValidationOptions => ({ minLength: length }),
    maxLength: (length: number): ValidationOptions => ({ maxLength: length }),
    pattern: (regex: RegExp): ValidationOptions => ({ pattern: regex }),
    numeric: (): ValidationOptions => ({ numeric: true }),
    minValue: (value: number): ValidationOptions => ({ minValue: value }),
    maxValue: (value: number): ValidationOptions => ({ maxValue: value }),
    custom: (validator: (value: any) => boolean | string): ValidationOptions => ({ custom: validator })
};

// Schemas de validação pré-definidos
export const validationSchemas = {
    setor: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        departamento: [
            commonValidators.required()
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    },
    tipoMaquina: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        departamento: [
            commonValidators.required()
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    },
    tipoTeste: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    },
    tipoAtividade: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    },
    descricaoAtividade: {
        descricao: [
            commonValidators.required(),
            commonValidators.minLength(10),
            commonValidators.maxLength(500)
        ]
    },
    tipoFalha: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    },
    causaRetrabalho: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    },
    fullSector: {
        nome: [
            commonValidators.required(),
            commonValidators.minLength(3),
            commonValidators.maxLength(100)
        ],
        departamento: [
            commonValidators.required()
        ],
        descricao: [
            commonValidators.maxLength(500)
        ]
    }
};

// Componente de erro de formulário
export const FormError: React.FC<{ message?: string }> = ({ message }) => {
    if (!message) return null;

    return (
        <p className="mt-1 text-sm text-red-600">{message}</p>
    );
};

// Hook para validassync
export const useAsyncValidation = () => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);

    const validateAndSubmit = async (
        validationFn: () => boolean,
        submitFn: () => Promise<void>,
        errorFn?: (error: any) => void
    ) => {
        setIsSubmitting(true);
        setSubmitError(null);

        try {
            const isValid = validationFn();
            if (!isValid) {
                toast.error('Por favor, corrija os erros no formulário antes de enviar');
                return;
            }

            await submitFn();
            toast.success('Operação realizada com sucesso!');
        } catch (error) {
            console.error('Validation or submission error:', error);
            setSubmitError('Ocorreu um erro durante a operação');
            
            if (errorFn) {
                errorFn(error);
            } else {
                toast.error('Ocorreu um erro durante a operação');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return {
        isSubmitting,
        submitError,
        validateAndSubmit
    };
};
