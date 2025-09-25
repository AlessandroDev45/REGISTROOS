import React, { useState, useEffect } from 'react';
import { ConfiguracaoSetor } from '../../../../pages/common/TiposApi';
import { useAuth } from '../../../../contexts/AuthContext';

interface ConfiguracaoTabProps {
  sectorConfig: ConfiguracaoSetor;
  sectorKey: string;
}

const ConfiguracaoTab: React.FC<ConfiguracaoTabProps> = ({ sectorConfig, sectorKey }) => {
  const { user } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState('geral');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Estados para configurações
  const [configuracoes, setConfiguracoes] = useState({
    nomeSetor: sectorConfig.NomeSetor,
    chaveSetor: sectorConfig.ChaveSetor,
    endpointApontamento: sectorConfig.ConfiguracaoBackend.endPointApontamento,
    endpointOS: sectorConfig.ConfiguracaoBackend.endPointOrdemServico
  });

  const subTabs = [
    { id: 'geral', label: 'Configurações Gerais', icon: '⚙️' },
    { id: 'atividades', label: 'Atividades', icon: '📝' },
    { id: 'testes', label: 'Testes', icon: '🧪' },
    { id: 'campos', label: 'Campos OS', icon: '📋' }
  ];

  const handleSaveConfig = async () => {
    setLoading(true);
    setMessage(null);

    try {
      // Aqui você implementaria a lógica para salvar as configurações
      // Por exemplo, uma chamada para a API
      
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simular delay
      
      setMessage({ type: 'success', text: 'Configurações salvas com sucesso!' });
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'Erro ao salvar configurações' 
      });
    } finally {
      setLoading(false);
    }
  };

  const renderConfiguracaoGeral = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium">Configurações Gerais do Setor</h3>
      
      {message && (
        <div className={`p-4 rounded-md ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nome do Setor
          </label>
          <input
            type="text"
            value={configuracoes.nomeSetor}
            onChange={(e) => setConfiguracoes(prev => ({ ...prev, nomeSetor: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Chave do Setor
          </label>
          <input
            type="text"
            value={configuracoes.chaveSetor}
            onChange={(e) => setConfiguracoes(prev => ({ ...prev, chaveSetor: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled
          />
          <p className="text-xs text-gray-500 mt-1">A chave do setor não pode ser alterada</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Endpoint Apontamentos
          </label>
          <input
            type="text"
            value={configuracoes.endpointApontamento}
            onChange={(e) => setConfiguracoes(prev => ({ ...prev, endpointApontamento: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Endpoint Ordens de Serviço
          </label>
          <input
            type="text"
            value={configuracoes.endpointOS}
            onChange={(e) => setConfiguracoes(prev => ({ ...prev, endpointOS: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSaveConfig}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </div>
    </div>
  );

  const renderAtividades = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Atividades do Setor</h3>
        <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
          Nova Atividade
        </button>
      </div>

      <div className="bg-white rounded-lg border overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nome
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Descrição
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sectorConfig.ListaAtividades?.map((atividade, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {atividade.nome}
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {atividade.descricao}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900 mr-4">
                    Editar
                  </button>
                  <button className="text-red-600 hover:text-red-900">
                    Excluir
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderTestes = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Tipos de Teste</h3>
        <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
          Novo Tipo de Teste
        </button>
      </div>

      <div className="space-y-4">
        {Object.entries(sectorConfig.DicionarioTestes || {}).map(([nomeTeste, configTeste]) => (
          <div key={nomeTeste} className="bg-white p-6 rounded-lg border">
            <div className="flex justify-between items-start mb-4">
              <h4 className="text-lg font-medium">{nomeTeste}</h4>
              <div className="flex space-x-2">
                <button className="text-blue-600 hover:text-blue-900">
                  Editar
                </button>
                <button className="text-red-600 hover:text-red-900">
                  Excluir
                </button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {configTeste.camposAdicionaisResultado?.map((campo, index) => (
                <div key={`${campo.name}-${index}`} className="bg-gray-50 p-3 rounded">
                  <p className="font-medium text-sm">{campo.label || campo.name}</p>
                  <p className="text-xs text-gray-600">Tipo: {campo.type}</p>
                  {campo.options && (
                    <p className="text-xs text-gray-500">Opções: {campo.options.join(', ')}</p>
                  )}
                </div>
              )) || []}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCamposOS = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Campos da Ordem de Serviço</h3>
        <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
          Novo Campo
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(sectorConfig.EsquemaCamposOS || {}).map(([nomeCampo, configCampo]: [string, any]) => (
          <div key={nomeCampo} className="bg-white p-4 rounded-lg border">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-medium">{configCampo.label || nomeCampo}</h4>
              <div className="flex space-x-2">
                <button className="text-blue-600 hover:text-blue-900 text-sm">
                  Editar
                </button>
                <button className="text-red-600 hover:text-red-900 text-sm">
                  Excluir
                </button>
              </div>
            </div>
            <p className="text-sm text-gray-600">Tipo: {configCampo.tipo}</p>
            {configCampo.opcoes && (
              <div className="mt-2">
                <p className="text-xs text-gray-500">Opções:</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {configCampo.opcoes.map((opcao: string, idx: number) => (
                    <span key={idx} className="inline-block bg-gray-100 text-xs px-2 py-1 rounded">
                      {opcao}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderSubTabContent = () => {
    switch (activeSubTab) {
      case 'geral':
        return renderConfiguracaoGeral();
      case 'atividades':
        return renderAtividades();
      case 'testes':
        return renderTestes();
      case 'campos':
        return renderCamposOS();
      default:
        return renderConfiguracaoGeral();
    }
  };

  // Verificar se o usuário tem permissão para configurar
  const hasConfigPermission = user?.privilege_level === 'ADMIN' || user?.privilege_level === 'SUPERVISOR';

  if (!hasConfigPermission) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-8">
          <p className="text-gray-500">Você não tem permissão para acessar as configurações.</p>
          <p className="text-sm text-gray-400 mt-2">Apenas administradores e supervisores podem configurar o setor.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-6">Configurações - {sectorConfig.NomeSetor}</h2>
      
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

export default ConfiguracaoTab;
