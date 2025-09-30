import React, { useState, useEffect } from 'react';
import { useClickOutside } from '../../../../hooks/useClickOutside';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { CausaRetrabalhoData, departamentoService, setorService } from '../../../../services/adminApi';

import { useGenericForm } from '../../../../hooks/useGenericForm';
// Update interface to match backend API payload and form fields
interface CausaRetrabalhoFormData {
    codigo: string;
    descricao: string;
    departamento: string; // Backend expects this string for mapping to id_departamento
    setor: string;
    ativo: boolean;
}

// Update errors interface
interface CausaRetrabalhoFormErrors {
    codigo?: string;
    descricao?: string;
    departamento?: string;
    setor?: string;
}

interface CausaRetrabalhoFormProps {
    initialData?: Partial<CausaRetrabalhoFormData>; // Use updated FormData
    onCancel: () => void;
    onSubmit: (data: CausaRetrabalhoFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const CausaRetrabalhoForm: React.FC<CausaRetrabalhoFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false
}) => {
    const [formData, setFormData] = useState<CausaRetrabalhoFormData>({
        codigo: initialData?.codigo || '',
        descricao: initialData?.descricao || '',
        departamento: initialData?.departamento || 'MOTORES',
        setor: initialData?.setor || '',
        ativo: initialData?.ativo ?? true,
    });
    const [errors, setErrors] = useState<CausaRetrabalhoFormErrors>({});
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<any[]>([]);

    // Hook para fechar ao clicar fora
    const formRef = useClickOutside<HTMLDivElement>(onCancel);

    // Atualizar formulário quando initialData muda (para edição)
    useEffect(() => {
        if (initialData && isEdit) {
            setFormData({
                codigo: initialData?.codigo || '',
                descricao: initialData?.descricao || '',
                departamento: initialData?.departamento || 'MOTORES',
                setor: initialData?.setor || '',
                ativo: initialData?.ativo ?? true,
            });
            setErrors({});
        }
    }, [initialData, isEdit]);

    useEffect(() => {
        const fetchDepartamentos = async () => {
            try {
                console.log("CausaRetrabalhoForm: Buscando departamentos...");
                const data = await departamentoService.getDepartamentos();
                console.log("CausaRetrabalhoForm: Departamentos recebidos:", data);
                setDepartamentos(data);
            } catch (error) {
                console.error("CausaRetrabalhoForm: Error fetching departments:", error);
            }
        };
        fetchDepartamentos();

        setFormData({
            codigo: initialData?.codigo || '',
            descricao: initialData?.descricao || '',
            departamento: initialData?.departamento || 'MOTORES',
            setor: initialData?.setor || '',
            ativo: initialData?.ativo ?? true,
        });
        setErrors({});
    }, [initialData, isEdit]);

    // Carregar setores quando departamento mudar
    useEffect(() => {
        const fetchSetores = async () => {
            if (formData.departamento) {
                try {
                    console.log("CausaRetrabalhoForm: Buscando setores para departamento:", formData.departamento);
                    const data = await setorService.getSetores();
                    console.log("CausaRetrabalhoForm: Todos os setores:", data);
                    const setoresFiltrados = data.filter(setor => {
                        const setorDept = setor.departamento?.trim();
                        const formDept = formData.departamento?.trim();
                        console.log(`CausaRetrabalhoForm: Comparando "${setorDept}" com "${formDept}"`);
                        return setorDept === formDept;
                    });
                    console.log("CausaRetrabalhoForm: Setores filtrados:", setoresFiltrados);
                    setSetores(setoresFiltrados);
                } catch (error) {
                    console.error("CausaRetrabalhoForm: Error fetching setores:", error);
                    setSetores([]);
                }
            } else {
                console.log("CausaRetrabalhoForm: Nenhum departamento selecionado, limpando setores");
                setSetores([]);
            }
        };
        fetchSetores();
    }, [formData.departamento]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
            // Reset setor quando departamento mudar
            ...(name === 'departamento' && { setor: '' })
        }));

        if (errors[name as keyof CausaRetrabalhoFormErrors]) { // Use updated errors interface
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: CausaRetrabalhoFormErrors = {}; // Use updated errors interface

        if (!formData.codigo.trim()) {
            newErrors.codigo = 'Código da causa de retrabalho é obrigatório';
        }
        if (!formData.descricao.trim()) {
            newErrors.descricao = 'Descrição da causa de retrabalho é obrigatória';
        }
        if (!formData.departamento) {
            newErrors.departamento = 'Departamento é obrigatório';
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
            <div ref={formRef} className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {isEdit ? 'Editar Causa de Retrabalho' : 'Adicionar Nova Causa de Retrabalho'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                <div className="mb-4">
                    <StyledInput
                        id="codigo"
                        name="codigo"
                        value={formData.codigo}
                        onChange={handleInputChange}
                        placeholder="Código da causa de retrabalho"
                        error={errors.codigo}
                        required
                    />
                </div>

                {/* Departamento e Setor */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <SelectField
                        id="departamento"
                        name="departamento"
                        value={formData.departamento}
                        onChange={handleInputChange}
                        label="Departamento *"
                        error={errors.departamento}
                        required
                    >
                        <option value="">Selecione um departamento</option>
                        {departamentos.map((dept) => (
                            <option key={dept.id} value={dept.nome_tipo}>
                                {dept.nome_tipo}
                            </option>
                        ))}
                    </SelectField>

                    <SelectField
                        id="setor"
                        name="setor"
                        value={formData.setor}
                        onChange={handleInputChange}
                        label="Setor"
                        className="mt-1 block w-full"
                    >
                        <option value="">Selecione um setor</option>
                        {setores.map((setor) => (
                            <option key={setor.id} value={setor.nome}>
                                {setor.nome}
                            </option>
                        ))}
                    </SelectField>
                </div>

                {/* Descrição */}
                <div>
                    <label htmlFor="descricao" className="block text-sm font-medium text-gray-700">
                        Descrição *
                    </label>
                    <textarea
                        id="descricao"
                        name="descricao"
                        value={formData.descricao}
                        onChange={handleInputChange}
                        placeholder="Descrição detalhada da causa de retrabalho"
                        rows={3}
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                    />
                    {errors.descricao && <p className="mt-1 text-sm text-red-600">{errors.descricao}</p>}
                </div>

                {/* Second Row: Ativo checkbox */}
                <div className="grid grid-cols-1 gap-6">
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
                            Causa de retrabalho ativa
                        </label>
                    </div>
                </div>

                {/* Buttons Area - Right Aligned */}
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
                        disabled={!formData.codigo?.trim()}
                        className={`px-6 py-3 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 ${
                            formData.codigo?.trim()
                                ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                    >
                        {isEdit ? 'Confirmar Edição' : 'Adicionar'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default CausaRetrabalhoForm;