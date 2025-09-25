import React, { useState, useEffect } from 'react';
import { getDashboardAvancado } from '../../../services/api';

interface RelatorioData {
  eficiencia_geral: number;
  tempo_medio_horas: number;
  taxa_cumprimento: number;
  os_processadas: number;
  distribuicao_setores: Array<{
    setor: string;
    total_os: number;
    tempo_medio: number;
    eficiencia: number;
  }>;
  evolucao_mensal: Array<{
    mes: string;
    os_abertas: number;
    os_fechadas: number;
    eficiencia: number;
  }>;
}

const RelatoriosAnalises: React.FC = () => {
  const [relatorioData, setRelatorioData] = useState<RelatorioData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [periodo, setPeriodo] = useState(30);

  const carregarRelatorios = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await getDashboardAvancado(periodo);
      
      // Processar dados para relatórios
      const processedData: RelatorioData = {
        eficiencia_geral: response.metricas_gerais?.taxa_cumprimento_prazo || 0,
        tempo_medio_horas: response.metricas_gerais?.tempo_ciclo_medio_dias * 24 || 0,
        taxa_cumprimento: response.metricas_gerais?.taxa_cumprimento_prazo || 0,
        os_processadas: response.metricas_gerais?.os_por_status?.reduce((total: number, item: any) => total + (item.total || 0), 0) || 0,
        distribuicao_setores: response.eficiencia_setores || [],
        evolucao_mensal: response.evolucao_mensal || []
      };
      
      setRelatorioData(processedData);
    } catch (err) {
      console.error('Erro ao carregar relatórios:', err);
      setError('Erro ao carregar dados dos relatórios');
      
      // Dados mock como fallback
      setRelatorioData({
        eficiencia_geral: 85,
        tempo_medio_horas: 12.5,
        taxa_cumprimento: 92,
        os_processadas: 156,
        distribuicao_setores: [
          { setor: 'Mecânica', total_os: 45, tempo_medio: 8.2, eficiencia: 88 },
          { setor: 'Elétrica', total_os: 38, tempo_medio: 6.5, eficiencia: 92 },
          { setor: 'Montagem', total_os: 73, tempo_medio: 15.3, eficiencia: 79 }
        ],
        evolucao_mensal: [
          { mes: 'Jan', os_abertas: 120, os_fechadas: 115, eficiencia: 96 },
          { mes: 'Fev', os_abertas: 135, os_fechadas: 128, eficiencia: 95 },
          { mes: 'Mar', os_abertas: 142, os_fechadas: 139, eficiencia: 98 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarRelatorios();
  }, [periodo]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Relatórios e Análises</h2>
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
          <button
            onClick={carregarRelatorios}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Atualizar
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="text-yellow-800">
            ⚠️ {error} - Exibindo dados de exemplo
          </div>
        </div>
      )}

      {/* Métricas Principais */}
      <div className="bg-white p-6 rounded-lg shadow border">
        <h3 className="text-lg font-semibold mb-4">Métricas Principais</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {relatorioData?.eficiencia_geral || 0}%
            </div>
            <div className="text-sm text-blue-700">Eficiência Geral</div>
          </div>
          <div className="bg-purple-50 p-4 rounded">
            <div className="text-2xl font-bold text-purple-600">
              {relatorioData?.tempo_medio_horas?.toFixed(1) || '0.0'}h
            </div>
            <div className="text-sm text-purple-700">Tempo Médio</div>
          </div>
          <div className="bg-orange-50 p-4 rounded">
            <div className="text-2xl font-bold text-orange-600">
              {relatorioData?.taxa_cumprimento || 0}%
            </div>
            <div className="text-sm text-orange-700">Taxa Cumprimento</div>
          </div>
          <div className="bg-indigo-50 p-4 rounded">
            <div className="text-2xl font-bold text-indigo-600">
              {relatorioData?.os_processadas || 0}
            </div>
            <div className="text-sm text-indigo-700">OS Processadas</div>
          </div>
        </div>
      </div>

      {/* Distribuição por Setores */}
      <div className="bg-white p-6 rounded-lg shadow border">
        <h3 className="text-lg font-semibold mb-4">Distribuição por Setores</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-700">Setor</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Total OS</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Tempo Médio</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Eficiência</th>
              </tr>
            </thead>
            <tbody>
              {relatorioData?.distribuicao_setores?.map((setor, index) => (
                <tr key={`setor-${index}`} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm font-medium">{setor.setor}</td>
                  <td className="py-3 px-4 text-sm text-center">{setor.total_os || setor.total_apontamentos}</td>
                  <td className="py-3 px-4 text-sm text-center">{(setor.tempo_medio || setor.tempo_medio_horas)?.toFixed(1)}h</td>
                  <td className="py-3 px-4 text-sm text-center">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      (setor.eficiencia || 0) >= 90 ? 'bg-green-100 text-green-800' :
                      (setor.eficiencia || 0) >= 80 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {setor.eficiencia || 0}%
                    </span>
                  </td>
                </tr>
              )) || []}
            </tbody>
          </table>
        </div>
      </div>

      {/* Evolução Mensal */}
      <div className="bg-white p-6 rounded-lg shadow border">
        <h3 className="text-lg font-semibold mb-4">Evolução Mensal</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-700">Mês</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">OS Abertas</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">OS Fechadas</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Saldo</th>
                <th className="text-center py-2 px-4 text-sm font-medium text-gray-700">Eficiência</th>
              </tr>
            </thead>
            <tbody>
              {relatorioData?.evolucao_mensal?.map((item, index) => {
                const saldo = (item.os_fechadas || 0) - (item.os_abertas || 0);
                return (
                  <tr key={`mes-${index}`} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm font-medium">{item.mes}</td>
                    <td className="py-3 px-4 text-sm text-center">{item.os_abertas}</td>
                    <td className="py-3 px-4 text-sm text-center">{item.os_fechadas}</td>
                    <td className="py-3 px-4 text-sm text-center">
                      <span className={`${saldo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {saldo > 0 ? '+' : ''}{saldo}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-center">
                      {item.eficiencia || Math.round(((item.os_fechadas || 0) / (item.os_abertas || 1)) * 100)}%
                    </td>
                  </tr>
                );
              }) || []}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default RelatoriosAnalises;
