import React, { useState, useEffect } from 'react';
import { SelectField } from '../../../../components/UIComponents';
import { setorService, tipoMaquinaService, tipoTesteService, atividadeTipoService, falhaTipoService } from '../../../../services/adminApi';

interface SetorOption {
    id: number;
    nome: string;
    departamento: string;
}

interface TipoMaquinaOption {
    id: number;
    nome: string;
    id_setor: number;
}

interface TipoTesteOption {
    id: number;
    nome: string;
    id_tipo_maquina: number;
}

interface AtividadeOption {
    id: number;
    nome: string;
    id_tipo_teste: number;
}

interface TipoFalhaOption {
    id: number;
    nome: string;
    id_tipo_teste: number;
}

interface HierarchicalProcessFormData {
    // Level 1 - SETORES
    id_setor?: number;
    nome_setor?: string;

    // Level 2 - TIPOS DE MÁQUINA
    id_tipo_maquina?: number;
    nome_tipo_maquina?: string;

    // Level 3 - TIPOS DE TESTES
    id_tipo_teste?: number;
    nome_tipo_teste?: string;

    // Level 4 - ATIVIDADES
    id_atividade?: number;
    nome_atividade?: string;

    // Level 5 - DESCRIÇÃO DE ATIVIDADES
    id_descricao_atividade?: number;
    descricao_detalhada?: string;

    // Level 6 - TIPOS DE FALHA
    id_tipo_falha?: number;
    nome_tipo_falha?: string;

    // Level 7 - CAUSAS DE RETRABALHO
    id_causa_retrabalho?: number;
    descricao_causa?: string;
}
type FormErrors = {
    [K in keyof HierarchicalProcessFormData]?: string;
};

interface HierarchicalProcessFormProps {
    activeTab: string;
    initialData?: Partial<HierarchicalProcessFormData>;
    onCancel: () => void;
    onSubmit: (data: HierarchicalProcessFormData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const HierarchicalProcessForm: React.FC<HierarchicalProcessFormProps> = ({
    activeTab,
    initialData,
    onCancel,
    onSubmit,
    isEdit = false
}) => {
    const [formData, setFormData] = useState<HierarchicalProcessFormData>({
        ...initialData,
    });
    const [errors, setErrors] = useState<FormErrors>({});

    // State for hierarchical data
    const [setores, setSetores] = useState<SetorOption[]>([]);
    const [tiposMaquina, setTiposMaquina] = useState<TipoMaquinaOption[]>([]);
    const [tiposTeste, setTiposTeste] = useState<TipoTesteOption[]>([]);
    const [atividades, setAtividades] = useState<AtividadeOption[]>([]);
    const [tiposFalha, setTiposFalha] = useState<TipoFalhaOption[]>([]);

    const [loading, setLoading] = useState(false);

    // Load initial data based on active tab
    useEffect(() => {
        loadInitialData();
    }, [activeTab]);

    const loadInitialData = async () => {
        setLoading(true);
        try {
            switch (activeTab) {
                case 'setores':
                    // No parent data needed for setores
                    break;
                case 'tipos-maquina':
                    const setoresData = await setorService.getSetores();
                    setSetores(setoresData.map(s => ({
                        id: s.id!,
                        nome: s.nome,
                        departamento: s.departamento
                    })));
                    break;
                case 'tipos-testes':
                    const setoresForMaquina = await setorService.getSetores();
                    setSetores(setoresForMaquina.map(s => ({
                        id: s.id!,
                        nome: s.nome,
                        departamento: s.departamento
                    })));
                    if (formData.id_setor) {
                        const maquinasData = await tipoMaquinaService.getTiposMaquina();
                        setTiposMaquina(maquinasData.map(m => ({
                            id: m.id!,
                            nome: m.nome,
                            id_setor: formData.id_setor || 0
                        })));
                    }
                    break;
                case 'atividades':
                    const setoresForAtividade = await setorService.getSetores();
                    setSetores(setoresForAtividade.map(s => ({
                        id: s.id!,
                        nome: s.nome,
                        departamento: s.departamento
                    })));
                    if (formData.id_setor) {
                        const maquinasForAtividade = await tipoMaquinaService.getTiposMaquina();
                        setTiposMaquina(maquinasForAtividade.map(m => ({
                            id: m.id!,
                            nome: m.nome,
                            id_setor: formData.id_setor || 0
                        })));
                        if (formData.id_tipo_maquina) {
                            const testesData = await tipoTesteService.getTiposTeste();
                            setTiposTeste(testesData.map(t => ({
                                id: t.id!,
                                nome: t.nome,
                                id_tipo_maquina: formData.id_tipo_maquina || 0
                            })));
                        }
                    }
                    break;
                case 'falhas':
                    const setoresForFalha = await setorService.getSetores();
                    setSetores(setoresForFalha.map(s => ({ ...s, id: s.id! })));
                    if (formData.id_setor) {
                        const maquinasForFalha = await tipoMaquinaService.getTiposMaquina();
                        setTiposMaquina(maquinasForFalha as unknown as TipoMaquinaOption[]);
                        if (formData.id_tipo_maquina) {
                            const testesForFalha = await tipoTesteService.getTiposTeste();
                            setTiposTeste(testesForFalha as unknown as TipoTesteOption[]);
                        }
                    }
                    break;
                case 'causas-retrabalho':
                    const setoresForCausa = await setorService.getSetores();
                    setSetores(setoresForCausa.map(s => ({ ...s, id: s.id! })));
                    if (formData.id_setor) {
                        const maquinasForFalha = await tipoMaquinaService.getTiposMaquina();
                        setTiposMaquina(maquinasForFalha.map(m => ({
                            id: m.id!,
                            nome: m.nome,
                            id_setor: formData.id_setor || 0
                        })));
                        if (formData.id_tipo_maquina) {
                            const testesForFalha = await tipoTesteService.getTiposTeste();
                            setTiposTeste(testesForFalha.map(t => ({
                                id: t.id!,
                                nome: t.nome,
                                id_tipo_maquina: formData.id_tipo_maquina || 0
                            })));
                            if (formData.id_tipo_teste) {
                                const falhasResponse = await falhaTipoService.getFalhasTipo();
                                let falhasData = [];
                                if (Array.isArray(falhasResponse)) {
                                    falhasData = falhasResponse;
                                } else if (falhasResponse && typeof falhasResponse === 'object' && 'status' in falhasResponse) {
                                    const statusResponse = falhasResponse as any;
                                    if (statusResponse.status === 'DISABLED') {
                                        console.warn('Funcionalidade de tipos de falha desabilitada');
                                        falhasData = []; // Array vazio para funcionalidade desabilitada
                                    }
                                }
                                setTiposFalha(falhasData.map(f => ({
                                    id: f.id!,
                                    nome: f.descricao,
                                    id_tipo_teste: formData.id_tipo_teste || 0
                                })));
                            }
                        }
                    }
                    break;
            }
        } catch (error) {
            console.error('Erro ao carregar dados:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;

        const numericFields = ['id_setor', 'id_tipo_maquina', 'id_tipo_teste', 'id_atividade', 'id_descricao_atividade', 'id_tipo_falha', 'id_causa_retrabalho'];
        const processedValue = numericFields.includes(name) ? (value ? Number(value) : undefined) : value;

        setFormData(prev => ({
            ...prev,
            [name]: processedValue
        }));

        if (errors[name as keyof HierarchicalProcessFormData]) {
            setErrors(prev => ({ ...prev, [name]: undefined }));
        }

        // Handle cascading updates
        handleCascadingChanges(name, processedValue);
    };

    const handleCascadingChanges = async (name: string, value: string | number | undefined) => {
        switch (name) {
            case 'id_setor':
                if (activeTab === 'tipos-maquina' || activeTab === 'tipos-testes' || activeTab === 'atividades' || activeTab === 'falhas' || activeTab === 'causas-retrabalho') {
                    const maquinasData = await tipoMaquinaService.getTiposMaquina();
                    setTiposMaquina(maquinasData.map(m => ({
                        id: m.id!,
                        nome: m.nome,
                        id_setor: Number(value) || 0
                    })));
                    setFormData(prev => ({ ...prev, id_tipo_maquina: undefined, id_tipo_teste: undefined, id_atividade: undefined, id_tipo_falha: undefined }));
                }
                break;
            case 'id_tipo_maquina':
                if (activeTab === 'tipos-testes' || activeTab === 'atividades' || activeTab === 'falhas' || activeTab === 'causas-retrabalho') {
                    const testesData = await tipoTesteService.getTiposTeste();
                    setTiposTeste(testesData.map(t => ({
                        id: t.id!,
                        nome: t.nome,
                        id_tipo_maquina: Number(value) || 0
                    })));
                    setFormData(prev => ({ ...prev, id_tipo_teste: undefined, id_atividade: undefined, id_tipo_falha: undefined }));
                }
                break;
            case 'id_tipo_teste':
                if (activeTab === 'atividades') {
                    const atividadesData = await atividadeTipoService.getAtividadesTipo();
                    setAtividades(atividadesData.map(a => ({
                        id: a.id!,
                        nome: a.nome_tipo,
                        id_tipo_teste: Number(value)
                    })));
                    setFormData(prev => ({ ...prev, id_atividade: undefined }));
                } else if (activeTab === 'falhas' || activeTab === 'causas-retrabalho') {
                    const falhasResponse = await falhaTipoService.getFalhasTipo();
                    let falhasData = [];
                    if (Array.isArray(falhasResponse)) {
                        falhasData = falhasResponse;
                    } else if (falhasResponse && typeof falhasResponse === 'object' && 'status' in falhasResponse) {
                        const statusResponse = falhasResponse as any;
                        if (statusResponse.status === 'DISABLED') {
                            console.warn('Funcionalidade de tipos de falha desabilitada');
                            falhasData = []; // Array vazio para funcionalidade desabilitada
                        }
                    }
                    setTiposFalha(falhasData.map(f => ({
                        id: f.id!,
                        nome: f.descricao,
                        id_tipo_teste: formData.id_tipo_teste || 0
                    })));
                    setFormData(prev => ({ ...prev, id_tipo_falha: undefined }));
                }
                break;
        }
    };

    const validateForm = (): boolean => {
        const newErrors: FormErrors = {};

        switch (activeTab) {
            case 'setores':
                if (!formData.nome_setor?.trim()) {
                    newErrors.nome_setor = 'Nome do setor é obrigatório';
                }
                break;
            case 'tipos-maquina':
                if (!formData.id_setor) {
                    newErrors.id_setor = 'Setor pai é obrigatório';
                }
                if (!formData.nome_tipo_maquina?.trim()) {
                    newErrors.nome_tipo_maquina = 'Nome do tipo de máquina é obrigatório';
                }
                break;
            case 'tipos-testes':
                if (!formData.id_tipo_maquina) {
                    newErrors.id_tipo_maquina = 'Tipo de máquina é obrigatório';
                }
                if (!formData.nome_tipo_teste?.trim()) {
                    newErrors.nome_tipo_teste = 'Nome do tipo de teste é obrigatório';
                }
                break;
            case 'atividades':
                if (!formData.id_tipo_teste) {
                    newErrors.id_tipo_teste = 'Tipo de teste é obrigatório';
                }
                if (!formData.nome_atividade?.trim()) {
                    newErrors.nome_atividade = 'Nome da atividade é obrigatório';
                }
                break;
            case 'falhas':
                if (!formData.id_tipo_teste) {
                    newErrors.id_tipo_teste = 'Tipo de teste é obrigatório';
                }
                if (!formData.nome_tipo_falha?.trim()) {
                    newErrors.nome_tipo_falha = 'Nome do tipo de falha é obrigatório';
                }
                break;
            case 'causas-retrabalho':
                if (!formData.id_tipo_falha) {
                    newErrors.id_tipo_falha = 'Tipo de falha é obrigatório';
                }
                if (!formData.descricao_causa?.trim()) {
                    newErrors.descricao_causa = 'Descrição da causa é obrigatória';
                }
                break;
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

    const renderFormFields = () => {
        switch (activeTab) {
            case 'setores':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="nome_setor" className="block text-sm font-medium text-gray-700">
                                Nome do Setor *
                            </label>
                            <input
                                type="text"
                                id="nome_setor"
                                name="nome_setor"
                                value={formData.nome_setor || ''}
                                onChange={handleInputChange}
                                placeholder="Ex: Montagem Motores"
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
                            {errors.nome_setor && <p className="mt-1 text-sm text-red-600">{errors.nome_setor}</p>}
                        </div>
                    </div>
                );

            case 'tipos-maquina':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="id_setor" className="block text-sm font-medium text-gray-700">
                                Setor Pai *
                            </label>
                            <select
                                id="id_setor"
                                name="id_setor"
                                value={formData.id_setor || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            >
                                <option value="">Selecione um setor</option>
                                {setores.map(setor => (
                                    <option key={setor.id} value={setor.id}>
                                        {setor.nome} ({setor.departamento})
                                    </option>
                                ))}
                            </select>
                            {errors.id_setor && <p className="mt-1 text-sm text-red-600">{errors.id_setor}</p>}
                        </div>
                        <div>
                            <label htmlFor="nome_tipo_maquina" className="block text-sm font-medium text-gray-700">
                                Nome do Tipo de Máquina *
                            </label>
                            <input
                                type="text"
                                id="nome_tipo_maquina"
                                name="nome_tipo_maquina"
                                value={formData.nome_tipo_maquina || ''}
                                onChange={handleInputChange}
                                placeholder="Ex: Máquina Estática CA"
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
                            {errors.nome_tipo_maquina && <p className="mt-1 text-sm text-red-600">{errors.nome_tipo_maquina}</p>}
                        </div>
                    </div>
                );

            case 'tipos-testes':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="id_setor" className="block text-sm font-medium text-gray-700">
                                Setor *
                            </label>
                            <select
                                id="id_setor"
                                name="id_setor"
                                value={formData.id_setor || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            >
                                <option value="">Selecione um setor</option>
                                {setores.map(setor => (
                                    <option key={setor.id} value={setor.id}>
                                        {setor.nome} ({setor.departamento})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_maquina" className="block text-sm font-medium text-gray-700">
                                Tipo de Máquina *
                            </label>
                            <select
                                id="id_tipo_maquina"
                                name="id_tipo_maquina"
                                value={formData.id_tipo_maquina || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_setor}
                            >
                                <option value="">Selecione um tipo de máquina</option>
                                {tiposMaquina.map(maquina => (
                                    <option key={maquina.id} value={maquina.id}>
                                        {maquina.nome}
                                    </option>
                                ))}
                            </select>
                            {errors.id_tipo_maquina && <p className="mt-1 text-sm text-red-600">{errors.id_tipo_maquina}</p>}
                        </div>
                        <div>
                            <label htmlFor="nome_tipo_teste" className="block text-sm font-medium text-gray-700">
                                Nome do Tipo de Teste *
                            </label>
                            <input
                                type="text"
                                id="nome_tipo_teste"
                                name="nome_tipo_teste"
                                value={formData.nome_tipo_teste || ''}
                                onChange={handleInputChange}
                                placeholder="Ex: Ensaio Elétrico"
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
                            {errors.nome_tipo_teste && <p className="mt-1 text-sm text-red-600">{errors.nome_tipo_teste}</p>}
                        </div>
                    </div>
                );

            case 'atividades':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="id_setor" className="block text-sm font-medium text-gray-700">
                                Setor *
                            </label>
                            <select
                                id="id_setor"
                                name="id_setor"
                                value={formData.id_setor || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            >
                                <option value="">Selecione um setor</option>
                                {setores.map(setor => (
                                    <option key={setor.id} value={setor.id}>
                                        {setor.nome} ({setor.departamento})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_maquina" className="block text-sm font-medium text-gray-700">
                                Tipo de Máquina *
                            </label>
                            <select
                                id="id_tipo_maquina"
                                name="id_tipo_maquina"
                                value={formData.id_tipo_maquina || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_setor}
                            >
                                <option value="">Selecione um tipo de máquina</option>
                                {tiposMaquina.map(maquina => (
                                    <option key={maquina.id} value={maquina.id}>
                                        {maquina.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_teste" className="block text-sm font-medium text-gray-700">
                                Tipo de Teste *
                            </label>
                            <select
                                id="id_tipo_teste"
                                name="id_tipo_teste"
                                value={formData.id_tipo_teste || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_tipo_maquina}
                            >
                                <option value="">Selecione um tipo de teste</option>
                                {tiposTeste.map(teste => (
                                    <option key={teste.id} value={teste.id}>
                                        {teste.nome}
                                    </option>
                                ))}
                            </select>
                            {errors.id_tipo_teste && <p className="mt-1 text-sm text-red-600">{errors.id_tipo_teste}</p>}
                        </div>
                        <div>
                            <label htmlFor="nome_atividade" className="block text-sm font-medium text-gray-700">
                                Nome da Atividade *
                            </label>
                            <input
                                type="text"
                                id="nome_atividade"
                                name="nome_atividade"
                                value={formData.nome_atividade || ''}
                                onChange={handleInputChange}
                                placeholder="Ex: Verificar isolamento"
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
                            {errors.nome_atividade && <p className="mt-1 text-sm text-red-600">{errors.nome_atividade}</p>}
                        </div>
                    </div>
                );

            case 'falhas':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="id_setor" className="block text-sm font-medium text-gray-700">
                                Setor *
                            </label>
                            <select
                                id="id_setor"
                                name="id_setor"
                                value={formData.id_setor || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            >
                                <option value="">Selecione um setor</option>
                                {setores.map(setor => (
                                    <option key={setor.id} value={setor.id}>
                                        {setor.nome} ({setor.departamento})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_maquina" className="block text-sm font-medium text-gray-700">
                                Tipo de Máquina *
                            </label>
                            <select
                                id="id_tipo_maquina"
                                name="id_tipo_maquina"
                                value={formData.id_tipo_maquina || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_setor}
                            >
                                <option value="">Selecione um tipo de máquina</option>
                                {tiposMaquina.map(maquina => (
                                    <option key={maquina.id} value={maquina.id}>
                                        {maquina.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_teste" className="block text-sm font-medium text-gray-700">
                                Tipo de Teste *
                            </label>
                            <select
                                id="id_tipo_teste"
                                name="id_tipo_teste"
                                value={formData.id_tipo_teste || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_tipo_maquina}
                            >
                                <option value="">Selecione um tipo de teste</option>
                                {tiposTeste.map(teste => (
                                    <option key={teste.id} value={teste.id}>
                                        {teste.nome}
                                    </option>
                                ))}
                            </select>
                            {errors.id_tipo_teste && <p className="mt-1 text-sm text-red-600">{errors.id_tipo_teste}</p>}
                        </div>
                        <div>
                            <label htmlFor="nome_tipo_falha" className="block text-sm font-medium text-gray-700">
                                Nome do Tipo de Falha *
                            </label>
                            <input
                                type="text"
                                id="nome_tipo_falha"
                                name="nome_tipo_falha"
                                value={formData.nome_tipo_falha || ''}
                                onChange={handleInputChange}
                                placeholder="Ex: Falha no isolamento"
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
                            {errors.nome_tipo_falha && <p className="mt-1 text-sm text-red-600">{errors.nome_tipo_falha}</p>}
                        </div>
                    </div>
                );

            case 'causas-retrabalho':
                return (
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="id_setor" className="block text-sm font-medium text-gray-700">
                                Setor *
                            </label>
                            <select
                                id="id_setor"
                                name="id_setor"
                                value={formData.id_setor || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            >
                                <option value="">Selecione um setor</option>
                                {setores.map(setor => (
                                    <option key={setor.id} value={setor.id}>
                                        {setor.nome} ({setor.departamento})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_maquina" className="block text-sm font-medium text-gray-700">
                                Tipo de Máquina *
                            </label>
                            <select
                                id="id_tipo_maquina"
                                name="id_tipo_maquina"
                                value={formData.id_tipo_maquina || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_setor}
                            >
                                <option value="">Selecione um tipo de máquina</option>
                                {tiposMaquina.map(maquina => (
                                    <option key={maquina.id} value={maquina.id}>
                                        {maquina.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_teste" className="block text-sm font-medium text-gray-700">
                                Tipo de Teste *
                            </label>
                            <select
                                id="id_tipo_teste"
                                name="id_tipo_teste"
                                value={formData.id_tipo_teste || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_tipo_maquina}
                            >
                                <option value="">Selecione um tipo de teste</option>
                                {tiposTeste.map(teste => (
                                    <option key={teste.id} value={teste.id}>
                                        {teste.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label htmlFor="id_tipo_falha" className="block text-sm font-medium text-gray-700">
                                Tipo de Falha *
                            </label>
                            <select
                                id="id_tipo_falha"
                                name="id_tipo_falha"
                                value={formData.id_tipo_falha || ''}
                                onChange={handleInputChange}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                                disabled={!formData.id_tipo_teste}
                            >
                                <option value="">Selecione um tipo de falha</option>
                                {tiposFalha.map(falha => (
                                    <option key={falha.id} value={falha.id}>
                                        {falha.nome}
                                    </option>
                                ))}
                            </select>
                            {errors.id_tipo_falha && <p className="mt-1 text-sm text-red-600">{errors.id_tipo_falha}</p>}
                        </div>
                        <div>
                            <label htmlFor="descricao_causa" className="block text-sm font-medium text-gray-700">
                                Descrição da Causa de Retrabalho *
                            </label>
                            <textarea
                                id="descricao_causa"
                                name="descricao_causa"
                                value={formData.descricao_causa || ''}
                                onChange={handleInputChange}
                                placeholder="Descreva a causa do retrabalho"
                                rows={3}
                                className="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm"
                            />
                            {errors.descricao_causa && <p className="mt-1 text-sm text-red-600">{errors.descricao_causa}</p>}
                        </div>
                    </div>
                );

            default:
                return <div>Formulário não implementado para esta aba</div>;
        }
    };

    const getFormTitle = () => {
        const titles = {
            'setores': isEdit ? 'Editar Setor' : 'Adicionar Novo Setor',
            'tipos-maquina': isEdit ? 'Editar Tipo de Máquina' : 'Adicionar Novo Tipo de Máquina',
            'tipos-testes': isEdit ? 'Editar Tipo de Teste' : 'Adicionar Novo Tipo de Teste',
            'atividades': isEdit ? 'Editar Atividade' : 'Adicionar Nova Atividade',
            'falhas': isEdit ? 'Editar Tipo de Falha' : 'Adicionar Novo Tipo de Falha',
            'causas-retrabalho': isEdit ? 'Editar Causa de Retrabalho' : 'Adicionar Nova Causa de Retrabalho'
        };
        return titles[activeTab as keyof typeof titles] || 'Formulário';
    };

    if (loading) {
        return (
            <div className="mt-6">
                <div className="p-6 bg-white rounded-lg shadow-md">
                    <div className="text-center">Carregando dados...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="mt-6">
            <div className="p-6 bg-white rounded-lg shadow-md">
                <div className="mb-6">
                    <h2 className="text-2xl font-semibold text-gray-700">
                        {getFormTitle()}
                    </h2>
                    <div className="mt-2 border-b border-gray-200"></div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                {renderFormFields()}

                {/* Buttons Area */}
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
                        {isEdit ? 'Confirmar Edição' : 'Adicionar'}
                    </button>
                </div>
                </form>
            </div>
        </div>
    );
};

export default HierarchicalProcessForm;