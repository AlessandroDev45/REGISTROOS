import React, { useState, useEffect } from 'react';
import { getDashboardAvancado, getAlertasPCP } from '../../../services/api';
import { setorService } from '../../../services/adminApi';

interface MetricasGerais {
  os_por_status: Array<{ status: string; total: number }>;
  tempo_ciclo_medio_dias: number;
  taxa_cumprimento_prazo: number;
  horas_trabalhadas_periodo: number;
}

interface EficienciaSetor {
  setor: string;
  total_apontamentos: number;
  tempo_medio_horas: number;
  taxa_retrabalho: number;
  pendencias_abertas: number;
  eficiencia: number;
}

interface ProdutividadeSemanal {
  dia_semana: number;
  nome_dia: string;
  total_apontamentos: number;
  tempo_medio_horas: number;
}

interface EvolucaoMensal {
  mes: string;
  os_abertas: number;
  os_fechadas: number;
}

interface DashboardData {
  periodo_analise: number;
  data_atualizacao: string;
  metricas_gerais: MetricasGerais;
  eficiencia_setores: EficienciaSetor[];
  tempo_por_tipo_maquina: Array<{ tipo_maquina: string; tempo_medio_horas: number; total_apontamentos: number }>;
  produtividade_semanal: ProdutividadeSemanal[];
  evolucao_mensal: EvolucaoMensal[];
}

interface Alerta {
  tipo: string;
  prioridade: string;
  titulo: string;
  descricao: string;
  data_alerta: string;
  dados: any;
}

interface DashboardPCPInterativoProps {
  periodoDias?: number;
  setorSelecionado?: number;
}

const DashboardPCPInterativo: React.FC<DashboardPCPInterativoProps> = ({
  periodoDias = 30,
  setorSelecionado
}) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [alertas, setAlertas] = useState<Alerta[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [periodo, setPeriodo] = useState(periodoDias);
  const [setor, setSetor] = useState(setorSelecionado);
  const [abaSelecionada, setAbaSelecionada] = useState<'geral' | 'eficiencia' | 'alertas'>('geral');
  const [setores, setSetores] = useState<Array<{id: number, nome: string}>>([]);

  useEffect(() => {
    carregarDashboard();
    carregarAlertas();
    carregarSetores();
  }, [periodo, setor]);

  const carregarSetores = async () => {
    try {
      const setoresData = await setorService.getSetores();
      setSetores(setoresData);
    } catch (error) {
      console.error('Erro ao carregar setores:', error);
    }
  };

  const carregarDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('Carregando dashboard com período:', periodo, 'setor:', setor);
      const data = await getDashboardAvancado(periodo, setor);
      console.log('Dados do dashboard recebidos:', data);
      setDashboardData(data);
    } catch (error: any) {
      console.error('Erro ao carregar dashboard:', error);
      setError(error.message || 'Erro ao carregar dados do dashboard');
      setDashboardData(null);
    } finally {
      setLoading(false);
    }
  };

  const carregarAlertas = async () => {
    try {
      const data = await getAlertasPCP();
      setAlertas(data.alertas || []);
    } catch (error) {
      console.error('Erro ao carregar alertas:', error);
    }
  };

  const getPrioridadeColor = (prioridade: string) => {
    switch (prioridade?.toUpperCase()) {
      case 'URGENTE':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'ALTA':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIA':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'BAIXA':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEficienciaColor = (eficiencia: number) => {
    if (eficiencia >= 90) return 'text-green-600';
    if (eficiencia >= 75) return 'text-blue-600';
    if (eficiencia >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatarTempo = (horas: number) => {
    if (horas < 24) {
      return `${Math.round(horas)}h`;
    } else {
      const dias = Math.floor(horas / 24);
      const horasRestantes = Math.round(horas % 24);
      return `${dias}d ${horasRestantes}h`;
    }
  };

  if (loading && !dashboardData) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Carregando dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="text-red-600">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-lg font-medium text-red-800">Erro no Dashboard</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <p className="text-sm text-red-600 mt-2">
              Verifique se o backend está rodando em localhost:8000 e se você está autenticado.
            </p>
          </div>
          <div className="ml-auto">
            <button
              onClick={carregarDashboard}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Tentar Novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header com Filtros */}
      <div className="bg-white p-4 rounded-lg shadow border">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Dashboard PCP Interativo</h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Período:</label>
              <select
                value={periodo}
                onChange={(e) => setPeriodo(Number(e.target.value))}
                className="border border-gray-300 rounded px-3 py-1 text-sm"
              >
                <option value={7}>7 dias</option>
                <option value={15}>15 dias</option>
                <option value={30}>30 dias</option>
                <option value={60}>60 dias</option>
                <option value={90}>90 dias</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Setor:</label>
              <select
                value={setor || ''}
                onChange={(e) => setSetor(e.target.value ? Number(e.target.value) : undefined)}
                className="border border-gray-300 rounded px-3 py-1 text-sm"
              >
                <option value="">Todos os setores</option>
                {setores.map((setorItem) => (
                  <option key={setorItem.id} value={setorItem.id}>
                    {setorItem.nome}
                  </option>
                ))}
              </select>
            </div>
            
            <button
              onClick={() => {
                carregarDashboard();
                carregarAlertas();
              }}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Atualizar
            </button>
          </div>
        </div>

        {/* Abas */}
        <div className="flex space-x-1 border-b border-gray-200">
          <button
            onClick={() => setAbaSelecionada('geral')}
            className={`px-4 py-2 text-sm font-medium ${
              abaSelecionada === 'geral'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Visão Geral
          </button>
          <button
            onClick={() => setAbaSelecionada('eficiencia')}
            className={`px-4 py-2 text-sm font-medium ${
              abaSelecionada === 'eficiencia'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Eficiência por Setor
          </button>
          <button
            onClick={() => setAbaSelecionada('alertas')}
            className={`px-4 py-2 text-sm font-medium ${
              abaSelecionada === 'alertas'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Alertas ({alertas.length})
          </button>
        </div>
      </div>

      {/* Conteúdo das Abas */}
      {abaSelecionada === 'geral' && dashboardData && dashboardData.metricas_gerais && (
        <div className="space-y-6">
          {/* Métricas Principais */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="text-2xl font-bold text-blue-600">
                {dashboardData.metricas_gerais.tempo_ciclo_medio_dias?.toFixed(1) || '0.0'}
              </div>
              <div className="text-sm text-gray-600">Tempo Médio de Ciclo (dias)</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="text-2xl font-bold text-green-600">
                {dashboardData.metricas_gerais.taxa_cumprimento_prazo || 0}%
              </div>
              <div className="text-sm text-gray-600">Taxa de Cumprimento de Prazo</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="text-2xl font-bold text-purple-600">
                {formatarTempo(dashboardData.metricas_gerais.horas_trabalhadas_periodo || 0)}
              </div>
              <div className="text-sm text-gray-600">Horas Trabalhadas no Período</div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="text-2xl font-bold text-orange-600">
                {Array.isArray(dashboardData.metricas_gerais.os_por_status)
                  ? dashboardData.metricas_gerais.os_por_status.reduce((sum, item) => sum + (item.total || 0), 0)
                  : 0
                }
              </div>
              <div className="text-sm text-gray-600">Total de OS</div>
            </div>
          </div>

          {/* Gráficos */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* OS por Status */}
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold mb-4">OS por Status</h3>
              <div className="space-y-3">
                {Array.isArray(dashboardData?.metricas_gerais?.os_por_status) ? dashboardData.metricas_gerais.os_por_status.map((item, index) => {
                  const total = dashboardData.metricas_gerais.os_por_status.reduce((sum, i) => sum + (i.total || 0), 0);
                  const percentage = total > 0 ? ((item.total || 0) / total) * 100 : 0;
                  
                  return (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 rounded bg-blue-500"></div>
                        <span className="text-sm font-medium">{item.status}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-blue-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600 w-16 text-right">
                          {item.total} ({Math.round(percentage)}%)
                        </span>
                      </div>
                    </div>
                  );
                }) : (
                  <div className="text-center text-gray-500 py-4">
                    Nenhum dado de status disponível
                  </div>
                )}
              </div>
            </div>

            {/* Produtividade Semanal */}
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold mb-4">Produtividade por Dia da Semana</h3>
              <div className="space-y-3">
                {Array.isArray(dashboardData?.produtividade_semanal) ? dashboardData.produtividade_semanal.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm font-medium">{item.nome_dia}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-gray-600">
                        {item.total_apontamentos} apontamentos
                      </span>
                      <span className="text-sm text-blue-600">
                        {item.tempo_medio_horas.toFixed(1)}h média
                      </span>
                    </div>
                  </div>
                )) : (
                  <div className="text-center text-gray-500 py-4">
                    Nenhum dado de produtividade disponível
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Evolução Mensal */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Evolução Mensal (OS Abertas vs Fechadas)</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4 text-sm font-medium text-gray-700">Mês</th>
                    <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">OS Abertas</th>
                    <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">OS Fechadas</th>
                    <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Saldo</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.isArray(dashboardData?.evolucao_mensal) ? dashboardData.evolucao_mensal.map((item, index) => {
                    const saldo = item.os_abertas - item.os_fechadas;
                    return (
                      <tr key={index} className="border-b">
                        <td className="py-2 px-4 text-sm">{item.mes}</td>
                        <td className="py-2 px-4 text-sm text-center text-red-600">{item.os_abertas}</td>
                        <td className="py-2 px-4 text-sm text-center text-green-600">{item.os_fechadas}</td>
                        <td className={`py-2 px-4 text-sm text-center font-medium ${
                          saldo > 0 ? 'text-red-600' : saldo < 0 ? 'text-green-600' : 'text-gray-600'
                        }`}>
                          {saldo > 0 ? '+' : ''}{saldo}
                        </td>
                      </tr>
                    );
                  }) : (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-gray-500">
                        Nenhum dado de evolução mensal disponível
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {abaSelecionada === 'eficiencia' && dashboardData && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Eficiência por Setor</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Setor</th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Apontamentos</th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Tempo Médio</th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Taxa Retrabalho</th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Pendências</th>
                  <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Eficiência</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(dashboardData?.eficiencia_setores) ? dashboardData.eficiencia_setores.map((setor, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm font-medium">{setor.setor}</td>
                    <td className="py-3 px-4 text-sm text-center">{setor.total_apontamentos}</td>
                    <td className="py-3 px-4 text-sm text-center">{setor.tempo_medio_horas}h</td>
                    <td className="py-3 px-4 text-sm text-center">{setor.taxa_retrabalho}%</td>
                    <td className="py-3 px-4 text-sm text-center">{setor.pendencias_abertas}</td>
                    <td className="py-3 px-4 text-sm text-center">
                      <span className={`font-semibold ${getEficienciaColor(setor.eficiencia)}`}>
                        {setor.eficiencia}%
                      </span>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-500">
                      Nenhum dado de eficiência disponível
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {abaSelecionada === 'alertas' && (
        <div className="space-y-4">
          {alertas.length === 0 ? (
            <div className="bg-white p-8 rounded-lg shadow border text-center text-gray-500">
              Nenhum alerta no momento
            </div>
          ) : (
            alertas.map((alerta, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow border">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 text-xs rounded border ${getPrioridadeColor(alerta.prioridade)}`}>
                        {alerta.prioridade}
                      </span>
                      <span className="text-xs text-gray-500">{alerta.tipo}</span>
                    </div>
                    <h4 className="font-semibold text-gray-900 mb-1">{alerta.titulo}</h4>
                    <p className="text-sm text-gray-600">{alerta.descricao}</p>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(alerta.data_alerta).toLocaleString('pt-BR')}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default DashboardPCPInterativo;
