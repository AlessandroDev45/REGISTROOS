import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useSetor } from '../../contexts/SetorContext';
import { ConfiguracaoSetor } from '../../pages/common/TiposApi';
import api from '../../services/api';
import logo from '../../logo/assets/logo.png';

// Componentes das abas originais
import DashTab from './components/tabs/DashTab';
import ApontamentoFormTab from './components/tabs/ApontamentoFormTab';
import MinhasOsTab from './components/tabs/MinhasOsTab';
import ProgramacaoTab from './components/tabs/ProgramacaoTab';
import PendenciasTab from './components/tabs/PendenciasTab';
import GerenciarTab from './components/tabs/GerenciarTab';
import AprovacaoUsuariosTab from './components/tabs/AprovacaoUsuariosTab';
import RelatorioCompletoModal from '../../components/RelatorioCompletoModal';

interface DevelopmentTemplateProps {
  sectorConfig: ConfiguracaoSetor;
  sectorKey: string;
  initialTab?: string;
}

interface TabItem {
  id: string;
  label: string;
  icon: string;
  badge?: number;
}

const DevelopmentTemplate: React.FC<DevelopmentTemplateProps> = ({ sectorConfig, sectorKey, initialTab }) => {
  const [searchParams] = useSearchParams();
  const { user } = useAuth();
  const { setorAtivo } = useSetor();

  // Detectar parâmetros da URL para programação
  const osFromUrl = searchParams.get('os');
  const programacaoId = searchParams.get('programacao_id');

  // Debug dos parâmetros da URL
  console.log('🔍 [DevelopmentTemplate] Parâmetros da URL:', {
    osFromUrl,
    programacaoId
  });

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
  const [activeTab, setActiveTab] = useState(initialTab || 'dashboard');
  const [loading, setLoading] = useState(false);
  const [programacoesCount, setProgramacoesCount] = useState(0);

  // Atualizar aba quando initialTab mudar
  useEffect(() => {
    if (initialTab && initialTab !== activeTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);



  // Estados para o formulário de apontamento
  interface FormData {
    inpNumOS?: string;
    statusOS?: string;
    inpCliente?: string;
    inpEquipamento?: string;
    selMaq?: string;
    selAtiv?: string;
    selDescAtiv?: string;
    inpData?: string;
    inpHora?: string;
    observacao?: string;
    resultadoGlobal?: string;
    inpDataFim?: string;
    inpHoraFim?: string;
    categoriaSelecionada?: string;
    subcategoriasSelecionadas?: string[];
    supervisor_horas_orcadas: number;
    supervisor_testes_iniciais: boolean;
    supervisor_testes_parciais: boolean;
    supervisor_testes_finais: boolean;
    [key: string]: any;
  }

  // Função para carregar dados do sessionStorage
  const loadFormDataFromStorage = (): FormData => {
    try {
      const savedData = sessionStorage.getItem('apontamento_form_data');
      if (savedData) {
        const parsed = JSON.parse(savedData);
        console.log('📂 Dados carregados do sessionStorage:', parsed);
        return parsed;
      }
    } catch (error) {
      console.error('❌ Erro ao carregar dados do sessionStorage:', error);
    }

    // Retornar dados padrão se não houver dados salvos
    return {
      inpNumOS: '',
      statusOS: '',
      inpCliente: '',
      inpEquipamento: '',
      selMaq: '',
      selAtiv: '',
      selDescAtiv: '',
      inpData: '',
      inpHora: '',
      observacao: '',
      resultadoGlobal: '',
      inpDataFim: '',
      inpHoraFim: '',
      categoriaSelecionada: '',
      subcategoriasSelecionadas: [],
      supervisor_horas_orcadas: 0,
      supervisor_testes_iniciais: false,
      supervisor_testes_parciais: false,
      supervisor_testes_finais: false
    };
  };

  const [formData, setFormData] = useState<FormData>(loadFormDataFromStorage);

  // Função para salvar dados no sessionStorage
  const saveFormDataToStorage = (data: FormData) => {
    try {
      sessionStorage.setItem('apontamento_form_data', JSON.stringify(data));
      console.log('💾 Dados salvos no sessionStorage:', data);
    } catch (error) {
      console.error('❌ Erro ao salvar dados no sessionStorage:', error);
    }
  };

  // Wrapper para setFormData que também salva no storage
  const setFormDataWithStorage = (data: FormData | ((prev: FormData) => FormData)) => {
    if (typeof data === 'function') {
      setFormData(prev => {
        const newData = data(prev);
        saveFormDataToStorage(newData);
        return newData;
      });
    } else {
      setFormData(data);
      saveFormDataToStorage(data);
    }
  };

  // Função para limpar dados do storage
  const clearFormDataStorage = () => {
    try {
      sessionStorage.removeItem('apontamento_form_data');
      console.log('🗑️ Dados do formulário removidos do sessionStorage');
    } catch (error) {
      console.error('❌ Erro ao limpar dados do sessionStorage:', error);
    }
  };
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [testObservations, setTestObservations] = useState<Record<string, string>>({});

  // Estados para o modal de relatório completo
  const [relatorioModalOpen, setRelatorioModalOpen] = useState(false);
  const [selectedOsId, setSelectedOsId] = useState<number | null>(null);

  // Estados para comunicação entre abas (resolução de pendências e programações)
  const [pendenciaParaResolver, setPendenciaParaResolver] = useState<any>(null);
  const [programacaoParaIniciar, setProgramacaoParaIniciar] = useState<any>(null);
  const [dadosPreenchidosApontamento, setDadosPreenchidosApontamento] = useState<any>(null);

  // Pré-preencher formData quando vem de uma programação
  useEffect(() => {
    console.log('🔍 [DevelopmentTemplate] useEffect preenchimento executado:', {
      osFromUrl,
      currentInpNumOS: formData.inpNumOS,
      shouldFill: osFromUrl && (!formData.inpNumOS || formData.inpNumOS === ''),
      formDataKeys: Object.keys(formData)
    });

    if (osFromUrl) {
      console.log('🎯 [DevelopmentTemplate] Forçando preenchimento da OS:', osFromUrl);

      // Remover zeros à esquerda e garantir máximo 5 dígitos
      const osFormatted = osFromUrl.replace(/^0+/, '').slice(0, 5);

      setFormDataWithStorage(prev => ({
        ...prev,
        inpNumOS: osFormatted
      }));

      // Buscar dados da OS automaticamente após preencher
      const buscarDadosOS = async () => {
        try {
          console.log('🔍 [DevelopmentTemplate] Buscando dados da OS:', osFormatted);

          // Usar o endpoint correto que faz scraping se necessário
          const response = await api.get(`/desenvolvimento/formulario/buscar-os/${osFormatted}`, {
            timeout: 300000 // 5 minutos para permitir scraping
          });

          if (response.data) {
            console.log('✅ [DevelopmentTemplate] OS encontrada, preenchendo campos:', {
              status: response.data.status,
              cliente: response.data.cliente,
              equipamento: response.data.equipamento,
              fonte: response.data.fonte
            });

            setFormDataWithStorage(prev => ({
              ...prev,
              statusOS: response.data.status || '',
              inpCliente: response.data.cliente || '',
              inpEquipamento: response.data.equipamento || ''
            }));
          }
        } catch (error) {
          console.log('⚠️ [DevelopmentTemplate] Erro ao buscar OS:', error);
          // Tentar endpoint alternativo se o principal falhar
          try {
            const fallbackResponse = await api.get(`/desenvolvimento/os/${osFormatted}`);
            if (fallbackResponse.data) {
              console.log('✅ [DevelopmentTemplate] OS encontrada via fallback');
              setFormDataWithStorage(prev => ({
                ...prev,
                statusOS: fallbackResponse.data.status || '',
                inpCliente: fallbackResponse.data.cliente || '',
                inpEquipamento: fallbackResponse.data.equipamento || ''
              }));
            }
          } catch (fallbackError) {
            console.log('⚠️ [DevelopmentTemplate] Fallback também falhou:', fallbackError);
          }
        }
      };

      // Buscar dados da OS com delay para evitar múltiplas chamadas
      setTimeout(buscarDadosOS, 1000);
    }
  }, [osFromUrl]);

  // Definir abas baseadas no nível de privilégio do usuário
  const getAvailableTabs = (): TabItem[] => {
    const baseTabs: TabItem[] = [
      { id: 'dashboard', label: 'Dashboard', icon: '📊' },
      { id: 'apontamento', label: 'Apontamento', icon: '📝' },
      { id: 'minhas-os', label: 'Meu Dashboard', icon: '📋' },
      { id: 'pendencias', label: 'Pendências', icon: '⚠️' }
    ];

    // Adicionar aba Programação apenas para SUPERVISOR e ADMIN
    if (user?.privilege_level === 'SUPERVISOR' || user?.privilege_level === 'ADMIN') {
      baseTabs.push({
        id: 'programacao',
        label: 'Programação',
        icon: '📅',
        badge: programacoesCount > 0 ? programacoesCount : undefined
      });
    }

    // Adicionar abas para supervisores e admins
    if (user?.privilege_level === 'SUPERVISOR' || user?.privilege_level === 'ADMIN') {
      baseTabs.push(
        { id: 'gerenciar', label: 'Gerenciar', icon: '⚙️' }
      );
    }

    // Adicionar aba de aprovação para admins e supervisores
    if (user?.privilege_level === 'ADMIN' || user?.privilege_level === 'SUPERVISOR') {
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

  // Função para resolver pendência via apontamento
  const handleResolverPendenciaViaApontamento = (pendencia: any) => {
    console.log('📋 [DevelopmentTemplate] Resolvendo pendência via apontamento:', pendencia);

    // Preparar dados para preencher no formulário de apontamento
    const dadosApontamento = {
      inpNumOS: pendencia.numero_os,
      // Não preencher cliente e equipamento aqui - deixar para busca automática da OS
      // inpCliente: pendencia.cliente,
      // inpEquipamento: pendencia.descricao_maquina || pendencia.equipamento,
      selMaq: pendencia.tipo_maquina,
      observacao: `RESOLUÇÃO DE PENDÊNCIA #${pendencia.id}: ${pendencia.descricao_pendencia || pendencia.descricao}`,
      pendencia_origem_id: pendencia.id
    };

    console.log('📋 [DevelopmentTemplate] Dados preparados para apontamento:', dadosApontamento);

    // Armazenar dados para usar na aba de apontamento
    setPendenciaParaResolver(pendencia);
    setDadosPreenchidosApontamento(dadosApontamento);

    // Mudar para a aba de apontamento
    setActiveTab('apontamento');
  };

  // Função para iniciar execução de programação via apontamento
  const handleIniciarExecucaoProgramacao = (programacao: any) => {
    console.log('🚀 [DevelopmentTemplate] Iniciando execução de programação:', programacao);

    // Preparar dados para preencher no formulário de apontamento
    const dadosApontamento = {
      inpNumOS: programacao.os_numero,
      // Não preencher cliente e equipamento aqui - deixar para busca automática da OS
      // inpCliente: programacao.cliente_nome,
      // inpEquipamento: programacao.equipamento_descricao,
      observacao: `EXECUÇÃO DE PROGRAMAÇÃO #${programacao.id}: ${programacao.observacoes || 'Execução da programação'}`,
      programacao_origem_id: programacao.id
    };

    console.log('📋 [DevelopmentTemplate] Dados preparados para apontamento:', dadosApontamento);

    // Armazenar dados para usar na aba de apontamento
    setProgramacaoParaIniciar(programacao);
    setDadosPreenchidosApontamento(dadosApontamento);

    // Mudar para a aba de apontamento
    setActiveTab('apontamento');
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
    setFormDataWithStorage((prev: FormData) => ({ ...prev, supervisor_horas_orcadas: parseFloat(e.target.value) || 0 }));
  };

  const handleSupervisorTestesIniciaisChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormDataWithStorage((prev: FormData) => ({ ...prev, supervisor_testes_iniciais: e.target.checked }));
  };

  const handleSupervisorTestesParciaisChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormDataWithStorage((prev: FormData) => ({ ...prev, supervisor_testes_parciais: e.target.checked }));
  };

  const handleSupervisorTestesFinaisChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormDataWithStorage((prev: FormData) => ({ ...prev, supervisor_testes_finais: e.target.checked }));
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
          setFormData={setFormDataWithStorage}
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
          dadosPreenchidos={dadosPreenchidosApontamento}
          pendenciaParaResolver={pendenciaParaResolver}
          programacaoParaIniciar={programacaoParaIniciar}
          onPendenciaResolvida={() => {
            setPendenciaParaResolver(null);
            setDadosPreenchidosApontamento(null);
          }}
          onProgramacaoIniciada={() => {
            setProgramacaoParaIniciar(null);
            setDadosPreenchidosApontamento(null);
          }}
        />;
      case 'minhas-os':
        return <MinhasOsTab onIniciarExecucao={handleIniciarExecucaoProgramacao} />;
      case 'programacao':
        return <ProgramacaoTab />;
      case 'pendencias':
        return <PendenciasTab
          onResolverViaApontamento={handleResolverPendenciaViaApontamento}
        />;
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
              <img src={logo} alt="RegistroOS Logo" className="h-8 w-auto" />
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
