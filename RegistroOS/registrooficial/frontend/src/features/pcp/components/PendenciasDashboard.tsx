import React, { useState, useEffect } from 'react';
import { getPendenciasDashboard } from '../../../services/api';

interface MetricasGerais {
  total_pendencias: number;
  pendencias_abertas: number;
  pendencias_fechadas: number;
  pendencias_periodo: number;
  pendencias_criticas: number;
  tempo_medio_resolucao_horas: number;
}

interface DistribuicaoItem {
  prioridade?: string;
  setor?: string;
  total: number;
}

interface EvolucaoItem {
  data: string;
  abertas: number;
  fechadas: number;
}

interface DashboardData {
  metricas_gerais: MetricasGerais;
  distribuicao_prioridade: DistribuicaoItem[];
  distribuicao_setor: DistribuicaoItem[];
  evolucao_7_dias: EvolucaoItem[];
}

interface PendenciasDashboardProps {
  periodoDias?: number;
  onPeriodoChange?: (periodo: number) => void;
}

const PendenciasDashboard: React.FC<PendenciasDashboardProps> = ({ 
  periodoDias = 30, 
  onPeriodoChange 
}) => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarDashboard();
  }, [periodoDias]);

  const carregarDashboard = async () => {
    setLoading(true);
    try {
      const data = await getPendenciasDashboard(periodoDias);
      setDashboardData(data);
    } catch (error) {
      console.error('Erro ao carregar dashboard de pendências:', error);
    } finally {
      setLoading(false);
    }
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

  const getPrioridadeColor = (prioridade: string) => {
    switch (prioridade?.toUpperCase()) {
      case 'URGENTE':
        return 'bg-red-500';
      case 'ALTA':
        return 'bg-orange-500';
      case 'MEDIA':
        return 'bg-yellow-500';
      case 'BAIXA':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Carregando dashboard...</span>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-8 text-gray-500">
        Erro ao carregar dados do dashboard
      </div>
    );
  }

  const { metricas_gerais, distribuicao_prioridade, distribuicao_setor, evolucao_7_dias } = dashboardData;

  // Verificação adicional para metricas_gerais
  if (!metricas_gerais) {
    return (
      <div className="text-center py-8 text-gray-500">
        Dados de métricas não disponíveis
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header com filtros */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Dashboard de Pendências</h2>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-600">Período:</label>
          <select
            value={periodoDias}
            onChange={(e) => onPeriodoChange?.(Number(e.target.value))}
            className="border border-gray-300 rounded px-3 py-1 text-sm"
          >
            <option value={7}>7 dias</option>
            <option value={15}>15 dias</option>
            <option value={30}>30 dias</option>
            <option value={60}>60 dias</option>
            <option value={90}>90 dias</option>
          </select>
          <button
            onClick={carregarDashboard}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Atualizar
          </button>
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-blue-600">{metricas_gerais.total_pendencias}</div>
          <div className="text-sm text-gray-600">Total de Pendências</div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-red-600">{metricas_gerais.pendencias_abertas}</div>
          <div className="text-sm text-gray-600">Pendências Abertas</div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-green-600">{metricas_gerais.pendencias_fechadas}</div>
          <div className="text-sm text-gray-600">Pendências Fechadas</div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-orange-600">{metricas_gerais.pendencias_criticas}</div>
          <div className="text-sm text-gray-600">Pendências Críticas</div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-purple-600">{metricas_gerais.pendencias_periodo}</div>
          <div className="text-sm text-gray-600">No Período</div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow border">
          <div className="text-2xl font-bold text-indigo-600">
            {formatarTempo(metricas_gerais.tempo_medio_resolucao_horas)}
          </div>
          <div className="text-sm text-gray-600">Tempo Médio Resolução</div>
        </div>
      </div>

      {/* Gráficos e Distribuições */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribuição por Prioridade */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Distribuição por Prioridade</h3>
          <div className="space-y-3">
            {distribuicao_prioridade.map((item, index) => {
              const total = distribuicao_prioridade.reduce((sum, i) => sum + i.total, 0);
              const percentage = total > 0 ? (item.total / total) * 100 : 0;
              
              return (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded ${getPrioridadeColor(item.prioridade || 'NORMAL')}`}></div>
                    <span className="text-sm font-medium">{item.prioridade || 'NORMAL'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getPrioridadeColor(item.prioridade || 'NORMAL')}`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">
                      {item.total} ({Math.round(percentage)}%)
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Distribuição por Setor */}
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Distribuição por Setor</h3>
          <div className="space-y-3">
            {distribuicao_setor.map((item, index) => {
              const total = distribuicao_setor.reduce((sum, i) => sum + i.total, 0);
              const percentage = total > 0 ? (item.total / total) * 100 : 0;
              
              return (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded bg-blue-500"></div>
                    <span className="text-sm font-medium">{item.setor}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">
                      {item.total} ({Math.round(percentage)}%)
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Evolução dos Últimos 7 Dias */}
      <div className="bg-white p-6 rounded-lg shadow border">
        <h3 className="text-lg font-semibold mb-4">Evolução dos Últimos 7 Dias</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-700">Data</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Abertas</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Fechadas</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Saldo</th>
              </tr>
            </thead>
            <tbody>
              {evolucao_7_dias.map((item, index) => {
                const saldo = item.abertas - item.fechadas;
                return (
                  <tr key={index} className="border-b">
                    <td className="py-2 px-4 text-sm">
                      {new Date(item.data).toLocaleDateString('pt-BR')}
                    </td>
                    <td className="py-2 px-4 text-sm text-center text-red-600">
                      {item.abertas}
                    </td>
                    <td className="py-2 px-4 text-sm text-center text-green-600">
                      {item.fechadas}
                    </td>
                    <td className={`py-2 px-4 text-sm text-center font-medium ${
                      saldo > 0 ? 'text-red-600' : saldo < 0 ? 'text-green-600' : 'text-gray-600'
                    }`}>
                      {saldo > 0 ? '+' : ''}{saldo}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PendenciasDashboard;
