import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../../components/UIComponents'; // Assuming StyledInput and SelectField exist
import { setorService, departamentoService, DepartamentoData, SetorData } from '../../../../services/adminApi'; // Import DepartamentoData as well
import { formatarTextoInput, criarHandlerTextoValidado } from '../../../../utils/textValidation';
import { useClickOutside } from '../../../../hooks/useClickOutside';

// Type for errors, where each value is a string message or undefined
interface SetorFormErrors {
    nome?: string;
    departamento?: string;
    descricao?: string;
    area_tipo?: string; // Added validation for new field
}

interface SetorFormProps {
    initialData?: Partial<SetorData>;
    onCancel: () => void;
    onSubmit: (data: SetorData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const SetorForm: React.FC<SetorFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false,
}) => {
    const [formData, setFormData] = useState<SetorData>({
        nome: initialData?.nome || '',
        departamento: initialData?.departamento || 'MOTORES', // Default department name
        descricao: initialData?.descricao || '',
        ativo: initialData?.ativo ?? true,
        area_tipo: initialData?.area_tipo || 'PRODUCAO', // Default value for new field
        id_departamento: initialData?.id_departamento,
        id: initialData?.id,
    });
    const [errors, setErrors] = useState<SetorFormErrors>({});
    const [departamentos, setDepartamentos] = useState<DepartamentoData[]>([]);
    const formRef = useClickOutside<HTMLDivElement>(onCancel);

    useEffect(() => {
        // Fetch departments for the dropdown
        const fetchDepartamentos = async () => {
            try {
                const data = await departamentoService.getDepartamentos(); // Using departamentoService
                setDepartamentos(data);
            } catch (error) {
                console.error("Error fetching departments:", error);
                // Handle error
            }
        };
        fetchDepartamentos();
    }, []);

    // Separar o useEffect para initialData para evitar limpeza de campos
    useEffect(() => {
        if (initialData && isEdit) {
            setFormData({
                nome: initialData?.nome || '',
                departamento: initialData?.departamento || 'MOTORES',
                descricao: initialData?.descricao || '',
                ativo: initialData?.ativo ?? true,
                area_tipo: initialData?.area_tipo || 'PRODUCAO',
                id_departamento: initialData?.id_departamento,
                id: initialData?.id,
            });
            setErrors({});
        }
    }, [initialData, isEdit]);

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        // Aplicar validação de texto para campos de texto
        let processedValue = value;
        if (type === 'text' || type === 'textarea') {
            processedValue = formatarTextoInput(value);
        }

        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : processedValue,
        }));

        if (errors[name as keyof SetorFormErrors]) {
            setErrors((prev) => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: SetorFormErrors = {};
        if (!formData.nome.trim()) {
            newErrors.nome = 'Nome do setor é obrigatório';
        }
        if (!formData.departamento) {
            newErrors.departamento = 'Departamento é obrigatório';
        }
        if (!formData.area_tipo) { // Added validation
            newErrors.area_tipo = 'Tipo de área é obrigatório';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validateForm()) {
            // Mapear nome do departamento para ID antes de enviar
            const departamentoSelecionado = departamentos.find(dept => (dept.nome || dept.nome) === formData.departamento);
            const dataToSubmit = {
                ...formData,
                id_departamento: departamentoSelecionado?.id
            };
            onSubmit(dataToSubmit, isEdit);
        }
    };

    return (
        <div className="mt-6">
            <div ref={formRef} className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {isEdit ? 'Editar Setor' : 'Adicionar Novo Setor'}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                        Nome do Setor *
                    </label>
                    <input
                        type="text"
                        id="nome"
                        name="nome"
                        value={formData.nome}
                        onChange={handleInputChange}
                        placeholder="Ex: Montagem Motores"
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
                        <p className="mt-1 text-sm text-gray-500">Digite o nome do setor para habilitar o botão</p>
                    )}
                    {!errors.nome && formData.nome.trim() && (
                        <p className="mt-1 text-sm text-green-600">✓ Nome válido</p>
                    )}
                </div>

                <div>
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
                    {errors.departamento && (
                        <p className="mt-1 text-sm text-red-600">{errors.departamento}</p>
                    )}
                </div>

                <div>
                    <SelectField
                        id="area_tipo"
                        name="area_tipo"
                        value={formData.area_tipo}
                        onChange={handleInputChange}
                        label="Tipo de Área *"
                        error={errors.area_tipo}
                        required
                    >
                        <option value="">Selecione o tipo de área</option>
                        <option value="PRODUCAO">Produção</option>
                        <option value="ADMINISTRATIVA">Administrativa</option>
                    </SelectField>
                    {errors.area_tipo && (
                        <p className="mt-1 text-sm text-red-600">{errors.area_tipo}</p>
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
                        onPaste={(e) => {
                            e.preventDefault();
                            const texto = e.clipboardData.getData('text');
                            const textoLimpo = formatarTextoInput(texto);
                            setFormData(prev => ({ ...prev, descricao: textoLimpo }));
                        }}
                        placeholder="DESCRIÇÃO DO SETOR (OPCIONAL)"
                        rows={3}
                        className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                        style={{ textTransform: 'uppercase' }}
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
                        Setor ativo
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
                        disabled={!formData.nome.trim() || !formData.departamento.trim()}
                        className={`px-6 py-3 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200 ${
                            (formData.nome.trim() && formData.departamento.trim())
                                ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                    >
                        {isEdit ? 'Confirmar Edição' : 'Adicionar Setor'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default SetorForm;
