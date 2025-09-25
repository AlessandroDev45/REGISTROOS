import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import { getStatusColorClass } from '../../../../utils/statusColors';
import api from '../../../../services/api';

interface DashboardMetric {
    title: string;
    value: string | number;
    subtitle: string;
    color: 'blue' | 'green' | 'yellow' | 'purple' | 'red' | 'gray';
    icon: string;
    trend?: 'up' | 'down' | 'stable';
    trendValue?: string;
}

interface PerformanceData {
    periodo: string;
    osConcluidas: number;
    tempoMedio: number;
    eficiencia: number;
    pendencias: number;
}

interface ApontamentoDetalhado {
    id: number;
    numero_os: string;
    cliente: string;
    nome_tecnico: string;
    data_hora_inicio: string;
    data_hora_fim: string;
    tempo_trabalhado: number;
    status_apontamento: string;
    aprovado_supervisor: boolean;
    tipo_atividade: string;
    descricao_atividade: string;
}

const DashTabContent: React.FC = () => {
    const { setorAtivo } = useSetor();
    const { user } = useAuth();
    const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'quarter'>('week');
    const [filtroUsuario, setFiltroUsuario] = useState<string>('');
    const [dataInicio, setDataInicio] = useState<string>('');
    const [dataFim, setDataFim] = useState<string>('');
    const [performanceData, setPerformanceData] = useState<PerformanceData[]>([]);
    const [apontamentos, setApontamentos] = useState<ApontamentoDetalhado[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            setLoading(true);
            try {
                console.log('🔍 Buscando dados reais do dashboard...', { user, setorAtivo });

                // Buscar apontamentos detalhados reais
                const params: any = {};

                // Filtros baseados no privilégio do usuário
                if (user?.privilege_level === 'USER') {
                    params.nome_tecnico = user.nome_completo;
                } else if (user?.privilege_level === 'SUPERVISOR') {
                    params.setor = user.setor;
                } else if (user?.privilege_level === 'GESTAO') {
                    params.departamento = user.departamento;
                }
                // ADMIN vê todos

                // Filtros de período
                if (dataInicio) params.data_inicio = dataInicio;
                if (dataFim) params.data_fim = dataFim;
                if (filtroUsuario) params.nome_tecnico = filtroUsuario;

                const response = await api.get('/apontamentos-detalhados', { params });
                console.log('📊 Dados recebidos:', response.data);

                const apontamentosData: ApontamentoDetalhado[] = Array.isArray(response.data) ? response.data : [];
                setApontamentos(apontamentosData);

                // Calcular métricas reais baseadas nos apontamentos
                const calcularMetricas = (apontamentos: ApontamentoDetalhado[]) => {
                    // Agrupar apontamentos por OS única
                    const osUnicas = new Set(apontamentos.map(a => a.numero_os));
                    const osConcluidas = osUnicas.size;

                    // Calcular tempo médio por OS
                    const tempoTotalPorOS = new Map<string, number>();
                    apontamentos.forEach(a => {
                        const atual = tempoTotalPorOS.get(a.numero_os) || 0;
                        tempoTotalPorOS.set(a.numero_os, atual + a.tempo_trabalhado);
                    });

                    const tempoMedio = osConcluidas > 0 ?
                        Array.from(tempoTotalPorOS.values()).reduce((a, b) => a + b, 0) / osConcluidas : 0;

                    // Calcular eficiência (apontamentos aprovados vs total)
                    const aprovados = apontamentos.filter(a => a.aprovado_supervisor).length;
                    const eficiencia = apontamentos.length > 0 ? (aprovados / apontamentos.length) * 100 : 0;

                    // Contar pendências (não aprovados)
                    const pendencias = apontamentos.filter(a => !a.aprovado_supervisor).length;

                    return {
                        osConcluidas,
                        tempoMedio,
                        eficiencia,
                        pendencias
                    };
                };

                const metricas = calcularMetricas(apontamentosData);

                // Criar dados de performance baseados nos dados reais
                const realData: PerformanceData[] = [{
                    periodo: selectedPeriod === 'week' ? 'Esta Semana' :
                             selectedPeriod === 'month' ? 'Este Mês' : 'Este Trimestre',
                    osConcluidas: metricas.osConcluidas,
                    tempoMedio: metricas.tempoMedio,
                    eficiencia: metricas.eficiencia,
                    pendencias: metricas.pendencias
                }];

                setPerformanceData(realData);

            } catch (error) {
                console.error('❌ Erro ao buscar dados do dashboard:', error);
                setApontamentos([]);
                setPerformanceData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [setorAtivo, selectedPeriod, dataInicio, dataFim, filtroUsuario]);

    const currentData = performanceData[0] || {
        periodo: 'Atual',
        osConcluidas: 0,
        tempoMedio: 0,
        eficiencia: 0,
        pendencias: 0
    };

    const metrics: DashboardMetric[] = [
        {
            title: 'OS Trabalhadas',
            value: currentData.osConcluidas,
            subtitle: selectedPeriod === 'week' ? 'Esta semana' : selectedPeriod === 'month' ? 'Este mês' : 'Este trimestre',
            color: 'blue',
            icon: '✅',
            trend: 'stable',
            trendValue: `${currentData.osConcluidas} OS únicas`
        },
        {
            title: 'Tempo Médio',
            value: `${currentData.tempoMedio.toFixed(1)}h`,
            subtitle: 'Por OS',
            color: 'green',
            icon: '⏱️',
            trend: 'stable',
            trendValue: `Baseado em ${apontamentos.length} apontamentos`
        },
        {
            title: 'Pendências',
            value: currentData.pendencias,
            subtitle: 'Não Aprovadas',
            color: currentData.pendencias > 2 ? 'red' : currentData.pendencias > 0 ? 'yellow' : 'green',
            icon: currentData.pendencias > 2 ? '🚨' : currentData.pendencias > 0 ? '⚠️' : '✅',
            trend: 'stable',
            trendValue: `${currentData.pendencias} apontamentos pendentes`
        },
        {
            title: 'Taxa Aprovação',
            value: `${currentData.eficiencia.toFixed(1)}%`,
            subtitle: 'Apontamentos Aprovados',
            color: currentData.eficiencia >= 90 ? 'purple' : currentData.eficiencia >= 80 ? 'green' : 'yellow',
            icon: '📊',
            trend: 'stable',
            trendValue: `${apontamentos.filter(a => a.aprovado_supervisor).length}/${apontamentos.length} aprovados`
        }
    ];

    const getMetricCardStyle = (color: string) => {
        const colorMap = {
            blue: 'bg-blue-50 border-blue-200 text-blue-900',
            green: 'bg-green-50 border-green-200 text-green-900',
            yellow: 'bg-yellow-50 border-yellow-200 text-yellow-900',
            purple: 'bg-purple-50 border-purple-200 text-purple-900',
            red: 'bg-red-50 border-red-200 text-red-900',
            gray: 'bg-gray-50 border-gray-200 text-gray-900'
        };
        return colorMap[color as keyof typeof colorMap] || colorMap.gray;
    };

    const getTrendIcon = (trend?: string) => {
        switch (trend) {
            case 'up': return '📈';
            case 'down': return '📉';
            default: return '➡️';
        }
    };

    return (
        <div className="w-full p-6">
            <div className="bg-white rounded-lg shadow-sm">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                Dashboard de Performance - {setorAtivo?.nome}
                            </h2>
                            <p className="text-sm text-gray-600 mt-1">
                                Acompanhe o desempenho da equipe e métricas importantes
                            </p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setSelectedPeriod('week')}
                                className={`px-3 py-2 text-sm rounded-md ${
                                    selectedPeriod === 'week' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                Semana
                            </button>
                            <button
                                onClick={() => setSelectedPeriod('month')}
                                className={`px-3 py-2 text-sm rounded-md ${
                                    selectedPeriod === 'month' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                Mês
                            </button>
                            <button
                                onClick={() => setSelectedPeriod('quarter')}
                                className={`px-3 py-2 text-sm rounded-md ${
                                    selectedPeriod === 'quarter' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                            >
                                Trimestre
                            </button>
                        </div>
                    </div>

                    {/* Filtros Especiais para SUPERVISOR e ADMIN */}
                    {user && ['SUPERVISOR', 'ADMIN'].includes(user.privilege_level) && (
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
                            <h4 className="text-sm font-medium text-gray-700 mb-3">Filtros Avançados</h4>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">Colaborador</label>
                                    <input
                                        type="text"
                                        value={filtroUsuario}
                                        onChange={(e) => setFiltroUsuario(e.target.value)}
                                        placeholder="Filtrar por colaborador"
                                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">Data Início</label>
                                    <input
                                        type="date"
                                        value={dataInicio}
                                        onChange={(e) => setDataInicio(e.target.value)}
                                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-gray-600 mb-1">Data Fim</label>
                                    <input
                                        type="date"
                                        value={dataFim}
                                        onChange={(e) => setDataFim(e.target.value)}
                                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Key Metrics */}
                <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        {metrics.map((metric, index) => (
                            <div key={index} className={`rounded-lg border p-4 ${getMetricCardStyle(metric.color)}`}>
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="font-medium">{metric.title}</h4>
                                    <span className="text-xl">{metric.icon}</span>
                                </div>
                                <div className="text-2xl font-bold mb-1">{metric.value}</div>
                                <p className="text-sm opacity-75 mb-2">{metric.subtitle}</p>
                                {metric.trend && (
                                    <div className="flex items-center text-xs">
                                        <span className="mr-1">{getTrendIcon(metric.trend)}</span>
                                        <span>{metric.trendValue}</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Performance Chart */}
                    <div className="bg-gray-50 rounded-lg p-6">
                        <h4 className="font-medium text-gray-900 mb-4">📊 Resumo de Performance</h4>
                        <div className="h-64 bg-white border border-gray-200 rounded-lg flex items-center justify-center">
                            {loading ? (
                                <div className="text-center">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                                    <p className="text-gray-500">Carregando dados...</p>
                                </div>
                            ) : performanceData.length > 0 ? (
                                <div className="text-center w-full p-6">
                                    <div className="text-4xl mb-4">📈</div>
                                    <p className="text-gray-700 mb-6 font-medium">Dados Reais do Período Selecionado</p>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
                                        <div className="text-center bg-blue-50 p-4 rounded-lg">
                                            <div className="font-bold text-gray-900 text-lg">{currentData.periodo}</div>
                                            <div className="text-blue-600 font-semibold text-xl">{currentData.osConcluidas} OS</div>
                                            <div className="text-xs text-gray-500">Trabalhadas</div>
                                        </div>
                                        <div className="text-center bg-green-50 p-4 rounded-lg">
                                            <div className="font-bold text-gray-900 text-lg">Tempo Médio</div>
                                            <div className="text-green-600 font-semibold text-xl">{currentData.tempoMedio.toFixed(1)}h</div>
                                            <div className="text-xs text-gray-500">Por OS</div>
                                        </div>
                                        <div className="text-center bg-purple-50 p-4 rounded-lg">
                                            <div className="font-bold text-gray-900 text-lg">Taxa Aprovação</div>
                                            <div className="text-purple-600 font-semibold text-xl">{currentData.eficiencia.toFixed(1)}%</div>
                                            <div className="text-xs text-gray-500">Aprovados</div>
                                        </div>
                                        <div className="text-center bg-yellow-50 p-4 rounded-lg">
                                            <div className="font-bold text-gray-900 text-lg">Pendências</div>
                                            <div className="text-yellow-600 font-semibold text-xl">{currentData.pendencias}</div>
                                            <div className="text-xs text-gray-500">Não Aprovadas</div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center">
                                    <div className="text-4xl mb-4">📊</div>
                                    <p className="text-gray-500">Nenhum dado encontrado para o período selecionado</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Recent Activities */}
                    <div className="mt-8">
                        <h4 className="font-medium text-gray-900 mb-4">🕒 Apontamentos Recentes</h4>
                        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                                <h5 className="font-medium text-gray-900">Últimos Apontamentos do Setor</h5>
                            </div>
                            <div className="divide-y divide-gray-200">
                                {loading ? (
                                    <div className="px-6 py-8 text-center">
                                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
                                        <p className="text-gray-500 text-sm">Carregando apontamentos...</p>
                                    </div>
                                ) : apontamentos.length === 0 ? (
                                    <div className="px-6 py-8 text-center">
                                        <div className="text-gray-400 text-4xl mb-2">📋</div>
                                        <p className="text-gray-500">Nenhum apontamento encontrado</p>
                                    </div>
                                ) : (
                                    apontamentos.slice(0, 5).map((apontamento, index) => (
                                        <div key={apontamento.id} className="px-6 py-4 flex justify-between items-center">
                                            <div>
                                                <div className="font-medium text-gray-900">
                                                    OS {apontamento.numero_os || 'N/A'} - {apontamento.tipo_atividade || 'N/A'}
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    {apontamento.usuario || apontamento.nome_tecnico || 'N/A'} • {apontamento.aprovado_supervisor ? '✅ Aprovado' : '⏳ Pendente'} • {apontamento.data_inicio ? new Date(apontamento.data_inicio).toLocaleDateString('pt-BR') : 'N/A'}
                                                </div>
                                                <div className="text-xs text-gray-500">
                                                    Setor: {apontamento.setor || 'N/A'}
                                                </div>
                                            </div>
                                            <div className={`text-sm font-medium ${
                                                apontamento.aprovado_supervisor ? 'text-green-600' : 'text-yellow-600'
                                            }`}>
                                                {apontamento.tempo_trabalhado ? apontamento.tempo_trabalhado.toFixed(1) : '0.0'}h
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                            📊 Gerar Relatório
                        </button>
                        <button className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 transition-colors">
                            📈 Análise Detalhada
                        </button>
                        <button className="bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-700 transition-colors">
                            🎯 Metas do Setor
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashTabContent;
