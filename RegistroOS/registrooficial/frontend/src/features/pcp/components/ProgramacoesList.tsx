import React, { useState, useEffect, useCallback } from 'react';
import { getProgramacoes, updateProgramacao, deleteProgramacao, enviarProgramacaoSetor } from '../../../services/api';
import { useCachedSetores } from '../../../hooks/useCachedSetores';

interface Programacao {
  id: number;
  id_ordem_servico: number;
  os_numero: string;
  responsavel_id?: number;
  responsavel_nome?: string;
  inicio_previsto: string;
  fim_previsto: string;
  status: string;
  prioridade?: string;
  atribuida_supervisor?: boolean;
  observacoes?: string;
  setor_nome?: string;
  departamento_nome?: string;
  id_setor?: number;
  created_at: string;
  updated_at: string;
}

interface ProgramacoesListProps {
  filtros?: {
    status?: string;
    setor?: string;
    departamento?: string;
    periodo?: number;
    atribuida_supervisor?: boolean;
    prioridade?: string;
  };
  onProgramacaoSelect?: (programacao: Programacao) => void;
  onProgramacaoUpdate?: () => void;
}

const ProgramacoesList: React.FC<ProgramacoesListProps> = ({ 
  filtros, 
  onProgramacaoSelect,
  onProgramacaoUpdate 
}) => {
  const [programacoes, setProgramacoes] = useState<Programacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProgramacao, setSelectedProgramacao] = useState<Programacao | null>(null);
  const [showActions, setShowActions] = useState<number | null>(null);
  const [showEnviarModal, setShowEnviarModal] = useState(false);
  const { todosSetores } = useCachedSetores();

  const carregarProgramacoes = useCallback(async () => {
    console.log('🔄 Carregando programações com filtros:', filtros);
    setLoading(true);
    try {
      const response = await getProgramacoes(filtros);
      setProgramacoes(Array.isArray(response) ? response : []);
      console.log('✅ Programações carregadas:', response?.length || 0);
    } catch (error) {
      console.error('❌ Erro ao carregar programações:', error);
      setProgramacoes([]);
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    carregarProgramacoes();
  }, [carregarProgramacoes]);

  const handleStatusChange = async (programacao: Programacao, novoStatus: string) => {
    try {
      await updateProgramacao(programacao.id, {
        ...programacao,
        status: novoStatus
      });
      carregarProgramacoes();
      onProgramacaoUpdate?.();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      alert('Erro ao atualizar status da programação');
    }
  };

  const handleCancelarProgramacao = async (programacao: Programacao) => {
    if (window.confirm('Tem certeza que deseja cancelar esta programação?')) {
      try {
        await deleteProgramacao(programacao.id);
        carregarProgramacoes();
        onProgramacaoUpdate?.();
      } catch (error) {
        console.error('Erro ao cancelar programação:', error);
        alert('Erro ao cancelar programação');
      }
    }
  };

  const handleEnviarSetor = async (setorId: number) => {
    if (!selectedProgramacao) return;
    
    try {
      await enviarProgramacaoSetor(selectedProgramacao.id, setorId);
      setShowEnviarModal(false);
      setSelectedProgramacao(null);
      carregarProgramacoes();
      onProgramacaoUpdate?.();
      alert('Programação enviada para o setor com sucesso!');
    } catch (error) {
      console.error('Erro ao enviar programação:', error);
      alert('Erro ao enviar programação para o setor');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'PROGRAMADA':
        return 'bg-blue-100 text-blue-800';
      case 'EM_ANDAMENTO':
        return 'bg-yellow-100 text-yellow-800';
      case 'ENVIADA':
        return 'bg-purple-100 text-purple-800';
      case 'CONCLUIDA':
        return 'bg-green-100 text-green-800';
      case 'CANCELADA':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusActions = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'PROGRAMADA':
        return ['EM_ANDAMENTO', 'ENVIADA', 'CANCELADA'];
      case 'EM_ANDAMENTO':
        return ['CONCLUIDA', 'CANCELADA'];
      case 'ENVIADA':
        return ['EM_ANDAMENTO', 'CONCLUIDA'];
      default:
        return [];
    }
  };

  const formatarData = (dataString: string) => {
    return new Date(dataString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calcularAtraso = (fimPrevisto: string, status: string) => {
    if (status === 'CONCLUIDA' || status === 'CANCELADA') return null;
    
    const agora = new Date();
    const prazo = new Date(fimPrevisto);
    
    if (agora > prazo) {
      const diffMs = agora.getTime() - prazo.getTime();
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      return diffHours;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Carregando programações...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">
          Programações ({programacoes.length})
        </h3>
        <button
          onClick={carregarProgramacoes}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Atualizar
        </button>
      </div>

      {/* Lista de Programações */}
      <div className="space-y-3">
        {programacoes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Nenhuma programação encontrada
          </div>
        ) : (
          programacoes.map((programacao) => {
            const atraso = calcularAtraso(programacao.fim_previsto, programacao.status);
            const actionsAvailable = getStatusActions(programacao.status);
            
            return (
              <div
                key={programacao.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-semibold text-gray-900">
                        OS {programacao.os_numero}
                      </span>
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(programacao.status)}`}>
                        {programacao.status}
                      </span>
                      {atraso && atraso > 0 && (
                        <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-800">
                          Atrasada {atraso}h
                        </span>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
                      <div>
                        <strong>Início:</strong> {formatarData(programacao.inicio_previsto)}
                      </div>
                      <div>
                        <strong>Fim:</strong> {formatarData(programacao.fim_previsto)}
                      </div>
                      {programacao.responsavel_nome && (
                        <div>
                          <strong>Responsável:</strong> {programacao.responsavel_nome}
                        </div>
                      )}
                      {programacao.setor_nome && (
                        <div>
                          <strong>Setor:</strong> {programacao.setor_nome}
                        </div>
                      )}
                      {programacao.departamento_nome && (
                        <div>
                          <strong>Departamento:</strong> {programacao.departamento_nome}
                        </div>
                      )}
                      {programacao.prioridade && (
                        <div>
                          <strong>Prioridade:</strong>
                          <span className={`ml-1 px-2 py-1 text-xs rounded ${
                            programacao.prioridade === 'URGENTE' ? 'bg-red-100 text-red-800' :
                            programacao.prioridade === 'ALTA' ? 'bg-orange-100 text-orange-800' :
                            programacao.prioridade === 'NORMAL' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {programacao.prioridade}
                          </span>
                        </div>
                      )}
                      {programacao.atribuida_supervisor && (
                        <div>
                          <span className="inline-flex items-center px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                            ✅ Atribuída pelo Supervisor
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {programacao.observacoes && (
                      <div className="mt-2 text-sm text-gray-700">
                        <strong>Observações:</strong> {programacao.observacoes}
                      </div>
                    )}
                  </div>
                  
                  {/* Actions Menu */}
                  <div className="relative">
                    <button
                      onClick={() => setShowActions(showActions === programacao.id ? null : programacao.id)}
                      className="p-2 text-gray-400 hover:text-gray-600"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                      </svg>
                    </button>
                    
                    {showActions === programacao.id && (
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
                        <div className="py-1">
                          {actionsAvailable.map((status) => (
                            <button
                              key={status}
                              onClick={() => {
                                handleStatusChange(programacao, status);
                                setShowActions(null);
                              }}
                              className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                              Marcar como {status.replace('_', ' ')}
                            </button>
                          ))}
                          
                          {programacao.status === 'PROGRAMADA' && (
                            <button
                              onClick={() => {
                                setSelectedProgramacao(programacao);
                                setShowEnviarModal(true);
                                setShowActions(null);
                              }}
                              className="block w-full text-left px-4 py-2 text-sm text-blue-700 hover:bg-blue-50"
                            >
                              Enviar para Setor
                            </button>
                          )}
                          
                          {programacao.status !== 'CONCLUIDA' && (
                            <button
                              onClick={() => {
                                handleCancelarProgramacao(programacao);
                                setShowActions(null);
                              }}
                              className="block w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-red-50"
                            >
                              Cancelar Programação
                            </button>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-xs text-gray-500 pt-2 border-t border-gray-100">
                  <span>
                    Criada em: {formatarData(programacao.created_at)}
                  </span>
                  <span>
                    Atualizada em: {formatarData(programacao.updated_at)}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Modal para Enviar para Setor */}
      {showEnviarModal && selectedProgramacao && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                Enviar Programação para Setor
              </h3>
              <button
                onClick={() => setShowEnviarModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">
                Programação: OS {selectedProgramacao.os_numero}
              </p>
              <p className="text-sm text-gray-600">
                Selecione o setor de destino:
              </p>
            </div>
            
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {todosSetores.map((setor) => (
                <button
                  key={setor.id}
                  onClick={() => handleEnviarSetor(setor.id)}
                  className="w-full text-left p-3 border border-gray-200 rounded hover:bg-blue-50 hover:border-blue-300"
                >
                  <div className="font-medium">{setor.nome}</div>
                  <div className="text-sm text-gray-500">{setor.departamento}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgramacoesList;
