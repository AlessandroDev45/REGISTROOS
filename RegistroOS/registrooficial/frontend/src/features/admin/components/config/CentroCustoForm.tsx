import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { CentroCustoData, DepartamentoData, departamentoService } from '../../../../services/adminApi';

interface CentroCustoFormErrors {
    nome?: string;
    descricao?: string;
}

interface CentroCustoFormProps {
    initialData?: Partial<CentroCustoData>;
    onCancel: () => void;
    onSubmit: (data: CentroCustoData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const CentroCustoForm: React.FC<CentroCustoFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false,
}) => {
    const [formData, setFormData] = useState<CentroCustoData>({
        nome: '',
        descricao: '',
        ativo: true,
        ...initialData,
    });
    const [errors, setErrors] = useState<CentroCustoFormErrors>({});
    const [hasSubmitted, setHasSubmitted] = useState(false); // ADICIONADO: Controla se já tentou submeter

    useEffect(() => {
        setFormData({
            nome: '',
            descricao: '',
            ativo: true,
            ...initialData,
        });
        setErrors({});
    }, [initialData]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
        }));
        // Clear error when user starts typing
        if (errors[name as keyof CentroCustoFormErrors]) {
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: CentroCustoFormErrors = {};

        if (!formData.nome.trim()) {
            newErrors.nome = 'Nome do departamento é obrigatório';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setHasSubmitted(true); // ADICIONADO: Marca que tentou submeter
        if (validateForm()) {
            onSubmit(formData, isEdit);
        }
    };

    return (
        <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
            <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-800">
                    {isEdit ? 'Editar Departamento' : 'Adicionar Novo Departamento'}
                </h2>
                <div className="mt-2 border-b border-gray-200"></div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Nome */}
                    <div>
                        <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                            Nome do Departamento <span className="text-red-500">*</span>
                        </label>
                        <StyledInput
                            id="nome"
                            name="nome"
                            type="text"
                            value={formData.nome}
                            onChange={handleInputChange}
                            placeholder="Ex: MOTORES, TRANSFORMADORES"
                            className={errors.nome ? 'border-red-500' : ''}
                        />
                        {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
                    </div>
                </div>

                {/* Descrição */}
                <div>
                    <label htmlFor="descricao" className="block text-sm font-medium text-gray-700">
                        Descrição
                    </label>
                    <textarea
                        id="descricao"
                        name="descricao"
                        rows={3}
                        value={formData.descricao || ''}
                        onChange={handleInputChange}
                        placeholder="Descrição detalhada do centro de custo..."
                        className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${errors.descricao ? 'border-red-500' : ''}`}
                    />
                    {errors.descricao && <p className="mt-1 text-sm text-red-600">{errors.descricao}</p>}
                </div>

                {/* Status Ativo */}
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
                        Centro de custo ativo
                    </label>
                </div>

                {/* Botões */}
                <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                    <button
                        type="button"
                        onClick={onCancel}
                        className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        {isEdit ? 'Atualizar' : 'Criar'} Centro de Custo
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CentroCustoForm;
