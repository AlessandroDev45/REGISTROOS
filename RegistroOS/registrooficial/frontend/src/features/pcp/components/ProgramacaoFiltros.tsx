import React, { useState, useEffect } from 'react';
import { useCachedSetores } from '../../../hooks/useCachedSetores';
import { departamentoService } from '../../../services/adminApi';

interface FiltrosProgramacao {
  status?: string;
  setor?: string;
  departamento?: string;
  periodo?: number;
  atribuida_supervisor?: boolean;
  prioridade?: string;
}

interface ProgramacaoFiltrosProps {
  filtros: FiltrosProgramacao;
  onFiltrosChange: (filtros: FiltrosProgramacao) => void;
}

const ProgramacaoFiltros: React.FC<ProgramacaoFiltrosProps> = ({
  filtros,
  onFiltrosChange
}) => {
  const { todosSetores } = useCachedSetores();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [departamentos, setDepartamentos] = useState<any[]>([]);

  const handleFiltroChange = (campo: keyof FiltrosProgramacao, valor: any) => {
    onFiltrosChange({
      ...filtros,
      [campo]: valor
    });
  };

  const limparFiltros = () => {
    onFiltrosChange({});
  };

  // Carregar departamentos da API apenas uma vez
  useEffect(() => {
    const carregarDepartamentos = async () => {
      try {
        const deptData = await departamentoService.getDepartamentos();
        setDepartamentos(deptData);
      } catch (error) {
        console.error('Erro ao carregar departamentos:', error);
        // Fallback: extrair departamentos únicos dos setores
        if (todosSetores.length > 0) {
          const deptFromSetores = Array.from(
            new Set(todosSetores.map(setor => setor.departamento).filter(Boolean))
          );
          setDepartamentos(deptFromSetores.map(nome => ({ nome_tipo: nome })));
        }
      }
    };

    // Só carregar se ainda não temos departamentos
    if (departamentos.length === 0) {
      carregarDepartamentos();
    }
  }, []); // Remover todosSetores da dependência para evitar loop

  // Fallback para departamentos usando setores (apenas se necessário)
  useEffect(() => {
    if (departamentos.length === 0 && todosSetores.length > 0) {
      const deptFromSetores = Array.from(
        new Set(todosSetores.map(setor => setor.departamento).filter(Boolean))
      );
      setDepartamentos(deptFromSetores.map(nome => ({ nome_tipo: nome })));
    }
  }, [todosSetores.length]); // Usar apenas o length para evitar re-renders desnecessários

  return (
    <div className="bg-white p-4 rounded-lg shadow border mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Filtros de Programação</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            {showAdvanced ? 'Ocultar' : 'Mais'} Filtros
          </button>
          <button
            onClick={limparFiltros}
            className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
          >
            Limpar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={filtros.status || ''}
            onChange={(e) => handleFiltroChange('status', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="PROGRAMADA">Programada</option>
            <option value="EM_ANDAMENTO">Em Andamento</option>
            <option value="ENVIADA">Enviada</option>
            <option value="CONCLUIDA">Concluída</option>
            <option value="CANCELADA">Cancelada</option>
          </select>
        </div>

        {/* Prioridade */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Prioridade
          </label>
          <select
            value={filtros.prioridade || ''}
            onChange={(e) => handleFiltroChange('prioridade', e.target.value || undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas</option>
            <option value="URGENTE">Urgente</option>
            <option value="ALTA">Alta</option>
            <option value="NORMAL">Normal</option>
            <option value="BAIXA">Baixa</option>
          </select>
        </div>

        {/* Período */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Período (dias)
          </label>
          <select
            value={filtros.periodo || ''}
            onChange={(e) => handleFiltroChange('periodo', e.target.value ? Number(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="7">Últimos 7 dias</option>
            <option value="15">Últimos 15 dias</option>
            <option value="30">Últimos 30 dias</option>
            <option value="60">Últimos 60 dias</option>
          </select>
        </div>

        {/* Atribuída pelo Supervisor */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Atribuição
          </label>
          <select
            value={filtros.atribuida_supervisor === undefined ? '' : filtros.atribuida_supervisor.toString()}
            onChange={(e) => handleFiltroChange('atribuida_supervisor', 
              e.target.value === '' ? undefined : e.target.value === 'true'
            )}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas</option>
            <option value="true">Atribuída pelo Supervisor</option>
            <option value="false">Não Atribuída</option>
          </select>
        </div>
      </div>

      {/* Filtros Avançados */}
      {showAdvanced && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Departamento */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Departamento
              </label>
              <select
                value={filtros.departamento || ''}
                onChange={(e) => handleFiltroChange('departamento', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos os departamentos</option>
                {departamentos.map((dept, index) => (
                  <option key={`dept-${index}`} value={dept.nome_tipo || dept}>
                    {dept.nome_tipo || dept}
                  </option>
                ))}
              </select>
            </div>

            {/* Setor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Setor
              </label>
              <select
                value={filtros.setor || ''}
                onChange={(e) => handleFiltroChange('setor', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos os setores</option>
                {todosSetores
                  .filter(setor => !filtros.departamento || setor.departamento === filtros.departamento)
                  .map((setor, index) => (
                    <option key={`setor-${index}-${setor.nome}`} value={setor.nome}>
                      {setor.nome}
                    </option>
                  ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Resumo dos Filtros Ativos */}
      {Object.keys(filtros).length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-600">Filtros ativos:</span>
            {Object.entries(filtros).map(([key, value]) => {
              if (value === undefined || value === '') return null;
              return (
                <span
                  key={key}
                  className="inline-flex items-center px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                >
                  {key}: {value.toString()}
                  <button
                    onClick={() => handleFiltroChange(key as keyof FiltrosProgramacao, undefined)}
                    className="ml-1 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgramacaoFiltros;
