import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../../components/Layout';

const GestaoPage: React.FC = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({
        totalUsers: 0,
        pendingUsers: 0,
        activeProjects: 0,
        completedTasks: 0
    });

    useEffect(() => {
        // Fetch management statistics
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            // This would normally fetch real statistics from the backend
            setStats({
                totalUsers: 45,
                pendingUsers: 3,
                activeProjects: 12,
                completedTasks: 156
            });
        } catch (error) {
            console.error('Erro ao buscar estatísticas:', error);
        }
    };

    return (
        <Layout>
            <div className="w-full p-4 md:p-6 lg:p-8">
                <h1 className="text-2xl font-bold text-gray-800 mb-6">Painel de Gestão</h1>

                {/* Statistics Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                    <span className="text-white text-sm font-bold">👥</span>
                                </div>
                            </div>
                            <div className="ml-4">
                                <h3 className="text-lg font-medium text-gray-900">Total de Usuários</h3>
                                <p className="text-2xl font-bold text-blue-600">{stats.totalUsers}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                                    <span className="text-white text-sm font-bold">⏳</span>
                                </div>
                            </div>
                            <div className="ml-4">
                                <h3 className="text-lg font-medium text-gray-900">Usuários Pendentes</h3>
                                <p className="text-2xl font-bold text-yellow-600">{stats.pendingUsers}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                                    <span className="text-white text-sm font-bold">📋</span>
                                </div>
                            </div>
                            <div className="ml-4">
                                <h3 className="text-lg font-medium text-gray-900">Projetos Ativos</h3>
                                <p className="text-2xl font-bold text-green-600">{stats.activeProjects}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                                    <span className="text-white text-sm font-bold">✅</span>
                                </div>
                            </div>
                            <div className="ml-4">
                                <h3 className="text-lg font-medium text-gray-900">Tarefas Concluídas</h3>
                                <p className="text-2xl font-bold text-purple-600">{stats.completedTasks}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Management Sections */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Recent Activities */}
                    <div className="bg-white rounded-lg shadow-sm">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900">Atividades Recentes</h2>
                        </div>
                        <div className="p-6">
                            <div className="space-y-4">
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                                    <div className="flex-1">
                                        <p className="text-sm text-gray-900">Novo usuário registrado</p>
                                        <p className="text-xs text-gray-500">2 horas atrás</p>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                                    <div className="flex-1">
                                        <p className="text-sm text-gray-900">OS #1234 foi atualizada</p>
                                        <p className="text-xs text-gray-500">4 horas atrás</p>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                                    <div className="flex-1">
                                        <p className="text-sm text-gray-900">Relatório mensal gerado</p>
                                        <p className="text-xs text-gray-500">1 dia atrás</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-white rounded-lg shadow-sm">
                        <div className="p-6 border-b border-gray-200">
                            <h2 className="text-lg font-semibold text-gray-900">Ações Rápidas</h2>
                        </div>
                        <div className="p-6">
                            <div className="grid grid-cols-2 gap-4">
                                <button className="p-4 bg-blue-50 hover:bg-blue-100 rounded-lg text-center transition-colors">
                                    <div className="text-2xl mb-2">📊</div>
                                    <div className="text-sm font-medium text-gray-900">Relatórios</div>
                                </button>
                                <button className="p-4 bg-green-50 hover:bg-green-100 rounded-lg text-center transition-colors">
                                    <div className="text-2xl mb-2">👥</div>
                                    <div className="text-sm font-medium text-gray-900">Usuários</div>
                                </button>
                                <button className="p-4 bg-yellow-50 hover:bg-yellow-100 rounded-lg text-center transition-colors">
                                    <div className="text-2xl mb-2">📋</div>
                                    <div className="text-sm font-medium text-gray-900">OS</div>
                                </button>
                                <button className="p-4 bg-purple-50 hover:bg-purple-100 rounded-lg text-center transition-colors">
                                    <div className="text-2xl mb-2">⚙️</div>
                                    <div className="text-sm font-medium text-gray-900">Configurações</div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Additional Management Content */}
                <div className="mt-6 bg-white rounded-lg shadow-sm">
                    <div className="p-6 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Visão Geral do Sistema</h2>
                    </div>
                    <div className="p-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="text-center">
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Setores Ativos</h3>
                                <p className="text-3xl font-bold text-blue-600">8</p>
                                <p className="text-sm text-gray-500 mt-1">Departamentos em operação</p>
                            </div>
                            <div className="text-center">
                                <h3 className="text-lg font-medium text-gray-900 mb-2">OS em Andamento</h3>
                                <p className="text-3xl font-bold text-orange-600">23</p>
                                <p className="text-sm text-gray-500 mt-1">Ordens de serviço ativas</p>
                            </div>
                            <div className="text-center">
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Eficiência</h3>
                                <p className="text-3xl font-bold text-green-600">94%</p>
                                <p className="text-sm text-gray-500 mt-1">Taxa de conclusão</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default GestaoPage;