import React, { useState, useEffect, useCallback } from 'react';
import { getPendencias, getPendenciaDetalhes } from '../../../services/api';

interface Pendencia {
  id: number;
  numero_os: string;
  cliente: string;
  tipo_maquina: string;
  equipamento: string; // Backend retorna 'equipamento', não 'descricao_maquina'
  descricao: string; // Backend retorna 'descricao', não 'descricao_pendencia'
  status: string;
  // prioridade removida - não deve existir para pendências
  data_abertura: string; // Backend retorna 'data_abertura', não 'data_inicio'
  data_fechamento?: string;
  responsavel_id: number; // Backend retorna 'responsavel_id'
  responsavel_nome: string; // Backend retorna 'responsavel_nome'
  tempo_aberto_horas?: number;
  observacoes_fechamento?: string;
}

interface PendenciasListProps {
  filtros?: {
    status?: string;
    setor?: string;
    prioridade?: string;
  };
  onPendenciaSelect?: (pendencia: Pendencia) => void;
}

const PendenciasList: React.FC<PendenciasListProps> = ({ filtros, onPendenciaSelect }) => {
  const [pendencias, setPendencias] = useState<Pendencia[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPendencia, setSelectedPendencia] = useState<Pendencia | null>(null);
  const [showDetalhes, setShowDetalhes] = useState(false);

  const carregarPendencias = useCallback(async () => {
    console.log('🔄 Carregando pendências com filtros:', filtros);
    setLoading(true);
    setError(null);
    try {
      const response = await getPendencias(filtros);
      console.log('✅ Resposta pendências:', response);

      // 🔧 CORREÇÃO: Backend retorna array direto, não objeto com propriedade pendencias
      const pendenciasData = Array.isArray(response) ? response : (Array.isArray(response?.pendencias) ? response.pendencias : []);
      setPendencias(pendenciasData);
      console.log('✅ Pendências carregadas:', pendenciasData.length);
    } catch (error: any) {
      console.error('❌ Erro ao carregar pendências:', error);
      setError(error.message || 'Erro ao carregar pendências');
      setPendencias([]); // Garantir que sempre seja um array
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  useEffect(() => {
    carregarPendencias();
  }, [carregarPendencias]);

  const handlePendenciaClick = async (pendencia: Pendencia) => {
    try {
      const detalhes = await getPendenciaDetalhes(pendencia.id);
      setSelectedPendencia(detalhes);
      setShowDetalhes(true);
      if (onPendenciaSelect) {
        onPendenciaSelect(detalhes);
      }
    } catch (error) {
      console.error('Erro ao carregar detalhes da pendência:', error);
    }
  };

  // getPrioridadeColor removida - prioridade não existe para pendências

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'ABERTA':
        return 'bg-red-100 text-red-800';
      case 'FECHADA':
        return 'bg-green-100 text-green-800';
      case 'EM_ANDAMENTO':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatarTempo = (horas: number) => {
    if (horas < 24) {
      return `${Math.round(horas)}h`;
    } else {
      const dias = Math.floor(horas / 24);
      const horasRestantes = Math.round(horas % 24);
      return `${dias}d ${horasRestantes}h`;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Carregando pendências...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <div className="text-red-600">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Erro ao carregar pendências</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
          <div className="ml-auto">
            <button
              onClick={carregarPendencias}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">
          Pendências ({pendencias.length})
        </h3>
      </div>

      {/* Lista de Pendências */}
      <div className="space-y-3">
        {pendencias.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Nenhuma pendência encontrada
          </div>
        ) : (
          pendencias.map((pendencia) => (
            <div
              key={pendencia.id}
              onClick={() => handlePendenciaClick(pendencia)}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-semibold text-gray-900">
                      OS {pendencia.numero_os}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(pendencia.status)}`}>
                      {pendencia.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">
                    <strong>Cliente:</strong> {pendencia.cliente}
                  </p>
                  <p className="text-sm text-gray-600 mb-2">
                    <strong>Máquina:</strong> {pendencia.tipo_maquina} - {pendencia.equipamento}
                  </p>
                  <p className="text-sm text-gray-800">
                    {pendencia.descricao}
                  </p>
                </div>
                <div className="text-right text-sm text-gray-500">
                  <div>Aberta há:</div>
                  <div className="font-semibold">
                    {formatarTempo(pendencia.tempo_aberto_horas || 0)}
                  </div>
                </div>
              </div>
              
              <div className="flex justify-between items-center text-xs text-gray-500 pt-2 border-t border-gray-100">
                <span>
                  Iniciada em: {new Date(pendencia.data_abertura).toLocaleDateString('pt-BR')}
                </span>
                {pendencia.data_fechamento && (
                  <span>
                    Fechada em: {new Date(pendencia.data_fechamento).toLocaleDateString('pt-BR')}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal de Detalhes */}
      {showDetalhes && selectedPendencia && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                Detalhes da Pendência - OS {selectedPendencia.numero_os}
              </h3>
              <button
                onClick={() => setShowDetalhes(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <span className={`inline-block px-2 py-1 text-sm rounded ${getStatusColor(selectedPendencia.status)}`}>
                    {selectedPendencia.status}
                  </span>
                </div>
                {/* Prioridade removida - não existe para pendências */}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Cliente</label>
                <p className="text-sm text-gray-900">{selectedPendencia.cliente}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Descrição da Pendência</label>
                <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded">
                  {selectedPendencia.descricao}
                </p>
              </div>
              
              {selectedPendencia.observacoes_fechamento && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Observações de Fechamento</label>
                  <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded">
                    {selectedPendencia.observacoes_fechamento}
                  </p>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <label className="block font-medium text-gray-700">Data de Início</label>
                  <p>{new Date(selectedPendencia.data_abertura).toLocaleString('pt-BR')}</p>
                </div>
                {selectedPendencia.data_fechamento && (
                  <div>
                    <label className="block font-medium text-gray-700">Data de Fechamento</label>
                    <p>{new Date(selectedPendencia.data_fechamento).toLocaleString('pt-BR')}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PendenciasList;
