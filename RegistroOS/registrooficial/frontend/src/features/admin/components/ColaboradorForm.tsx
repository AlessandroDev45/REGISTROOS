import React, { useState, useEffect } from 'react';
import { StyledInput, SelectField } from '../../../components/UIComponents';
import { useCachedSetores } from '../../../hooks/useCachedSetores';

// Função para determinar o tipo de produção e privilégio com base no setor
const determinarPrivilegioEProducao = (setor: string, todosSetores: Array<{nome: string}>) => {
    const setorNomeLower = (setor || '').toLowerCase();

    // Define o tipo de produção com base no setor
    let tipoProducao = 'Producao'; // Padrão
    let trabalhaProducao = false;

    if (setorNomeLower.includes('gestao') || setorNomeLower.includes('gestão') || setorNomeLower.includes('gerencia')) {
        tipoProducao = 'Gestao';
        trabalhaProducao = false;
    } else if (setorNomeLower.includes('pcp')) {
        tipoProducao = 'Pcp';
        trabalhaProducao = false;
    } else if (todosSetores.some(s => s.nome === setor)) {
        tipoProducao = 'Producao';
        trabalhaProducao = true;
    }

    // Define o nível de privilégio
    let privilegeLevel = 'USER'; // Default

    if (setorNomeLower.includes('admin')) {
        privilegeLevel = 'ADMIN';
    } else if (setorNomeLower.includes('gestao') || setorNomeLower.includes('gerencia')) {
        privilegeLevel = 'GESTAO';
    } else if (setorNomeLower.includes('supervisor')) {
        privilegeLevel = 'SUPERVISOR';
    } else if (setorNomeLower.includes('pcp')) {
        privilegeLevel = 'PCP';
    }
    // Para todos os outros, permanece 'USER'

    return {
        privilegeLevel,
        tipoProducao,
        trabalhaProducao,
    };
};

interface ColaboradorFormData {
    primeiroNome: string;
    sobrenome: string;
    email: string;
    password: string;
    matricula: string;
    telefone: string;
    setorTrabalho: string;
    privilegeLevel: string; // Novo campo para nível de privilégio
    trabalhaProducao: boolean; // Novo campo para indicar se trabalha na produção
}

interface ColaboradorFormProps {
    initialData: Partial<ColaboradorFormData>;
    onCancel: () => void;
    onSubmit: (data: ColaboradorFormData, isEdit: boolean) => void;
    isEdit?: boolean; // Optional prop to indicate if it's an edit form
}

    const ColaboradorForm: React.FC<ColaboradorFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false // Default to false if not provided
}) => {
    const { todosSetores, loading: setoresLoading } = useCachedSetores();
    const [formData, setFormData] = useState<ColaboradorFormData>({
        primeiroNome: '',
        sobrenome: '',
        email: '',
        password: '',
        matricula: '',
        telefone: '',
        setorTrabalho: '',
        privilegeLevel: 'USER', // Default para USER
        trabalhaProducao: false, // Default para false,
        ...initialData, // Spread initialData to populate form
    });
    const [showPassword, setShowPassword] = useState(false);
    const [errors, setErrors] = useState<Partial<ColaboradorFormData>>({});

    // Effect to update form data when initialData changes (e.g. when editing a different collaborator)
    useEffect(() => {
        setFormData(prev => ({
            primeiroNome: '',
            sobrenome: '',
            email: '',
            password: '',
            matricula: '',
            telefone: '',
            setorTrabalho: '',
            privilegeLevel: 'USER', // Reset to default or ensure initialData provides it
            trabalhaProducao: false, // Reset to default
            ...initialData,
        }));
        setErrors({}); // Clear errors when initial data changes
    }, [initialData]);

    // Efeito para atualizar o nível de privilégio e tipo de produção com base no setor
    useEffect(() => {
        if (formData.setorTrabalho) {
            const { privilegeLevel, trabalhaProducao } = determinarPrivilegioEProducao(formData.setorTrabalho, todosSetores);
            setFormData(prev => ({ ...prev, privilegeLevel, trabalhaProducao }));
        }
    }, [formData.setorTrabalho, todosSetores]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

        setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
        // Clear error when user starts typing
        if (errors[name as keyof ColaboradorFormData]) {
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }
    };

    const validateForm = (): boolean => {
        const newErrors: Partial<ColaboradorFormData> = {};
        if (!formData.primeiroNome.trim()) newErrors.primeiroNome = 'Campo obrigatório';
        if (!formData.sobrenome.trim()) newErrors.sobrenome = 'Campo obrigatório';
        if (!formData.email.trim()) {
            newErrors.email = 'Campo obrigatório';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Formato de email inválido';
        }
        if (!isEdit && !formData.password) {
             newErrors.password = 'Campo obrigatório para cadastro';
        }
        if (isEdit && formData.password && formData.password.length < 6) {
            newErrors.password = 'A senha deve ter pelo menos 6 caracteres';
        }
        if (!formData.matricula.trim()) newErrors.matricula = 'Campo obrigatório';
        if (!formData.setorTrabalho) newErrors.setorTrabalho = 'Campo obrigatório';
        if (!formData.privilegeLevel) newErrors.privilegeLevel = 'Campo obrigatório';

        if (formData.telefone && !/^\(\d{2}\) \d{5}-\d{4}$/.test(formData.telefone)) {
            newErrors.telefone = 'Formato de telefone inválido (XX) XXXXX-XXXX';
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

    const sectoresDisponiveis = setoresLoading ? [] : [...new Set([...todosSetores.map(s => s.nome), 'ADMIN', 'GESTAO', 'PCP', 'SUPERVISOR', 'RH', 'TI'])];

    return (
        <div className="p-6 bg-white rounded-lg shadow-md">
            <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-700">{isEdit ? 'Editar Colaborador' : 'Adicionar Novo Colaborador'}</h2>
                <div className="mt-2 border-b border-gray-200"></div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <StyledInput
                        id="primeiroNome"
                        name="primeiroNome"
                        value={formData.primeiroNome}
                        onChange={handleInputChange}
                        placeholder="Primeiro nome"
                        error={errors.primeiroNome}
                        required
                    />
                    <StyledInput
                        id="sobrenome"
                        name="sobrenome"
                        value={formData.sobrenome}
                        onChange={handleInputChange}
                        placeholder="Sobrenome"
                        error={errors.sobrenome}
                        required
                    />
                    <StyledInput
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        type="email"
                        placeholder="nome@empresa.com"
                        error={errors.email}
                        required
                    />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="relative">
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                            Senha {isEdit ? '(Deixe em branco para não alterar)' : '(Obrigatório)'} <span className="text-red-500">*</span>
                        </label>
                        <StyledInput
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleInputChange}
                            type={showPassword ? "text" : "password"}
                            placeholder={isEdit ? "Nova senha (opcional)" : "Digite a nova senha"}
                            error={errors.password}
                            required={!isEdit}
                        />
                        <button
                            type="button"
                            className="absolute inset-y-0 right-0 pr-3 flex items-center top-12"
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? (
                                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                                </svg>
                            ) : (
                                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            )}
                        </button>
                    </div>
                    <StyledInput
                        id="matricula"
                        name="matricula"
                        value={formData.matricula}
                        onChange={handleInputChange}
                        placeholder="Alfanumérica"
                        error={errors.matricula}
                        required
                    />
                    <StyledInput
                        id="telefone"
                        name="telefone"
                        value={formData.telefone}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            let value = e.target.value.replace(/\D/g, '');
                            if (value.length > 0) {
                                if (value.length <= 2) value = `(${value}`;
                                else if (value.length <= 7) value = `(${value.slice(0, 2)}) ${value.slice(2)}`;
                                else value = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7, 11)}`;
                            }
                            setFormData(prev => ({ ...prev, telefone: value }));
                            if (errors.telefone) setErrors(prev => ({ ...prev, telefone: undefined }));
                        }}
                        placeholder="(XX) XXXXX-XXXX"
                        error={errors.telefone}
                    />
                </div>

                <div className="grid grid-cols-1 gap-6">
                    <SelectField
                        id="setorTrabalho"
                        name="setorTrabalho"
                        value={formData.setorTrabalho}
                        onChange={handleInputChange}
                        label="Setor de Trabalho"
                        error={errors.setorTrabalho}
                        required
                    >
                        <option value="">Selecione um setor</option>
                        {sectoresDisponiveis.map((setor, index) => (
                            <option key={`setor-${index}-${setor}`} value={setor}>{setor}</option>
                        ))}
                    </SelectField>
                </div>

                <div className="grid grid-cols-1 gap-6">
                    <SelectField
                        id="privilegeLevel"
                        name="privilegeLevel"
                        value={formData.privilegeLevel}
                        onChange={handleInputChange}
                        label="Nível de Privilégio"
                        error={errors.privilegeLevel}
                        required
                    >
                        <option value="">Selecione um nível</option>
                        <option value="USER">USER</option>
                        <option value="SUPERVISOR">SUPERVISOR</option>
                        <option value="PCP">PCP</option>
                        <option value="GESTAO">GESTAO</option>
                        <option value="ADMIN">ADMIN</option>
                    </SelectField>
                </div>

                <div className="grid grid-cols-1 gap-6">
                    <div className="flex items-center">
                        <input
                            id="trabalhaProducao"
                            name="trabalhaProducao"
                            type="checkbox"
                            checked={formData.trabalhaProducao}
                            onChange={(e) => {
                                setFormData(prev => ({ ...prev, trabalhaProducao: e.target.checked }));
                            }}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <label htmlFor="trabalhaProducao" className="ml-2 block text-sm text-gray-900">
                            Trabalha na Produção
                        </label>
                    </div>
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
                        {isEdit ? 'Confirmar Edição' : 'Adicionar Colaborador'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ColaboradorForm;
