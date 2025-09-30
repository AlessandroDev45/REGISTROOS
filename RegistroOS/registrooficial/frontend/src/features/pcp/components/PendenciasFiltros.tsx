import React, { useState, useEffect } from 'react';
import { departamentoService } from '../../../services/adminApi';
import { publicSetorService } from '../../../services/api';

interface FiltrosPendencias {
  status?: string;
  setor?: string;
  departamento?: string;
  prioridade?: string;
  periodo?: number;
}

interface PendenciasFiltrosProps {
  filtros: FiltrosPendencias;
  onFiltrosChange: (filtros: FiltrosPendencias) => void;
  onLimparFiltros: () => void;
}

const PendenciasFiltros: React.FC<PendenciasFiltrosProps> = ({
  filtros,
  onFiltrosChange,
  onLimparFiltros
}) => {
  const [filtrosLocais, setFiltrosLocais] = useState<FiltrosPendencias>(filtros);
  const [departamentos, setDepartamentos] = useState<any[]>([]);
  const [setores, setSetores] = useState<any[]>([]);
  const [setoresFiltrados, setSetoresFiltrados] = useState<any[]>([]);

  useEffect(() => {
    setFiltrosLocais(filtros);
  }, [filtros]);

  // Carregar departamentos e setores
  useEffect(() => {
    const carregarDados = async () => {
      try {
        const [deptData, setorData] = await Promise.all([
          departamentoService.getDepartamentos(),
          publicSetorService.getSetores()
        ]);
        setDepartamentos(deptData);
        setSetores(setorData);
        setSetoresFiltrados(setorData);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    };
    carregarDados();
  }, []);

  // Filtrar setores quando departamento mudar
  useEffect(() => {
    if (filtrosLocais.departamento) {
      const setoresDoDepartamento = setores.filter(setor =>
        setor.departamento === filtrosLocais.departamento
      );
      setSetoresFiltrados(setoresDoDepartamento);
    } else {
      setSetoresFiltrados(setores);
    }
  }, [filtrosLocais.departamento, setores]);

  const handleFiltroChange = (campo: keyof FiltrosPendencias, valor: string | number) => {
    const novosFiltros = {
      ...filtrosLocais,
      [campo]: valor === '' ? undefined : valor
    };
    setFiltrosLocais(novosFiltros);
    onFiltrosChange(novosFiltros);
  };

  const handleLimparFiltros = () => {
    const filtrosVazios = {};
    setFiltrosLocais(filtrosVazios);
    onLimparFiltros();
  };

  const statusOptions = [
    { value: '', label: 'Todos os Status' },
    { value: 'ABERTA', label: 'Aberta' },
    { value: 'FECHADA', label: 'Fechada' },
    { value: 'EM_ANDAMENTO', label: 'Em Andamento' }
  ];

  const prioridadeOptions = [
    { value: '', label: 'Todas as Prioridades' },
    { value: 'BAIXA', label: 'Baixa' },
    { value: 'NORMAL', label: 'Normal' },
    { value: 'MEDIA', label: 'Média' },
    { value: 'ALTA', label: 'Alta' },
    { value: 'URGENTE', label: 'Urgente' }
  ];

  const periodoOptions = [
    { value: '', label: 'Todo o período' },
    { value: 7, label: 'Últimos 7 dias' },
    { value: 15, label: 'Últimos 15 dias' },
    { value: 30, label: 'Últimos 30 dias' },
    { value: 60, label: 'Últimos 60 dias' },
    { value: 90, label: 'Últimos 90 dias' }
  ];

  const temFiltrosAtivos = Object.values(filtrosLocais).some(valor => valor !== undefined && valor !== '');

  return (
    <div className="bg-white p-4 rounded-lg shadow border mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Filtros de Pendências</h3>
        {temFiltrosAtivos && (
          <button
            onClick={handleLimparFiltros}
            className="px-3 py-1 text-sm text-red-600 hover:text-red-800 border border-red-300 rounded hover:bg-red-50"
          >
            Limpar Filtros
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Filtro de Departamento */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Departamento
          </label>
          <select
            value={filtrosLocais.departamento || ''}
            onChange={(e) => handleFiltroChange('departamento', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Todos os Departamentos</option>
            {departamentos.map((dept) => (
              <option key={dept.id} value={dept.nome_tipo}>
                {dept.nome_tipo}
              </option>
            ))}
          </select>
        </div>

        {/* Filtro de Setor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Setor
          </label>
          <select
            value={filtrosLocais.setor || ''}
            onChange={(e) => handleFiltroChange('setor', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Todos os Setores</option>
            {setoresFiltrados.map((setor) => (
              <option key={setor.id} value={setor.nome}>
                {setor.nome}
              </option>
            ))}
          </select>
        </div>

        {/* Filtro de Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={filtrosLocais.status || ''}
            onChange={(e) => handleFiltroChange('status', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>



        {/* Filtro de Prioridade */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Prioridade
          </label>
          <select
            value={filtrosLocais.prioridade || ''}
            onChange={(e) => handleFiltroChange('prioridade', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {prioridadeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Filtro de Período */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Período
          </label>
          <select
            value={filtrosLocais.periodo || ''}
            onChange={(e) => handleFiltroChange('periodo', e.target.value ? Number(e.target.value) : '')}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {periodoOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Indicadores de Filtros Ativos */}
      {temFiltrosAtivos && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-600">Filtros ativos:</span>
            
            {filtrosLocais.status && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                Status: {statusOptions.find(opt => opt.value === filtrosLocais.status)?.label}
                <button
                  onClick={() => handleFiltroChange('status', '')}
                  className="ml-1 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            )}
            
            {filtrosLocais.setor && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                Setor: {filtrosLocais.setor}
                <button
                  onClick={() => handleFiltroChange('setor', '')}
                  className="ml-1 text-green-600 hover:text-green-800"
                >
                  ×
                </button>
              </span>
            )}
            
            {filtrosLocais.prioridade && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-orange-100 text-orange-800">
                Prioridade: {prioridadeOptions.find(opt => opt.value === filtrosLocais.prioridade)?.label}
                <button
                  onClick={() => handleFiltroChange('prioridade', '')}
                  className="ml-1 text-orange-600 hover:text-orange-800"
                >
                  ×
                </button>
              </span>
            )}
            
            {filtrosLocais.periodo && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                Período: {periodoOptions.find(opt => opt.value === filtrosLocais.periodo)?.label}
                <button
                  onClick={() => handleFiltroChange('periodo', '')}
                  className="ml-1 text-purple-600 hover:text-purple-800"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}

      {/* Resumo dos Filtros */}
      <div className="mt-4 text-sm text-gray-600">
        <div className="flex items-center space-x-4">
          <span>
            <strong>Filtros aplicados:</strong> {Object.values(filtrosLocais).filter(v => v !== undefined && v !== '').length}
          </span>
          {filtrosLocais.periodo && (
            <span>
              <strong>Período de análise:</strong> {periodoOptions.find(opt => opt.value === filtrosLocais.periodo)?.label}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default PendenciasFiltros;
