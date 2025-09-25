// frontend/src/features/admin/components/config/DepartamentoForm.tsx
import React, { useState, useEffect } from 'react';
import { StyledInput } from '../../../../components/UIComponents'; // Assuming StyledInput exists
import { DepartamentoData } from '../../../../services/adminApi';

interface DepartamentoFormData {
    nome_tipo: string; // Campo correto da DB
    descricao: string;
    ativo: boolean;
}

interface DepartamentoFormErrors {
    nome_tipo?: string;
    descricao?: string;
}

interface DepartamentoFormProps {
    initialData?: Partial<DepartamentoFormData>;
    onCancel: () => void;
    onSubmit: (data: DepartamentoFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const DepartamentoForm: React.FC<DepartamentoFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false,
}) => {
    const [formData, setFormData] = useState<DepartamentoFormData>({
        nome_tipo: initialData?.nome_tipo || '',
        descricao: initialData?.descricao || '',
        ativo: initialData?.ativo ?? true,
    });
    const [errors, setErrors] = useState<DepartamentoFormErrors>({});

    useEffect(() => {
        setFormData({
            nome_tipo: initialData?.nome_tipo || '',
            descricao: initialData?.descricao || '',
            ativo: initialData?.ativo ?? true,
        });
        setErrors({});
    }, [initialData]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));

        if (errors[name as keyof DepartamentoFormErrors]) {
            setErrors((prev) => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: DepartamentoFormErrors = {};
        if (!formData.nome_tipo.trim()) {
            newErrors.nome_tipo = 'Nome do departamento é obrigatório';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validateForm()) {
            onSubmit(formData, isEdit);
        }
    };

    return (
        <div className="mt-6">
            <div className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {isEdit ? 'Editar Departamento' : 'Adicionar Novo Departamento'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                        Nome do Departamento *
                    </label>
                    <StyledInput
                        id="nome_tipo"
                        name="nome_tipo"
                        value={formData.nome_tipo}
                        onChange={handleInputChange}
                        placeholder="Ex: MOTORES"
                        error={errors.nome_tipo}
                        required
                    />
                    {errors.nome_tipo && <p className="mt-1 text-sm text-red-600">{errors.nome_tipo}</p>}
                </div>

                <div>
                    <label htmlFor="descricao" className="block text-sm font-medium text-gray-700">
                        Descrição
                    </label>
                    <textarea
                        id="descricao"
                        name="descricao"
                        value={formData.descricao}
                        onChange={handleInputChange}
                        placeholder="Descrição do departamento (opcional)"
                        rows={3}
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                    />
                </div>

                <div className="flex items-center">
                    <input
                        id="ativo"
                        name="ativo"
                        type="checkbox"
                        checked={formData.ativo}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="ativo" className="ml-2 block text-sm text-gray-900">
                        Departamento ativo
                    </label>
                </div>

                <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-6 py-3 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors duration-200"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isEdit ? 'Confirmar Edição' : 'Adicionar Departamento'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default DepartamentoForm;