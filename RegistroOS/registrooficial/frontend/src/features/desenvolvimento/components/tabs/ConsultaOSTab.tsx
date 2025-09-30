import React, { useState } from 'react';
import api from '../../../../services/api';

interface OSData {
  os_info: {
    numero: string;
    status: string;
    descricao_maquina: string;
    prioridade: string;
    data_criacao: string;
    observacoes_gerais: string;
  };
  apontamentos: Array<{
    id: number;
    data_hora_inicio: string;
    data_hora_fim: string;
    status: string;
    tipo_maquina: string;
    tipo_atividade: string;
    descricao_atividade: string;
    categoria: string;
    subcategoria: string;
    observacao_os: string;
    observacoes_gerais: string;
    foi_retrabalho: boolean;
    criado_por: string;
    criado_por_email: string;
    resultados_teste: Array<{
      id: number;
      teste_nome: string;
      teste_categoria: string;
      teste_tipo: string;
      resultado: string;
      observacao: string;
      data_registro: string;
    }>;
    total_testes: number;
  }>;
  programacoes: Array<{
    id: number;
    descricao_atividade: string;
    data_inicio: string;
    data_fim: string;
    status: string;
    prioridade: string;
    setor: string;
    observacoes: string;
    data_criacao: string;
  }>;
  pendencias: Array<{
    id: number;
    numero_os: string;
    cliente: string;
    tipo_maquina: string;
    descricao_maquina: string;
    descricao_pendencia: string;
    status: string;
    prioridade: string;
    data_inicio: string;
    data_fechamento: string;
    solucao_aplicada: string;
  }>;
  estatisticas: {
    total_apontamentos: number;
    total_programacoes: number;
    total_pendencias: number;
    total_testes: number;
    testes_aprovados: number;
    testes_reprovados: number;
    testes_inconclusivos: number;
  };
}

const ConsultaOSTab: React.FC = () => {
  const [numeroOS, setNumeroOS] = useState('');
  const [osData, setOsData] = useState<OSData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const buscarOS = async () => {
    if (!numeroOS.trim()) {
      setError('Digite o número da OS');
      return;
    }

    setLoading(true);
    setError('');
    setOsData(null);

    try {
      console.log(`🔍 Buscando dados completos da OS: ${numeroOS}`);
      const response = await api.get(`/os/${numeroOS}/dados-completos`);
      setOsData(response.data);
      console.log('✅ Dados da OS carregados:', response.data);
    } catch (error: any) {
      console.error('❌ Erro ao buscar OS:', error);
      if (error.response?.status === 404) {
        setError(`OS ${numeroOS} não encontrada`);
      } else {
        setError('Erro ao buscar dados da OS');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('pt-BR');
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'APROVADO': return 'text-green-600 bg-green-100';
      case 'REPROVADO': return 'text-red-600 bg-red-100';
      case 'INCONCLUSIVO': return 'text-yellow-600 bg-yellow-100';
      case 'CONCLUIDO': return 'text-blue-600 bg-blue-100';
      case 'EM_ANDAMENTO': return 'text-orange-600 bg-orange-100';
      case 'PENDENTE': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-sm">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">🔍 Consulta de Ordem de Serviço</h2>
        
        {/* Campo de busca */}
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número da OS
            </label>
            <input
              type="text"
              value={numeroOS}
              onChange={(e) => setNumeroOS(e.target.value)}
              placeholder="Ex: OS-2025-001"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && buscarOS()}
            />
          </div>
          <button
            onClick={buscarOS}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>

      {/* Resultados */}
      {osData && (
        <div className="space-y-6">
          {/* Informações da OS */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">📋 Informações da OS</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <span className="font-medium text-gray-700">Número:</span>
                <span className="ml-2 text-gray-900">{osData.os_info.numero}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Status:</span>
                <span className={`ml-2 px-2 py-1 rounded text-xs ${getStatusColor(osData.os_info.status)}`}>
                  {osData.os_info.status}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Prioridade:</span>
                <span className="ml-2 text-gray-900">{osData.os_info.prioridade}</span>
              </div>
              <div className="md:col-span-2 lg:col-span-3">
                <span className="font-medium text-gray-700">Descrição:</span>
                <span className="ml-2 text-gray-900">{osData.os_info.descricao_maquina}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Criada em:</span>
                <span className="ml-2 text-gray-900">{formatDate(osData.os_info.data_criacao)}</span>
              </div>
            </div>
          </div>

          {/* Estatísticas */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">📊 Estatísticas</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{osData.estatisticas.total_apontamentos}</div>
                <div className="text-sm text-gray-600">Apontamentos</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{osData.estatisticas.total_programacoes}</div>
                <div className="text-sm text-gray-600">Programações</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{osData.estatisticas.total_pendencias}</div>
                <div className="text-sm text-gray-600">Pendências</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">{osData.estatisticas.total_testes}</div>
                <div className="text-sm text-gray-600">Total Testes</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{osData.estatisticas.testes_aprovados}</div>
                <div className="text-sm text-gray-600">Aprovados</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{osData.estatisticas.testes_reprovados}</div>
                <div className="text-sm text-gray-600">Reprovados</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{osData.estatisticas.testes_inconclusivos}</div>
                <div className="text-sm text-gray-600">Inconclusivos</div>
              </div>
            </div>
          </div>

          {/* Apontamentos */}
          <div className="bg-white border rounded-lg">
            <div className="bg-gray-50 px-4 py-3 border-b">
              <h3 className="text-lg font-semibold text-gray-900">📝 Apontamentos ({osData.apontamentos.length})</h3>
            </div>
            <div className="p-4">
              {osData.apontamentos.length === 0 ? (
                <p className="text-gray-500 text-center py-4">Nenhum apontamento encontrado</p>
              ) : (
                <div className="space-y-4">
                  {osData.apontamentos.map((apt, index) => (
                    <div key={apt.id} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-semibold text-gray-900">Apontamento #{index + 1}</h4>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(apt.status)}`}>
                          {apt.status}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
                        <div>
                          <span className="font-medium text-gray-700">Tipo Máquina:</span>
                          <span className="ml-2 text-gray-900">{apt.tipo_maquina || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Atividade:</span>
                          <span className="ml-2 text-gray-900">{apt.tipo_atividade || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Subcategoria:</span>
                          <span className="ml-2 text-gray-900">{apt.subcategoria || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Início:</span>
                          <span className="ml-2 text-gray-900">{formatDate(apt.data_hora_inicio)}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Fim:</span>
                          <span className="ml-2 text-gray-900">{formatDate(apt.data_hora_fim)}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Criado por:</span>
                          <span className="ml-2 text-gray-900">{apt.criado_por_email || 'N/A'}</span>
                        </div>
                      </div>

                      {apt.observacao_os && (
                        <div className="mb-3">
                          <span className="font-medium text-gray-700">Observação:</span>
                          <span className="ml-2 text-gray-900">{apt.observacao_os}</span>
                        </div>
                      )}

                      {/* Resultados de Teste */}
                      {apt.resultados_teste.length > 0 && (
                        <div className="mt-3">
                          <h5 className="font-medium text-gray-700 mb-2">🧪 Resultados de Teste ({apt.total_testes})</h5>
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                              <thead className="bg-gray-100">
                                <tr>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Teste</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Categoria</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Resultado</th>
                                  <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Observação</th>
                                </tr>
                              </thead>
                              <tbody className="bg-white divide-y divide-gray-200">
                                {apt.resultados_teste.map((teste) => (
                                  <tr key={teste.id}>
                                    <td className="px-3 py-2 text-sm text-gray-900">{teste.teste_nome}</td>
                                    <td className="px-3 py-2 text-sm text-gray-500">{teste.teste_categoria || 'N/A'}</td>
                                    <td className="px-3 py-2 text-sm text-gray-500">{teste.teste_tipo || 'N/A'}</td>
                                    <td className="px-3 py-2">
                                      <span className={`px-2 py-1 rounded text-xs ${getStatusColor(teste.resultado)}`}>
                                        {teste.resultado}
                                      </span>
                                    </td>
                                    <td className="px-3 py-2 text-sm text-gray-500">{teste.observacao || 'N/A'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Programações */}
          <div className="bg-white border rounded-lg">
            <div className="bg-gray-50 px-4 py-3 border-b">
              <h3 className="text-lg font-semibold text-gray-900">📅 Programações ({osData.programacoes.length})</h3>
            </div>
            <div className="p-4">
              {osData.programacoes.length === 0 ? (
                <p className="text-gray-500 text-center py-4">Nenhuma programação encontrada</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Setor</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Prioridade</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Data Início</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Data Fim</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {osData.programacoes.map((prog) => (
                        <tr key={prog.id}>
                          <td className="px-4 py-2 text-sm text-gray-900">{prog.descricao_atividade}</td>
                          <td className="px-4 py-2 text-sm text-gray-500">{prog.setor || 'N/A'}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2 py-1 rounded text-xs ${getStatusColor(prog.status)}`}>
                              {prog.status}
                            </span>
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-500">{prog.prioridade || 'N/A'}</td>
                          <td className="px-4 py-2 text-sm text-gray-500">{formatDate(prog.data_inicio)}</td>
                          <td className="px-4 py-2 text-sm text-gray-500">{formatDate(prog.data_fim)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Pendências */}
          <div className="bg-white border rounded-lg">
            <div className="bg-gray-50 px-4 py-3 border-b">
              <h3 className="text-lg font-semibold text-gray-900">⚠️ Pendências ({osData.pendencias.length})</h3>
            </div>
            <div className="p-4">
              {osData.pendencias.length === 0 ? (
                <p className="text-gray-500 text-center py-4">Nenhuma pendência encontrada</p>
              ) : (
                <div className="space-y-4">
                  {osData.pendencias.map((pend) => (
                    <div key={pend.id} className="border rounded-lg p-4 bg-red-50">
                      <div className="flex justify-between items-start mb-3">
                        <h4 className="font-semibold text-gray-900">Pendência #{pend.id}</h4>
                        <span className={`px-2 py-1 rounded text-xs ${getStatusColor(pend.status)}`}>
                          {pend.status}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
                        <div>
                          <span className="font-medium text-gray-700">Cliente:</span>
                          <span className="ml-2 text-gray-900">{pend.cliente || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Tipo Máquina:</span>
                          <span className="ml-2 text-gray-900">{pend.tipo_maquina || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Prioridade:</span>
                          <span className="ml-2 text-gray-900">{pend.prioridade || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Data Início:</span>
                          <span className="ml-2 text-gray-900">{formatDate(pend.data_inicio)}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Data Fechamento:</span>
                          <span className="ml-2 text-gray-900">{formatDate(pend.data_fechamento)}</span>
                        </div>
                      </div>

                      <div className="mb-3">
                        <span className="font-medium text-gray-700">Descrição:</span>
                        <span className="ml-2 text-gray-900">{pend.descricao_pendencia}</span>
                      </div>

                      {pend.solucao_aplicada && (
                        <div className="mb-3">
                          <span className="font-medium text-gray-700">Solução Aplicada:</span>
                          <span className="ml-2 text-gray-900">{pend.solucao_aplicada}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConsultaOSTab;
