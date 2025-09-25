import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents'; // Assuming StyledInput and SelectField exist
import { TipoTesteData, DepartamentoData, TipoMaquinaData, departamentoService, setorService, tipoMaquinaService } from '../../../../services/adminApi'; // Import DepartamentoData and service

// Interface para os dados do TipoTeste (matches backend `TipoTeste`)
interface TipoTesteFormData {
    nome: string;
    departamento: string;
    setor: string;
    tipo_teste: string;
    descricao: string;
    ativo: boolean;
    tipo_maquina?: string;
    teste_exclusivo_setor?: boolean;
    descricao_teste_exclusivo?: string;
    categoria?: string;  // Novo campo categoria
    subcategoria?: number;  // Novo campo subcategoria
}

// Tipo para erros
interface TipoTesteFormErrors {
    nome?: string;
    departamento?: string;
    setor?: string;
    tipo_teste?: string;
    descricao?: string;
    tipo_maquina?: string;
    descricao_teste_exclusivo?: string;
    categoria?: string;
    subcategoria?: string;
}

interface TipoTesteFormProps {
    initialData?: Partial<TipoTesteFormData>;
    onCancel: () => void;
    onSubmit: (data: TipoTesteFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const TipoTesteForm: React.FC<TipoTesteFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false,
}) => {
    const [formData, setFormData] = useState<TipoTesteFormData>({
        nome: initialData?.nome || '',
        departamento: initialData?.departamento || 'MOTORES', // Default to MOTORES
        setor: initialData?.setor || '',
        tipo_teste: initialData?.tipo_teste || '',
        descricao: initialData?.descricao || '',
        ativo: initialData?.ativo ?? true,
        tipo_maquina: initialData?.tipo_maquina || '',
        teste_exclusivo_setor: initialData?.teste_exclusivo_setor ?? false,
        descricao_teste_exclusivo: initialData?.descricao_teste_exclusivo || '',
        categoria: initialData?.categoria || 'Visual', // Default to Visual
        subcategoria: initialData?.subcategoria ?? 0, // Default to 0 (Padrão)
    });
    const [errors, setErrors] = useState<TipoTesteFormErrors>({});
    const [departamentos, setDepartamentos] = useState<DepartamentoData[]>([]);
    const [setores, setSetores] = useState<any[]>([]);
    const [tiposMaquina, setTiposMaquina] = useState<TipoMaquinaData[]>([]);
    const [tiposTesteValores, setTiposTesteValores] = useState<string[]>([]);
    const [showTipoTesteSuggestions, setShowTipoTesteSuggestions] = useState(false);
    const [filteredTiposTesteSuggestions, setFilteredTiposTesteSuggestions] = useState<string[]>([]);

    // Atualizar formulário quando initialData muda (para edição)
    useEffect(() => {
        if (initialData) {
            setFormData({
                nome: initialData?.nome || '',
                departamento: initialData?.departamento || 'MOTORES',
                setor: initialData?.setor || '',
                tipo_teste: initialData?.tipo_teste || '',
                descricao: initialData?.descricao || '',
                ativo: initialData?.ativo ?? true,
                tipo_maquina: initialData?.tipo_maquina || '',
                teste_exclusivo_setor: initialData?.teste_exclusivo_setor ?? false,
                descricao_teste_exclusivo: initialData?.descricao_teste_exclusivo || '',
                categoria: initialData?.categoria || 'Visual',
                subcategoria: initialData?.subcategoria ?? 0,
            });
            setErrors({});
        }
    }, [initialData]);

    useEffect(() => {
        const fetchDepartamentos = async () => {
            try {
                console.log("TipoTesteForm: Buscando departamentos...");
                const data = await departamentoService.getDepartamentos();
                console.log("TipoTesteForm: Departamentos recebidos:", data);
                console.log("TipoTesteForm: Número de departamentos:", data.length);
                setDepartamentos(data);
            } catch (error) {
                console.error("TipoTesteForm: Error fetching departments:", error);
                // Fallback para departamentos padrão em caso de erro
                setDepartamentos([
                    { id: 1, nome: 'MOTORES', nome_tipo: 'MOTORES' },
                    { id: 2, nome: 'TRANSFORMADORES', nome_tipo: 'TRANSFORMADORES' }
                ]);
            }
        };

        const fetchTiposMaquina = async () => {
            try {
                console.log("TipoTesteForm: Buscando tipos de máquina...");
                const data = await tipoMaquinaService.getTiposMaquina();
                console.log("TipoTesteForm: Tipos de máquina recebidos:", data);
                setTiposMaquina(data);
            } catch (error) {
                console.error("TipoTesteForm: Error fetching tipos de máquina:", error);
                setTiposMaquina([]);
            }
        };

        const fetchTiposTesteValores = async () => {
            try {
                console.log("TipoTesteForm: Buscando valores de tipo_teste...");
                const response = await fetch('/api/tipos-teste-valores', {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });
                const data = await response.json();
                console.log("TipoTesteForm: Valores de tipo_teste carregados:", data);
                setTiposTesteValores(data.valores || []);
            } catch (error) {
                console.error("TipoTesteForm: Erro ao carregar valores de tipo_teste:", error);
            }
        };

        fetchDepartamentos();
        fetchTiposMaquina();
        fetchTiposTesteValores();

        setFormData({
            nome: initialData?.nome || '',
            departamento: initialData?.departamento || 'MOTORES',
            setor: initialData?.setor || '',
            tipo_teste: initialData?.tipo_teste || '',
            descricao: initialData?.descricao || '',
            ativo: initialData?.ativo ?? true,
            tipo_maquina: initialData?.tipo_maquina || '',
            teste_exclusivo_setor: initialData?.teste_exclusivo_setor ?? false,
            descricao_teste_exclusivo: initialData?.descricao_teste_exclusivo || '',
            categoria: initialData?.categoria || 'Visual',
            subcategoria: initialData?.subcategoria ?? 0,
        });
        setErrors({});
    }, [initialData]);

    // Carregar setores quando departamento mudar
    useEffect(() => {
        const fetchSetores = async () => {
            if (formData.departamento) {
                try {
                    console.log("TipoTesteForm: Buscando setores para departamento:", formData.departamento);
                    const data = await setorService.getSetores();
                    console.log("TipoTesteForm: Todos os setores:", data);
                    const setoresFiltrados = data.filter(setor => {
                        const setorDept = setor.departamento?.trim();
                        const formDept = formData.departamento?.trim();
                        console.log(`TipoTesteForm: Comparando "${setorDept}" com "${formDept}"`);
                        return setorDept === formDept;
                    });
                    console.log("TipoTesteForm: Setores filtrados:", setoresFiltrados);
                    setSetores(setoresFiltrados);
                } catch (error) {
                    console.error("TipoTesteForm: Error fetching setores:", error);
                    setSetores([]);
                }
            } else {
                console.log("TipoTesteForm: Nenhum departamento selecionado, limpando setores");
                setSetores([]);
            }
        };
        fetchSetores();
    }, [formData.departamento]);

    // Função para filtrar sugestões de tipo_teste
    const handleTipoTesteChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.toUpperCase();
        setFormData(prev => ({ ...prev, tipo_teste: value }));

        if (value.length > 0) {
            const filtered = tiposTesteValores.filter(tipo =>
                tipo.toUpperCase().includes(value)
            );
            setFilteredTiposTesteSuggestions(filtered);
            setShowTipoTesteSuggestions(filtered.length > 0);
        } else {
            setShowTipoTesteSuggestions(false);
        }
    };

    // Função para selecionar uma sugestão
    const handleTipoTesteSuggestionClick = (valor: string) => {
        setFormData(prev => ({ ...prev, tipo_teste: valor }));
        setShowTipoTesteSuggestions(false);
    };

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value,
            // Reset setor quando departamento mudar
            ...(name === 'departamento' && { setor: '' })
        }));

        if (errors[name as keyof TipoTesteFormErrors]) {
            setErrors((prev) => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: TipoTesteFormErrors = {};
        if (!formData.nome.trim()) {
            newErrors.nome = 'Nome do tipo de teste é obrigatório';
        }
        if (!formData.departamento) {
            newErrors.departamento = 'Departamento é obrigatório';
        }
        if (!formData.setor) {
            newErrors.setor = 'Setor é obrigatório';
        }
        if (!formData.tipo_teste) {
            newErrors.tipo_teste = 'Tipo de teste é obrigatório';
        }

        // Validações para categoria e subcategoria
        if (!formData.categoria) {
            newErrors.categoria = 'Categoria é obrigatória';
        }
        if (formData.subcategoria === undefined || formData.subcategoria === null) {
            newErrors.subcategoria = 'Subcategoria é obrigatória';
        }

        // Validações para teste exclusivo
        if (formData.teste_exclusivo_setor) {
            if (!formData.tipo_maquina?.trim()) {
                newErrors.tipo_maquina = 'Tipo de máquina é obrigatório para testes exclusivos';
            }
            if (!formData.descricao_teste_exclusivo?.trim()) {
                newErrors.descricao_teste_exclusivo = 'Descrição do teste exclusivo é obrigatória';
            }
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

    // Log para debug
    console.log("TipoTesteForm: Renderizando formulário", {
        isEdit,
        formData,
        departamentos: departamentos.length,
        initialData
    });

    return (
        <div className="mt-6">
            <div className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {isEdit ? 'Editar Tipo de Teste' : 'Adicionar Novo Tipo de Teste'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                        Nome do Tipo de Teste *
                    </label>
                    <StyledInput
                        id="nome"
                        name="nome"
                        value={formData.nome}
                        onChange={handleInputChange}
                        placeholder="Ex: Ensaio Elétrico"
                        error={errors.nome}
                        required
                    />
                    {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
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
                        {departamentos.length > 0 ? (
                            departamentos.map(dept => (
                                <option key={dept.id} value={dept.nome_tipo || dept.nome}>
                                    {dept.nome_tipo || dept.nome}
                                </option>
                            ))
                        ) : (
                            <option value="" disabled>Carregando departamentos...</option>
                        )}
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
                        {setores.map(setor => (
                            <option key={setor.id} value={setor.nome}>
                                {setor.nome}
                            </option>
                        ))}
                    </SelectField>
                </div>
                {/* Debug info */}
                {process.env.NODE_ENV === 'development' && (
                    <p className="mt-1 text-xs text-gray-500">
                        Debug: {departamentos.length} departamentos carregados, valor atual: "{formData.departamento}"
                    </p>
                )}
                {errors.departamento && (
                    <p className="mt-1 text-sm text-red-600">{errors.departamento}</p>
                )}

                <div className="relative">
                    <label htmlFor="tipo_teste" className="block text-sm font-medium text-gray-700">
                        Tipo de Teste *
                    </label>
                    <input
                        id="tipo_teste"
                        name="tipo_teste"
                        type="text"
                        value={formData.tipo_teste}
                        onChange={handleTipoTesteChange}
                        onFocus={() => {
                            if (tiposTesteValores.length > 0) {
                                setFilteredTiposTesteSuggestions(tiposTesteValores);
                                setShowTipoTesteSuggestions(true);
                            }
                        }}
                        onBlur={() => {
                            // Delay para permitir clique nas sugestões
                            setTimeout(() => setShowTipoTesteSuggestions(false), 200);
                        }}
                        placeholder="Ex: ESTÁTICO, DINÂMICO, FUNCIONAL..."
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                        style={{ textTransform: 'uppercase' }}
                        required
                    />

                    {/* Dropdown de sugestões */}
                    {showTipoTesteSuggestions && filteredTiposTesteSuggestions.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                            {filteredTiposTesteSuggestions.map((valor, index) => (
                                <div
                                    key={index}
                                    onClick={() => handleTipoTesteSuggestionClick(valor)}
                                    className="px-3 py-2 cursor-pointer hover:bg-blue-50 hover:text-blue-700 border-b border-gray-100 last:border-b-0"
                                >
                                    <span className="font-medium">{valor}</span>
                                </div>
                            ))}
                        </div>
                    )}

                    {errors.tipo_teste && <p className="mt-1 text-sm text-red-600">{errors.tipo_teste}</p>}
                </div>

                <div>
                    <SelectField
                        id="tipo_maquina"
                        name="tipo_maquina"
                        value={formData.tipo_maquina || ''}
                        onChange={handleInputChange}
                        label="Tipo de Máquina"
                        error={errors.tipo_maquina}
                    >
                        <option value="">Selecione um tipo de máquina</option>
                        {tiposMaquina.length > 0 ? (
                            tiposMaquina.map(tipo => (
                                <option key={tipo.id} value={tipo.nome_tipo}>
                                    {tipo.nome_tipo}
                                </option>
                            ))
                        ) : (
                            <option value="" disabled>Carregando tipos de máquina...</option>
                        )}
                    </SelectField>
                    {/* Debug info */}
                    {process.env.NODE_ENV === 'development' && (
                        <p className="mt-1 text-xs text-gray-500">
                            Debug: {tiposMaquina.length} tipos de máquina carregados
                        </p>
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
                        placeholder="Descrição do tipo de teste (opcional)"
                        rows={3}
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                    />
                </div>

                {/* Novos campos de Categoria e Subcategoria */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label htmlFor="categoria" className="block text-sm font-medium text-gray-700">
                            Categoria *
                        </label>
                        <select
                            id="categoria"
                            name="categoria"
                            value={formData.categoria || 'Visual'}
                            onChange={handleInputChange}
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                            required
                        >
                            <option value="Visual">Visual</option>
                            <option value="Elétricos">Elétricos</option>
                            <option value="Mecânicos">Mecânicos</option>
                        </select>
                        {errors.categoria && <p className="mt-1 text-sm text-red-600">{errors.categoria}</p>}
                    </div>

                    <div>
                        <label htmlFor="subcategoria" className="block text-sm font-medium text-gray-700">
                            Subcategoria *
                        </label>
                        <select
                            id="subcategoria"
                            name="subcategoria"
                            value={formData.subcategoria ?? 0}
                            onChange={handleInputChange}
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                            required
                        >
                            <option value={0}>Padrão</option>
                            <option value={1}>Especiais</option>
                        </select>
                        {errors.subcategoria && <p className="mt-1 text-sm text-red-600">{errors.subcategoria}</p>}
                    </div>
                </div>

                <div className="flex items-center">
                    <input
                        id="teste_exclusivo_setor"
                        name="teste_exclusivo_setor"
                        type="checkbox"
                        checked={formData.teste_exclusivo_setor || false}
                        onChange={handleInputChange}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="teste_exclusivo_setor" className="ml-2 block text-sm text-gray-900">
                        Teste exclusivo do setor
                    </label>
                </div>

                {formData.teste_exclusivo_setor && (
                    <div>
                        <label htmlFor="descricao_teste_exclusivo" className="block text-sm font-medium text-gray-700">
                            Descrição do Teste Exclusivo *
                        </label>
                        <input
                            id="descricao_teste_exclusivo"
                            name="descricao_teste_exclusivo"
                            type="text"
                            value={formData.descricao_teste_exclusivo || ''}
                            onChange={handleInputChange}
                            placeholder="Ex: Teste Daimer, Teste Carga"
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                            required={formData.teste_exclusivo_setor}
                        />
                        {errors.descricao_teste_exclusivo && <p className="mt-1 text-sm text-red-600">{errors.descricao_teste_exclusivo}</p>}
                    </div>
                )}

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
                        Tipo de teste ativo
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
                        {isEdit ? 'Confirmar Edição' : 'Adicionar Tipo de Teste'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default TipoTesteForm;