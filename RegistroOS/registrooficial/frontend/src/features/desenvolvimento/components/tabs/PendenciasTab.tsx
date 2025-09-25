import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../../../../services/api';
import ResolucaoPendenciaModal from '../../../../components/ResolucaoPendenciaModal';

import { getStatusColorClass, getPriorityColorClass } from '../../../../utils/statusColors';
interface Pendencia {
    id: number;
    numero_os: string;
    cliente: string;
    tipo_maquina: string;
    descricao_maquina: string;
    descricao_pendencia: string;
    status: 'ABERTA' | 'FECHADA';
    prioridade: 'BAIXA' | 'NORMAL' | 'ALTA' | 'URGENTE';
    data_inicio: string;
    data_fechamento?: string;
    responsavel_inicio_id: number;
    responsavel_fechamento_id?: number;
    apontamento_origem_id?: number;
    solucao_aplicada?: string;
    observacoes_fechamento?: string;
}

const PendenciasTab: React.FC = () => {
    const { setorAtivo } = useSetor();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [pendencias, setPendencias] = useState<Pendencia[]>([]);
    const [loading, setLoading] = useState(true);
    const [filtroStatus, setFiltroStatus] = useState<string>('');
    const [filtroPrioridade, setFiltroPrioridade] = useState<string>('');
    const [filtroCliente, setFiltroCliente] = useState<string>('');
    const [filtroResponsavel, setFiltroResponsavel] = useState<string>('');
    const [dataInicio, setDataInicio] = useState<string>('');
    const [dataFim, setDataFim] = useState<string>('');
    const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
    const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
    const [sortBy, setSortBy] = useState<'data' | 'prioridade' | 'status'>('data');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
    const [modalResolucaoOpen, setModalResolucaoOpen] = useState(false);
    const [pendenciaSelecionada, setPendenciaSelecionada] = useState<Pendencia | null>(null);

    useEffect(() => {
        const fetchPendencias = async () => {
            if (!user) return;

            setLoading(true);
            try {
                // Buscar pendências reais da API com filtros baseados no privilégio
                const params: any = {};
                if (filtroStatus) params.status = filtroStatus;
                if (dataInicio) params.data_inicio = dataInicio;
                if (dataFim) params.data_fim = dataFim;

                // Filtros baseados no privilégio do usuário
                if (user.privilege_level === 'USER') {
                    params.usuario_id = user.id;
                } else if (user.privilege_level === 'SUPERVISOR') {
                    params.setor = user.setor;
                }
                // ADMIN vê todas as pendências

                const response = await api.get('/pendencias', { params });

                setPendencias(response.data || []);
            } catch (error) {
                console.error('Erro ao buscar pendências:', error);
            } finally {
                setLoading(false);
            }
        };

        if (setorAtivo && user) {
            fetchPendencias();
        }
    }, [setorAtivo, user, filtroStatus, dataInicio, dataFim]);

    const handleResolverPendencia = (pendencia: Pendencia) => {
        setPendenciaSelecionada(pendencia);
        setModalResolucaoOpen(true);
    };

    const handleResolucaoSuccess = async () => {
        // Recarregar lista de pendências
        try {
            const response = await api.get('/pendencias', {
                params: {
                    status: filtroStatus || undefined
                }
            });
            setPendencias(response.data || []);
        } catch (error) {
            console.error('Erro ao recarregar pendências:', error);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'AGUARDANDO_APROVACAO': return 'bg-yellow-100 text-yellow-800';
            case 'EM_ANALISE': return 'bg-blue-100 text-blue-800';
            case 'APROVADO': return 'bg-green-100 text-green-800';
            case 'REJEITADO': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getPriorityColor = (prioridade: string) => {
        switch (prioridade) {
            case 'URGENTE': return 'bg-red-100 text-red-800';
            case 'ALTA': return 'bg-orange-100 text-orange-800';
            case 'NORMAL': return 'bg-blue-100 text-blue-800';
            case 'BAIXA': return 'bg-gray-100 text-gray-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    // Filtros e ordenação avançados
    const pendenciasFiltradas = pendencias
        .filter(pendencia => {
            if (filtroStatus && pendencia.status !== filtroStatus) return false;
            if (filtroPrioridade && pendencia.prioridade !== filtroPrioridade) return false;
            if (filtroCliente && !pendencia.cliente.toLowerCase().includes(filtroCliente.toLowerCase())) return false;
            if (dataInicio && pendencia.data_inicio && new Date(pendencia.data_inicio) < new Date(dataInicio)) return false;
            if (dataFim && pendencia.data_inicio && new Date(pendencia.data_inicio) > new Date(dataFim)) return false;
            return true;
        })
        .sort((a, b) => {
            let comparison = 0;
            switch (sortBy) {
                case 'data':
                    comparison = (a.data_inicio && b.data_inicio) ? (new Date(a.data_inicio).getTime() - new Date(b.data_inicio).getTime()) : 0;
                    break;
                case 'prioridade':
                    const prioridadeOrder = { 'URGENTE': 4, 'ALTA': 3, 'NORMAL': 2, 'BAIXA': 1 };
                    comparison = (prioridadeOrder[a.prioridade] || 0) - (prioridadeOrder[b.prioridade] || 0);
                    break;
                case 'status':
                    comparison = a.status.localeCompare(b.status);
                    break;
            }
            return sortOrder === 'asc' ? comparison : -comparison;
        });

    // Métricas calculadas
    const metricas = {
        total: pendencias.length,
        abertas: pendencias.filter(p => p.status === 'ABERTA').length,
        fechadas: pendencias.filter(p => p.status === 'FECHADA').length,
        urgentes: pendencias.filter(p => p.prioridade === 'URGENTE' && p.status === 'ABERTA').length,
        tempoMedioResolucao: pendencias
            .filter(p => p.status === 'FECHADA' && p.data_fechamento)
            .reduce((acc, p) => {
                if (!p.data_inicio || !p.data_fechamento) return acc;
                const inicio = new Date(p.data_inicio);
                const fim = new Date(p.data_fechamento);
                return acc + (fim.getTime() - inicio.getTime()) / (1000 * 60 * 60 * 24);
            }, 0) / Math.max(1, pendencias.filter(p => p.status === 'FECHADA').length)
    };

    const handleLimparFiltros = () => {
        setFiltroStatus('');
        setFiltroPrioridade('');
        setFiltroCliente('');
        setFiltroResponsavel('');
        setDataInicio('');
        setDataFim('');
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2">Carregando pendências...</span>
            </div>
        );
    }

    return (
        <div className="w-full p-6">
            <div className="bg-white rounded-lg shadow-sm">
                {/* Header com gradiente */}
                <div className="bg-gradient-to-r from-purple-600 to-indigo-700 p-6 text-white">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-3xl font-bold">
                                🚨 Pendências - {setorAtivo?.nome}
                            </h2>
                            <p className="text-purple-100 mt-2">
                                Gerencie e resolva pendências de apontamentos e testes
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-bold">{metricas.total}</div>
                            <div className="text-sm text-purple-200">Total de Pendências</div>
                        </div>
                    </div>
                </div>

                {/* Cards de Métricas */}
                <div className="p-6 border-b border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div className="bg-gradient-to-br from-red-500 to-red-600 text-white p-4 rounded-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-2xl font-bold">{metricas.abertas}</div>
                                    <div className="text-sm text-red-100">Pendências Abertas</div>
                                </div>
                                <div className="text-3xl opacity-80">🔴</div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-4 rounded-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-2xl font-bold">{metricas.fechadas}</div>
                                    <div className="text-sm text-green-100">Pendências Resolvidas</div>
                                </div>
                                <div className="text-3xl opacity-80">✅</div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white p-4 rounded-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-2xl font-bold">{metricas.urgentes}</div>
                                    <div className="text-sm text-orange-100">Urgentes Abertas</div>
                                </div>
                                <div className="text-3xl opacity-80">🚨</div>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-4 rounded-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-2xl font-bold">{metricas.tempoMedioResolucao.toFixed(1)}</div>
                                    <div className="text-sm text-blue-100">Dias Médio Resolução</div>
                                </div>
                                <div className="text-3xl opacity-80">⏱️</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Filtros Avançados */}
                <div className="p-6 border-b border-gray-200">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-medium text-gray-900">🔍 Filtros e Visualização</h3>
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                                className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                            >
                                {showAdvancedFilters ? '🔼 Filtros Simples' : '🔽 Filtros Avançados'}
                            </button>
                            <div className="flex bg-gray-100 rounded-md p-1">
                                <button
                                    onClick={() => setViewMode('cards')}
                                    className={`px-3 py-1 text-sm rounded ${viewMode === 'cards' ? 'bg-white shadow-sm' : ''}`}
                                >
                                    📋 Cards
                                </button>
                                <button
                                    onClick={() => setViewMode('table')}
                                    className={`px-3 py-1 text-sm rounded ${viewMode === 'table' ? 'bg-white shadow-sm' : ''}`}
                                >
                                    📊 Tabela
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Filtros Básicos */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                            <select
                                value={filtroStatus}
                                onChange={(e) => setFiltroStatus(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value="">Todos os Status</option>
                                <option value="ABERTA">🔴 Aberta</option>
                                <option value="FECHADA">✅ Fechada</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Prioridade</label>
                            <select
                                value={filtroPrioridade}
                                onChange={(e) => setFiltroPrioridade(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value="">Todas as Prioridades</option>
                                <option value="URGENTE">🚨 Urgente</option>
                                <option value="ALTA">🔥 Alta</option>
                                <option value="NORMAL">📋 Normal</option>
                                <option value="BAIXA">📝 Baixa</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Ordenar por</label>
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as any)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value="data">📅 Data</option>
                                <option value="prioridade">⚡ Prioridade</option>
                                <option value="status">📊 Status</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Ordem</label>
                            <select
                                value={sortOrder}
                                onChange={(e) => setSortOrder(e.target.value as any)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value="desc">⬇️ Decrescente</option>
                                <option value="asc">⬆️ Crescente</option>
                            </select>
                        </div>
                    </div>

                    {/* Filtros Avançados */}
                    {showAdvancedFilters && (
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Cliente</label>
                                <input
                                    type="text"
                                    value={filtroCliente}
                                    onChange={(e) => setFiltroCliente(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    placeholder="Nome do cliente..."
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Data Início</label>
                                <input
                                    type="date"
                                    value={dataInicio}
                                    onChange={(e) => setDataInicio(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Data Fim</label>
                                <input
                                    type="date"
                                    value={dataFim}
                                    onChange={(e) => setDataFim(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                            </div>
                            <div className="flex items-end">
                                <button
                                    onClick={handleLimparFiltros}
                                    className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                                >
                                    🧹 Limpar Filtros
                                </button>
                            </div>
                        </div>
                    )}

                    <div className="flex justify-between items-center mt-4">
                        <span className="text-sm text-gray-500">
                            📊 {pendenciasFiltradas.length} de {metricas.total} pendência(s) encontrada(s)
                        </span>
                        {metricas.urgentes > 0 && (
                            <div className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                                🚨 {metricas.urgentes} urgente(s) pendente(s)
                            </div>
                        )}
                    </div>
                </div>

                {/* Lista de Pendências */}
                <div className="p-6">
                    {pendenciasFiltradas.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">
                                {metricas.total === 0 ? '🎉' : '🔍'}
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                {metricas.total === 0 ? 'Parabéns! Nenhuma pendência!' : 'Nenhuma pendência encontrada'}
                            </h3>
                            <p className="text-gray-500">
                                {metricas.total === 0
                                    ? 'Todas as pendências foram resolvidas com sucesso!'
                                    : 'Tente ajustar os filtros para encontrar as pendências desejadas'
                                }
                            </p>
                            {metricas.total > 0 && (
                                <button
                                    onClick={handleLimparFiltros}
                                    className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                                >
                                    🧹 Limpar Todos os Filtros
                                </button>
                            )}
                        </div>
                    ) : viewMode === 'cards' ? (
                        /* Visualização em Cards */
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {pendenciasFiltradas.map((pendencia) => {
                                const diasAberta = pendencia.data_inicio ? Math.floor((new Date().getTime() - new Date(pendencia.data_inicio).getTime()) / (1000 * 60 * 60 * 24)) : 0;
                                const isUrgente = pendencia.prioridade === 'URGENTE';
                                const isVencida = diasAberta > 7 && pendencia.status === 'ABERTA';

                                return (
                                    <div
                                        key={pendencia.id}
                                        className={`border-2 rounded-xl p-6 hover:shadow-lg transition-all duration-300 ${
                                            isUrgente ? 'border-red-300 bg-red-50' :
                                            isVencida ? 'border-orange-300 bg-orange-50' :
                                            'border-gray-200 bg-white hover:border-purple-300'
                                        }`}
                                    >
                                        {/* Header do Card */}
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-3 mb-2">
                                                    <h3 className="text-xl font-bold text-gray-900">
                                                        📋 OS {pendencia.numero_os}
                                                    </h3>
                                                    <span className={`inline-flex px-3 py-1 text-xs font-bold rounded-full ${
                                                        pendencia.status === 'ABERTA' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                                                    }`}>
                                                        {pendencia.status === 'ABERTA' ? '🔴 ABERTA' : '✅ FECHADA'}
                                                    </span>
                                                    <span className={`inline-flex px-3 py-1 text-xs font-bold rounded-full ${getPriorityColor(pendencia.prioridade)}`}>
                                                        {pendencia.prioridade === 'URGENTE' ? '🚨' :
                                                         pendencia.prioridade === 'ALTA' ? '🔥' :
                                                         pendencia.prioridade === 'NORMAL' ? '📋' : '📝'} {pendencia.prioridade}
                                                    </span>
                                                </div>

                                                {/* Indicadores de Tempo */}
                                                <div className="flex items-center space-x-4 mb-3">
                                                    <span className={`text-sm font-medium ${
                                                        isVencida ? 'text-red-600' : 'text-gray-600'
                                                    }`}>
                                                        ⏱️ {diasAberta} dia(s) em aberto
                                                    </span>
                                                    {isVencida && (
                                                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-bold">
                                                            ⚠️ VENCIDA
                                                        </span>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Botão de Ação */}
                                            <div className="ml-4">
                                                {pendencia.status === 'ABERTA' ? (
                                                    <button
                                                        onClick={() => handleResolverPendencia(pendencia)}
                                                        className={`px-6 py-3 text-white text-sm font-medium rounded-lg transition-all duration-200 ${
                                                            isUrgente ? 'bg-red-600 hover:bg-red-700 shadow-lg' :
                                                            'bg-purple-600 hover:bg-purple-700'
                                                        }`}
                                                    >
                                                        🔧 Resolver Agora
                                                    </button>
                                                ) : (
                                                    <div className="bg-green-100 text-green-800 px-6 py-3 rounded-lg font-medium">
                                                        ✅ Resolvida
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Informações Principais */}
                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div className="bg-gray-50 p-3 rounded-lg">
                                                <div className="text-xs text-gray-500 font-medium">CLIENTE</div>
                                                <div className="text-sm font-semibold text-gray-900">{pendencia.cliente}</div>
                                            </div>
                                            <div className="bg-gray-50 p-3 rounded-lg">
                                                <div className="text-xs text-gray-500 font-medium">DATA ABERTURA</div>
                                                <div className="text-sm font-semibold text-gray-900">
                                                    {pendencia.data_inicio ? new Date(pendencia.data_inicio).toLocaleDateString('pt-BR') : 'Data não informada'}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Equipamento */}
                                        <div className="bg-blue-50 p-3 rounded-lg mb-4">
                                            <div className="text-xs text-blue-600 font-medium">EQUIPAMENTO</div>
                                            <div className="text-sm font-semibold text-blue-900">{pendencia.descricao_maquina}</div>
                                            <div className="text-xs text-blue-700">{pendencia.tipo_maquina}</div>
                                        </div>

                                        {/* Descrição da Pendência */}
                                        <div className="border-t border-gray-200 pt-4">
                                            <div className="text-xs text-gray-500 font-medium mb-2">DESCRIÇÃO DA PENDÊNCIA</div>
                                            <p className="text-sm text-gray-700 mb-3 leading-relaxed">
                                                {pendencia.descricao_pendencia}
                                            </p>

                                            {/* Solução e Observações */}
                                            {pendencia.solucao_aplicada && (
                                                <div className="bg-green-50 p-3 rounded-lg mb-3">
                                                    <div className="text-xs text-green-600 font-medium">SOLUÇÃO APLICADA</div>
                                                    <p className="text-sm text-green-800">{pendencia.solucao_aplicada}</p>
                                                </div>
                                            )}
                                            {pendencia.observacoes_fechamento && (
                                                <div className="bg-gray-50 p-3 rounded-lg">
                                                    <div className="text-xs text-gray-500 font-medium">OBSERVAÇÕES</div>
                                                    <p className="text-sm text-gray-700">{pendencia.observacoes_fechamento}</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        /* Visualização em Tabela */
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OS</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Equipamento</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prioridade</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dias Aberta</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {pendenciasFiltradas.map((pendencia) => {
                                        const diasAberta = pendencia.data_inicio ? Math.floor((new Date().getTime() - new Date(pendencia.data_inicio).getTime()) / (1000 * 60 * 60 * 24)) : 0;
                                        const isVencida = diasAberta > 7 && pendencia.status === 'ABERTA';

                                        return (
                                            <tr key={pendencia.id} className={`hover:bg-gray-50 ${isVencida ? 'bg-red-50' : ''}`}>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    {pendencia.numero_os}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {pendencia.cliente}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={pendencia.descricao_maquina}>
                                                    {pendencia.descricao_maquina}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                                        pendencia.status === 'ABERTA' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                                                    }`}>
                                                        {pendencia.status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(pendencia.prioridade)}`}>
                                                        {pendencia.prioridade}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    <span className={isVencida ? 'text-red-600 font-bold' : ''}>
                                                        {diasAberta} dia(s)
                                                        {isVencida && ' ⚠️'}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                    {pendencia.status === 'ABERTA' ? (
                                                        <button
                                                            onClick={() => handleResolverPendencia(pendencia)}
                                                            className="text-purple-600 hover:text-purple-900 font-medium"
                                                        >
                                                            🔧 Resolver
                                                        </button>
                                                    ) : (
                                                        <span className="text-green-600">✅ Resolvida</span>
                                                    )}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Modal de Resolução de Pendência */}
            <ResolucaoPendenciaModal
                isOpen={modalResolucaoOpen}
                onClose={() => {
                    setModalResolucaoOpen(false);
                    setPendenciaSelecionada(null);
                }}
                pendencia={pendenciaSelecionada}
                onSuccess={handleResolucaoSuccess}
            />
        </div>
    );
};

export default PendenciasTab;
