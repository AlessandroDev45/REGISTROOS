import React, { useState } from 'react';

interface MaquinaRotativaCCProps {
  testResults: Record<string, any>;
  testObservations: Record<string, string>;
  onTestResultChange: (tab: string, field: string, value: any) => void;
  onTestCheckboxChange: (tab: string, field: string, checked: boolean) => void;
  onTestObservationChange: (tab: string, value: string) => void;
}

const MaquinaRotativaCC: React.FC<MaquinaRotativaCCProps> = ({
  testResults,
  testObservations,
  onTestResultChange,
  onTestCheckboxChange,
  onTestObservationChange
}) => {
  const [activeTab, setActiveTab] = useState('carcaça');
  const [saveData, setSaveData] = useState(false);

  const tabs = [
    { id: 'carcaça', label: 'CARCAÇA/CX LIGAÇÃO' },
    { id: 'armadura', label: 'ARMADURA' },
    { id: 'shunt', label: 'CAMPO SHUNT' },
    { id: 'interpolos', label: 'INTERPOLOS' },
    { id: 'compensacao', label: 'COMPENSAÇÃO' },
    { id: 'camposerie', label: 'CAMPO SÉRIE' },
  ];

  const renderTabContent = (tabId: string) => {
    const tabData = testResults[tabId] || {};
    const observation = testObservations[tabId] || '';

    switch (tabId) {
      case 'carcaça':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">CARCAÇA/CX LIGAÇÃO</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA DE ISOLAMENTO (MΩ)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={tabData.resistenciaIsolamento || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaIsolamento', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  TENSÃO DE TESTE (V)
                </label>
                <input
                  type="number"
                  value={tabData.tensaoTeste || ''}
                  onChange={(e) => onTestResultChange(tabId, 'tensaoTeste', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OBSERVAÇÕES
              </label>
              <textarea
                value={observation}
                onChange={(e) => onTestObservationChange(tabId, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Observações sobre a carcaça/cx ligação..."
              />
            </div>
          </div>
        );

      case 'armadura':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">ARMADURA</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA DE ISOLAMENTO (MΩ)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={tabData.resistenciaIsolamento || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaIsolamento', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA ÔHMICA (Ω)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={tabData.resistenciaOhmica || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaOhmica', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OBSERVAÇÕES
              </label>
              <textarea
                value={observation}
                onChange={(e) => onTestObservationChange(tabId, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Observações sobre a armadura..."
              />
            </div>
          </div>
        );

      case 'shunt':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">CAMPO SHUNT</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA DE ISOLAMENTO (MΩ)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={tabData.resistenciaIsolamento || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaIsolamento', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA ÔHMICA (Ω)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={tabData.resistenciaOhmica || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaOhmica', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OBSERVAÇÕES
              </label>
              <textarea
                value={observation}
                onChange={(e) => onTestObservationChange(tabId, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Observações sobre o campo shunt..."
              />
            </div>
          </div>
        );

      case 'interpolos':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">INTERPOLOS</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA DE ISOLAMENTO (MΩ)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={tabData.resistenciaIsolamento || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaIsolamento', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA ÔHMICA (Ω)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={tabData.resistenciaOhmica || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaOhmica', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OBSERVAÇÕES
              </label>
              <textarea
                value={observation}
                onChange={(e) => onTestObservationChange(tabId, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Observações sobre os interpolos..."
              />
            </div>
          </div>
        );

      case 'compensacao':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">COMPENSAÇÃO</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA DE ISOLAMENTO (MΩ)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={tabData.resistenciaIsolamento || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaIsolamento', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA ÔHMICA (Ω)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={tabData.resistenciaOhmica || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaOhmica', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OBSERVAÇÕES
              </label>
              <textarea
                value={observation}
                onChange={(e) => onTestObservationChange(tabId, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Observações sobre a compensação..."
              />
            </div>
          </div>
        );

      case 'camposerie':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">CAMPO SÉRIE</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA DE ISOLAMENTO (MΩ)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={tabData.resistenciaIsolamento || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaIsolamento', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RESISTÊNCIA ÔHMICA (Ω)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={tabData.resistenciaOhmica || ''}
                  onChange={(e) => onTestResultChange(tabId, 'resistenciaOhmica', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0.000"
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OBSERVAÇÕES
              </label>
              <textarea
                value={observation}
                onChange={(e) => onTestObservationChange(tabId, e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Observações sobre o campo série..."
              />
            </div>
          </div>
        );

      default:
        return <div>Conteúdo não encontrado</div>;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-6">MAQUINA ROTATIVA CC - MOTOR CC</h2>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {renderTabContent(activeTab)}
      </div>

      {/* Save Button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={() => setSaveData(!saveData)}
          className={`px-4 py-2 rounded-md font-medium ${
            saveData
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {saveData ? 'Dados Salvos ✓' : 'Salvar Dados'}
        </button>
      </div>
    </div>
  );
};

export default MaquinaRotativaCC;