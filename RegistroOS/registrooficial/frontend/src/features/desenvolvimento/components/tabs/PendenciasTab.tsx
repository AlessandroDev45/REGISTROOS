import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../../../../services/api';


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
    data_criacao: string;
    data_fechamento?: string;
    responsavel_inicio_id: number;
    responsavel_fechamento_id?: number;
    apontamento_origem_id?: number;
    solucao_aplicada?: string;
    observacoes_fechamento?: string;
}

interface PendenciasTabProps {
    onResolverViaApontamento?: (pendencia: Pendencia) => void;
}

const PendenciasTab: React.FC<PendenciasTabProps> = ({ onResolverViaApontamento }) => {
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

                // DESENVOLVIMENTO: Sempre filtra apenas pelo setor do usuário logado
                // O backend já aplica o filtro automaticamente baseado no setor do usuário

                const response = await api.get('/desenvolvimento/pendencias', { params });

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
        <div className="w-full p-3">
            <div className="bg-white rounded shadow-sm">
                {/* Header técnico compacto */}
                <div className="bg-slate-800 border-b border-slate-700 px-4 py-3 text-white">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-lg font-semibold tracking-wide">
                                PENDÊNCIAS - {setorAtivo?.nome?.toUpperCase()}
                            </h2>
                            <p className="text-slate-400 text-xs font-mono">
                                Gestão de Pendências | Apontamentos e Testes
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-2xl font-mono font-bold">{metricas.total}</div>
                            <div className="text-xs text-slate-400 uppercase">Total</div>
                        </div>
                    </div>
                </div>

                {/* Métricas compactas */}
                <div className="px-4 py-2 border-b border-slate-200 bg-slate-50">
                    <div className="grid grid-cols-4 gap-3">
                        <div className="bg-white border-l-4 border-red-500 px-3 py-2">
                            <div className="text-lg font-mono font-bold text-red-700">{metricas.abertas}</div>
                            <div className="text-xs text-slate-600 uppercase">Abertas</div>
                        </div>
                        <div className="bg-white border-l-4 border-green-500 px-3 py-2">
                            <div className="text-lg font-mono font-bold text-green-700">{metricas.fechadas}</div>
                            <div className="text-xs text-slate-600 uppercase">Resolvidas</div>
                        </div>
                        <div className="bg-white border-l-4 border-orange-500 px-3 py-2">
                            <div className="text-lg font-mono font-bold text-orange-700">{metricas.urgentes}</div>
                            <div className="text-xs text-slate-600 uppercase">Críticas</div>
                        </div>
                        <div className="bg-white border-l-4 border-blue-500 px-3 py-2">
                            <div className="text-lg font-mono font-bold text-blue-700">{metricas.tempoMedioResolucao.toFixed(1)}</div>
                            <div className="text-xs text-slate-600 uppercase">Dias Médio</div>
                        </div>
                    </div>
                </div>

                {/* Filtros compactos */}
                <div className="px-4 py-3 border-b border-gray-200 bg-white">
                    <div className="flex justify-between items-center mb-3">
                        <h3 className="text-sm font-semibold text-gray-800 uppercase tracking-wide">Filtros</h3>
                        <div className="flex items-center space-x-2">
                            <button
                                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                                className="px-2 py-1 text-xs bg-slate-100 text-slate-700 rounded hover:bg-slate-200"
                            >
                                {showAdvancedFilters ? 'Simples' : 'Avançado'}
                            </button>
                            <div className="flex bg-slate-100 rounded text-xs">
                                <button
                                    onClick={() => setViewMode('cards')}
                                    className={`px-2 py-1 rounded ${viewMode === 'cards' ? 'bg-white shadow-sm' : ''}`}
                                >
                                    Cards
                                </button>
                                <button
                                    onClick={() => setViewMode('table')}
                                    className={`px-2 py-1 rounded ${viewMode === 'table' ? 'bg-white shadow-sm' : ''}`}
                                >
                                    Tabela
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Filtros compactos */}
                    <div className="grid grid-cols-4 gap-2">
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Status</label>
                            <select
                                value={filtroStatus}
                                onChange={(e) => setFiltroStatus(e.target.value)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500"
                            >
                                <option value="">Todos</option>
                                <option value="ABERTA">Aberta</option>
                                <option value="FECHADA">Fechada</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Prioridade</label>
                            <select
                                value={filtroPrioridade}
                                onChange={(e) => setFiltroPrioridade(e.target.value)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500"
                            >
                                <option value="">Todas</option>
                                <option value="URGENTE">Urgente</option>
                                <option value="ALTA">Alta</option>
                                <option value="NORMAL">Normal</option>
                                <option value="BAIXA">Baixa</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Ordenar</label>
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as any)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500"
                            >
                                <option value="data">Data</option>
                                <option value="prioridade">Prioridade</option>
                                <option value="status">Status</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-gray-600 mb-1">Ordem</label>
                            <select
                                value={sortOrder}
                                onChange={(e) => setSortOrder(e.target.value as any)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-slate-500"
                            >
                                <option value="desc">Desc</option>
                                <option value="asc">Asc</option>
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

                {/* Lista compacta */}
                <div className="p-3">
                    {pendenciasFiltradas.length === 0 ? (
                        <div className="text-center py-8">
                            <div className="text-gray-400 text-4xl mb-3">
                                {metricas.total === 0 ? '✓' : '?'}
                            </div>
                            <h3 className="text-sm font-medium text-gray-900 mb-1">
                                {metricas.total === 0 ? 'Nenhuma pendência' : 'Nenhuma pendência encontrada'}
                            </h3>
                            <p className="text-xs text-gray-500">
                                {metricas.total === 0
                                    ? 'Todas resolvidas'
                                    : 'Ajuste os filtros'
                                }
                            </p>
                            {metricas.total > 0 && (
                                <button
                                    onClick={handleLimparFiltros}
                                    className="mt-3 px-3 py-1 bg-slate-600 text-white text-xs rounded hover:bg-slate-700"
                                >
                                    Limpar Filtros
                                </button>
                            )}
                        </div>
                    ) : viewMode === 'cards' ? (
                        /* Cards compactos */
                        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-3">
                            {pendenciasFiltradas.map((pendencia) => {
                                const diasAberta = pendencia.data_inicio ? Math.floor((new Date().getTime() - new Date(pendencia.data_inicio).getTime()) / (1000 * 60 * 60 * 24)) : 0;
                                const isUrgente = pendencia.prioridade === 'URGENTE';
                                const isVencida = diasAberta > 7 && pendencia.status === 'ABERTA';

                                return (
                                    <div
                                        key={pendencia.id}
                                        className={`border rounded p-3 hover:shadow-md transition-shadow ${
                                            isUrgente ? 'border-red-400 bg-red-50' :
                                            isVencida ? 'border-orange-400 bg-orange-50' :
                                            'border-gray-300 bg-white hover:border-slate-400'
                                        }`}
                                    >
                                        {/* Header compacto */}
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <h3 className="text-sm font-bold text-gray-900 font-mono">
                                                        OS {pendencia.numero_os}
                                                    </h3>
                                                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                                                        pendencia.status === 'ABERTA' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                                                    }`}>
                                                        {pendencia.status}
                                                    </span>
                                                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${getPriorityColor(pendencia.prioridade)}`}>
                                                        {pendencia.prioridade}
                                                    </span>
                                                </div>

                                                {/* Indicadores compactos */}
                                                <div className="flex items-center space-x-3 text-xs">
                                                    <span className={`font-medium ${
                                                        isVencida ? 'text-red-600' : 'text-gray-600'
                                                    }`}>
                                                        {diasAberta}d aberto
                                                    </span>
                                                    {isVencida && (
                                                        <span className="bg-red-100 text-red-800 px-1 py-0.5 rounded text-xs font-medium">
                                                            VENCIDA
                                                        </span>
                                                    )}
                                                </div>
                                            </div>

                                            {/* Botões compactos */}
                                            <div className="ml-2">
                                                {pendencia.status === 'ABERTA' ? (
                                                    <button
                                                        onClick={() => onResolverViaApontamento && onResolverViaApontamento(pendencia)}
                                                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded"
                                                        title="Resolver via apontamento"
                                                    >
                                                        Resolver
                                                    </button>
                                                ) : (
                                                    <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                                                        Resolvida
                                                    </div>
                                                )}
                                            </div>
                                        </div>

                                        {/* Informações compactas */}
                                        <div className="grid grid-cols-3 gap-2 mb-2 text-xs">
                                            <div>
                                                <div className="text-gray-500 font-medium">Cliente</div>
                                                <div className="font-semibold text-gray-900 truncate">{pendencia.cliente}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-500 font-medium">Equipamento</div>
                                                <div className="font-semibold text-gray-900 truncate">{pendencia.equipamento}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-500 font-medium">Data</div>
                                                <div className="font-semibold text-gray-900">
                                                    {pendencia.data_criacao ? new Date(pendencia.data_criacao).toLocaleDateString('pt-BR') : 'N/A'}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Descrição compacta */}
                                        <div className="border-t border-gray-200 pt-2">
                                            <div className="text-xs text-gray-500 font-medium mb-1">Descrição</div>
                                            <p className="text-xs text-gray-700 line-clamp-2">
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
                                        const diasAberta = pendencia.data_criacao ? Math.floor((new Date().getTime() - new Date(pendencia.data_criacao).getTime()) / (1000 * 60 * 60 * 24)) : 0;
                                        const isVencida = diasAberta > 7 && pendencia.status === 'ABERTA';

                                        return (
                                            <tr key={pendencia.id} className={`hover:bg-gray-50 ${isVencida ? 'bg-red-50' : ''}`}>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    {pendencia.numero_os}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {pendencia.cliente}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate" title={pendencia.equipamento}>
                                                    {pendencia.equipamento}
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
                                                            onClick={() => onResolverViaApontamento && onResolverViaApontamento(pendencia)}
                                                            className="text-blue-600 hover:text-blue-900 font-medium text-xs"
                                                            title="Resolver via apontamento"
                                                        >
                                                            📝 Resolver via Apontamento
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


        </div>
    );
};

export default PendenciasTab;
