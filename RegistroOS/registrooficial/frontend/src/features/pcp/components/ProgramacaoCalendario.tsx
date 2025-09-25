import React, { useState, useEffect } from 'react';
import { getProgramacoes } from '../../../services/api';

interface Programacao {
  id: number;
  id_ordem_servico: number;
  os_numero: string;
  responsavel_nome?: string;
  inicio_previsto: string;
  fim_previsto: string;
  status: string;
  observacoes?: string;
  setor_nome?: string;
}

interface ProgramacaoCalendarioProps {
  onProgramacaoSelect?: (programacao: Programacao) => void;
  filtros?: any;
}

const ProgramacaoCalendario: React.FC<ProgramacaoCalendarioProps> = ({
  onProgramacaoSelect,
  filtros
}) => {
  const [programacoes, setProgramacoes] = useState<Programacao[]>([]);
  const [loading, setLoading] = useState(false);
  const [dataAtual, setDataAtual] = useState(new Date());
  const [visualizacao, setVisualizacao] = useState<'semana' | 'mes'>('semana');
  const [selectedProgramacao, setSelectedProgramacao] = useState<Programacao | null>(null);

  useEffect(() => {
    carregarProgramacoes();
  }, [dataAtual, filtros]);

  const carregarProgramacoes = async () => {
    setLoading(true);
    try {
      console.log('Carregando programações para calendário...');
      const response = await getProgramacoes(filtros);
      console.log('Programações recebidas:', response);

      // A API retorna um array diretamente
      const programacoesArray = Array.isArray(response) ? response : [];
      setProgramacoes(programacoesArray);

      console.log(`${programacoesArray.length} programações carregadas para o calendário`);
    } catch (error) {
      console.error('Erro ao carregar programações:', error);
      setProgramacoes([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'PROGRAMADA':
        return 'bg-blue-500';
      case 'EM_ANDAMENTO':
        return 'bg-yellow-500';
      case 'ENVIADA':
        return 'bg-purple-500';
      case 'CONCLUIDA':
        return 'bg-green-500';
      case 'CANCELADA':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatarHora = (dataString: string) => {
    return new Date(dataString).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatarData = (data: Date) => {
    return data.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const obterDiasSemana = () => {
    const inicio = new Date(dataAtual);
    inicio.setDate(dataAtual.getDate() - dataAtual.getDay()); // Domingo
    
    const dias = [];
    for (let i = 0; i < 7; i++) {
      const dia = new Date(inicio);
      dia.setDate(inicio.getDate() + i);
      dias.push(dia);
    }
    return dias;
  };

  const obterDiasMes = () => {
    const ano = dataAtual.getFullYear();
    const mes = dataAtual.getMonth();
    
    const primeiroDia = new Date(ano, mes, 1);
    const ultimoDia = new Date(ano, mes + 1, 0);
    
    // Ajustar para começar no domingo
    const inicioCalendario = new Date(primeiroDia);
    inicioCalendario.setDate(primeiroDia.getDate() - primeiroDia.getDay());
    
    const dias = [];
    const dataAtualIteracao = new Date(inicioCalendario);
    
    // Gerar 42 dias (6 semanas)
    for (let i = 0; i < 42; i++) {
      dias.push(new Date(dataAtualIteracao));
      dataAtualIteracao.setDate(dataAtualIteracao.getDate() + 1);
    }
    
    return dias;
  };

  const obterProgramacoesDoDia = (data: Date) => {
    const dataStr = data.toISOString().split('T')[0];
    return programacoes.filter(prog => {
      const inicioData = new Date(prog.inicio_previsto).toISOString().split('T')[0];
      const fimData = new Date(prog.fim_previsto).toISOString().split('T')[0];
      return dataStr >= inicioData && dataStr <= fimData;
    });
  };

  const navegarData = (direcao: 'anterior' | 'proximo') => {
    const novaData = new Date(dataAtual);
    
    if (visualizacao === 'semana') {
      novaData.setDate(dataAtual.getDate() + (direcao === 'proximo' ? 7 : -7));
    } else {
      novaData.setMonth(dataAtual.getMonth() + (direcao === 'proximo' ? 1 : -1));
    }
    
    setDataAtual(novaData);
  };

  const irParaHoje = () => {
    setDataAtual(new Date());
  };

  const handleProgramacaoClick = (programacao: Programacao) => {
    setSelectedProgramacao(programacao);
    onProgramacaoSelect?.(programacao);
  };

  const renderizarVisualizacaoSemana = () => {
    const diasSemana = obterDiasSemana();
    const nomesDias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

    return (
      <div className="grid grid-cols-7 gap-1">
        {/* Cabeçalho dos dias */}
        {nomesDias.map((nome, index) => (
          <div key={nome} className="p-2 text-center font-medium text-gray-700 bg-gray-50">
            <div>{nome}</div>
            <div className="text-sm">{diasSemana[index].getDate()}</div>
          </div>
        ))}
        
        {/* Células dos dias */}
        {diasSemana.map((dia, index) => {
          const programacoesDoDia = obterProgramacoesDoDia(dia);
          const isHoje = dia.toDateString() === new Date().toDateString();
          
          return (
            <div
              key={index}
              className={`min-h-32 p-1 border border-gray-200 ${
                isHoje ? 'bg-blue-50' : 'bg-white'
              }`}
            >
              <div className="space-y-1">
                {programacoesDoDia.map((prog) => (
                  <div
                    key={prog.id}
                    onClick={() => handleProgramacaoClick(prog)}
                    className={`p-1 rounded text-xs text-white cursor-pointer hover:opacity-80 ${getStatusColor(prog.status)}`}
                    title={`OS ${prog.os_numero} - ${prog.status}\n${formatarHora(prog.inicio_previsto)} - ${formatarHora(prog.fim_previsto)}`}
                  >
                    <div className="font-medium truncate">OS {prog.os_numero}</div>
                    <div className="truncate">{formatarHora(prog.inicio_previsto)}</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  const renderizarVisualizacaoMes = () => {
    const diasMes = obterDiasMes();
    const nomesDias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
    const mesAtual = dataAtual.getMonth();

    return (
      <div className="grid grid-cols-7 gap-1">
        {/* Cabeçalho dos dias */}
        {nomesDias.map((nome) => (
          <div key={nome} className="p-2 text-center font-medium text-gray-700 bg-gray-50">
            {nome}
          </div>
        ))}
        
        {/* Células dos dias */}
        {diasMes.map((dia, index) => {
          const programacoesDoDia = obterProgramacoesDoDia(dia);
          const isHoje = dia.toDateString() === new Date().toDateString();
          const isMesAtual = dia.getMonth() === mesAtual;
          
          return (
            <div
              key={index}
              className={`min-h-20 p-1 border border-gray-200 ${
                isHoje ? 'bg-blue-50' : 
                isMesAtual ? 'bg-white' : 'bg-gray-50'
              }`}
            >
              <div className={`text-sm ${isMesAtual ? 'text-gray-900' : 'text-gray-400'}`}>
                {dia.getDate()}
              </div>
              <div className="space-y-1">
                {programacoesDoDia.slice(0, 2).map((prog) => (
                  <div
                    key={prog.id}
                    onClick={() => handleProgramacaoClick(prog)}
                    className={`w-2 h-2 rounded-full cursor-pointer ${getStatusColor(prog.status)}`}
                    title={`OS ${prog.os_numero} - ${prog.status}`}
                  />
                ))}
                {programacoesDoDia.length > 2 && (
                  <div className="text-xs text-gray-500">
                    +{programacoesDoDia.length - 2}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow border">
      {/* Header do Calendário */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {visualizacao === 'semana' ? 'Calendário Semanal' : 'Calendário Mensal'}
            </h3>
            <div className="text-sm text-gray-600">
              {visualizacao === 'semana' 
                ? `Semana de ${formatarData(obterDiasSemana()[0])}`
                : dataAtual.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
              }
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Controles de Visualização */}
            <div className="flex border border-gray-300 rounded">
              <button
                onClick={() => setVisualizacao('semana')}
                className={`px-3 py-1 text-sm ${
                  visualizacao === 'semana' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Semana
              </button>
              <button
                onClick={() => setVisualizacao('mes')}
                className={`px-3 py-1 text-sm ${
                  visualizacao === 'mes' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Mês
              </button>
            </div>
            
            {/* Navegação */}
            <button
              onClick={() => navegarData('anterior')}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            
            <button
              onClick={irParaHoje}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              Hoje
            </button>
            
            <button
              onClick={() => navegarData('proximo')}
              className="p-2 text-gray-600 hover:text-gray-800"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            
            <button
              onClick={carregarProgramacoes}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Atualizar
            </button>
          </div>
        </div>
      </div>

      {/* Conteúdo do Calendário */}
      <div className="p-4">
        {loading ? (
          <div className="flex justify-center items-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Carregando programações...</span>
          </div>
        ) : (
          <>
            {visualizacao === 'semana' ? renderizarVisualizacaoSemana() : renderizarVisualizacaoMes()}
            
            {/* Legenda */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded bg-blue-500"></div>
                  <span>Programada</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded bg-yellow-500"></div>
                  <span>Em Andamento</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded bg-purple-500"></div>
                  <span>Enviada</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded bg-green-500"></div>
                  <span>Concluída</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-3 h-3 rounded bg-red-500"></div>
                  <span>Cancelada</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Modal de Detalhes da Programação */}
      {selectedProgramacao && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                Detalhes da Programação
              </h3>
              <button
                onClick={() => setSelectedProgramacao(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-3">
              <div>
                <strong>OS:</strong> {selectedProgramacao.os_numero}
              </div>
              <div>
                <strong>Status:</strong> 
                <span className={`ml-2 px-2 py-1 text-xs rounded text-white ${getStatusColor(selectedProgramacao.status)}`}>
                  {selectedProgramacao.status}
                </span>
              </div>
              <div>
                <strong>Início:</strong> {new Date(selectedProgramacao.inicio_previsto).toLocaleString('pt-BR')}
              </div>
              <div>
                <strong>Fim:</strong> {new Date(selectedProgramacao.fim_previsto).toLocaleString('pt-BR')}
              </div>
              {selectedProgramacao.responsavel_nome && (
                <div>
                  <strong>Responsável:</strong> {selectedProgramacao.responsavel_nome}
                </div>
              )}
              {selectedProgramacao.setor_nome && (
                <div>
                  <strong>Setor:</strong> {selectedProgramacao.setor_nome}
                </div>
              )}
              {selectedProgramacao.observacoes && (
                <div>
                  <strong>Observações:</strong> {selectedProgramacao.observacoes}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgramacaoCalendario;
