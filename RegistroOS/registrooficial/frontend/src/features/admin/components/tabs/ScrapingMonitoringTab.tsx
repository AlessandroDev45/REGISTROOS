import React, { useState, useEffect } from 'react';
import api from '../../../../services/api';

interface ScrapingStats {
    dashboard_data: {
        periodo_dias: number;
        timestamp: string;
        estatisticas_gerais: {
            total_requests: number;
            successful_requests: number;
            failed_requests: number;
            success_rate: number;
            avg_processing_time: number;
        };
        status_fila: {
            workers_online: number;
            active_tasks: number;
            scheduled_tasks: number;
        };
        metricas_sistema: {
            total_os_sistema: number;
            os_via_scraping_periodo: number;
            percentual_scraping: number;
        };
        usuarios_mais_ativos: Array<{
            nome: string;
            email: string;
            departamento: string;
            total_requests: number;
        }>;
        horarios_maior_uso: Array<{
            hora: string;
            requests: number;
        }>;
        estatisticas_diarias: Array<{
            date: string;
            requests: number;
            success_rate: number;
        }>;
        top_os_consultadas: Array<{
            os_number: string;
            requests: number;
        }>;
    };
}

interface UsersRanking {
    ranking_usuarios: Array<{
        posicao: number;
        nome: string;
        email: string;
        departamento: string;
        nivel_privilegio: string;
        total_requests: number;
        successful_requests: number;
        failed_requests: number;
        success_rate: number;
        avg_processing_time: number;
        last_usage: string;
        first_usage: string;
        dias_usando: number;
    }>;
    periodo_dias: number;
    total_usuarios: number;
}

const ScrapingMonitoringTab: React.FC = () => {
    const [stats, setStats] = useState<ScrapingStats | null>(null);
    const [usersRanking, setUsersRanking] = useState<UsersRanking | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedPeriod, setSelectedPeriod] = useState(30);
    const [activeView, setActiveView] = useState<'dashboard' | 'users' | 'performance'>('dashboard');

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const [statsResponse, usersResponse] = await Promise.all([
                api.get(`/admin/scraping/dashboard?days=${selectedPeriod}`),
                api.get(`/admin/scraping/users-ranking?days=${selectedPeriod}`)
            ]);

            setStats(statsResponse.data);
            setUsersRanking(usersResponse.data);
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados';
            setError(errorMessage);
            console.error('Erro ao carregar estatísticas:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [selectedPeriod]);

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('pt-BR');
    };

    const formatDuration = (seconds: number) => {
        if (seconds < 60) return `${seconds.toFixed(1)}s`;
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                <span className="ml-3 text-gray-600">Carregando estatísticas...</span>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                    <div className="text-red-400">⚠️</div>
                    <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800">Erro ao carregar dados</h3>
                        <p className="text-sm text-red-700 mt-1">{error}</p>
                        <button
                            onClick={fetchData}
                            className="mt-2 text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded"
                        >
                            Tentar novamente
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">📊 Monitoramento de Scraping</h3>
                <div className="flex items-center space-x-4">
                    <select
                        value={selectedPeriod}
                        onChange={(e) => setSelectedPeriod(Number(e.target.value))}
                        className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                    >
                        <option value={7}>Últimos 7 dias</option>
                        <option value={30}>Últimos 30 dias</option>
                        <option value={90}>Últimos 90 dias</option>
                    </select>
                    <button
                        onClick={fetchData}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm"
                    >
                        🔄 Atualizar
                    </button>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveView('dashboard')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${
                            activeView === 'dashboard'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        📈 Dashboard
                    </button>
                    <button
                        onClick={() => setActiveView('users')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${
                            activeView === 'users'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        👥 Usuários
                    </button>
                    <button
                        onClick={() => setActiveView('performance')}
                        className={`py-2 px-1 border-b-2 font-medium text-sm ${
                            activeView === 'performance'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        ⚡ Performance
                    </button>
                </nav>
            </div>

            {/* Dashboard View */}
            {activeView === 'dashboard' && stats && (
                <div className="space-y-6">
                    {/* Estatísticas Gerais */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <div className="flex items-center">
                                <div className="text-blue-500 text-2xl">📊</div>
                                <div className="ml-3">
                                    <p className="text-sm font-medium text-blue-900">Total de Requests</p>
                                    <p className="text-2xl font-bold text-blue-600">
                                        {stats.dashboard_data?.estatisticas_gerais?.total_requests || 0}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-center">
                                <div className="text-green-500 text-2xl">✅</div>
                                <div className="ml-3">
                                    <p className="text-sm font-medium text-green-900">Taxa de Sucesso</p>
                                    <p className="text-2xl font-bold text-green-600">
                                        {(stats.dashboard_data?.estatisticas_gerais?.success_rate || 0).toFixed(1)}%
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <div className="flex items-center">
                                <div className="text-yellow-500 text-2xl">⏱️</div>
                                <div className="ml-3">
                                    <p className="text-sm font-medium text-yellow-900">Tempo Médio</p>
                                    <p className="text-2xl font-bold text-yellow-600">
                                        {formatDuration(stats.dashboard_data?.estatisticas_gerais?.avg_processing_time || 0)}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <div className="flex items-center">
                                <div className="text-purple-500 text-2xl">🔄</div>
                                <div className="ml-3">
                                    <p className="text-sm font-medium text-purple-900">Workers Online</p>
                                    <p className="text-2xl font-bold text-purple-600">
                                        {stats.dashboard_data?.status_fila?.workers_online || 0}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Métricas do Sistema */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-medium text-gray-900 mb-4">📋 Métricas do Sistema</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="text-center">
                                <p className="text-3xl font-bold text-gray-900">
                                    {stats.dashboard_data?.metricas_sistema?.total_os_sistema || 0}
                                </p>
                                <p className="text-sm text-gray-600">Total de OS no Sistema</p>
                            </div>
                            <div className="text-center">
                                <p className="text-3xl font-bold text-blue-600">
                                    {stats.dashboard_data?.metricas_sistema?.os_via_scraping_periodo || 0}
                                </p>
                                <p className="text-sm text-gray-600">OS via Scraping (período)</p>
                            </div>
                            <div className="text-center">
                                <p className="text-3xl font-bold text-green-600">
                                    {(stats.dashboard_data?.metricas_sistema?.percentual_scraping || 0).toFixed(1)}%
                                </p>
                                <p className="text-sm text-gray-600">% via Scraping</p>
                            </div>
                        </div>
                    </div>

                    {/* Usuários Mais Ativos */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-medium text-gray-900 mb-4">👥 Top 5 Usuários Mais Ativos</h4>
                        <div className="space-y-3">
                            {(stats.dashboard_data?.usuarios_mais_ativos || []).slice(0, 5).map((user, index) => (
                                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center">
                                        <div className="text-lg font-bold text-gray-500 w-8">#{index + 1}</div>
                                        <div className="ml-3">
                                            <p className="font-medium text-gray-900">{user?.nome || 'N/A'}</p>
                                            <p className="text-sm text-gray-600">{user?.departamento || 'N/A'}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-bold text-blue-600">{user?.total_requests || 0}</p>
                                        <p className="text-sm text-gray-600">requests</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Users View */}
            {activeView === 'users' && usersRanking && (
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-medium text-gray-900 mb-4">
                        👥 Ranking Completo de Usuários ({usersRanking?.total_usuarios || 0} usuários)
                    </h4>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pos</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Departamento</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requests</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Taxa Sucesso</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tempo Médio</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Último Uso</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {(usersRanking?.ranking_usuarios || []).map((user) => (
                                    <tr key={user?.posicao || index} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            #{user?.posicao || index + 1}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">{user?.nome || 'N/A'}</div>
                                                <div className="text-sm text-gray-500">{user?.email || 'N/A'}</div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {user?.departamento || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900">{user?.total_requests || 0}</div>
                                            <div className="text-xs text-gray-500">
                                                ✅ {user?.successful_requests || 0} | ❌ {user?.failed_requests || 0}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                                (user?.success_rate || 0) >= 90
                                                    ? 'bg-green-100 text-green-800'
                                                    : (user?.success_rate || 0) >= 70
                                                    ? 'bg-yellow-100 text-yellow-800'
                                                    : 'bg-red-100 text-red-800'
                                            }`}>
                                                {(user?.success_rate || 0).toFixed(1)}%
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                            {formatDuration(user?.avg_processing_time || 0)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {user?.last_usage ? formatDate(user.last_usage) : 'N/A'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Performance View */}
            {activeView === 'performance' && stats && (
                <div className="space-y-6">
                    {/* Horários de Maior Uso */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-medium text-gray-900 mb-4">⏰ Horários de Maior Uso</h4>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                            {(stats.dashboard_data?.horarios_maior_uso || []).map((horario, index) => (
                                <div key={horario?.hora || index} className="text-center p-3 bg-gray-50 rounded-lg">
                                    <p className="text-sm font-medium text-gray-900">{horario?.hora || 'N/A'}</p>
                                    <p className="text-lg font-bold text-blue-600">{horario?.requests || 0}</p>
                                    <p className="text-xs text-gray-500">requests</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Top OS Consultadas */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-medium text-gray-900 mb-4">🔍 Top OS Mais Consultadas</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {(stats.dashboard_data?.top_os_consultadas || []).slice(0, 9).map((os, index) => (
                                <div key={os?.os_number || index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center">
                                        <div className="text-sm font-bold text-gray-500 w-6">#{index + 1}</div>
                                        <div className="ml-2">
                                            <p className="font-medium text-gray-900">OS {os?.os_number || 'N/A'}</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-bold text-blue-600">{os?.requests || 0}</p>
                                        <p className="text-xs text-gray-500">consultas</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Footer com timestamp */}
            {stats && (
                <div className="text-center text-sm text-gray-500 border-t pt-4">
                    Última atualização: {stats.dashboard_data?.timestamp ? formatDate(stats.dashboard_data.timestamp) : 'N/A'}
                </div>
            )}
        </div>
    );
};

export default ScrapingMonitoringTab;
