import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { DescricaoAtividadeData, departamentoService, setorService, categoriaService } from '../../../../services/adminApi';
import api from '../../../../services/api';

// Interface para os dados da Descrição de Atividade (matches backend `CatalogoAtividadeDescricao`)
interface DescricaoAtividadeFormData {
    codigo: string;
    descricao: string;
    setor: string;
    departamento: string;
    categoria: string;
    ativo: boolean;
}

// Tipo para erros
interface DescricaoAtividadeFormErrors {
    codigo?: string;
    descricao?: string;
    setor?: string;
    categoria?: string;
}

interface DescricaoAtividadeFormProps {
    initialData?: Partial<DescricaoAtividadeFormData>;
    onCancel: () => void;
    onSubmit: (data: DescricaoAtividadeFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const DescricaoAtividadeForm: React.FC<DescricaoAtividadeFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false,
}) => {
    const [formData, setFormData] = useState<DescricaoAtividadeFormData>({
        codigo: initialData?.codigo || '',
        descricao: initialData?.descricao || '',
        setor: initialData?.setor || '',
        departamento: initialData?.departamento || 'MOTORES',
        categoria: initialData?.categoria || '',
        ativo: initialData?.ativo ?? true,
    });
    const [errors, setErrors] = useState<DescricaoAtividadeFormErrors>({});
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<any[]>([]);
    const [categoriasMaquina, setCategoriasMaquina] = useState<string[]>([]);

    // Função para carregar categorias de máquina
    const loadCategoriasMaquina = async () => {
        try {
            // Usar o novo endpoint de categorias
            const categorias = await categoriaService.getCategoriasMaquina();
            setCategoriasMaquina(categorias.length > 0 ? categorias : ['MOTOR', 'GERADOR', 'TRANSFORMADOR']);
        } catch (error) {
            console.error('Erro ao carregar categorias de máquina:', error);
            setCategoriasMaquina(['MOTOR', 'GERADOR', 'TRANSFORMADOR', 'BOMBA', 'COMPRESSOR', 'VENTILADOR']);
        }
    };

    // Carregar dados iniciais apenas uma vez
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                console.log("DescricaoAtividadeForm: Buscando dados iniciais...");
                const data = await departamentoService.getDepartamentos();
                console.log("DescricaoAtividadeForm: Departamentos recebidos:", data);
                setDepartamentos(data);
            } catch (error) {
                console.error("DescricaoAtividadeForm: Error fetching departments:", error);
            }
        };
        fetchInitialData();
        loadCategoriasMaquina();
    }, []);

    // Resetar formulário apenas quando initialData muda (para edição)
    useEffect(() => {
        if (isEdit && initialData) {
            setFormData({
                codigo: initialData?.codigo || '',
                descricao: initialData?.descricao || '',
                setor: initialData?.setor || '',
                departamento: initialData?.departamento || 'MOTORES',
                categoria: initialData?.categoria || '',
                ativo: initialData?.ativo ?? true,
            });
            setErrors({});
        }
    }, [initialData, isEdit]);

    // Carregar setores quando departamento mudar
    useEffect(() => {
        const fetchSetores = async () => {
            if (formData.departamento) {
                try {
                    console.log("DescricaoAtividadeForm: Buscando setores para departamento:", formData.departamento);
                    const data = await setorService.getSetores();
                    console.log("DescricaoAtividadeForm: Todos os setores:", data);
                    const setoresFiltrados = data.filter(setor => {
                        const setorDept = setor.departamento?.trim();
                        const formDept = formData.departamento?.trim();
                        console.log(`DescricaoAtividadeForm: Comparando "${setorDept}" com "${formDept}"`);
                        return setorDept === formDept;
                    });
                    console.log("DescricaoAtividadeForm: Setores filtrados:", setoresFiltrados);
                    setSetores(setoresFiltrados);
                } catch (error) {
                    console.error("DescricaoAtividadeForm: Error fetching setores:", error);
                    setSetores([]);
                }
            } else {
                setSetores([]);
            }
        };
        fetchSetores();
    }, [formData.departamento]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
        }));

        if (errors[name as keyof DescricaoAtividadeFormErrors]) {
            setErrors((prev) => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: DescricaoAtividadeFormErrors = {};
        if (!formData.codigo.trim()) {
            newErrors.codigo = 'Código da descrição é obrigatório';
        }
        if (!formData.descricao.trim()) {
            newErrors.descricao = 'Descrição é obrigatória';
        }
        if (!formData.setor.trim()) {
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
                        {isEdit ? 'Editar Descrição de Atividade' : 'Adicionar Nova Descrição de Atividade'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="codigo" className="block text-sm font-medium text-gray-700">
                        Código *
                    </label>
                    <StyledInput
                        id="codigo"
                        name="codigo"
                        value={formData.codigo}
                        onChange={handleInputChange}
                        placeholder="Ex: MONTAGEM-001"
                        error={errors.codigo}
                        required
                    />
                    {errors.codigo && <p className="mt-1 text-sm text-red-600">{errors.codigo}</p>}
                </div>

                <div>
                    <label htmlFor="descricao" className="block text-sm font-medium text-gray-700">
                        Descrição *
                    </label>
                    <textarea
                        id="descricao"
                        name="descricao"
                        value={formData.descricao}
                        onChange={handleInputChange}
                        placeholder="Descrição detalhada da atividade"
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
                        onChange={handleInputChange}
                        label="Departamento"
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
                    >
                        <option value="">Selecione um setor</option>
                        {setores.map((setor) => (
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
                        Selecione a categoria da máquina para esta descrição
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
                        {categoriasMaquina.map((categoria) => (
                            <option key={categoria} value={categoria}>
                                {categoria}
                            </option>
                        ))}
                    </select>
                    {errors.categoria && <p className="mt-1 text-sm text-red-600">{errors.categoria}</p>}
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
                        Descrição ativa
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
                        {isEdit ? 'Confirmar Edição' : 'Adicionar Descrição'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default DescricaoAtividadeForm;