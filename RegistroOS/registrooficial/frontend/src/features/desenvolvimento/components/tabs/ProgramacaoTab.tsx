import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useCachedSetores } from '../../../../hooks/useCachedSetores';
import { getStatusColorClass, getPriorityColorClass, getPriorityBorderColorClass } from '../../../../utils/statusColors';
import api from '../../../../services/api';
import AtribuicaoProgramacaoModal from '../../../../components/AtribuicaoProgramacaoModal';

interface OrdemServico {
    id: number;
    numero: string;
    cliente: string;
    equipamento: string;
    prioridade: 'BAIXA' | 'NORMAL' | 'ALTA' | 'URGENTE';
    status: 'AGENDADO' | 'EM_ANDAMENTO' | 'CONCLUIDO' | 'ATRASADO';
    data_prevista: string;
    responsavel_atual?: string;
    tempo_estimado: number; // em horas
    descricao: string;
}

interface Programacao {
    id: number;
    id_ordem_servico: number;
    os_numero: string;
    responsavel_id?: number;
    responsavel_nome?: string;
    inicio_previsto: string;
    fim_previsto: string;
    status: string;
    observacoes?: string;
    setor_nome?: string;
    departamento_nome?: string;
    id_setor?: number;
    created_at: string;
    updated_at: string;
}

const ProgramacaoTab: React.FC = () => {
    const { setorAtivo } = useSetor();
    const [ordensServico, setOrdensServico] = useState<OrdemServico[]>([]);
    // const [programacoes, setProgramacoes] = useState<Programacao[]>([]); // Removido - usando apenas ordensServico
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'calendar' | 'list'>('list');
    const [filtroStatus, setFiltroStatus] = useState<string>('');
    const [filtroPrioridade, setFiltroPrioridade] = useState<string>('');

    // Estados dos modais
    const [showAtribuicaoModal, setShowAtribuicaoModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showReatribuirModal, setShowReatribuirModal] = useState(false);
    const [selectedProgramacao, setSelectedProgramacao] = useState<Programacao | null>(null);

    useEffect(() => {
        const fetchProgramacao = async () => {
            if (!setorAtivo) return;

            try {
                setLoading(true);

                // DESENVOLVIMENTO: Buscar APENAS programações do setor do usuário
                const response = await api.get('/desenvolvimento/programacao', {
                    params: {
                        status: filtroStatus || undefined
                    }
                });

                // Programações do setor com deduplicação por ID único
                const programacoesData = response.data || [];
                console.log('🔧 Programações recebidas:', programacoesData.length);

                // Deduplicar por ID da programação (não por OS)
                const programacoesUnicas = new Map();
                programacoesData.forEach((prog: any) => {
                    if (!programacoesUnicas.has(prog.id)) {
                        programacoesUnicas.set(prog.id, prog);
                    }
                });
                const programacoesDeduplicadas = Array.from(programacoesUnicas.values());
                console.log('🔧 Após deduplicação:', programacoesDeduplicadas.length);

                // Converter para formato de OrdemServico para compatibilidade
                const ordensFormatadas: OrdemServico[] = programacoesDeduplicadas.map((prog: any) => ({
                    id: prog.id,
                    numero: prog.os_numero || prog.numero || String(prog.id),
                    status: prog.status || 'PROGRAMADA',
                    responsavel_atual: prog.responsavel_nome || prog.responsavel_atual,
                    data_prevista: prog.inicio_previsto?.split('T')[0] || prog.data_prevista,
                    descricao: prog.observacoes || prog.descricao || `Programação ${prog.id}`,
                    prioridade: prog.prioridade || 'MEDIA',
                    tempo_estimado: prog.tempo_estimado || 8,
                    cliente: prog.cliente_nome || '', // Dados reais do cliente
                    equipamento: prog.equipamento_descricao || '' // Dados reais do equipamento
                }));
                setOrdensServico(ordensFormatadas);

                // Usando apenas ordensServico - sem conversão desnecessária

                // Usar apenas dados reais da API - sem fallback para dados mock
                // Se não há dados, mostrar lista vazia
            } catch (error) {
                console.error('Erro ao buscar programação:', error);
                // Em caso de erro, usar dados mock
                setOrdensServico([]);
            } finally {
                setLoading(false);
            }
        };

        fetchProgramacao();
    }, [setorAtivo, filtroStatus, filtroPrioridade]);

    const handleEditProgramacao = (programacao: Programacao) => {
        setSelectedProgramacao(programacao);
        setShowEditModal(true);
    };

    const handleReatribuirProgramacao = (programacao: Programacao) => {
        setSelectedProgramacao(programacao);
        setShowReatribuirModal(true);
    };

    const handleModalSuccess = () => {
        // Recarregar dados após sucesso - usar o mesmo useEffect
        window.location.reload(); // Força recarregamento completo
    };

    const getPriorityColor = (prioridade: string) => {
        switch (prioridade) {
            case 'URGENTE': return 'bg-red-100 text-red-800 border-red-200';
            case 'ALTA': return 'bg-orange-100 text-orange-800 border-orange-200';
            case 'NORMAL': return 'bg-blue-100 text-blue-800 border-blue-200';
            case 'BAIXA': return 'bg-gray-100 text-gray-800 border-gray-200';
            default: return 'bg-gray-100 text-gray-800 border-gray-200';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'AGENDADO': return 'bg-blue-100 text-blue-800';
            case 'EM_ANDAMENTO': return 'bg-yellow-100 text-yellow-800';
            case 'CONCLUIDO': return 'bg-green-100 text-green-800';
            case 'ATRASADO': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const handleReatribuirOS = (osId: number) => {
        const novoResponsavel = prompt('Digite o nome do novo responsável:');
        if (novoResponsavel) {
            setOrdensServico(prev =>
                prev.map(os =>
                    os.id === osId
                        ? { ...os, responsavel_atual: novoResponsavel }
                        : os
                )
            );
            alert(`OS reatribuída para ${novoResponsavel}`);
        }
    };

    const ordemsFiltradas = ordensServico.filter(os => {
        const statusMatch = !filtroStatus || os.status === filtroStatus;
        const prioridadeMatch = !filtroPrioridade || os.prioridade === filtroPrioridade;
        return statusMatch && prioridadeMatch;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2">Carregando programação...</span>
            </div>
        );
    }

    if (!setorAtivo) {
        return (
            <div className="max-w-6xl mx-auto p-8">
                <div className="text-center text-gray-500">
                    <p>Carregando informações do setor...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full p-6">
            <div className="bg-white rounded-lg shadow-sm">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">
                                Programação - {setorAtivo.nome}
                            </h2>
                            <p className="text-sm text-gray-600 mt-1">
                                Gerencie e acompanhe a programação de ordens de serviço
                            </p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setViewMode('list')}
                                className={`px-3 py-2 text-sm rounded-md ${viewMode === 'list'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                            >
                                📋 Lista
                            </button>
                            <button
                                onClick={() => setViewMode('calendar')}
                                className={`px-3 py-2 text-sm rounded-md ${viewMode === 'calendar'
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                            >
                                📅 Calendário
                            </button>
                        </div>
                    </div>
                </div>

                {/* Filtros */}
                <div className="p-6 border-b border-gray-200 bg-gray-50">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Filtrar por Status
                            </label>
                            <select
                                value={filtroStatus}
                                onChange={(e) => setFiltroStatus(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Todos os Status</option>
                                <option value="AGENDADO">Agendado</option>
                                <option value="EM_ANDAMENTO">Em Andamento</option>
                                <option value="CONCLUIDO">Concluído</option>
                                <option value="ATRASADO">Atrasado</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Filtrar por Prioridade
                            </label>
                            <select
                                value={filtroPrioridade}
                                onChange={(e) => setFiltroPrioridade(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="">Todas as Prioridades</option>
                                <option value="URGENTE">Urgente</option>
                                <option value="ALTA">Alta</option>
                                <option value="NORMAL">Normal</option>
                                <option value="BAIXA">Baixa</option>
                            </select>
                        </div>
                        <div className="flex items-end">
                            <div className="text-sm text-gray-500">
                                {ordemsFiltradas.length} OS encontrada(s)
                            </div>
                        </div>
                    </div>
                </div>

                {/* Seção de Programações removida para evitar duplicação */}

                {/* Conteúdo */}
                <div className="p-6">
                    {viewMode === 'calendar' ? (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">📅</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                Visualização em Calendário
                            </h3>
                            <p className="text-gray-500">
                                A visualização em calendário será implementada em breve
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {ordemsFiltradas.length === 0 ? (
                                <div className="text-center py-12">
                                    <div className="text-gray-400 text-6xl mb-4">📋</div>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                                        Nenhuma OS encontrada
                                    </h3>
                                    <p className="text-gray-500">
                                        {filtroStatus || filtroPrioridade
                                            ? 'Tente ajustar os filtros'
                                            : 'Não há ordens de serviço programadas'}
                                    </p>
                                </div>
                            ) : (
                                ordemsFiltradas.map((os) => (
                                    <div key={os.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex-1">
                                                <div className="flex items-center space-x-3 mb-2">
                                                    <h3 className="text-lg font-medium text-gray-900">
                                                        {os.numero}
                                                    </h3>
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(os.status || 'PROGRAMADA')}`}>
                                                        {(os.status || 'PROGRAMADA').replace('_', ' ')}
                                                    </span>
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getPriorityColor(os.prioridade || 'MEDIA')}`}>
                                                        {os.prioridade || 'MEDIA'}
                                                    </span>
                                                </div>
                                                
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                                                    <div>
                                                        <p><span className="font-medium">Cliente:</span> {os.cliente}</p>
                                                        <p><span className="font-medium">Equipamento:</span> {os.equipamento}</p>
                                                        <p><span className="font-medium">Responsável:</span> {os.responsavel_atual || 'Não atribuído'}</p>
                                                    </div>
                                                    <div>
                                                        <p><span className="font-medium">Data Prevista:</span> {new Date(os.data_prevista).toLocaleDateString('pt-BR')}</p>
                                                        <p><span className="font-medium">Tempo Estimado:</span> {os.tempo_estimado}h</p>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div className="ml-6 flex space-x-2">
                                                <button
                                                    onClick={() => handleReatribuirProgramacao({
                                                        id: os.id,
                                                        id_ordem_servico: os.id,
                                                        os_numero: os.numero,
                                                        status: os.status || 'PROGRAMADA',
                                                        responsavel_nome: os.responsavel_atual || '',
                                                        inicio_previsto: os.data_prevista || '',
                                                        fim_previsto: os.data_prevista || '',
                                                        setor_nome: setorAtivo?.nome || '',
                                                        created_at: new Date().toISOString(),
                                                        updated_at: new Date().toISOString(),
                                                        observacoes: os.descricao || '',
                                                        departamento_nome: '',
                                                        id_setor: undefined,
                                                        responsavel_id: undefined
                                                    })}
                                                    className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                                                >
                                                    🔄 Reatribuir
                                                </button>
                                                <button
                                                    onClick={() => handleEditProgramacao({
                                                        id: os.id,
                                                        id_ordem_servico: os.id,
                                                        os_numero: os.numero,
                                                        status: os.status || 'PROGRAMADA',
                                                        responsavel_nome: os.responsavel_atual || '',
                                                        inicio_previsto: os.data_prevista || '',
                                                        fim_previsto: os.data_prevista || '',
                                                        setor_nome: setorAtivo?.nome || '',
                                                        created_at: new Date().toISOString(),
                                                        updated_at: new Date().toISOString(),
                                                        observacoes: os.descricao || '',
                                                        departamento_nome: '',
                                                        id_setor: undefined,
                                                        responsavel_id: undefined
                                                    })}
                                                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                                                >
                                                    ✏️ Editar
                                                </button>
                                            </div>
                                        </div>
                                        
                                        <div className="border-t border-gray-100 pt-4">
                                            <p className="text-sm text-gray-700">
                                                <span className="font-medium">Descrição:</span> {os.descricao}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Modais */}
            <AtribuicaoProgramacaoModal
                isOpen={showAtribuicaoModal}
                onClose={() => setShowAtribuicaoModal(false)}
                onSuccess={handleModalSuccess}
                isEdit={false}
                isReatribuir={false}
            />

            <AtribuicaoProgramacaoModal
                isOpen={showEditModal}
                onClose={() => setShowEditModal(false)}
                onSuccess={handleModalSuccess}
                isEdit={true}
                isReatribuir={false}
                programacaoId={selectedProgramacao?.id}
                programacaoData={selectedProgramacao}
            />

            <AtribuicaoProgramacaoModal
                isOpen={showReatribuirModal}
                onClose={() => setShowReatribuirModal(false)}
                onSuccess={handleModalSuccess}
                isEdit={false}
                isReatribuir={true}
                programacaoId={selectedProgramacao?.id}
                programacaoData={selectedProgramacao}
            />
        </div>
    );
};

export default ProgramacaoTab;
