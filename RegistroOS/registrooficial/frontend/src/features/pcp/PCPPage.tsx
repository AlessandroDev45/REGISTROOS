import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Layout from '../../components/Layout';
import { useCachedSetores } from '../../hooks/useCachedSetores';
import {
  getProgramacoes,
  createProgramacao,
  getProgramacaoFormData,
  getOsDisponiveisForPcp,
  getTiposAtividade,
  getDescricoesAtividade
} from '../../services/api';
import { getStatusColorClass, getPriorityColorClass, getTipoColorClass } from '../../utils/statusColors';

// Importar novos componentes
import DashboardPCPInterativo from './components/DashboardPCPInterativo';
import PendenciasList from './components/PendenciasList';
import PendenciasDashboard from './components/PendenciasDashboard';
import PendenciasFiltros from './components/PendenciasFiltros';
import ProgramacoesList from './components/ProgramacoesList';
import ProgramacaoForm from './components/ProgramacaoForm';
import ProgramacaoFormSimples from './components/ProgramacaoFormSimples';
import ProgramacaoCalendario from './components/ProgramacaoCalendario';
import ProgramacaoFiltros from './components/ProgramacaoFiltros';
import RelatoriosAnalises from './components/RelatoriosAnalises';

interface OrdemServico {
  id: number;
  os_numero: string;
  cliente_id?: number;
  equipamento_id?: number;
  setor: string;
  departamento: string;
  status: string;
  descricao_maquina?: string;
}

interface Programacao {
  id: number;
  id_ordem_servico: number;
  os_numero: string;
  cliente: string;
  equipamento: string;
  setor: string;
  departamento: string;
  responsavel: string;
  responsavel_id?: number;
  status: string;
  inicio_previsto: string;
  fim_previsto: string;
  observacoes?: string;
  created_at?: string;
  updated_at?: string;
}

const PCPPage: React.FC = () => {
  const { user } = useAuth();
  const { todosSetores, loading: setoresLoading } = useCachedSetores();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'pendencias' | 'programacoes' | 'calendario' | 'relatorios'>('dashboard');
  const [ordensServico, setOrdensServico] = useState<OrdemServico[]>([]);
  const [programacoes, setProgramacoes] = useState<Programacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [filtroStatus, setFiltroStatus] = useState<string>('TODOS');
  const [filtroSetor, setFiltroSetor] = useState<string>('TODOS');
  const [filtroPrioridade, setFiltroPrioridade] = useState<string>('TODOS');
  const [showNovaProgramacaoModal, setShowNovaProgramacaoModal] = useState(false);

  // Estados para os novos componentes
  const [filtrosPendencias, setFiltrosPendencias] = useState({});
  const [periodoDashboard, setPeriodoDashboard] = useState(30);
  const [setorSelecionado, setSetorSelecionado] = useState<number | undefined>();
  const [showProgramacaoForm, setShowProgramacaoForm] = useState(false);
  const [programacaoEditando, setProgramacaoEditando] = useState(null);
  const [filtrosProgramacao, setFiltrosProgramacao] = useState<any>({});
  const [novaProgramacao, setNovaProgramacao] = useState({
    id_ordem_servico: '',
    cliente: '',
    equipamento: '',
    tipo_atividade: '',
    descricao_atividade: '',
    inicio_previsto: '',
    fim_previsto: '',
    setor: '',
    responsavel_id: '',
    observacoes: ''
  });

  // Dados do formulário vindos da database
  const [formData, setFormData] = useState({
    ordens_servico: [],
    clientes: [],
    equipamentos: [],
    tipos_atividade: [],
    descricoes_atividade: [],
    setores: [],
    supervisores: []
  });

  // Carregar dados reais da database
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Carregar ordens de serviço
        const osData = await getOsDisponiveisForPcp();
        setOrdensServico(osData);

        // Carregar programações
        const progData = await getProgramacoes();
        setProgramacoes(progData);

        // Carregar dados do formulário
        const formDataResponse = await getProgramacaoFormData();
        setFormData(formDataResponse);

      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const ordensFiltradas = ordensServico.filter(os => {
    const statusMatch = filtroStatus === 'TODOS' || os.status === filtroStatus;
    const setorMatch = filtroSetor === 'TODOS' || os.setor === filtroSetor;
    // Removido filtro de prioridade pois não existe no modelo atual
    return statusMatch && setorMatch;
  });

  // Estabilizar objetos filtros para evitar loops infinitos
  const filtrosProgramacaoEstavel = useMemo(() => filtrosProgramacao, [
    filtrosProgramacao.status,
    filtrosProgramacao.setor,
    filtrosProgramacao.departamento,
    filtrosProgramacao.periodo,
    filtrosProgramacao.atribuida_supervisor,
    filtrosProgramacao.prioridade
  ]);

  const filtrosPendenciasEstavel = useMemo(() => filtrosPendencias, [
    filtrosPendencias.status,
    filtrosPendencias.setor,
    filtrosPendencias.departamento,
    filtrosPendencias.periodo,
    filtrosPendencias.prioridade,
    filtrosPendencias.tipo
  ]);


  const Dashboard = () => (
    <div className="space-y-6">
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Total OS</h3>
          <p className="text-3xl font-bold text-blue-600">{ordensServico.length}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Em Andamento</h3>
          <p className="text-3xl font-bold text-yellow-600">
            {ordensServico.filter(os => os.status === 'EM_ANDAMENTO').length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Finalizadas</h3>
          <p className="text-3xl font-bold text-green-600">
            {ordensServico.filter(os => os.status === 'FINALIZADA').length}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-900">Atrasadas</h3>
          <p className="text-3xl font-bold text-red-600">
            {ordensServico.filter(os => os.status === 'ATRASADA').length}
          </p>
        </div>
      </div>

      {/* Timeline Visual */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Timeline de Produção</h3>
        <div className="space-y-4">
          {ordensServico.slice(0, 5).map(os => (
            <div key={os.id} className="flex items-center space-x-4">
              <div className="w-4 h-4 rounded-full" style={{
                backgroundColor: os.status === 'FINALIZADA' ? '#10B981' :
                                os.status === 'EM_ANDAMENTO' ? '#3B82F6' : '#F59E0B'
              }}></div>
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="font-medium">{os.os_numero}</span>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColorClass(os.status)}`}>
                    {os.status}
                  </span>
                </div>
                <div className="text-sm text-gray-600">{os.descricao_maquina || 'Equipamento não informado'}</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${os.status === 'ABERTA' ? 0 : os.status === 'EM_ANDAMENTO' ? 50 : 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const OrdensServico = () => (
    <div className="space-y-6">
      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-wrap gap-4">
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="TODOS">Todos Status</option>
            <option value="PENDENTE">Pendente</option>
            <option value="EM_ANDAMENTO">Em Andamento</option>
            <option value="FINALIZADA">Finalizada</option>
            <option value="ATRASADA">Atrasada</option>
          </select>

          <select
            value={filtroSetor}
            onChange={(e) => setFiltroSetor(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="TODOS">Todos Setores</option>
            {setoresLoading ? (
                <option>Carregando setores...</option>
            ) : (
                todosSetores.map((setor, index) => (
                    <option key={`setor-${index}-${setor.nome}`} value={setor.nome}>{setor.nome}</option>
                ))
            )}
          </select>

          <select
            value={filtroPrioridade}
            onChange={(e) => setFiltroPrioridade(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="TODOS">Todas Prioridades</option>
            <option value="BAIXA">Baixa</option>
            <option value="MEDIA">Média</option>
            <option value="ALTA">Alta</option>
            <option value="URGENTE">Urgente</option>
          </select>

          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Nova OS
          </button>
        </div>
      </div>

      {/* Tabela de OS */}
      <div className="bg-white shadow overflow-hidden rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OS</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Equipamento</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prioridade</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progresso</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {ordensFiltradas.map((os) => (
              <tr key={os.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{os.os_numero}</div>
                  <div className="text-sm text-gray-500">{os.setor}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Cliente não informado</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{os.descricao_maquina || 'Equipamento não informado'}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColorClass(os.status)}`}>
                    {os.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded bg-gray-100 text-gray-800`}>
                    {os.departamento}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${os.status === 'ABERTA' ? 0 : os.status === 'EM_ANDAMENTO' ? 50 : 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-500">{os.status === 'ABERTA' ? 0 : os.status === 'EM_ANDAMENTO' ? 50 : 100}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                  <button className="text-red-600 hover:text-red-900">Excluir</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const Programacao = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Programação de Produção</h2>
        <button
          onClick={() => setShowNovaProgramacaoModal(true)}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Nova Programação
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-wrap gap-4">
          <select className="px-3 py-2 border border-gray-300 rounded-md">
            <option value="TODOS">Todos Status</option>
            <option value="PLANEJADA">Planejada</option>
            <option value="EXECUTANDO">Executando</option>
            <option value="CONCLUIDA">Concluída</option>
            <option value="ATRASADA">Atrasada</option>
          </select>

          <select className="px-3 py-2 border border-gray-300 rounded-md">
            <option value="TODOS">Todos Tipos</option>
            <option value="MANUTENCAO">Manutenção</option>
            <option value="TESTE">Teste</option>
            <option value="MONTAGEM">Montagem</option>
            <option value="DESMONTAGEM">Desmontagem</option>
          </select>

          <select className="px-3 py-2 border border-gray-300 rounded-md">
            <option value="TODOS">Todos Setores</option>
            {setoresLoading ? (
                <option>Carregando setores...</option>
            ) : (
                todosSetores.map((setor, index) => (
                    <option key={`setor-${index}-${setor.nome}`} value={setor.nome}>{setor.nome}</option>
                ))
            )}
          </select>
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OS</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Atividade</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição da Atividade</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Período</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Setor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Responsável</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {programacoes.map((prog) => (
              <tr key={prog.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{prog.os_numero}</div>
                  <div className="text-xs text-gray-500">ID: {prog.id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{prog.cliente}</div>
                  <div className="text-xs text-gray-500">Setor: {prog.setor}</div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-xs truncate" title={prog.equipamento}>
                    {prog.equipamento}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 font-medium">
                    {new Date(prog.inicio_previsto).toLocaleDateString('pt-BR')} - {new Date(prog.fim_previsto).toLocaleDateString('pt-BR')}
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(prog.inicio_previsto).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})} - {new Date(prog.fim_previsto).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                    {prog.setor}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {prog.responsavel}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColorClass(prog.status)}`}>
                    {prog.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-indigo-600 hover:text-indigo-900 mr-3">Editar</button>
                  <button className="text-red-600 hover:text-red-900 mr-3">Excluir</button>
                  <button className="text-green-600 hover:text-green-900">Iniciar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const Calendario = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Calendário de Produção</h2>
        <div className="flex space-x-2">
          <button className="px-3 py-2 bg-gray-200 text-gray-700 rounded-md">Dia</button>
          <button className="px-3 py-2 bg-gray-200 text-gray-700 rounded-md">Semana</button>
          <button className="px-3 py-2 bg-blue-600 text-white rounded-md">Mês</button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-7 gap-4 mb-4">
          {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(day => (
            <div key={day} className="text-center font-medium text-gray-500 py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-4">
          {/* Calendário simplificado - em produção seria mais complexo */}
          {Array.from({ length: 35 }, (_, i) => (
            <div key={i} className="min-h-24 border border-gray-200 rounded p-2">
              <div className="text-sm font-medium text-gray-900 mb-1">{i + 1}</div>
              {i === 15 && (
                <div className="text-xs bg-blue-100 text-blue-800 p-1 rounded mb-1">
                  OS-001 Manutenção
                </div>
              )}
              {i === 20 && (
                <div className="text-xs bg-green-100 text-green-800 p-1 rounded">
                  OS-002 Testes
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Timeline de OS */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Timeline das Ordens de Serviço</h3>
        <div className="space-y-4">
          {ordensServico.map(os => (
            <div key={os.id} className="flex items-center space-x-4">
              <div className="w-32 text-sm text-gray-600">{os.os_numero}</div>
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span>{os.descricao_maquina || 'Equipamento não informado'}</span>
                  <span>{os.status}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full ${
                      os.status === 'FINALIZADA' ? 'bg-green-500' :
                      os.status === 'EM_ANDAMENTO' ? 'bg-blue-500' :
                      os.status === 'ATRASADA' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${os.status === 'ABERTA' ? 0 : os.status === 'EM_ANDAMENTO' ? 50 : 100}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {os.setor} - {os.departamento}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const NovaProgramacaoModal = () => {
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setLoading(true);

      try {
        // Criar nova programação usando API real
        const programacaoData = {
          id_ordem_servico: parseInt(novaProgramacao.id_ordem_servico),
          inicio_previsto: novaProgramacao.inicio_previsto,
          fim_previsto: novaProgramacao.fim_previsto,
          responsavel_id: novaProgramacao.responsavel_id ? parseInt(novaProgramacao.responsavel_id) : undefined,
          observacoes: novaProgramacao.observacoes
        };

        const result = await createProgramacao(programacaoData);

        // Recarregar programações
        const updatedProgramacoes = await getProgramacoes();
        setProgramacoes(updatedProgramacoes);

        // Reset form
        setNovaProgramacao({
          id_ordem_servico: '',
          cliente: '',
          equipamento: '',
          tipo_atividade: '',
          descricao_atividade: '',
          inicio_previsto: '',
          fim_previsto: '',
          setor: '',
          responsavel_id: '',
          observacoes: ''
        });

        setShowNovaProgramacaoModal(false);
        alert('Programação criada com sucesso!');

      } catch (error) {
        console.error('Erro ao criar programação:', error);
        alert('Erro ao criar programação. Tente novamente.');
      } finally {
        setLoading(false);
      }
    };

    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-2xl shadow-lg rounded-md bg-white">
          <div className="mt-3">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Nova Programação de Produção</h3>
              <button
                onClick={() => setShowNovaProgramacaoModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Ordem de Serviço</label>
                  <select
                    required
                    value={novaProgramacao.id_ordem_servico}
                    onChange={(e) => {
                      const osId = e.target.value;
                      const os = (formData.ordens_servico || []).find((o: any) => o.id.toString() === osId);

                      setNovaProgramacao({
                        ...novaProgramacao,
                        id_ordem_servico: osId,
                        cliente: 'Cliente da OS',
                        equipamento: os?.descricao_maquina || 'Equipamento não informado',
                        setor: os?.setor || ''
                      });
                    }}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Selecione uma OS</option>
                    {(formData.ordens_servico || []).map((os: any) => (
                      <option key={os.id} value={os.id}>
                        {os.os_numero} - {os.setor}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Cliente</label>
                  <input
                    type="text"
                    readOnly
                    value={novaProgramacao.cliente}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50"
                    placeholder="Será preenchido automaticamente"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Equipamento</label>
                  <input
                    type="text"
                    readOnly
                    value={novaProgramacao.equipamento}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50"
                    placeholder="Será preenchido automaticamente"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Tipo de Atividade</label>
                  <select
                    required
                    value={novaProgramacao.tipo_atividade}
                    onChange={(e) => setNovaProgramacao({...novaProgramacao, tipo_atividade: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Selecione o tipo</option>
                    {(formData.tipos_atividade || [])
                      .filter((tipo: any) => !novaProgramacao.setor || tipo.setor === novaProgramacao.setor)
                      .map((tipo: any) => (
                        <option key={tipo.id} value={tipo.nome_tipo}>
                          {tipo.nome_tipo}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Descrição da Atividade</label>
                  <select
                    required
                    value={novaProgramacao.descricao_atividade}
                    onChange={(e) => setNovaProgramacao({...novaProgramacao, descricao_atividade: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Selecione a descrição</option>
                    {(formData.descricoes_atividade || [])
                      .filter((desc: any) => !novaProgramacao.setor || desc.setor === novaProgramacao.setor)
                      .map((desc: any) => (
                        <option key={desc.id} value={desc.descricao}>
                          {desc.codigo} - {desc.descricao}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Data/Hora Início</label>
                  <input
                    type="datetime-local"
                    required
                    value={novaProgramacao.inicio_previsto}
                    onChange={(e) => setNovaProgramacao({...novaProgramacao, inicio_previsto: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Data/Hora Fim</label>
                  <input
                    type="datetime-local"
                    required
                    value={novaProgramacao.fim_previsto}
                    onChange={(e) => setNovaProgramacao({...novaProgramacao, fim_previsto: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Setor</label>
                  <input
                    type="text"
                    readOnly
                    value={novaProgramacao.setor}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50"
                    placeholder="Será preenchido automaticamente"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Responsável</label>
                  <select
                    value={novaProgramacao.responsavel_id}
                    onChange={(e) => setNovaProgramacao({...novaProgramacao, responsavel_id: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Supervisor do setor (automático)</option>
                    {(formData.supervisores || []).map((supervisor: any) => (
                      <option key={supervisor.id} value={supervisor.id}>
                        {supervisor.nome_completo} - {supervisor.setor}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700">Observações</label>
                  <textarea
                    rows={3}
                    value={novaProgramacao.observacoes}
                    onChange={(e) => setNovaProgramacao({...novaProgramacao, observacoes: e.target.value})}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Observações adicionais (opcional)"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowNovaProgramacaoModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  Criar Programação
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Navigation Tabs */}
        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'dashboard', label: '📊 Dashboard Executivo', icon: '📊' },
                { id: 'pendencias', label: '⚠️ Pendências', icon: '⚠️' },
                { id: 'programacoes', label: '⚙️ Programações', icon: '⚙️' },
                { id: 'calendario', label: '📅 Calendário', icon: '📅' },
                { id: 'relatorios', label: '📈 Relatórios', icon: '📈' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'dashboard' && (
              <DashboardPCPInterativo
                periodoDias={periodoDashboard}
                setorSelecionado={setorSelecionado}
              />
            )}

            {activeTab === 'pendencias' && (
              <div className="space-y-6">
                <PendenciasFiltros
                  filtros={filtrosPendencias}
                  onFiltrosChange={setFiltrosPendencias}
                  onLimparFiltros={() => setFiltrosPendencias({})}
                />

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                  <div className="lg:col-span-2">
                    <PendenciasList
                      filtros={filtrosPendenciasEstavel}
                    />
                  </div>
                  <div className="lg:col-span-3">
                    <PendenciasDashboard
                      periodoDias={periodoDashboard}
                      onPeriodoChange={setPeriodoDashboard}
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'programacoes' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold text-gray-900">Gestão de Programações</h2>
                  <button
                    onClick={() => setShowProgramacaoForm(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Nova Programação
                  </button>
                </div>

                {showProgramacaoForm ? (
                  <ProgramacaoForm
                    programacaoInicial={programacaoEditando}
                    isEditing={!!programacaoEditando}
                    onSalvar={(programacao) => {
                      console.log('Programação salva:', programacao);
                      setShowProgramacaoForm(false);
                      setProgramacaoEditando(null);
                      // Recarregar lista de programações
                    }}
                    onCancelar={() => {
                      setShowProgramacaoForm(false);
                      setProgramacaoEditando(null);
                    }}
                  />
                ) : (
                  <>
                    <ProgramacaoFiltros
                      filtros={filtrosProgramacao}
                      onFiltrosChange={setFiltrosProgramacao}
                    />
                    <ProgramacoesList
                      filtros={filtrosProgramacaoEstavel}
                      onProgramacaoUpdate={() => {
                        // Callback para atualizar dados
                      }}
                    />
                  </>
                )}
              </div>
            )}

            {activeTab === 'calendario' && (
              <ProgramacaoCalendario
                onProgramacaoSelect={(programacao) => {
                  console.log('Programação selecionada no calendário:', programacao);
                }}
                filtros={{}}
              />
            )}

            {activeTab === 'relatorios' && (
              <RelatoriosAnalises />
            )}
          </div>
        </div>
      </div>

      {/* Modal para Nova Programação */}
      {showNovaProgramacaoModal && <NovaProgramacaoModal />}
    </Layout>
  );
};

export default PCPPage;
