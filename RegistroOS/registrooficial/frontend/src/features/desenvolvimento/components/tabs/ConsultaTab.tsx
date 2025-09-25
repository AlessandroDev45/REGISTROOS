import React, { useState, useEffect } from 'react';
import { ConfiguracaoSetor } from '../../../../pages/common/TiposApi';
import { useAuth } from '../../../../contexts/AuthContext';
import api from '../../../../services/api';

interface ConsultaTabProps {
  sectorConfig: ConfiguracaoSetor;
  sectorKey: string;
}

const ConsultaTab: React.FC<ConsultaTabProps> = ({ sectorConfig, sectorKey }) => {
  const { user } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState('consulta-os');
  const [loading, setLoading] = useState(false);

  // Estados para consulta por OS
  const [numeroOS, setNumeroOS] = useState('');
  const [registrosOS, setRegistrosOS] = useState<any[]>([]);
  const [osDetalhes, setOsDetalhes] = useState<any>(null);

  // Estados para consulta geral
  const [ordensServico, setOrdensServico] = useState<any[]>([]);
  const [filtroOS, setFiltroOS] = useState('');
  const [filtroStatus, setFiltroStatus] = useState('');

  // Estados para consulta de apontamentos
  const [apontamentos, setApontamentos] = useState<any[]>([]);
  const [osIdConsulta, setOsIdConsulta] = useState('');

  const subTabs = [
    { id: 'consulta-os', label: 'Consulta por OS', icon: '🔍' },
    { id: 'ordens', label: 'Ordens de Serviço', icon: '📋' },
    { id: 'apontamentos', label: 'Apontamentos', icon: '📝' },
    { id: 'relatorios', label: 'Relatórios', icon: '📊' }
  ];

  useEffect(() => {
    if (activeSubTab === 'ordens') {
      carregarOrdensServico();
    }
  }, [activeSubTab]);

  // Função para consultar registros por OS
  const consultarRegistrosPorOS = async () => {
    if (!numeroOS.trim()) {
      alert('Por favor, digite o número da OS');
      return;
    }

    try {
      setLoading(true);

      // Buscar detalhes da OS
      const responseOS = await api.get(`/ordens-servico`, {
        params: { os_numero: numeroOS.trim() }
      });

      if (responseOS.data && responseOS.data.length > 0) {
        setOsDetalhes(responseOS.data[0]);

        // Buscar todos os apontamentos da OS
        const responseApontamentos = await api.get(`/apontamentos`, {
          params: { os_numero: numeroOS.trim() }
        });

        // Buscar pendências da OS
        const responsePendencias = await api.get(`/pendencias`, {
          params: { numero_os: numeroOS.trim() }
        });

        // Buscar programações da OS
        const responseProgramacao = await api.get(`/programacao`, {
          params: { os_numero: numeroOS.trim() }
        });

        // Consolidar todos os registros
        const registros = [
          ...responseApontamentos.data.map((item: any) => ({
            ...item,
            tipo: 'Apontamento',
            data: item.data_criacao,
            responsavel: item.nome_tecnico || 'Não informado'
          })),
          ...responsePendencias.data.map((item: any) => ({
            ...item,
            tipo: 'Pendência',
            data: item.data_criacao,
            responsavel: item.responsavel_inicio || 'Não informado'
          })),
          ...responseProgramacao.data.map((item: any) => ({
            ...item,
            tipo: 'Programação',
            data: item.created_at,
            responsavel: item.criado_por || 'Não informado'
          }))
        ];

        // Ordenar por data
        registros.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());

        setRegistrosOS(registros);
      } else {
        alert('OS não encontrada');
        setOsDetalhes(null);
        setRegistrosOS([]);
      }

    } catch (error) {
      console.error('Erro ao consultar registros da OS:', error);
      alert('Erro ao consultar registros da OS');
    } finally {
      setLoading(false);
    }
  };

  const carregarOrdensServico = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filtroStatus) params.status = filtroStatus;
      if (filtroOS) params.os_numero = filtroOS;

      const response = await api.get('/ordens-servico', { params });
      setOrdensServico(response.data);
    } catch (error) {
      console.error('Erro ao carregar ordens de serviço:', error);
    } finally {
      setLoading(false);
    }
  };

  const carregarApontamentos = async () => {
    if (!osIdConsulta) return;
    
    try {
      setLoading(true);
      const data = await listarApontamentosOS(parseInt(osIdConsulta), sectorKey);
      setApontamentos(data);
    } catch (error) {
      console.error('Erro ao carregar apontamentos:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderOrdensServico = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Ordens de Serviço - {sectorConfig.NomeSetor}</h3>
        <div className="flex space-x-4">
          <input
            type="text"
            value={filtroOS}
            onChange={(e) => setFiltroOS(e.target.value)}
            placeholder="Filtrar por número..."
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos os Status</option>
            <option value="ABERTA">Aberta</option>
            <option value="EM_ANDAMENTO">Em Andamento</option>
            <option value="CONCLUIDA">Concluída</option>
            <option value="CANCELADA">Cancelada</option>
          </select>
          <button
            onClick={carregarOrdensServico}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Buscar
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Número OS
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cliente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Equipamento
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data Criação
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {ordensServico.map((os, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {os.os_numero}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {os.cliente_nome}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {os.equipamento_descricao}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      os.status_os === 'CONCLUIDA' ? 'bg-green-100 text-green-800' :
                      os.status_os === 'EM_ANDAMENTO' ? 'bg-yellow-100 text-yellow-800' :
                      os.status_os === 'ABERTA' ? 'bg-blue-100 text-blue-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {os.status_os}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(os.data_criacao).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => setOsIdConsulta(os.id.toString())}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Ver Detalhes
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderApontamentos = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Apontamentos por OS</h3>
        <div className="flex space-x-4">
          <input
            type="text"
            value={osIdConsulta}
            onChange={(e) => setOsIdConsulta(e.target.value)}
            placeholder="ID da OS..."
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={carregarApontamentos}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Consultar
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : apontamentos.length > 0 ? (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Colaborador
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Atividade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hora Início
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hora Fim
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Observações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {apontamentos.map((apontamento, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(apontamento.data_apontamento).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {apontamento.usuario_nome}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {apontamento.atividade_tipo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {apontamento.hora_inicio}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {apontamento.hora_fim || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {apontamento.observacoes || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <p className="text-gray-500">Nenhum apontamento encontrado. Digite o ID de uma OS para consultar.</p>
        </div>
      )}
    </div>
  );

  const renderRelatorios = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Relatórios - {sectorConfig.NomeSetor}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <h4 className="font-medium mb-2">Relatório de Produtividade</h4>
          <p className="text-sm text-gray-600 mb-4">Apontamentos por período</p>
          <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Gerar Relatório
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <h4 className="font-medium mb-2">Relatório de Testes</h4>
          <p className="text-sm text-gray-600 mb-4">Resultados de testes por período</p>
          <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Gerar Relatório
          </button>
        </div>
        
        <div className="bg-white p-6 rounded-lg border hover:shadow-md transition-shadow">
          <h4 className="font-medium mb-2">Relatório de OS</h4>
          <p className="text-sm text-gray-600 mb-4">Status das ordens de serviço</p>
          <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Gerar Relatório
          </button>
        </div>
      </div>
    </div>
  );

  // Renderizar consulta por OS
  const renderConsultaPorOS = () => (
    <div className="space-y-6">
      {/* Formulário de consulta */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-medium mb-4">🔍 Consultar Registros por OS</h3>
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número da OS
            </label>
            <input
              type="text"
              value={numeroOS}
              onChange={(e) => setNumeroOS(e.target.value)}
              placeholder="Digite o número da OS (ex: OS-2024-0001)"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && consultarRegistrosPorOS()}
            />
          </div>
          <button
            onClick={consultarRegistrosPorOS}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Consultando...' : 'Consultar'}
          </button>
        </div>
      </div>

      {/* Detalhes da OS */}
      {osDetalhes && (
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-medium mb-4">📋 Detalhes da OS: {osDetalhes.os_numero}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Status</label>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                osDetalhes.status_os === 'FINALIZADA' ? 'bg-green-100 text-green-800' :
                osDetalhes.status_os === 'EM_ANDAMENTO' ? 'bg-yellow-100 text-yellow-800' :
                osDetalhes.status_os === 'ABERTA' ? 'bg-blue-100 text-blue-800' :
                'bg-red-100 text-red-800'
              }`}>
                {osDetalhes.status_os}
              </span>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Setor</label>
              <p className="text-sm text-gray-900">{osDetalhes.setor}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Departamento</label>
              <p className="text-sm text-gray-900">{osDetalhes.departamento}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Data Criação</label>
              <p className="text-sm text-gray-900">
                {osDetalhes.data_criacao ? new Date(osDetalhes.data_criacao).toLocaleDateString() : 'Não informado'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Horas Orçadas</label>
              <p className="text-sm text-gray-900">{osDetalhes.horas_orcadas || 0}h</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Horas Reais</label>
              <p className="text-sm text-gray-900">{osDetalhes.horas_reais || 0}h</p>
            </div>
          </div>
        </div>
      )}

      {/* Lista de registros */}
      {registrosOS.length > 0 && (
        <div className="bg-white rounded-lg border">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium">📝 Todos os Registros ({registrosOS.length})</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Parte/Máquina
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Categoria
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Subcategoria
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data/Hora
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Responsável
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Descrição
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {registrosOS.map((registro, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        registro.tipo === 'Apontamento' ? 'bg-blue-100 text-blue-800' :
                        registro.tipo === 'Pendência' ? 'bg-orange-100 text-orange-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {registro.tipo}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {registro.tipo_maquina || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                        registro.categoria === 'ESTATICOS' ? 'bg-blue-50 text-blue-700' :
                        registro.categoria === 'DINAMICOS' ? 'bg-green-50 text-green-700' :
                        'bg-gray-50 text-gray-700'
                      }`}>
                        {registro.categoria || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                        registro.subcategoria === 'VISUAL' ? 'bg-purple-50 text-purple-700' :
                        registro.subcategoria === 'ELETRICO' ? 'bg-yellow-50 text-yellow-700' :
                        registro.subcategoria === 'MECANICO' ? 'bg-red-50 text-red-700' :
                        'bg-gray-50 text-gray-700'
                      }`}>
                        {registro.subcategoria || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(registro.data).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {registro.responsavel}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                      {registro.observacoes || registro.descricao_pendencia || registro.observacoes || 'Sem descrição'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {registro.status_apontamento || registro.status || 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Mensagem quando não há registros */}
      {numeroOS && registrosOS.length === 0 && !loading && osDetalhes && (
        <div className="bg-white p-6 rounded-lg border text-center">
          <p className="text-gray-500">Nenhum registro encontrado para esta OS.</p>
        </div>
      )}
    </div>
  );

  const renderSubTabContent = () => {
    switch (activeSubTab) {
      case 'consulta-os':
        return renderConsultaPorOS();
      case 'ordens':
        return renderOrdensServico();
      case 'apontamentos':
        return renderApontamentos();
      case 'relatorios':
        return renderRelatorios();
      default:
        return renderConsultaPorOS();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-6">Consultas - {sectorConfig.NomeSetor}</h2>
      
      {/* Sub-tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {subTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`${
                activeSubTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {renderSubTabContent()}
    </div>
  );
};

export default ConsultaTab;
