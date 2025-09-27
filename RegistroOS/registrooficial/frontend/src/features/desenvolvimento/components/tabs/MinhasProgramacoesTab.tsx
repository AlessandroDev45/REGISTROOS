import React, { useState, useEffect } from 'react';
import api from '../../../../services/api';

interface Programacao {
    id: number;
    os_numero: string;
    cliente_nome: string;
    equipamento_descricao: string;
    inicio_previsto: string;
    fim_previsto: string;
    status: string;
    observacoes: string;
    setor_nome: string;
    responsavel_nome: string;
    created_at: string;
    updated_at: string;
}

interface Apontamento {
    id?: number;
    programacao_id: number;
    data_inicio: string;
    hora_inicio: string;
    data_fim?: string;
    hora_fim?: string;
    observacoes: string;
    status: 'EM_ANDAMENTO' | 'PAUSADO' | 'CONCLUIDO';
}

const MinhasProgramacoesTab: React.FC = () => {
    const [programacoes, setProgramacoes] = useState<Programacao[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedProgramacao, setSelectedProgramacao] = useState<Programacao | null>(null);
    const [showApontamentoModal, setShowApontamentoModal] = useState(false);
    const [apontamentoAtivo, setApontamentoAtivo] = useState<Apontamento | null>(null);

    useEffect(() => {
        carregarMinhasProgramacoes();
    }, []);

    const carregarMinhasProgramacoes = async () => {
        try {
            setLoading(true);
            // Buscar programações atribuídas ao usuário logado
            const response = await api.get('/desenvolvimento/minhas-programacoes');
            setProgramacoes(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar programações:', error);
            setProgramacoes([]);
        } finally {
            setLoading(false);
        }
    };

    const iniciarExecucao = async (programacao: Programacao) => {
        try {
            // Criar apontamento inicial
            const novoApontamento: Apontamento = {
                programacao_id: programacao.id,
                data_inicio: new Date().toISOString().split('T')[0],
                hora_inicio: new Date().toTimeString().split(' ')[0].substring(0, 5),
                observacoes: 'Execução iniciada',
                status: 'EM_ANDAMENTO'
            };

            await api.post('/desenvolvimento/apontamentos', novoApontamento);
            
            // Atualizar status da programação
            await api.patch(`/pcp/programacoes/${programacao.id}/status`, {
                status: 'EM_ANDAMENTO'
            });

            setApontamentoAtivo(novoApontamento);
            alert('✅ Execução iniciada com sucesso!');
            carregarMinhasProgramacoes();
        } catch (error) {
            console.error('Erro ao iniciar execução:', error);
            alert('❌ Erro ao iniciar execução');
        }
    };

    const pausarExecucao = async (programacao: Programacao) => {
        try {
            if (apontamentoAtivo) {
                // Finalizar apontamento atual
                await api.patch(`/desenvolvimento/apontamentos/${apontamentoAtivo.id}`, {
                    data_fim: new Date().toISOString().split('T')[0],
                    hora_fim: new Date().toTimeString().split(' ')[0].substring(0, 5),
                    status: 'PAUSADO'
                });

                setApontamentoAtivo(null);
                alert('⏸️ Execução pausada');
            }
        } catch (error) {
            console.error('Erro ao pausar execução:', error);
            alert('❌ Erro ao pausar execução');
        }
    };

    const finalizarExecucao = async (programacao: Programacao) => {
        try {
            if (apontamentoAtivo) {
                // Finalizar apontamento atual
                await api.patch(`/desenvolvimento/apontamentos/${apontamentoAtivo.id}`, {
                    data_fim: new Date().toISOString().split('T')[0],
                    hora_fim: new Date().toTimeString().split(' ')[0].substring(0, 5),
                    status: 'CONCLUIDO'
                });
            }

            // Atualizar status da programação para aguardando aprovação
            await api.patch(`/pcp/programacoes/${programacao.id}/status`, {
                status: 'AGUARDANDO_APROVACAO'
            });

            setApontamentoAtivo(null);
            alert('✅ Execução finalizada! Aguardando aprovação do supervisor.');
            carregarMinhasProgramacoes();
        } catch (error) {
            console.error('Erro ao finalizar execução:', error);
            alert('❌ Erro ao finalizar execução');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'PROGRAMADA': return 'bg-blue-100 text-blue-800';
            case 'EM_ANDAMENTO': return 'bg-yellow-100 text-yellow-800';
            case 'AGUARDANDO_APROVACAO': return 'bg-purple-100 text-purple-800';
            case 'APROVADA': return 'bg-green-100 text-green-800';
            case 'REJEITADA': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'PROGRAMADA': return '📋';
            case 'EM_ANDAMENTO': return '⚡';
            case 'AGUARDANDO_APROVACAO': return '⏳';
            case 'APROVADA': return '✅';
            case 'REJEITADA': return '❌';
            default: return '📄';
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">
                    👷‍♂️ Minhas Programações
                </h2>
                <button
                    onClick={carregarMinhasProgramacoes}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                    🔄 Atualizar
                </button>
            </div>

            {programacoes.length === 0 ? (
                <div className="text-center py-12">
                    <div className="text-6xl mb-4">📋</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Nenhuma programação atribuída
                    </h3>
                    <p className="text-gray-500">
                        Você não possui programações atribuídas no momento.
                    </p>
                </div>
            ) : (
                <div className="grid gap-6">
                    {programacoes.map((programacao) => (
                        <div
                            key={programacao.id}
                            className="bg-white rounded-lg shadow-md border border-gray-200 p-6"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900">
                                        OS: {programacao.os_numero}
                                    </h3>
                                    <p className="text-sm text-gray-600">
                                        {programacao.cliente_nome} - {programacao.equipamento_descricao}
                                    </p>
                                </div>
                                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(programacao.status)}`}>
                                    {getStatusIcon(programacao.status)} {programacao.status.replace('_', ' ')}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <p className="text-sm font-medium text-gray-700">Início Previsto:</p>
                                    <p className="text-sm text-gray-600">
                                        {new Date(programacao.inicio_previsto).toLocaleString('pt-BR')}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-700">Fim Previsto:</p>
                                    <p className="text-sm text-gray-600">
                                        {new Date(programacao.fim_previsto).toLocaleString('pt-BR')}
                                    </p>
                                </div>
                            </div>

                            {programacao.observacoes && (
                                <div className="mb-4">
                                    <p className="text-sm font-medium text-gray-700">Observações:</p>
                                    <p className="text-sm text-gray-600">{programacao.observacoes}</p>
                                </div>
                            )}

                            <div className="flex space-x-3">
                                {programacao.status === 'PROGRAMADA' && (
                                    <button
                                        onClick={() => iniciarExecucao(programacao)}
                                        className="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                                    >
                                        ▶️ Iniciar Execução
                                    </button>
                                )}

                                {programacao.status === 'EM_ANDAMENTO' && (
                                    <>
                                        <button
                                            onClick={() => pausarExecucao(programacao)}
                                            className="px-4 py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700 transition-colors"
                                        >
                                            ⏸️ Pausar
                                        </button>
                                        <button
                                            onClick={() => finalizarExecucao(programacao)}
                                            className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                                        >
                                            ✅ Finalizar
                                        </button>
                                    </>
                                )}

                                <button
                                    onClick={() => {
                                        setSelectedProgramacao(programacao);
                                        setShowApontamentoModal(true);
                                    }}
                                    className="px-4 py-2 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
                                >
                                    📝 Ver Apontamentos
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MinhasProgramacoesTab;
