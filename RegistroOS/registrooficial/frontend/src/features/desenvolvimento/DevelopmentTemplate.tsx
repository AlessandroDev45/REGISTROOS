import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSetor } from '../../contexts/SetorContext';
import { ConfiguracaoSetor } from '../../pages/common/TiposApi';
import api from '../../services/api';

// Componentes das abas originais
import DashTab from './components/tabs/DashTab';
import ApontamentoFormTab from './components/tabs/ApontamentoFormTab';
import MinhasOsTab from './components/tabs/MinhasOsTab';
import PesquisaOSTab from './components/tabs/PesquisaOSTab';
import ProgramacaoTab from './components/tabs/ProgramacaoTab';
import PendenciasTab from './components/tabs/PendenciasTab';
import GerenciarTab from './components/tabs/GerenciarTab';
import AprovacaoUsuariosTab from './components/tabs/AprovacaoUsuariosTab';
import RelatorioCompletoModal from '../../components/RelatorioCompletoModal';

interface DevelopmentTemplateProps {
  sectorConfig: ConfiguracaoSetor;
  sectorKey: string;
}

const DevelopmentTemplate: React.FC<DevelopmentTemplateProps> = ({ sectorConfig, sectorKey }) => {
  const { user } = useAuth();
  const { setorAtivo } = useSetor();

  // Buscar contagem de programações para o setor
  useEffect(() => {
    const fetchProgramacoesCount = async () => {
      if (!setorAtivo) return;

      try {
        const response = await api.get('/desenvolvimento/programacao', {
          params: { status: 'PROGRAMADA' }
        });
        setProgramacoesCount(response.data?.length || 0);
      } catch (error) {
        console.error('Erro ao buscar programações:', error);
        setProgramacoesCount(0);
      }
    };

    fetchProgramacoesCount();

    // Atualizar a cada 30 segundos
    const interval = setInterval(fetchProgramacoesCount, 30000);
    return () => clearInterval(interval);
  }, [setorAtivo]);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [programacoesCount, setProgramacoesCount] = useState(0);

  // Estados para o formulário de apontamento
  interface FormData {
    supervisor_horas_orcadas: number;
    supervisor_testes_iniciais: boolean;
    supervisor_testes_parciais: boolean;
    supervisor_testes_finais: boolean;
    [key: string]: any;
  }

  const [formData, setFormData] = useState<FormData>({
    supervisor_horas_orcadas: 0,
    supervisor_testes_iniciais: false,
    supervisor_testes_parciais: false,
    supervisor_testes_finais: false
  });
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [testObservations, setTestObservations] = useState<Record<string, string>>({});

  // Estados para o modal de relatório completo
  const [relatorioModalOpen, setRelatorioModalOpen] = useState(false);
  const [selectedOsId, setSelectedOsId] = useState<number | null>(null);

  // Definir abas baseadas no nível de privilégio do usuário
  const getAvailableTabs = () => {
    const baseTabs = [
      { id: 'dashboard', label: 'Dashboard', icon: '📊' },
      { id: 'apontamento', label: 'Apontamento', icon: '📝' },
      { id: 'minhas-os', label: 'Meus Apontamentos', icon: '📋' },
      { id: 'pesquisa', label: 'Pesquisa Apontamentos', icon: '🔍' },
      {
        id: 'programacao',
        label: 'Programação',
        icon: '📅',
        badge: programacoesCount > 0 ? programacoesCount : undefined
      },
      { id: 'pendencias', label: 'Pendências', icon: '⚠️' }
    ];

    // Adicionar abas para supervisores e admins
    if (user?.privilege_level === 'SUPERVISOR' || user?.privilege_level === 'ADMIN') {
      baseTabs.push(
        { id: 'gerenciar', label: 'Gerenciar', icon: '⚙️' }
      );
    }

    // Adicionar aba de aprovação apenas para admins
    if (user?.privilege_level === 'ADMIN') {
      baseTabs.push(
        { id: 'aprovacao', label: 'Aprovação Usuários', icon: '👥' }
      );
    }

    return baseTabs;
  };

  const tabs = getAvailableTabs();

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
  };

  // Handlers para o formulário de apontamento
  const onTestResultChange = (testId: string, result: string) => {
    setTestResults((prev: Record<string, any>) => ({ ...prev, [testId]: result }));
  };

  const onTestCheckboxChange = (testId: string, checked: boolean) => {
    setTestResults((prev: Record<string, any>) => ({ ...prev, [testId]: checked }));
  };

  const onTestObservationChange = (testId: string, obs: string) => {
    setTestObservations((prev: Record<string, string>) => ({ ...prev, [testId]: obs }));
  };





  const handleSupervisorHorasOrcadasChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev: FormData) => ({ ...prev, supervisor_horas_orcadas: parseFloat(e.target.value) || 0 }));
  };

  const handleSupervisorTestesIniciaisChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev: FormData) => ({ ...prev, supervisor_testes_iniciais: e.target.checked }));
  };

  const handleSupervisorTestesParciaisChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev: FormData) => ({ ...prev, supervisor_testes_parciais: e.target.checked }));
  };

  const handleSupervisorTestesFinaisChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev: FormData) => ({ ...prev, supervisor_testes_finais: e.target.checked }));
  };

  const handleSaveApontamento = async () => {
    try {
      setLoading(true);
      // Implementar lógica de salvamento
      console.log('Salvando apontamento:', { formData, testResults, testObservations });
    } catch (error) {
      console.error('Erro ao salvar apontamento:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashTab />;
      case 'apontamento':
        return <ApontamentoFormTab
          formData={formData}
          setFormData={setFormData}
          testResults={testResults}
          testObservations={testObservations}
          onTestResultChange={onTestResultChange}
          onTestCheckboxChange={onTestCheckboxChange}
          onTestObservationChange={onTestObservationChange}
          handleSupervisorHorasOrcadasChange={handleSupervisorHorasOrcadasChange}
          handleSupervisorTestesIniciaisChange={handleSupervisorTestesIniciaisChange}
          handleSupervisorTestesParciaisChange={handleSupervisorTestesParciaisChange}
          handleSupervisorTestesFinaisChange={handleSupervisorTestesFinaisChange}
          handleSaveApontamento={handleSaveApontamento}
        />;
      case 'minhas-os':
        return <MinhasOsTab />;
      case 'pesquisa':
        return <PesquisaOSTab
          onVerOS={(osId: number) => {
            setSelectedOsId(osId);
            setRelatorioModalOpen(true);
          }}
        />;
      case 'programacao':
        return <ProgramacaoTab />;
      case 'pendencias':
        return <PendenciasTab />;
      case 'gerenciar':
        return <GerenciarTab />;
      case 'aprovacao':
        return <AprovacaoUsuariosTab />;
      default:
        return <DashTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                <span>🏠</span>
                <span className="hidden sm:inline">Menu Principal</span>
              </button>
              <button
                onClick={() => window.location.href = '/desenvolvimento'}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
              >
                <span>🔧</span>
                <span className="hidden sm:inline">Setores</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {sectorConfig?.NomeSetor || sectorKey || 'Desenvolvimento'}
                </h1>
                <p className="text-sm text-gray-500">
                  {user?.primeiro_nome || (user?.nome_completo ? user.nome_completo.split(' ')[0] : 'Usuário')} | {user?.privilege_level}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Online
              </span>
              <button
                onClick={() => {
                  localStorage.clear();
                  sessionStorage.clear();
                  window.location.href = '/login';
                }}
                className="px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
              >
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      </div>

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
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 relative`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                    {tab.badge}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="w-full px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          renderTabContent()
        )}
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

export default DevelopmentTemplate;
