import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents';
import { TipoTesteData, DepartamentoData, TipoMaquinaData, SetorData, departamentoService, setorService, tipoMaquinaService } from '../../../../services/adminApi';

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
    categoria?: string;
    subcategoria?: number;
}

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
        departamento: initialData?.departamento || 'MOTORES',
        setor: initialData?.setor || '',
        tipo_teste: initialData?.tipo_teste || '',
        descricao: initialData?.descricao || '',
        ativo: initialData?.ativo ?? true,
        tipo_maquina: initialData?.tipo_maquina,
        teste_exclusivo_setor: initialData?.teste_exclusivo_setor ?? false,
        descricao_teste_exclusivo: initialData?.descricao_teste_exclusivo || '',
        categoria: initialData?.categoria || '',
        subcategoria: initialData?.subcategoria,
    });
    const [errors, setErrors] = useState<TipoTesteFormErrors>({});
    const [departamentos, setDepartamentos] = useState<DepartamentoData[]>([]);
    const [setores, setSetores] = useState<SetorData[]>([]);
    const [tiposMaquina, setTiposMaquina] = useState<TipoMaquinaData[]>([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [deptData, setorData, tipoMaquinaData] = await Promise.all([
                    departamentoService.getDepartamentos(),
                    setorService.getSetores(),
                    tipoMaquinaService.getTiposMaquina()
                ]);
                setDepartamentos(deptData);
                setSetores(setorData);
                setTiposMaquina(tipoMaquinaData);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        fetchData();
    }, []);

    useEffect(() => {
        if (formData.departamento) {
            const filteredSetores = setores.filter(setor => 
                setor.departamento === formData.departamento
            );
            setSetores(filteredSetores);
        }
    }, [formData.departamento, setores]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        if (errors[name as keyof TipoTesteFormErrors]) {
            setErrors(prev => ({ ...prev, [name]: undefined }));
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
        
        if (!formData.tipo_teste) {
            newErrors.tipo_teste = 'Tipo de teste é obrigatório';
        }
        
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validateForm()) {
            const dataToSubmit = {
                ...formData,
                tipo_maquina: formData.tipo_maquina || undefined,
                teste_exclusivo_setor: formData.teste_exclusivo_setor || false,
                descricao_teste_exclusivo: formData.descricao_teste_exclusivo || '',
                categoria: formData.categoria || undefined,
                subcategoria: formData.subcategoria || undefined,
            };
            onSubmit(dataToSubmit, isEdit);
        }
    };

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
                                <option key={dept.id} value={dept.nome}>
                                    {dept.nome}
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

                    <div>
                        <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                            Nome do Tipo de Teste *
                        </label>
                        <StyledInput
                            id="nome"
                            name="nome"
                            value={formData.nome}
                            onChange={handleInputChange}
                            placeholder="Ex: Teste de Tensão"
                            error={errors.nome}
                            required
                        />
                    </div>

                    <div>
                        <SelectField
                            id="tipo_teste"
                            name="tipo_teste"
                            value={formData.tipo_teste}
                            onChange={handleInputChange}
                            label="Tipo de Teste *"
                            error={errors.tipo_teste}
                            required
                        >
                            <option value="">Selecione o tipo de teste</option>
                            <option value="ELETRICO">Elétrico</option>
                            <option value="MECANICO">Mecânico</option>
                            <option value="VISUAL">Visual</option>
                        </SelectField>
                    </div>

                    <div>
                        <SelectField
                            id="tipo_maquina"
                            name="tipo_maquina"
                            value={formData.tipo_maquina}
                            onChange={handleInputChange}
                            label="Tipo de Máquina"
                            error={errors.tipo_maquina}
                        >
                            <option value="">Selecione o tipo de máquina</option>
                            {tiposMaquina.map((tipo) => (
                                <option key={tipo.id} value={tipo.nome}>
                                    {tipo.nome}
                                </option>
                            ))}
                        </SelectField>
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
                            placeholder="Descrição do tipo de teste"
                            rows={3}
                            className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <SelectField
                                id="categoria"
                                name="categoria"
                                value={formData.categoria}
                                onChange={handleInputChange}
                                label="Categoria"
                                error={errors.categoria}
                            >
                                <option value="">Selecione a categoria</option>
                                <option value="Visual">Visual</option>
                                <option value="Elétricos">Elétricos</option>
                                <option value="Mecânicos">Mecânicos</option>
                            </SelectField>
                        </div>

                        <div>
                            <SelectField
                                id="subcategoria"
                                name="subcategoria"
                                value={formData.subcategoria?.toString()}
                                onChange={handleInputChange}
                                label="Subcategoria"
                                error={errors.subcategoria}
                            >
                                <option value="">Selecione a subcategoria</option>
                                <option value="0">Padrão</option>
                                <option value="1">Especiais</option>
                            </SelectField>
                        </div>
                    </div>

                    <div className="flex items-center">
                        <input
                            id="teste_exclusivo_setor"
                            name="teste_exclusivo_setor"
                            type="checkbox"
                            checked={formData.teste_exclusivo_setor}
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
                                Descrição do Teste Exclusivo
                            </label>
                            <textarea
                                id="descricao_teste_exclusivo"
                                name="descricao_teste_exclusivo"
                                value={formData.descricao_teste_exclusivo}
                                onChange={handleInputChange}
                                placeholder="Descrição específica do teste exclusivo"
                                rows={2}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
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
