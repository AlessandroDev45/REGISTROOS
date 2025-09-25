import React, { useState } from 'react';

interface ProgramacaoFormSimplesProps {
  onSalvar: (programacao: any) => void;
  onCancelar: () => void;
}

const ProgramacaoFormSimples: React.FC<ProgramacaoFormSimplesProps> = ({
  onSalvar,
  onCancelar
}) => {
  const [programacao, setProgramacao] = useState({
    id_ordem_servico: '',
    inicio_previsto: '',
    fim_previsto: '',
    responsavel_id: '',
    observacoes: '',
    status: 'PROGRAMADA'
  });

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Simular salvamento
      await new Promise(resolve => setTimeout(resolve, 1000));
      onSalvar(programacao);
    } catch (error) {
      console.error('Erro ao salvar programação:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setProgramacao(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow border">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Nova Programação
        </h3>
        <button
          onClick={onCancelar}
          className="text-gray-400 hover:text-gray-600"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ordem de Serviço
          </label>
          <select
            value={programacao.id_ordem_servico}
            onChange={(e) => handleChange('id_ordem_servico', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Selecione uma OS</option>
            <option value="1">OS 20001 - Motor Elétrico</option>
            <option value="2">OS 20002 - Transformador</option>
            <option value="3">OS 20003 - Gerador</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Início Previsto
            </label>
            <input
              type="datetime-local"
              value={programacao.inicio_previsto}
              onChange={(e) => handleChange('inicio_previsto', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fim Previsto
            </label>
            <input
              type="datetime-local"
              value={programacao.fim_previsto}
              onChange={(e) => handleChange('fim_previsto', e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Responsável
          </label>
          <select
            value={programacao.responsavel_id}
            onChange={(e) => handleChange('responsavel_id', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Selecione um responsável</option>
            <option value="1">João Silva</option>
            <option value="2">Maria Santos</option>
            <option value="3">Pedro Oliveira</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={programacao.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="PROGRAMADA">Programada</option>
            <option value="EM_ANDAMENTO">Em Andamento</option>
            <option value="ENVIADA">Enviada</option>
            <option value="CONCLUIDA">Concluída</option>
            <option value="CANCELADA">Cancelada</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Observações
          </label>
          <textarea
            value={programacao.observacoes}
            onChange={(e) => handleChange('observacoes', e.target.value)}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Observações adicionais..."
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancelar}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Salvar Programação'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProgramacaoFormSimples;
