import React, { useState, useEffect } from 'react';
import { ConfiguracaoSetor } from '../../../../pages/common/TiposApi';
import { registrarTesteSetor, listarTestesOS } from '../../../../services/api';
import { useAuth } from '../../../../contexts/AuthContext';

interface TesteTabProps {
  sectorConfig: ConfiguracaoSetor;
  sectorKey: string;
}

const TesteTab: React.FC<TesteTabProps> = ({ sectorConfig, sectorKey }) => {
  const { user } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState('novo');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Estados para novo teste
  const [osNumero, setOsNumero] = useState('');
  const [tipoTeste, setTipoTeste] = useState('');
  const [resultados, setResultados] = useState<any>({});
  const [observacoes, setObservacoes] = useState('');
  
  // Estados para listagem
  const [testes, setTestes] = useState<any[]>([]);
  const [filtroOS, setFiltroOS] = useState('');

  const subTabs = [
    { id: 'novo', label: 'Novo Teste', icon: '🧪' },
    { id: 'historico', label: 'Histórico', icon: '📋' },
    { id: 'relatorios', label: 'Relatórios', icon: '📊' }
  ];

  useEffect(() => {
    if (activeSubTab === 'historico') {
      carregarTestes();
    }
  }, [activeSubTab]);

  const carregarTestes = async () => {
    try {
      setLoading(true);
      const data = await listarTestesOS(0, sectorKey); // 0 para todos
      setTestes(data);
    } catch (error) {
      console.error('Erro ao carregar testes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitTeste = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const testeData = {
        os_numero: osNumero,
        usuario_id: user?.id,
        setor: sectorKey,
        tipo_teste: tipoTeste,
        resultados: JSON.stringify(resultados),
        observacoes,
        data_teste: new Date().toISOString().split('T')[0]
      };

      await registrarTesteSetor(0, testeData); // 0 será substituído pelo ID real da OS
      
      setMessage({ type: 'success', text: 'Teste registrado com sucesso!' });
      
      // Limpar formulário
      setOsNumero('');
      setTipoTeste('');
      setResultados({});
      setObservacoes('');
      
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'Erro ao registrar teste' 
      });
    } finally {
      setLoading(false);
    }
  };

  const renderNovoTeste = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Registrar Novo Teste</h3>
      
      {message && (
        <div className={`p-4 rounded-md ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmitTeste} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Número da OS *
            </label>
            <input
              type="text"
              value={osNumero}
              onChange={(e) => setOsNumero(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: OS-2024-001"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo de Teste *
            </label>
            <select
              value={tipoTeste}
              onChange={(e) => setTipoTeste(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Selecione...</option>
              {Object.keys(sectorConfig.DicionarioTestes || {}).map((teste) => (
                <option key={teste} value={teste}>{teste}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Campos de resultado específicos do teste */}
        {tipoTeste && sectorConfig.DicionarioTestes?.[tipoTeste] && (
          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium mb-3">Resultados do Teste: {tipoTeste}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(sectorConfig.DicionarioTestes[tipoTeste].campos || {}).map(([campo, config]: [string, any]) => (
                <div key={campo}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {config.label || campo}
                  </label>
                  {config.tipo === 'number' ? (
                    <input
                      type="number"
                      step="0.01"
                      value={resultados[campo] || ''}
                      onChange={(e) => setResultados(prev => ({ ...prev, [campo]: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={config.placeholder}
                    />
                  ) : (
                    <input
                      type="text"
                      value={resultados[campo] || ''}
                      onChange={(e) => setResultados(prev => ({ ...prev, [campo]: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={config.placeholder}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Observações
          </label>
          <textarea
            value={observacoes}
            onChange={(e) => setObservacoes(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Observações sobre o teste..."
          />
        </div>

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => {
              setOsNumero('');
              setTipoTeste('');
              setResultados({});
              setObservacoes('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Limpar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Registrar Teste'}
          </button>
        </div>
      </form>
    </div>
  );

  const renderHistorico = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Histórico de Testes</h3>
        <div className="flex space-x-4">
          <input
            type="text"
            value={filtroOS}
            onChange={(e) => setFiltroOS(e.target.value)}
            placeholder="Filtrar por OS..."
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={carregarTestes}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Atualizar
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
                  OS
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo de Teste
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Colaborador
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {testes
                .filter(teste => !filtroOS || teste.os_numero?.includes(filtroOS))
                .map((teste, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {teste.os_numero}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {teste.tipo_teste}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {teste.data_teste}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {teste.usuario_nome}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      Concluído
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderRelatorios = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Relatórios de Testes</h3>
      <div className="bg-gray-50 p-8 rounded-lg text-center">
        <p className="text-gray-500">Funcionalidade de relatórios em desenvolvimento</p>
      </div>
    </div>
  );

  const renderSubTabContent = () => {
    switch (activeSubTab) {
      case 'novo':
        return renderNovoTeste();
      case 'historico':
        return renderHistorico();
      case 'relatorios':
        return renderRelatorios();
      default:
        return renderNovoTeste();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-6">Testes - {sectorConfig.NomeSetor}</h2>
      
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

export default TesteTab;
