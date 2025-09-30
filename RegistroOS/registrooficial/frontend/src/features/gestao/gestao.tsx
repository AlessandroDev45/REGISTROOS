import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../../components/Layout';
import PesquisaOSTab from '../desenvolvimento/components/tabs/PesquisaOSTab';
import RelatorioCompletoModal from '../../components/RelatorioCompletoModal';

interface TabItem {
    id: string;
    label: string;
    icon: string;
}

const GestaoPage: React.FC = () => {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState<string>('dashboard');
    const [stats, setStats] = useState({
        totalUsers: 0,
        pendingUsers: 0,
        activeProjects: 0,
        completedTasks: 0
    });

    // Estados para o modal de relatório
    const [relatorioModalOpen, setRelatorioModalOpen] = useState(false);
    const [selectedOsId, setSelectedOsId] = useState<number | null>(null);

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

    // Definir abas disponíveis
    const getAvailableTabs = (): TabItem[] => {
        const tabs: TabItem[] = [
            { id: 'dashboard', label: 'Dashboard Gestão', icon: '📊' },
            { id: 'consulta-os', label: 'Consulta OS', icon: '🔍' }
        ];
        return tabs;
    };

    const tabs = getAvailableTabs();

    const handleTabChange = (tabId: string) => {
        setActiveTab(tabId);
    };

    const renderTabContent = () => {
        switch (activeTab) {
            case 'consulta-os':
                return <PesquisaOSTab
                    onVerOS={(osId: number) => {
                        setSelectedOsId(osId);
                        setRelatorioModalOpen(true);
                    }}
                />;
            case 'dashboard':
            default:
                return renderDashboardContent();
        }
    };

    const renderDashboardContent = () => (
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
                                <span className="text-white text-sm font-bold">📊</span>
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

            {/* Management Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Gestão de Usuários</h3>
                    <p className="text-gray-600 mb-4">Gerencie usuários, permissões e acessos do sistema.</p>
                    <button className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                        Gerenciar Usuários
                    </button>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Relatórios</h3>
                    <p className="text-gray-600 mb-4">Acesse relatórios detalhados e análises de performance.</p>
                    <button className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
                        Ver Relatórios
                    </button>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Configurações</h3>
                    <p className="text-gray-600 mb-4">Configure parâmetros do sistema e preferências.</p>
                    <button className="w-full bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
                        Configurar
                    </button>
                </div>
            </div>
        </div>
    );

    return (
        <Layout>
            <div className="w-full">
                {/* Navigation Tabs */}
                <div className="bg-white border-b">
                    <div className="w-full px-4 sm:px-6 lg:px-8">
                        <nav className="flex space-x-8" aria-label="Tabs">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => handleTabChange(tab.id)}
                                    className={`${
                                        activeTab === tab.id
                                            ? 'border-blue-500 text-blue-600'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                                >
                                    <span>{tab.icon}</span>
                                    <span>{tab.label}</span>
                                </button>
                            ))}
                        </nav>
                    </div>
                </div>

                {/* Tab Content */}
                <div className="w-full">
                    {renderTabContent()}
                </div>

                {/* Modal de Relatório Completo */}
                {relatorioModalOpen && selectedOsId && (
                    <RelatorioCompletoModal
                        osId={selectedOsId}
                        isOpen={relatorioModalOpen}
                        onClose={() => {
                            setRelatorioModalOpen(false);
                            setSelectedOsId(null);
                        }}
                    />
                )}
            </div>
        </Layout>
    );
};

export default GestaoPage;