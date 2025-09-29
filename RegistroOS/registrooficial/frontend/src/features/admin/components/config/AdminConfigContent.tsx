import React, { useState, useEffect } from 'react';
import SetorForm from './SetorForm';
import SetorList from './SetorList';
import TipoMaquinaForm from './TipoMaquinaForm';
import TipoMaquinaList from './TipoMaquinaList';
import TipoTesteForm from './TipoTesteForm';
import TipoTesteList from './TipoTesteList';
import DescricaoAtividadeList from './DescricaoAtividadeList';
import CentroCustoList from './CentroCustoList';
import CentroCustoForm from './CentroCustoForm';
import TipoAtividadeForm from './TipoAtividadeForm';
import TipoFalhaForm from './TipoFalhaForm';
import CausaRetrabalhoForm from './CausaRetrabalhoForm';
import TipoAtividadeList from './TipoAtividadeList';
import TipoFalhaList from './TipoFalhaList';
import CausaRetrabalhoList from './CausaRetrabalhoList';
import DescricaoAtividadeForm from './DescricaoAtividadeForm';
import DepartamentoForm from './DepartamentoForm';
import HierarchicalSectorViewer from './HierarchicalSectorViewer';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
    setorService,
    tipoMaquinaService,
    tipoTesteService,
    atividadeTipoService,
    falhaTipoService,
    causaRetrabalhoService,
    departamentoService,
    centroCustoService,
    descricaoAtividadeService
} from '../../../../services/adminApi';

import { useGenericForm } from '../../../../hooks/useGenericForm';

// Definindo os tipos aqui para evitar dependências circulares ou importações complexas
interface SetorData {
    id: number;
    nome: string;
    departamento: 'MOTORES' | 'TRANSFORMADORES';
    descricao: string;
    ativo: boolean;
    tiposMaquina?: string[];
    tiposAtividade?: string[];
    descricoesAtividade?: string[];
    tiposFalha?: string[];
    testesEstaticos?: {
        carcaca: string[];
        estator: string[];
        rotor: string[];
        auxPmg: string[];
        rotorPmg: string[];
    };
    testesDinamicos?: {
        tipo: string;
        vazio: string[];
        carga: string[];
    };
}

interface TipoMaquinaData {
    id?: number;
    nome: string;
    departamento: 'MOTORES' | 'TRANSFORMADORES';
    descricao: string;
    campos_teste_resultado?: string; // JSON string
    ativo: boolean;
}

interface DepartamentoData {
    id?: number;
    nome: string;
    nome_tipo?: string;
    descricao?: string;
    ativo?: boolean;
}

interface TipoTesteData {
    id?: number;
    nome: string;
    tipo_teste: string;
    descricao: string;
    ativo: boolean;
    tipo_maquina?: string;
    teste_exclusivo_setor?: boolean;
    descricao_teste_exclusivo?: string;
    categoria?: string;
    subcategoria?: number;
}

interface AtividadeTipoData {
    id?: number;
    nome: string;
    descricao: string;
    tipo_atividade: string;
    ativo: boolean;
    nome_tipo?: string; // Adicionado para compatibilidade
}

interface FalhaTipoData {
    id?: number;
    nome: string;
    descricao: string;
    ativo: boolean;
    nome_tipo?: string; // Adicionado para compatibilidade
}

interface CausaRetrabalhoData {
    id?: number;
    nome: string;
    descricao: string;
    ativo: boolean;
    nome_tipo?: string; // Adicionado para compatibilidade
}

interface CentroCustoData {
    id?: number;
    nome: string;
    descricao?: string;
    ativo?: boolean;
    nome_tipo?: string; // Adicionado para compatibilidade
}

interface DescricaoAtividadeData {
    id?: number;
    codigo: string;
    descricao: string;
    setor: string;
    departamento: string;
    categoria: string;
    ativo: boolean;
}

type ConfigTabKey = 'centro_custo' | 'setores' | 'tipos_maquina' | 'tipos_testes' | 'atividades' | 'descricao_atividades' | 'falhas' | 'causas_retrabalho' | 'hierarchy';

interface AdminConfigContentProps {
    // Props para comunicação com o componente pai (administrador.tsx)
    onEdit: (item: any, type?: string) => void; // Agora aceita tipo como segundo parâmetro
    onDelete: (type: string, item: any) => Promise<void>;
    onCreateNew: () => void; // O tipo 'type' é implícito pela aba ativa
    onSubmit: (data: any, isEdit: boolean) => void; // A assinatura foi simplificada
    onCancelForm: () => void;
    currentConfigItem: any;
    configType: string; // Indica qual formulário/lista está ativa
    showConfigForm: boolean;
    loadingConfig: boolean;
    configData: { [key: string]: any[] }; // Dados para a lista ativa
}

const AdminConfigContent: React.FC<AdminConfigContentProps> = ({
    onEdit,
    onDelete,
    onCreateNew,
    onSubmit,
    onCancelForm,
    currentConfigItem,
    configType,
    showConfigForm,
    loadingConfig,
    configData
}) => {
    const [activeTab, setActiveTab] = useState<ConfigTabKey>('centro_custo');
    const [isCreatingFullInstance, setIsCreatingFullInstance] = useState(false);
    const [selectedTreeItem, setSelectedTreeItem] = useState<any>(null);

    // Estados para filtros
    const [selectedDepartamento, setSelectedDepartamento] = useState<string>('');
    const [selectedSetor, setSelectedSetor] = useState<string>('');
    const [selectedStatus, setSelectedStatus] = useState<string>(''); // Filtro de status para todas as abas
    const [selectedTipoTeste, setSelectedTipoTeste] = useState<string>(''); // Filtro tipo_teste para aba tipos_testes
    const [selectedCategoria, setSelectedCategoria] = useState<string>(''); // Filtro categoria para aba tipos_testes
    const [selectedSubcategoria, setSelectedSubcategoria] = useState<string>(''); // Filtro subcategoria para aba tipos_testes
    const [searchTerm, setSearchTerm] = useState<string>(''); // Campo de pesquisa para todas as abas
    const [departamentos, setDepartamentos] = useState<any[]>([]);
    const [setores, setSetores] = useState<any[]>([]);

    // Carregar dados para filtros
    useEffect(() => {
        const loadFilterData = async () => {
            try {
                const [deptData, setorData] = await Promise.all([
                    departamentoService.getDepartamentos(),
                    setorService.getSetores()
                ]);
                setDepartamentos(deptData);
                setSetores(setorData);
            } catch (error) {
                console.error('Erro ao carregar dados dos filtros:', error);
            }
        };
        loadFilterData();
    }, []);

    // Filtrar setores baseado no departamento selecionado
    const setoresFiltrados = selectedDepartamento
        ? setores.filter(setor => setor.departamento === selectedDepartamento)
        : setores;

    // Debug: Log quando o componente é renderizado
    useEffect(() => {
        console.log('🔧 AdminConfigContent renderizado');
        console.log('📋 activeTab:', activeTab);
        console.log('📊 configData keys:', Object.keys(configData || {}));
    }, [activeTab, configData]);

    // Efeito para mudar o tipo de configuração se a aba mudar
    useEffect(() => {
        if (activeTab === 'setores' || activeTab === 'hierarchy') {
            // Se necessário, dispara uma recarga de dados ou atualização de estado no pai
        }
    }, [activeTab]);

    const handleCreateNewForTab = (tabType: ConfigTabKey) => {
        setActiveTab(tabType);
        if (tabType === 'setores') { // Ajustado para 'setores' em vez de 'full_sector'
            setIsCreatingFullInstance(true);
        }
        // Chamar a função onCreateNew do componente pai
        onCreateNew();
    };

    const handleTreeSelect = (item: any) => {
        console.log('🌳 Admin - Item selecionado na árvore:', item.name, item.type);
        setSelectedTreeItem(item);

        // Mostrar informações do item selecionado
        if (item.type === 'setor') {
            console.log('📋 Setor selecionado:', item.data);
            // Mostrar toast com informações do setor
            toast.info(`Setor selecionado: ${item.name}. Use os botões de ação para editar.`);
        }

        // NÃO chama onEdit automaticamente - apenas seleciona o item
        // Para editar, o usuário deve usar os botões específicos de edição
    };

    // Função para filtrar dados baseado nos filtros selecionados
    const getFilteredData = (data: any[], tabType: ConfigTabKey) => {
        if (!data) return [];

        let filtered = [...data];

        // Aplicar filtro de departamento (para todas as abas exceto centro_custo)
        if (selectedDepartamento && tabType !== 'centro_custo') {
            filtered = filtered.filter(item =>
                item.departamento === selectedDepartamento
            );
        }

        // Aplicar filtro de setor (para abas que têm setor)
        if (selectedSetor && ['tipos_maquina', 'tipos_testes', 'atividades', 'descricao_atividades', 'falhas', 'causas_retrabalho'].includes(tabType)) {
            filtered = filtered.filter(item =>
                item.setor === selectedSetor
            );
        }

        // Aplicar filtro de tipo_teste (apenas para aba tipos_testes)
        if (selectedTipoTeste && tabType === 'tipos_testes') {
            filtered = filtered.filter(item =>
                item.tipo_teste === selectedTipoTeste
            );
        }

        // Aplicar filtro de categoria (apenas para aba tipos_testes)
        if (selectedCategoria && tabType === 'tipos_testes') {
            filtered = filtered.filter(item =>
                item.categoria === selectedCategoria
            );
        }

        // Aplicar filtro de subcategoria (apenas para aba tipos_testes)
        if (selectedSubcategoria && tabType === 'tipos_testes') {
            const subcategoriaValue = selectedSubcategoria === 'especiais' ? 1 : 0;
            filtered = filtered.filter(item =>
                item.subcategoria === subcategoriaValue
            );
        }

        // Aplicar filtro de status (para todas as abas)
        if (selectedStatus) {
            if (selectedStatus === 'ativo') {
                filtered = filtered.filter(item => item.ativo === true);
            } else if (selectedStatus === 'inativo') {
                filtered = filtered.filter(item => item.ativo === false);
            }
        }

        // Aplicar filtro de pesquisa (para todas as abas)
        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            filtered = filtered.filter(item => {
                // Pesquisar em diferentes campos dependendo do tipo
                const searchFields = [];
                if (item.nome) searchFields.push(item.nome);
                if (item.nome_tipo) searchFields.push(item.nome_tipo);
                if (item.descricao) searchFields.push(item.descricao);
                if (item.tipo_teste) searchFields.push(item.tipo_teste);
                if (item.categoria) searchFields.push(item.categoria);
                if (item.codigo) searchFields.push(item.codigo);

                return searchFields.some(field =>
                    field && field.toLowerCase().includes(searchLower)
                );
            });
        }

        return filtered;
    };

    // Componente de filtros
    const renderFilters = () => {
        // Mostrar filtros para todas as abas exceto hierarchy
        const tabsWithoutFilters = ['hierarchy'];

        if (tabsWithoutFilters.includes(activeTab)) {
            return null;
        }

        // Definir quais filtros mostrar para cada aba conforme especificado
        const showDepartamentoFilter = ['setores', 'tipos_maquina', 'tipos_testes', 'atividades', 'descricao_atividades', 'falhas', 'causas_retrabalho'].includes(activeTab);
        const showSetorFilter = ['tipos_maquina', 'tipos_testes', 'atividades', 'descricao_atividades', 'falhas', 'causas_retrabalho'].includes(activeTab);
        const showStatusFilter = true; // Mostrar em todas as abas

        return (
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {/* Campo de Pesquisa - SEMPRE PRESENTE */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Pesquisar
                        </label>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Nome, descrição, tipo..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                        />
                    </div>

                    {/* Filtro de Departamento */}
                    {showDepartamentoFilter && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Departamento
                            </label>
                            <select
                                value={selectedDepartamento}
                                onChange={(e) => setSelectedDepartamento(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                                disabled={false}
                            >
                                <option value="">Todos os Departamentos</option>
                                {departamentos.map((dept) => (
                                    <option key={dept.id} value={dept.nome_tipo || dept.nome}>
                                        {dept.nome_tipo || dept.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {/* Filtro de Setor */}
                    {showSetorFilter && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Setor
                            </label>
                            <select
                                value={selectedSetor}
                                onChange={(e) => setSelectedSetor(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                                disabled={false}
                            >
                                <option value="">Todos os Setores</option>
                                {setoresFiltrados.map((setor) => (
                                    <option key={setor.id} value={setor.nome}>
                                        {setor.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {/* Filtro de Tipo de Teste - apenas para aba tipos_testes */}
                    {activeTab === 'tipos_testes' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Tipo de Teste
                            </label>
                            <select
                                value={selectedTipoTeste}
                                onChange={(e) => setSelectedTipoTeste(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                            >
                                <option value="">Todos os Tipos</option>
                                {configData.tipos_testes && [...new Set(configData.tipos_testes.map(item => item.tipo_teste).filter(Boolean))].sort().map(tipo => (
                                    <option key={tipo} value={tipo}>{tipo}</option>
                                ))}
                            </select>
                        </div>
                    )}

                    {/* Filtro de Categoria - apenas para aba tipos_testes */}
                    {activeTab === 'tipos_testes' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Categoria
                            </label>
                            <select
                                value={selectedCategoria}
                                onChange={(e) => setSelectedCategoria(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                            >
                                <option value="">Todas as Categorias</option>
                                <option value="Visual">Visual</option>
                                <option value="Elétricos">Elétricos</option>
                                <option value="Mecânicos">Mecânicos</option>
                            </select>
                        </div>
                    )}

                    {/* Filtro de Subcategoria - apenas para aba tipos_testes */}
                    {activeTab === 'tipos_testes' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Subcategoria
                            </label>
                            <select
                                value={selectedSubcategoria}
                                onChange={(e) => setSelectedSubcategoria(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                            >
                                <option value="">Todas as Subcategorias</option>
                                <option value="padrao">Padrão</option>
                                <option value="especiais">Especiais</option>
                            </select>
                        </div>
                    )}

                    {/* Filtro de Status */}
                    {showStatusFilter && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Status
                            </label>
                            <select
                                value={selectedStatus}
                                onChange={(e) => setSelectedStatus(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                            >
                                <option value="">Todos</option>
                                <option value="ativo">Ativo</option>
                                <option value="inativo">Inativo</option>
                            </select>
                        </div>
                    )}
                </div>

                {/* Botão Limpar Filtros */}
                <div className="mt-4 flex justify-end">
                    <button
                        onClick={() => {
                            setSelectedDepartamento('');
                            setSelectedSetor('');
                            setSelectedStatus('');
                            setSelectedTipoTeste('');
                            setSelectedCategoria('');
                            setSelectedSubcategoria('');
                            setSearchTerm('');
                        }}
                        className="px-4 py-2 text-sm text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                        Limpar Filtros
                    </button>
                </div>
            </div>
        );
    };

    const renderListContent = () => {
        if (loadingConfig) {
            return <div className="p-4 text-center">Carregando...</div>;
        }

        console.log('🎯 Renderizando aba:', activeTab);
        switch (activeTab) {
            case 'centro_custo':
                return (
                    <CentroCustoList
                        data={getFilteredData(configData.centro_custo || [], 'centro_custo')}
                        onEdit={(centroCusto) => onEdit(centroCusto, 'centro_custo')}
                        onDelete={async (centroCusto) => await onDelete('centro_custo', centroCusto)}
                        onCreateNew={() => handleCreateNewForTab('centro_custo')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'setores':
                return (
                    <SetorList
                        data={getFilteredData(configData.setores || [], 'setores')}
                        onEdit={(setor) => onEdit(setor, 'setores')}
                        onDelete={async (setor) => await onDelete('setores', setor)}
                        onCreateNew={() => handleCreateNewForTab('setores')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'tipos_maquina':
                return (
                    <TipoMaquinaList
                        data={getFilteredData(configData.tipos_maquina || [], 'tipos_maquina')}
                        onEdit={(tipoMaquina) => onEdit(tipoMaquina, 'tipos_maquina')}
                        onDelete={async (tipoMaquina) => await onDelete('tipos_maquina', tipoMaquina)}
                        onCreateNew={() => handleCreateNewForTab('tipos_maquina')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'tipos_testes':
                return (
                    <TipoTesteList
                        data={getFilteredData(configData.tipos_testes || [], 'tipos_testes')}
                        onEdit={(tipoTeste) => onEdit(tipoTeste, 'tipos_testes')}
                        onDelete={async (tipoTeste) => await onDelete('tipos_testes', tipoTeste)}
                        onCreateNew={() => handleCreateNewForTab('tipos_testes')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'atividades':
                return (
                    <TipoAtividadeList
                        data={getFilteredData(configData.atividades || [], 'atividades')}
                        onEdit={(atividade) => onEdit(atividade, 'atividades')}
                        onDelete={async (atividade) => await onDelete('atividades', atividade)}
                        onCreateNew={() => handleCreateNewForTab('atividades')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'descricao_atividades':
                return (
                    <DescricaoAtividadeList
                        data={getFilteredData(configData.descricao_atividades || [], 'descricao_atividades')}
                        onEdit={(descricaoAtividade) => onEdit(descricaoAtividade, 'descricao_atividades')}
                        onDelete={async (descricaoAtividade) => await onDelete('descricao_atividades', descricaoAtividade)}
                        onCreateNew={() => handleCreateNewForTab('descricao_atividades')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'falhas':
                return (
                    <TipoFalhaList
                        data={getFilteredData(configData.falhas || [], 'falhas')}
                        onEdit={(falha) => onEdit(falha, 'falhas')}
                        onDelete={async (falha) => await onDelete('falhas', falha)}
                        onCreateNew={() => handleCreateNewForTab('falhas')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'causas_retrabalho':
                return (
                    <CausaRetrabalhoList
                        data={getFilteredData(configData.causas_retrabalho || [], 'causas_retrabalho')}
                        onEdit={(causa) => onEdit(causa, 'causas_retrabalho')}
                        onDelete={async (causa) => await onDelete('causas_retrabalho', causa)}
                        onCreateNew={() => handleCreateNewForTab('causas_retrabalho')}
                        loading={loadingConfig}
                        error={null}
                    />
                );
            case 'hierarchy':
                console.log('🌳 Renderizando HierarchicalSectorViewer');
                try {
                    return (
                        <div>
                            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                <h4 className="font-medium text-blue-900 mb-2">🌳 Estrutura Hierárquica</h4>
                                <p className="text-sm text-blue-700">
                                    Visualize a estrutura organizacional completa. Clique nos ícones 📁/📂 para expandir/contrair.
                                    Use o botão "Selecionar" para escolher um setor específico.
                                </p>
                                {selectedTreeItem && (
                                    <div className="mt-2 p-2 bg-white border border-blue-300 rounded">
                                        <span className="text-sm font-medium text-blue-800">
                                            Item selecionado: {selectedTreeItem.name} ({selectedTreeItem.type})
                                        </span>
                                    </div>
                                )}
                            </div>
                            <HierarchicalSectorViewer
                                onSelectItem={handleTreeSelect}
                                selectedItemId={selectedTreeItem?.id}
                                height="600px"
                            />
                        </div>
                    );
                } catch (error) {
                    console.error('❌ Erro ao renderizar HierarchicalSectorViewer:', error);
                    return <div className="p-4 text-red-600">Erro ao carregar Estrutura Hierárquica: {(error as Error).message}</div>;
                }

            default:
                return null;
        }
    };

    const renderFormContent = () => {
        if (!showConfigForm || !configType) return null;

        switch (configType) {
            case 'centro_custo':
                return (
                    <DepartamentoForm
                        initialData={currentConfigItem}
                        onCancel={onCancelForm}
                        onSubmit={(data: any, isEdit: boolean) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );
            case 'setores':
                return (
                    <React.Fragment>
                        <SetorForm
                            initialData={currentConfigItem}
                            onCancel={onCancelForm}
                            onSubmit={(data: any, isEdit: boolean) => onSubmit(data, isEdit)}
                            isEdit={!!currentConfigItem}
                        />
                    </React.Fragment>
                );
            case 'tipos_maquina':
                return (
                    <TipoMaquinaForm
                        initialData={currentConfigItem ? { ...currentConfigItem, campos_teste_resultado: currentConfigItem.campos_teste_resultado || '[]' } : undefined}
                        onCancel={onCancelForm}
                        onSubmit={(data, isEdit) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );
            case 'tipos_testes':
                return (
                    <TipoTesteForm
                        initialData={currentConfigItem}
                        onCancel={onCancelForm}
                        onSubmit={(data, isEdit) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );
            case 'atividades':
                return (
                    <TipoAtividadeForm
                        initialData={currentConfigItem}
                        onCancel={onCancelForm}
                        onSubmit={(data, isEdit) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );
            case 'descricao_atividades':
                return (
                    <DescricaoAtividadeForm
                        initialData={currentConfigItem}
                        onCancel={onCancelForm}
                        onSubmit={(data, isEdit) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );
            case 'falhas':
                return (
                    <TipoFalhaForm
                        initialData={currentConfigItem}
                        onCancel={onCancelForm}
                        onSubmit={(data, isEdit) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );
            case 'causas_retrabalho':
                return (
                    <CausaRetrabalhoForm
                        initialData={currentConfigItem}
                        onCancel={onCancelForm}
                        onSubmit={(data, isEdit) => onSubmit(data, isEdit)}
                        isEdit={!!currentConfigItem}
                    />
                );

            default:
                return (
                    <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-sm">
                        <p className="text-gray-700">O formulário para "{configType}" ainda não foi implementado nesta nova interface.</p>
                        <button onClick={onCancelForm} className="mt-4 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">Voltar</button>
                    </div>
                );
        }
    };

    return (
        <div className="space-y-6">
            {/* Abas de Navegação para Configurações */}
            <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8 overflow-x-auto">
                    <button
                        onClick={() => setActiveTab('centro_custo')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'centro_custo'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        ⚙️🔌 Departamento
                    </button>
                    <button
                        onClick={() => setActiveTab('setores')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'setores'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        🏭 Setores
                    </button>
                    <button
                        onClick={() => setActiveTab('tipos_maquina')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'tipos_maquina'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        🔧 Tipos de Máquina
                    </button>
                    <button
                        onClick={() => setActiveTab('tipos_testes')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'tipos_testes'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        🧪 Tipos de Testes
                    </button>
                    <button
                        onClick={() => setActiveTab('atividades')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'atividades'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        📋 Atividades
                    </button>
                    <button
                        onClick={() => setActiveTab('descricao_atividades')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'descricao_atividades'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        📄 Descrição de Atividades
                    </button>
                    <button
                        onClick={() => setActiveTab('falhas')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'falhas'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        ⚠️ Tipos de Falha
                    </button>
                    <button
                        onClick={() => setActiveTab('causas_retrabalho')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'causas_retrabalho'
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        🔄 Causas de Retrabalho
                    </button>

                    {/* Abas de navegação especial */}
                    <button
                        onClick={() => setActiveTab('hierarchy')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${activeTab === 'hierarchy'
                            ? 'border-purple-500 text-purple-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        🌳 Estrutura Hierárquica
                    </button>
                </nav>
            </div>

            {/* Filtros */}
            {!showConfigForm && renderFilters()}

            {/* Conteúdo da Aba Ativa */}
            <div className="mt-6">
                {showConfigForm ? (
                    renderFormContent()
                ) : (
                    renderListContent()
                )}
            </div>
        </div>
    );
};

export default AdminConfigContent;