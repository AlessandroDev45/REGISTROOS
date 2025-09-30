// frontend/src/features/admin/components/config/DepartamentoForm.tsx
import React, { useState, useEffect } from 'react';
import { StyledInput } from '../../../../components/UIComponents';
import { useClickOutside } from '../../../../hooks/useClickOutside'; // Assuming StyledInput exists
import { DepartamentoData } from '../../../../services/adminApi';

interface DepartamentoFormData {
    nome: string; // Frontend usa 'nome', backend recebe via alias
    descricao: string;
    ativo: boolean;
}

interface DepartamentoFormErrors {
    nome?: string;
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
        nome: initialData?.nome || '',
        descricao: initialData?.descricao || '',
        ativo: initialData?.ativo ?? true,
    });
    const [errors, setErrors] = useState<DepartamentoFormErrors>({});
    const formRef = useClickOutside<HTMLDivElement>(onCancel);

    useEffect(() => {
        // Só atualizar se initialData mudou e não é null/undefined
        if (initialData !== undefined) {
            const newFormData = {
                nome: initialData?.nome || '',
                descricao: initialData?.descricao || '',
                ativo: initialData?.ativo ?? true,
            };
            console.log('🏢 [DEPARTAMENTO FORM] useEffect - initialData:', initialData);
            console.log('🏢 [DEPARTAMENTO FORM] useEffect - newFormData:', newFormData);
            setFormData(newFormData);
            setErrors({});
        }
    }, [initialData]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        console.log('🏢 [DEPARTAMENTO FORM] Input change:', { name, value, type, checked });

        setFormData((prev) => {
            const newData = {
                ...prev,
                [name]: type === 'checkbox' ? checked : value,
            };
            console.log('🏢 [DEPARTAMENTO FORM] FormData atualizado:', newData);
            return newData;
        });

        if (errors[name as keyof DepartamentoFormErrors]) {
            setErrors((prev) => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        console.log('🏢 [DEPARTAMENTO FORM] Validando form:', formData);
        const newErrors: DepartamentoFormErrors = {};
        if (!formData.nome.trim()) {
            console.log('🏢 [DEPARTAMENTO FORM] Erro: nome vazio');
            newErrors.nome = 'Nome do departamento é obrigatório';
        } else {
            console.log('🏢 [DEPARTAMENTO FORM] Nome OK:', formData.nome);
        }
        setErrors(newErrors);
        const isValid = Object.keys(newErrors).length === 0;
        console.log('🏢 [DEPARTAMENTO FORM] Validação resultado:', { isValid, errors: newErrors });
        return isValid;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('🏢 [DEPARTAMENTO FORM] Submit chamado:', { formData, isEdit });
        if (validateForm()) {
            // Mapear 'nome' para 'nome_tipo' que o backend espera
            const dataToSubmit = {
                nome_tipo: formData.nome,  // Backend espera nome_tipo
                nome: formData.nome,       // Manter nome também para compatibilidade
                descricao: formData.descricao,
                ativo: formData.ativo
            };
            console.log('🏢 [DEPARTAMENTO FORM] Validação OK, enviando dados:', dataToSubmit);
            onSubmit(dataToSubmit, isEdit);
        } else {
            console.log('🏢 [DEPARTAMENTO FORM] Validação falhou');
        }
    };

    return (
        <div className="mt-6">
            <div ref={formRef} className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {isEdit ? 'Editar Departamento' : 'Adicionar Novo Departamento'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="nome" className="block text-sm font-medium text-gray-700 mb-2">
                        Nome do Departamento *
                    </label>
                    <input
                        type="text"
                        id="nome"
                        name="nome"
                        value={formData.nome}
                        onChange={handleInputChange}
                        placeholder="Ex: MOTORES"
                        required
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
                            errors.nome
                                ? 'border-red-500 focus:ring-red-500'
                                : formData.nome.trim()
                                    ? 'border-green-500 focus:ring-green-500'
                                    : 'border-gray-300 focus:ring-blue-500'
                        }`}
                    />
                    {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
                    {!errors.nome && !formData.nome.trim() && (
                        <p className="mt-1 text-sm text-gray-500">Digite o nome do departamento para habilitar o botão</p>
                    )}
                    {!errors.nome && formData.nome.trim() && (
                        <p className="mt-1 text-sm text-green-600">✓ Nome válido</p>
                    )}
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
                        disabled={!formData.nome.trim()}
                        onClick={(e) => {
                            console.log('🏢 [DEPARTAMENTO FORM] Botão submit clicado, formData atual:', formData);
                            if (!formData.nome.trim()) {
                                e.preventDefault();
                                console.log('🏢 [DEPARTAMENTO FORM] Botão desabilitado - campo vazio');
                                return;
                            }
                        }}
                        className={`px-6 py-3 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 ${
                            formData.nome.trim()
                                ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
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