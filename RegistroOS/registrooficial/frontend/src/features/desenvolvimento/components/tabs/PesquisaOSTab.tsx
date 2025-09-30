import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import api from '../../../../services/api';
import RelatorioCompletoModal from '../../../../components/RelatorioCompletoModal';
import { useCachedSetores } from '../../../../hooks/useCachedSetores';

interface ApontamentoDetalhado {
    id: number;
    numero_os: string;
    cliente: string;
    equipamento: string;
    data_hora_inicio: string;
    data_hora_fim: string;
    tempo_trabalhado: number;
    status_apontamento: string;
    setor: string;
    departamento: string;
    nome_tecnico: string;
    tipo_atividade: string;
    descricao_atividade: string;
    observacoes: string;
    observacao_os: string;
    foi_retrabalho: boolean;
    causa_retrabalho?: string;
    aprovado_supervisor: boolean;
    data_aprovacao_supervisor?: string;
    servico_de_campo: boolean;
}

interface PesquisaOSTabProps {
    setorFiltro?: string;
    onVerOS?: (osId: number) => void;
}

const PesquisaOSTab: React.FC<PesquisaOSTabProps> = ({ setorFiltro, onVerOS }) => {
    const { setorAtivo } = useSetor();
    const { user } = useAuth();
    const { todosSetores } = useCachedSetores();
    const [apontamentos, setApontamentos] = useState<ApontamentoDetalhado[]>([]);
    const [osAgrupadas, setOsAgrupadas] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [relatorioModalOpen, setRelatorioModalOpen] = useState(false);
    const [selectedOsId, setSelectedOsId] = useState<number | null>(null);

    // Estados para filtros
    const [filtros, setFiltros] = useState({
        numeroOS: '',
        cliente: '',
        equipamento: '',
        departamento: '',
        setor: '',
        colaborador: '',
        tecnico: '',
        tipoAtividade: '',
        dataInicio: '',
        dataFim: '',
        status: '',
        prioridade: '',
        responsavel: ''
    });

    const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
    const [colaboradoresDisponiveis, setColaboradoresDisponiveis] = useState<string[]>([]);
    const [departamentosDisponiveis, setDepartamentosDisponiveis] = useState<string[]>([]);
    const [statusDisponiveis, setStatusDisponiveis] = useState<string[]>([]);
    const [prioridadesDisponiveis, setPrioridadesDisponiveis] = useState<string[]>([]);

    const [pagination, setPagination] = useState({
        page: 1,
        per_page: 50,
        total: 0,
        total_pages: 0,
        has_next: false,
        has_prev: false
    });

    // Função para aplicar filtros localmente
    const aplicarFiltrosLocais = (osArray: any[]) => {
        return osArray.filter(os => {
            // Filtro por número OS
            if (filtros.numeroOS && !os.numero_os?.toString().includes(filtros.numeroOS)) {
                return false;
            }

            // Filtro por cliente
            if (filtros.cliente && !os.cliente?.toLowerCase().includes(filtros.cliente.toLowerCase())) {
                return false;
            }

            // Filtro por departamento
            if (filtros.departamento && os.departamento !== filtros.departamento) {
                return false;
            }

            // Filtro por setor
            if (filtros.setor && os.setor !== filtros.setor) {
                return false;
            }

            // Filtro por colaborador/técnico
            if (filtros.colaborador && !os.colaboradores?.toLowerCase().includes(filtros.colaborador.toLowerCase())) {
                return false;
            }

            return true;
        });
    };

    const handlePesquisa = async (page: number = 1) => {
        setLoading(true);
        try {
            console.log('🔍 [GESTÃO] Buscando apontamentos detalhados...', { filtros, page, user });

            // Buscar apontamentos detalhados reais
            const params: any = {};

            // Adicionar filtros
            if (filtros.numeroOS) params.numero_os = filtros.numeroOS;
            if (filtros.status) params.status_apontamento = filtros.status;
            if (filtros.dataInicio) params.data_inicio = filtros.dataInicio;
            if (filtros.dataFim) params.data_fim = filtros.dataFim;
            if (filtros.cliente) params.cliente = filtros.cliente;
            if (filtros.tecnico) params.nome_tecnico = filtros.tecnico;
            if (filtros.tipoAtividade) params.tipo_atividade = filtros.tipoAtividade;
            if (filtros.departamento) params.departamento = filtros.departamento;
            if (filtros.setor) params.setor = filtros.setor;
            if (filtros.colaborador) params.nome_tecnico = filtros.colaborador;

            // Filtros baseados no privilégio do usuário (apenas se não houver filtros manuais)
            if (user?.privilege_level === 'USER') {
                // Usuários normais só veem seus próprios apontamentos
                params.nome_tecnico = user.nome_completo;
            } else if (user?.privilege_level === 'SUPERVISOR') {
                // Supervisores veem do seu setor, mas podem filtrar por outros setores se especificado
                if (!filtros.setor && user.setor) {
                    params.setor = user.setor;
                }
            } else if (user?.privilege_level === 'GESTAO') {
                // Gestão vê do seu departamento, mas pode filtrar por outros departamentos se especificado
                if (!filtros.departamento && user.departamento) {
                    params.departamento = user.departamento;
                }
            }
            // ADMIN vê todos sem restrições

            console.log('🚀 [GESTÃO] Fazendo requisição para /apontamentos-detalhados com params:', params);
            const response = await api.get('/apontamentos-detalhados', { params });
            console.log('📊 [GESTÃO] Resposta da API:', response.data);

            // Os dados já vêm no formato correto da API
            const apontamentosData: ApontamentoDetalhado[] = Array.isArray(response.data) ? response.data : [];

            console.log('✅ Apontamentos carregados:', apontamentosData.length, 'registros');
            setApontamentos(apontamentosData);

            // Agrupar por número de OS
            const osGrouped = apontamentosData.reduce((acc: any, apontamento: ApontamentoDetalhado) => {
                const osNum = apontamento.numero_os;
                if (!acc[osNum]) {
                    acc[osNum] = {
                        numero_os: osNum,
                        id_os: null, // Será preenchido depois
                        cliente: apontamento.cliente,
                        equipamento: apontamento.equipamento,
                        departamento: apontamento.departamento,
                        setor: apontamento.setor,
                        total_apontamentos: 0,
                        total_horas: 0,
                        colaboradores: new Set(),
                        status_geral: 'EM ANDAMENTO',
                        data_inicio: apontamento.data_hora_inicio,
                        data_fim: null,
                        apontamentos: []
                    };
                }

                acc[osNum].total_apontamentos += 1;
                acc[osNum].total_horas += apontamento.tempo_trabalhado || 0;
                acc[osNum].colaboradores.add(apontamento.nome_tecnico);
                acc[osNum].apontamentos.push(apontamento);

                // Atualizar data de fim se for mais recente
                if (apontamento.data_hora_fim && (!acc[osNum].data_fim || apontamento.data_hora_fim > acc[osNum].data_fim)) {
                    acc[osNum].data_fim = apontamento.data_hora_fim;
                }

                // Determinar status geral
                if (apontamento.aprovado_supervisor) {
                    acc[osNum].status_geral = 'APROVADO';
                } else if (apontamento.status_apontamento === 'FINALIZADO') {
                    acc[osNum].status_geral = 'FINALIZADO';
                }

                return acc;
            }, {});

            // Converter para array e adicionar colaboradores como string
            const osArray = Object.values(osGrouped).map((os: any) => ({
                ...os,
                colaboradores: Array.from(os.colaboradores).join(', ')
            }));

            // Buscar IDs reais das OSs via API
            try {
                const osNumeros = osArray.map(os => os.numero_os).filter(Boolean);
                if (osNumeros.length > 0) {
                    const idsResponse = await api.post('/desenvolvimento/buscar-ids-os', {
                        numeros_os: osNumeros
                    });

                    if (idsResponse.data && idsResponse.data.mapeamento) {
                        for (const os of osArray) {
                            if (os.numero_os && idsResponse.data.mapeamento[os.numero_os]) {
                                os.id_os = idsResponse.data.mapeamento[os.numero_os];
                                console.log(`✅ Mapeado OS ${os.numero_os} -> ID ${os.id_os}`);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Erro ao buscar IDs das OSs:', error);
            }

            // Aplicar filtros localmente também (para garantir que funcionem)
            const osArrayFiltrado = aplicarFiltrosLocais(osArray);
            console.log(`🔍 [GESTÃO] Filtros aplicados: ${osArray.length} -> ${osArrayFiltrado.length} resultados`);

            setOsAgrupadas(osArrayFiltrado);

            // Simular paginação no frontend
            setPagination({
                page: 1,
                per_page: 50,
                total: osArrayFiltrado.length,
                total_pages: Math.ceil(osArrayFiltrado.length / 50),
                has_next: false,
                has_prev: false
            });

        } catch (error) {
            console.error('❌ [GESTÃO] Erro ao buscar apontamentos:', error);
            console.error('❌ [GESTÃO] Detalhes do erro:', error.response?.data || error.message);
            setApontamentos([]);
            setOsAgrupadas([]);
        } finally {
            setLoading(false);
        }
    };

    const handlePageChange = (newPage: number) => {
        if (newPage >= 1 && newPage <= pagination.total_pages) {
            handlePesquisa(newPage);
        }
    };

    // Carregar dados dinâmicos para filtros
    const carregarDadosFiltros = async () => {
        try {
            // Carregar departamentos da API
            try {
                console.log('🏢 [GESTÃO] Carregando departamentos...');
                const deptResponse = await api.get('/admin/departamentos');
                console.log('🏢 [GESTÃO] Resposta departamentos:', deptResponse.data);
                if (deptResponse.data && Array.isArray(deptResponse.data)) {
                    const departamentos = deptResponse.data.map((dept: any) => dept.nome || dept.nome_departamento).filter(Boolean);
                    setDepartamentosDisponiveis(departamentos);
                    console.log('✅ [GESTÃO] Departamentos carregados:', departamentos);
                } else {
                    console.warn('⚠️ [GESTÃO] Resposta de departamentos não é um array:', deptResponse.data);
                    setDepartamentosDisponiveis(['MOTORES', 'GERADORES', 'TRANSFORMADORES']);
                }
            } catch (deptError) {
                console.error('❌ [GESTÃO] Erro ao carregar departamentos:', deptError);
                console.error('❌ [GESTÃO] Detalhes do erro departamentos:', deptError.response?.data || deptError.message);
                // Fallback para departamentos padrão
                setDepartamentosDisponiveis(['MOTORES', 'GERADORES', 'TRANSFORMADORES']);
            }

            // Status padrão do sistema
            setStatusDisponiveis([
                'PROGRAMADA',
                'EM_ANDAMENTO',
                'PENDENTE',
                'FINALIZADA',
                'TERMINADA',
                'CANCELADA'
            ]);

            // Prioridades padrão do sistema
            setPrioridadesDisponiveis([
                'URGENTE',
                'ALTA',
                'NORMAL',
                'BAIXA'
            ]);

            console.log('✅ Dados dos filtros carregados');
        } catch (error) {
            console.error('Erro ao carregar dados dos filtros:', error);
            // Fallback para valores padrão
            setDepartamentosDisponiveis(['MOTORES', 'GERADORES', 'TRANSFORMADORES']);
            setStatusDisponiveis(['FINALIZADA', 'EM_ANDAMENTO', 'PENDENTE']);
            setPrioridadesDisponiveis(['URGENTE', 'ALTA', 'NORMAL', 'BAIXA']);
        }
    };

    useEffect(() => {
        // Carregar dados iniciais
        carregarDadosFiltros();
        handlePesquisa();
    }, []);

    useEffect(() => {
        if (setorAtivo) {
            handlePesquisa(1);
        }
    }, [setorAtivo]);

    const handleFiltroChange = (campo: string, valor: string) => {
        console.log(`🔧 [GESTÃO] Filtro alterado - ${campo}: ${valor}`);
        setFiltros(prev => ({ ...prev, [campo]: valor }));
    };

    // Função para reaplicar filtros sem nova requisição à API
    const reaplicarFiltros = () => {
        if (apontamentos.length > 0) {
            console.log('🔄 [GESTÃO] Reaplicando filtros localmente...');

            // Reagrupar dados originais
            const osGrouped = apontamentos.reduce((acc: any, apontamento: ApontamentoDetalhado) => {
                const osNum = apontamento.numero_os;
                if (!acc[osNum]) {
                    acc[osNum] = {
                        numero_os: osNum,
                        id_os: null,
                        cliente: apontamento.cliente,
                        equipamento: apontamento.equipamento,
                        departamento: apontamento.departamento,
                        setor: apontamento.setor,
                        total_apontamentos: 0,
                        total_horas: 0,
                        colaboradores: new Set(),
                        status_geral: 'EM ANDAMENTO',
                        data_inicio: apontamento.data_hora_inicio,
                        data_fim: null,
                        apontamentos: []
                    };
                }

                acc[osNum].total_apontamentos += 1;
                acc[osNum].total_horas += apontamento.tempo_trabalhado || 0;
                acc[osNum].colaboradores.add(apontamento.nome_tecnico);
                acc[osNum].apontamentos.push(apontamento);

                if (apontamento.data_hora_fim && (!acc[osNum].data_fim || apontamento.data_hora_fim > acc[osNum].data_fim)) {
                    acc[osNum].data_fim = apontamento.data_hora_fim;
                }

                if (apontamento.aprovado_supervisor) {
                    acc[osNum].status_geral = 'APROVADO';
                } else if (apontamento.status_apontamento === 'FINALIZADO') {
                    acc[osNum].status_geral = 'FINALIZADO';
                }

                return acc;
            }, {});

            const osArray = Object.values(osGrouped).map((os: any) => ({
                ...os,
                colaboradores: Array.from(os.colaboradores).join(', ')
            }));

            // Aplicar filtros
            const osArrayFiltrado = aplicarFiltrosLocais(osArray);
            console.log(`🔍 [GESTÃO] Filtros reaplicados: ${osArray.length} -> ${osArrayFiltrado.length} resultados`);

            setOsAgrupadas(osArrayFiltrado);

            setPagination(prev => ({
                ...prev,
                total: osArrayFiltrado.length,
                total_pages: Math.ceil(osArrayFiltrado.length / 50)
            }));
        }
    };

    const handleLimparFiltros = () => {
        console.log('🧹 [GESTÃO] Limpando filtros...');
        setFiltros({
            numeroOS: '',
            cliente: '',
            equipamento: '',
            departamento: '',
            setor: '',
            colaborador: '',
            tecnico: '',
            tipoAtividade: '',
            dataInicio: '',
            dataFim: '',
            status: '',
            prioridade: '',
            responsavel: ''
        });

        // Reaplicar filtros (agora vazios) para mostrar todos os dados
        setTimeout(() => {
            reaplicarFiltros();
        }, 100); // Pequeno delay para garantir que o estado foi atualizado
    };





    return (
        <div className="w-full p-6">
            <div className="bg-white rounded-lg shadow-sm">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                🔍 Pesquisa de Apontamentos - {setorAtivo?.nome}
                            </h2>
                            <p className="text-sm text-gray-600 mt-1">
                                Busque e filtre apontamentos detalhados do setor
                            </p>
                        </div>
                        <div className="flex items-center space-x-3">
                            <span className="text-sm text-gray-500">
                                {apontamentos.length} apontamento(s) encontrado(s)
                            </span>
                            <button
                                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                                className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                            >
                                {showAdvancedFilters ? '🔽' : '🔼'} Filtros Avançados
                            </button>
                        </div>
                    </div>
                </div>

                {/* Basic Filters */}
                <div className="p-6 border-b border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Número OS
                            </label>
                            <input
                                type="text"
                                value={filtros.numeroOS}
                                onChange={(e) => handleFiltroChange('numeroOS', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Ex: 20203"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Cliente
                            </label>
                            <input
                                type="text"
                                value={filtros.cliente}
                                onChange={(e) => handleFiltroChange('cliente', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Nome do cliente"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Técnico
                            </label>
                            <input
                                type="text"
                                value={filtros.tecnico}
                                onChange={(e) => handleFiltroChange('tecnico', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Nome do técnico"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Departamento
                            </label>
                            <select
                                value={filtros.departamento}
                                onChange={(e) => handleFiltroChange('departamento', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Todos os departamentos</option>
                                {departamentosDisponiveis.map((dept) => (
                                    <option key={dept} value={dept}>
                                        {dept}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Setor
                            </label>
                            <select
                                value={filtros.setor}
                                onChange={(e) => handleFiltroChange('setor', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Todos os setores</option>
                                {todosSetores.map((setor, index) => (
                                    <option key={`setor-${index}-${setor.nome}`} value={setor.nome}>
                                        {setor.nome}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Status
                            </label>
                            <select
                                value={filtros.status}
                                onChange={(e) => handleFiltroChange('status', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Todos</option>
                                                {statusDisponiveis.map((status, index) => (
                                                    <option key={`status-${index}`} value={status}>
                                                        {status}
                                                    </option>
                                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Data Início
                            </label>
                            <input
                                type="date"
                                value={filtros.dataInicio}
                                onChange={(e) => handleFiltroChange('dataInicio', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Data Fim
                            </label>
                            <input
                                type="date"
                                value={filtros.dataFim}
                                onChange={(e) => handleFiltroChange('dataFim', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    </div>

                    {/* Advanced Filters */}
                    {showAdvancedFilters && (
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Equipamento
                                </label>
                                <input
                                    type="text"
                                    value={filtros.equipamento}
                                    onChange={(e) => handleFiltroChange('equipamento', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Tipo de equipamento"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Prioridade
                                </label>
                                <select
                                    value={filtros.prioridade}
                                    onChange={(e) => handleFiltroChange('prioridade', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Todas</option>
                                                    {prioridadesDisponiveis.map((prioridade, index) => (
                                                        <option key={`prioridade-${index}`} value={prioridade}>
                                                            {prioridade}
                                                        </option>
                                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Responsável
                                </label>
                                <input
                                    type="text"
                                    value={filtros.responsavel}
                                    onChange={(e) => handleFiltroChange('responsavel', e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Nome do responsável"
                                />
                            </div>
                        </div>
                    )}

                    <div className="mt-4 flex space-x-2">
                        <button
                            onClick={() => {
                                console.log('🔍 [GESTÃO] Botão Pesquisar clicado!');
                                if (apontamentos.length > 0) {
                                    console.log('🔄 [GESTÃO] Reaplicando filtros...');
                                    reaplicarFiltros();
                                } else {
                                    console.log('🚀 [GESTÃO] Fazendo nova busca...');
                                    handlePesquisa(1);
                                }
                            }}
                            disabled={loading}
                            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? '🔄 Buscando...' : '🔍 Pesquisar'}
                        </button>
                        <button
                            onClick={() => {
                                console.log('🔄 [GESTÃO] Recarregando dados da API...');
                                handlePesquisa(1);
                            }}
                            disabled={loading}
                            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            🔄 Recarregar Dados
                        </button>
                        <button
                            onClick={handleLimparFiltros}
                            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                        >
                            🧹 Limpar Filtros
                        </button>
                    </div>
                </div>

                {/* Results */}
                <div className="p-6">
                    {loading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                            <span className="ml-2">Buscando apontamentos...</span>
                        </div>
                    ) : osAgrupadas.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">📋</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                Nenhuma OS encontrada
                            </h3>
                            <p className="text-gray-500">
                                Tente ajustar os filtros de pesquisa
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Número OS
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Cliente
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Equipamento
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Departamento/Setor
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Colaboradores
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Total Horas
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Ações
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {osAgrupadas.map((os, index) => (
                                        <tr key={`os-${os.numero_os}-${index}`} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {os.numero_os || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {os.cliente || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={os.equipamento || 'N/A'}>
                                                {os.equipamento || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {os.departamento || 'N/A'} / {os.setor || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={os.colaboradores}>
                                                {os.colaboradores || 'N/A'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {os.total_horas ? `${os.total_horas.toFixed(2)}h` : '0h'}
                                                <div className="text-xs text-gray-500">
                                                    {os.total_apontamentos} apontamento(s)
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                                    os.status_geral === 'APROVADO' ? 'bg-green-100 text-green-800' :
                                                    os.status_geral === 'FINALIZADO' ? 'bg-blue-100 text-blue-800' :
                                                    'bg-yellow-100 text-yellow-800'
                                                }`}>
                                                    {os.status_geral}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <div className="flex space-x-2">
                                                    <button
                                                        onClick={() => {
                                                            console.log('🔍 Ver relatório da OS:', os.numero_os, 'ID:', os.id_os);
                                                            if (os.id_os) {
                                                                setSelectedOsId(os.id_os);
                                                                setRelatorioModalOpen(true);
                                                            } else {
                                                                alert('ID da OS não encontrado. Tente recarregar a página.');
                                                            }
                                                        }}
                                                        className="text-blue-600 hover:text-blue-900 px-3 py-1 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
                                                        title="Ver Relatório Completo"
                                                        disabled={!os.id_os}
                                                    >
                                                        📊 Ver Relatório
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Controles de Paginação */}
                    {!loading && apontamentos.length > 0 && (
                        <div className="mt-6 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
                            <div className="flex flex-1 justify-between sm:hidden">
                                <button
                                    onClick={() => handlePageChange(pagination.page - 1)}
                                    disabled={!pagination.has_prev}
                                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Anterior
                                </button>
                                <button
                                    onClick={() => handlePageChange(pagination.page + 1)}
                                    disabled={!pagination.has_next}
                                    className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Próxima
                                </button>
                            </div>
                            <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                                <div>
                                    <p className="text-sm text-gray-700">
                                        Mostrando{' '}
                                        <span className="font-medium">
                                            {((pagination.page - 1) * pagination.per_page) + 1}
                                        </span>{' '}
                                        até{' '}
                                        <span className="font-medium">
                                            {Math.min(pagination.page * pagination.per_page, pagination.total)}
                                        </span>{' '}
                                        de{' '}
                                        <span className="font-medium">{pagination.total}</span> resultados
                                    </p>
                                </div>
                                <div>
                                    <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                                        <button
                                            onClick={() => handlePageChange(pagination.page - 1)}
                                            disabled={!pagination.has_prev}
                                            className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            <span className="sr-only">Anterior</span>
                                            ←
                                        </button>

                                        {/* Números das páginas */}
                                        {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                                            let pageNum;
                                            if (pagination.total_pages <= 5) {
                                                pageNum = i + 1;
                                            } else if (pagination.page <= 3) {
                                                pageNum = i + 1;
                                            } else if (pagination.page >= pagination.total_pages - 2) {
                                                pageNum = pagination.total_pages - 4 + i;
                                            } else {
                                                pageNum = pagination.page - 2 + i;
                                            }

                                            return (
                                                <button
                                                    key={pageNum}
                                                    onClick={() => handlePageChange(pageNum)}
                                                    className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                                                        pageNum === pagination.page
                                                            ? 'z-10 bg-blue-600 text-white focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                                                            : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0'
                                                    }`}
                                                >
                                                    {pageNum}
                                                </button>
                                            );
                                        })}

                                        <button
                                            onClick={() => handlePageChange(pagination.page + 1)}
                                            disabled={!pagination.has_next}
                                            className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            <span className="sr-only">Próxima</span>
                                            →
                                        </button>
                                    </nav>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Modal de Relatório Completo */}
            <RelatorioCompletoModal
                isOpen={relatorioModalOpen}
                onClose={() => {
                    setRelatorioModalOpen(false);
                    setSelectedOsId(null);
                }}
                osId={selectedOsId || 0}
                origemPagina="desenvolvimento"
            />
        </div>
    );
};

export default PesquisaOSTab;
