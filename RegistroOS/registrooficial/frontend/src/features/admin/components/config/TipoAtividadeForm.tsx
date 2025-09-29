import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { AtividadeTipoData, departamentoService, setorService } from '../../../../services/adminApi'; // Import AtividadeTipoData

// Update interface to match backend API payload and form fields
interface TipoAtividadeFormData {
    nome_tipo: string;
    descricao: string;
    departamento: string;
    setor: string;
    categoria: string;
    ativo: boolean;
}

// Update errors interface
interface TipoAtividadeFormErrors {
    nome_tipo?: string;
    descricao?: string;
    departamento?: string;
    setor?: string;
    categoria?: string;
}

interface TipoAtividadeFormProps {
    initialData?: Partial<TipoAtividadeFormData>; // Use updated FormData
    onCancel: () => void;
    onSubmit: (data: TipoAtividadeFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const TipoAtividadeForm: React.FC<TipoAtividadeFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false
}) => {
    const [formData, setFormData] = useState<TipoAtividadeFormData>({
        nome_tipo: initialData?.nome_tipo || '',
        descricao: initialData?.descricao || '',
        departamento: initialData?.departamento || 'MOTORES',
        setor: initialData?.setor || '',
        categoria: initialData?.categoria || '',
        ativo: initialData?.ativo ?? true,
    });
    const [errors, setErrors] = useState<TipoAtividadeFormErrors>({}); // Use updated errors interface
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<any[]>([]);
    const [categorias, setCategorias] = useState<string[]>([]);


    useEffect(() => {
        setFormData({
            nome_tipo: initialData?.nome_tipo || '',
            descricao: initialData?.descricao || '',
            departamento: initialData?.departamento || 'MOTORES',
            setor: initialData?.setor || '',
            categoria: initialData?.categoria || '',
            ativo: initialData?.ativo ?? true,
        });
        setErrors({});
    }, [initialData]);

    // Carregar dados para filtros
    useEffect(() => {
        const loadFilterData = async () => {
            try {
                console.log("TipoAtividadeForm: Carregando dados dos filtros...");
                const [deptData, setorData] = await Promise.all([
                    departamentoService.getDepartamentos(),
                    setorService.getSetores()
                ]);
                console.log("TipoAtividadeForm: Departamentos:", deptData);
                console.log("TipoAtividadeForm: Setores:", setorData);
                setDepartamentos(deptData);
                setSetores(setorData);
                // Usar categorias fixas
                setCategorias(['MOTOR', 'TRANSFORMADOR', 'GERADOR', 'OUTROS']);
                console.log("TipoAtividadeForm: Categorias definidas:", ['MOTOR', 'TRANSFORMADOR', 'GERADOR', 'OUTROS']);
            } catch (error) {
                console.error('TipoAtividadeForm: Erro ao carregar dados dos filtros:', error);
                // Fallback para categorias padrão em caso de erro
                setCategorias(['MOTOR', 'TRANSFORMADOR', 'GERADOR', 'OUTROS']);
            }
        };
        loadFilterData();
    }, []);

    // Filtrar setores baseado no departamento selecionado
    const setoresFiltrados = formData.departamento
        ? setores.filter(setor => {
            const setorDept = setor.departamento?.trim();
            const formDept = formData.departamento?.trim();
            console.log(`TipoAtividadeForm: Comparando "${setorDept}" com "${formDept}"`);
            return setorDept === formDept;
        })
        : setores;

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        if (errors[name as keyof TipoAtividadeFormErrors]) { // Use updated errors interface
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: TipoAtividadeFormErrors = {}; // Use updated errors interface

        if (!formData.nome_tipo.trim()) {
            newErrors.nome_tipo = 'Nome do tipo de atividade é obrigatório';
        }
        if (!formData.descricao.trim()) {
            newErrors.descricao = 'Descrição do tipo de atividade é obrigatória';
        }
        if (!formData.departamento) {
            newErrors.departamento = 'Departamento é obrigatório';
        }
        if (!formData.setor) {
            newErrors.setor = 'Setor é obrigatório';
        }
        if (!formData.categoria.trim()) {
            newErrors.categoria = 'Categoria é obrigatória';
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
                        {isEdit ? 'Editar Tipo de Atividade' : 'Adicionar Novo Tipo de Atividade'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                {/* Nome do Tipo de Atividade */}
                <div>
                    <label htmlFor="nome_tipo" className="block text-sm font-medium text-gray-700">
                        Nome do Tipo de Atividade *
                    </label>
                    <StyledInput
                        id="nome_tipo"
                        name="nome_tipo"
                        value={formData.nome_tipo}
                        onChange={handleInputChange}
                        placeholder="Nome do tipo de atividade"
                        error={errors.nome_tipo}
                        required
                    />
                    {errors.nome_tipo && <p className="mt-1 text-sm text-red-600">{errors.nome_tipo}</p>}
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
                        placeholder="Descrição detalhada do tipo de atividade"
                        rows={3}
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                    />
                    {errors.descricao && <p className="mt-1 text-sm text-red-600">{errors.descricao}</p>}
                </div>

                {/* Departamento e Setor */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <SelectField
                        id="departamento"
                        name="departamento"
                        value={formData.departamento}
                        onChange={(e) => {
                            handleInputChange(e);
                            // Reset setor quando departamento muda
                            setFormData(prev => ({ ...prev, setor: '' }));
                        }}
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
                        label="Setor *"
                        error={errors.setor}
                        required
                        disabled={!formData.departamento}
                    >
                        <option value="">Selecione um setor</option>
                        {setoresFiltrados.map((setor) => (
                            <option key={setor.id} value={setor.nome}>
                                {setor.nome}
                            </option>
                        ))}
                    </SelectField>
                </div>

                {/* Categoria */}
                <div>
                    <label htmlFor="categoria" className="block text-sm font-medium text-gray-700">
                        🎯 Categoria *
                    </label>
                    <p className="text-xs text-gray-500 mb-2">
                        Selecione a categoria da máquina para esta atividade
                    </p>
                    <select
                        id="categoria"
                        name="categoria"
                        value={formData.categoria}
                        onChange={handleInputChange}
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                        required
                    >
                        <option value="">Selecione uma categoria</option>
                        {categorias.map((categoria) => (
                            <option key={categoria} value={categoria}>
                                {categoria}
                            </option>
                        ))}
                    </select>
                    {errors.categoria && <p className="mt-1 text-sm text-red-600">{errors.categoria}</p>}
                </div>

                {/* Ativo checkbox */}
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
                            Tipo de atividade ativo
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
                        className="px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isEdit ? 'Confirmar Edição' : 'Adicionar Tipo de Atividade'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default TipoAtividadeForm;