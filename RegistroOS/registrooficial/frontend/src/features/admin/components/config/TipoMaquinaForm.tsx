import React, { useState, useEffect } from 'react';
import { SelectField } from '../../../../components/UIComponents';
import { TipoMaquinaData, departamentoService, setorService } from '../../../../services/adminApi';
import { useClickOutside } from '../../../../hooks/useClickOutside';

// Update interface to match backend API payload and form fields
interface TipoMaquinaFormData {
    nome: string;
    descricao: string;
    departamento: string;
    setor: string;
    id_departamento?: number;
    categoria: string;
    subcategoria: string | string[]; // String separada por vírgulas ou array
    ativo: boolean;
}

// Update errors interface
interface TipoMaquinaFormErrors {
    nome?: string;
    descricao?: string;
    departamento?: string;
    setor?: string;
    categoria?: string;
    subcategoria?: string;
}

interface TipoMaquinaFormProps {
    initialData?: Partial<TipoMaquinaFormData>;
    onCancel: () => void;
    onSubmit: (data: TipoMaquinaFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const TipoMaquinaForm: React.FC<TipoMaquinaFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false
}) => {
    const [formData, setFormData] = useState<TipoMaquinaFormData>({
        nome: initialData?.nome || '',
        descricao: initialData?.descricao || '',
        departamento: initialData?.departamento || 'MOTORES',
        setor: initialData?.setor || '',
        categoria: initialData?.categoria || '',
        subcategoria: Array.isArray(initialData?.subcategoria) ? initialData.subcategoria.join(', ') : (initialData?.subcategoria || ''),
        ativo: initialData?.ativo ?? true,
    });
    const [errors, setErrors] = useState<TipoMaquinaFormErrors>({});
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<any[]>([]);
    const formRef = useClickOutside<HTMLDivElement>(onCancel);

    // Atualizar formData quando initialData mudar (para edição) - APENAS se for edição
    useEffect(() => {
        if (initialData && isEdit) {
            setFormData({
                nome: initialData?.nome || '',
                descricao: initialData?.descricao || '',
                departamento: initialData?.departamento || 'MOTORES',
                setor: initialData?.setor || '',
                categoria: initialData?.categoria || '',
                subcategoria: Array.isArray(initialData?.subcategoria) ? initialData.subcategoria.join(', ') : (initialData?.subcategoria || ''),
                ativo: initialData?.ativo ?? true,
            });
        }
    }, [initialData, isEdit]);

    // Carregar departamentos
    useEffect(() => {
        const fetchDepartamentos = async () => {
            try {
                console.log("TipoMaquinaForm: Buscando departamentos...");
                const data = await departamentoService.getDepartamentos();
                console.log("TipoMaquinaForm: Departamentos recebidos:", data);
                setDepartamentos(data);
            } catch (error) {
                console.error("TipoMaquinaForm: Error fetching departments:", error);
            }
        };
        fetchDepartamentos();
    }, []);

    // Carregar setores quando departamento mudar
    useEffect(() => {
        const fetchSetores = async () => {
            if (formData.departamento) {
                try {
                    console.log("TipoMaquinaForm: Buscando setores para departamento:", formData.departamento);
                    const data = await setorService.getSetores();
                    console.log("TipoMaquinaForm: Todos os setores recebidos:", data);

                    const setoresFiltrados = data.filter(setor => {
                        const setorDept = setor.departamento?.trim();
                        const formDept = formData.departamento?.trim();
                        console.log(`TipoMaquinaForm: Comparando setor.departamento "${setorDept}" com formData.departamento "${formDept}"`);
                        return setorDept === formDept;
                    });

                    console.log("TipoMaquinaForm: Setores filtrados:", setoresFiltrados);
                    setSetores(setoresFiltrados);
                } catch (error) {
                    console.error("TipoMaquinaForm: Error fetching setores:", error);
                    setSetores([]);
                }
            } else {
                console.log("TipoMaquinaForm: Nenhum departamento selecionado, limpando setores");
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
            [name]: type === 'checkbox' ? checked : value
        }));

        if (errors[name as keyof TipoMaquinaFormErrors]) {
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: TipoMaquinaFormErrors = {};

        if (!formData.nome.trim()) {
            newErrors.nome = 'Nome do tipo de máquina é obrigatório';
        }

        if (!formData.departamento) {
            newErrors.departamento = 'Departamento é obrigatório';
        }

        if (!formData.categoria.trim()) {
            newErrors.categoria = 'Categoria é obrigatória';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log('🔧 [TIPO MAQUINA FORM] Submit chamado:', { formData, isEdit });
        if (validateForm()) {
            // Mapear nome do departamento para ID antes de enviar
            const departamentoSelecionado = departamentos.find(dept => (dept.nome || dept.nome) === formData.departamento);

            // Converter subcategoria de string para array
            const subcategoriaArray = formData.subcategoria
                ? Array.isArray(formData.subcategoria)
                    ? formData.subcategoria
                    : formData.subcategoria.split(',').map((s: string) => s.trim()).filter((s: string) => s.length > 0)
                : [];

            const dataToSubmit = {
                nome_tipo: formData.nome,  // Backend espera nome_tipo
                nome: formData.nome,       // Manter nome também
                departamento: formData.departamento,
                setor: formData.setor,
                categoria: formData.categoria,
                subcategoria: subcategoriaArray, // Enviar como array
                descricao: formData.descricao,
                ativo: formData.ativo,
                id_departamento: departamentoSelecionado?.id
            };
            console.log('🔧 [TIPO MAQUINA FORM] Enviando dados:', dataToSubmit);
            onSubmit(dataToSubmit, isEdit);
        }
    };

    return (
        <div className="mt-6">
            <div ref={formRef} className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {isEdit ? 'Editar Tipo de Máquina' : 'Adicionar Novo Tipo de Máquina'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* First Row: Departamento e Setor */}
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
                                <option key={dept.id} value={dept.nome || dept.nome}>
                                    {dept.nome || dept.nome}
                                </option>
                            ))}
                        </SelectField>

                        <SelectField
                            id="setor"
                            name="setor"
                            value={formData.setor}
                            onChange={handleInputChange}
                            label="Setor"
                            error={errors.setor}
                        >
                            <option value="">Selecione um setor</option>
                            {setores.map((setor) => (
                                <option key={setor.id} value={setor.nome}>
                                    {setor.nome}
                                </option>
                            ))}
                        </SelectField>
                    </div>

                    {/* Second Row: Nome */}
                    <div className="grid grid-cols-1 gap-6">
                        <div>
                            <label htmlFor="nome" className="block text-sm font-medium text-gray-700">Nome do tipo de máquina *</label>
                            <input
                                type="text"
                                id="nome"
                                name="nome"
                                value={formData.nome}
                                onChange={handleInputChange}
                                placeholder="EX: MAQUINA ROTATIVA CA, MAQUINA ROTATIVA CC, MAQUINA ESTATICA CA"
                                className={`mt-1 block w-full p-2 border rounded-md shadow-sm transition-colors ${
                                    errors.nome
                                        ? 'border-red-500 focus:ring-red-500'
                                        : formData.nome.trim()
                                            ? 'border-green-500 focus:ring-green-500'
                                            : 'border-gray-300 focus:ring-blue-500'
                                }`}
                            />
                            {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
                            {!errors.nome && !formData.nome.trim() && (
                                <p className="mt-1 text-sm text-gray-500">Digite o nome do tipo de máquina para habilitar o botão</p>
                            )}
                            {!errors.nome && formData.nome.trim() && (
                                <p className="mt-1 text-sm text-green-600">✓ Nome válido</p>
                            )}
                        </div>
                    </div>

                    {/* Categoria */}
                    <div>
                        <label htmlFor="categoria" className="block text-sm font-medium text-gray-700">
                            🎯 Categoria da Máquina *
                        </label>
                        <p className="text-xs text-gray-500 mb-2">
                            Defina a categoria principal desta máquina (ex: MOTOR, GERADOR, TRANSFORMADOR, etc.)
                        </p>
                        <input
                            type="text"
                            id="categoria"
                            name="categoria"
                            value={formData.categoria}
                            onChange={handleInputChange}
                            placeholder=" EX: MOTOR, GERADOR, TRANSFORMADOR"
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            required
                        />
                        {errors.categoria && <p className="mt-1 text-sm text-red-600">{errors.categoria}</p>}
                    </div>

                    {/* Descrição */}
                    <div>
                        <label htmlFor="descricao" className="block text-sm font-medium text-gray-700">
                            Descrição
                        </label>
                        <textarea
                            id="descricao"
                            name="descricao"
                            value={formData.descricao}
                            onChange={handleInputChange}
                            placeholder="Descrição do tipo de máquina (opcional)"
                            rows={3}
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                        />
                    </div>

                    {/* Subcategoria */}
                    <div>
                        <label htmlFor="subcategoria" className="block text-sm font-medium text-gray-700">
                            🔧 Subcategoria *
                        </label>
                        <p className="text-xs text-gray-500 mb-2">
                            Defina a subcategoria desta máquina (ex: ESTATOR, ROTOR, NÚCLEO, CARCAÇA, etc.)
                        </p>
                        <input
                            type="text"
                            id="subcategoria"
                            name="subcategoria"
                            value={Array.isArray(formData.subcategoria) ? formData.subcategoria.join(', ') : formData.subcategoria}
                            onChange={handleInputChange}
                            placeholder="Ex: ESTATOR, ROTOR, NÚCLEO, CARCAÇA"
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                        />
                        {errors.subcategoria && <p className="mt-1 text-sm text-red-600">{errors.subcategoria}</p>}
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
                                Tipo de máquina ativo
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
                            disabled={!formData.nome.trim() || !formData.departamento.trim() || !formData.categoria.trim()}
                            className={`px-6 py-3 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 ${
                                (formData.nome.trim() && formData.departamento.trim() && formData.categoria.trim())
                                    ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            }`}
                        >
                            {isEdit ? 'Confirmar Edição' : 'Adicionar Tipo de Máquina'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TipoMaquinaForm;
