import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import api from '../../../../services/api';
import { getStatusColorClass } from '../../../../utils/statusColors';

interface Apontamento {
    id: number;
    numero_os: string;
    cliente: string;
    equipamento: string;
    data_hora_inicio: string;
    data_hora_fim?: string;
    tempo_trabalhado?: number;
    tipo_atividade: string;
    descricao_atividade: string;
    status_apontamento: string;
    setor: string;
    departamento: string;
    nome_tecnico: string;
    aprovado_supervisor?: boolean;
    foi_retrabalho?: boolean;
    servico_de_campo?: boolean;
    observacoes?: string;
    observacao_os?: string;
    causa_retrabalho?: string;
    data_aprovacao_supervisor?: string;
}

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

interface MinhasOsTabProps {
    onIniciarExecucao?: (programacao: any) => void;
}

const MinhasOsTab: React.FC<MinhasOsTabProps> = ({ onIniciarExecucao }) => {
    const navigate = useNavigate();
    const { setorAtivo } = useSetor();
    const { user } = useAuth();

    // Estados para abas internas
    const [activeInternalTab, setActiveInternalTab] = useState<'apontamentos' | 'programacoes'>('apontamentos');

    // Estados para apontamentos
    const [apontamentos, setApontamentos] = useState<Apontamento[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [filtroUsuario, setFiltroUsuario] = useState<string>('');
    const [dataInicio, setDataInicio] = useState<string>('');
    const [dataFim, setDataFim] = useState<string>('');
    const [filtroStatus, setFiltroStatus] = useState<string>('');

    // Estados para programações
    const [programacoes, setProgramacoes] = useState<Programacao[]>([]);
    const [loadingProgramacoes, setLoadingProgramacoes] = useState(false);

    useEffect(() => {
        const fetchApontamentos = async () => {
            if (!user) return;

            try {
                setLoading(true);
                setError(null);

                const params: any = {};

                // Filtros de data
                if (dataInicio) params.data_inicio = dataInicio;
                if (dataFim) params.data_fim = dataFim;
                if (selectedDate && !dataInicio && !dataFim) {
                    params.data_inicio = selectedDate;
                    params.data_fim = selectedDate;
                }

                // Filtros automáticos baseados na autenticação do usuário
                if (user.privilege_level === 'USER') {
                    params.usuario_id = user.id;
                    params.setor = user.setor;
                    params.departamento = user.departamento;
                } else if (user.privilege_level === 'SUPERVISOR') {
                    params.setor = user.setor;
                    params.departamento = user.departamento;
                    if (filtroUsuario) {
                        params.usuario_id = filtroUsuario;
                        params.usuario_setor = user.setor;
                    }
                    if (filtroStatus) params.status = filtroStatus;
                } else if (user.privilege_level === 'ADMIN') {
                    if (filtroUsuario) params.usuario_id = filtroUsuario;
                    if (filtroStatus) params.status = filtroStatus;
                }

                const response = await api.get('/apontamentos-detalhados', { params });

                // Converter para formato esperado da interface
                const apontamentosConvertidos = response.data.map((apt: any) => ({
                    id: apt.id,
                    numero_os: apt.numero_os || `APT-${apt.id}`,
                    cliente: apt.cliente || 'Cliente não informado',
                    equipamento: apt.equipamento || 'Equipamento não informado',
                    data_hora_inicio: apt.data_hora_inicio || apt.data_inicio,
                    data_hora_fim: apt.data_hora_fim || apt.data_fim,
                    tempo_trabalhado: apt.tempo_trabalhado,
                    tipo_atividade: apt.tipo_atividade || 'N/A',
                    descricao_atividade: apt.descricao_atividade || 'N/A',
                    status_apontamento: apt.status_apontamento || apt.status || 'N/A',
                    setor: apt.setor || 'N/A',
                    departamento: apt.departamento || 'N/A',
                    nome_tecnico: apt.nome_tecnico || apt.usuario || 'N/A',
                    aprovado_supervisor: apt.aprovado_supervisor || false,
                    foi_retrabalho: apt.foi_retrabalho || false,
                    servico_de_campo: apt.servico_de_campo || false,
                    observacoes: apt.observacoes || '',
                    observacao_os: apt.observacao_os || '',
                    causa_retrabalho: apt.causa_retrabalho || '',
                    data_aprovacao_supervisor: apt.data_aprovacao_supervisor
                }));

                setApontamentos(apontamentosConvertidos);
            } catch (err: any) {
                console.error('Erro ao buscar apontamentos:', err);
                setError(err.response?.data?.detail || 'Erro ao carregar apontamentos');
            } finally {
                setLoading(false);
            }
        };

        fetchApontamentos();
    }, [user, selectedDate, filtroUsuario, dataInicio, dataFim, filtroStatus]);

    // Função para carregar programações
    const fetchProgramacoes = async () => {
        if (!user) return;

        try {
            setLoadingProgramacoes(true);

            // Buscar programações atribuídas ao usuário logado
            const response = await api.get('/desenvolvimento/minhas-programacoes');
            setProgramacoes(response.data || []);
        } catch (error) {
            console.error('Erro ao carregar programações:', error);
            setProgramacoes([]);
        } finally {
            setLoadingProgramacoes(false);
        }
    };

    // Carregar programações sempre que o usuário mudar (para mostrar contador correto)
    useEffect(() => {
        if (user) {
            fetchProgramacoes();
        }
    }, [user]);

    // Atualizar programações automaticamente quando na aba de programações
    useEffect(() => {
        if (activeInternalTab === 'programacoes' && user) {
            // Atualizar automaticamente a cada 30 segundos quando na aba de programações
            const interval = setInterval(() => {
                fetchProgramacoes();
            }, 30000);

            return () => clearInterval(interval);
        }
    }, [activeInternalTab, user]);

    // Funções para gerenciar programações
    const iniciarExecucao = async (programacao: Programacao) => {
        try {
            console.log('🚀 [MinhasOsTab] Iniciando execução:', {
                programacao: programacao.id,
                os_numero: programacao.os_numero,
                setorAtivo: setorAtivo
            });

            // Atualizar status da programação para EM_ANDAMENTO
            await api.patch(`/pcp/programacoes/${programacao.id}/status`, {
                status: 'EM_ANDAMENTO'
            });

            console.log('✅ Status da programação atualizado');

            // Se há callback para iniciar execução, usar ele (redirecionamento interno)
            if (onIniciarExecucao) {
                console.log('🔄 Usando redirecionamento interno para apontamento');
                onIniciarExecucao(programacao);
            } else {
                // Fallback: redirecionar para página de apontamento com OS pré-preenchida
                const setorSlug = setorAtivo?.chave || 'laboratorio-eletrico';
                const targetUrl = `/desenvolvimento/${setorSlug}?tab=apontamento&os=${programacao.os_numero}&programacao_id=${programacao.id}`;

                console.log('🔗 Redirecionando para:', targetUrl);
                navigate(targetUrl);
            }

        } catch (error) {
            console.error('Erro ao iniciar execução:', error);
            alert('❌ Erro ao iniciar execução');
        }
    };



    // Funções utilitárias para programações
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

    const calculateTotalHours = () => {
        return apontamentos.reduce((total, apt) => {
            if (apt.tempo_trabalhado) {
                total += apt.tempo_trabalhado;
            }
            return total;
        }, 0);
    };

    const formatDate = (dateString: string) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const formatTime = (dateString: string) => {
        if (!dateString) return '--';
        return new Date(dateString).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'});
    };

    const handleDeleteLastOS = async () => {
        if (apontamentos.length === 0) return;

        const lastApontamento = apontamentos[apontamentos.length - 1];
        
        if (lastApontamento.aprovado_supervisor) {
            alert('Não é possível excluir um apontamento já aprovado pelo supervisor.');
            return;
        }

        if (!window.confirm('Tem certeza que deseja excluir o último apontamento?')) {
            return;
        }

        try {
            await api.delete('/desenvolvimento/minhas-os', {
                data: [lastApontamento.id]
            });
            setApontamentos(prev => prev.filter(apt => apt.id !== lastApontamento.id));
            alert('Apontamento excluído com sucesso!');
        } catch (err: any) {
            console.error('Erro ao deletar apontamento:', err);
            alert('Erro ao deletar apontamento. Verifique suas permissões.');
        }
    };

    const totalHours = calculateTotalHours();
    const horasRegulamentares = 8.8;
    const abstinencia = Math.max(0, horasRegulamentares - totalHours);
    const extraHours = Math.max(0, totalHours - horasRegulamentares);

    if (loading) {
        return (
            <div className="max-w-6xl mx-auto p-4">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-2 text-gray-600 text-sm">Carregando seus apontamentos...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-6xl mx-auto p-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex items-center">
                        <div className="text-red-400 text-lg mr-2">⚠️</div>
                        <p className="text-red-800 text-sm">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full p-3">
            <div className="bg-white rounded shadow overflow-hidden">
                {/* Header técnico */}
                <div className="bg-slate-800 border-b border-slate-700 px-4 py-3">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-lg font-semibold text-white tracking-wide">
                                MEU DASHBOARD
                            </h2>
                            <p className="text-slate-300 text-xs font-mono">
                                Apontamentos e Programações Pessoais
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-slate-400 text-xs uppercase">
                                {activeInternalTab === 'apontamentos' ? 'Apontamentos' : 'Programações'}
                            </div>
                            <div className="text-2xl font-mono font-bold text-white">
                                {activeInternalTab === 'apontamentos' ? apontamentos.length : programacoes.length}
                            </div>
                        </div>
                    </div>

                    {/* Abas técnicas */}
                    <div className="mt-3 flex space-x-1">
                        <button
                            onClick={() => setActiveInternalTab('apontamentos')}
                            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                activeInternalTab === 'apontamentos'
                                    ? 'bg-white text-slate-800'
                                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                        >
                            APONTAMENTOS
                        </button>
                        <button
                            onClick={() => setActiveInternalTab('programacoes')}
                            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                activeInternalTab === 'programacoes'
                                    ? 'bg-white text-slate-800'
                                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                        >
                            PROGRAMAÇÕES
                        </button>
                    </div>
                </div>

                {/* Filtros compactos */}
                {activeInternalTab === 'apontamentos' && (
                <div className="bg-slate-50 px-4 py-2 border-b border-gray-200">
                    <div className="grid grid-cols-4 gap-2">
                        {/* Data */}
                        <div>
                            <label className="text-xs font-medium text-gray-600 mb-1 block">Data</label>
                            <input
                                type="date"
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-slate-500 bg-white"
                            />
                        </div>

                        {/* Colaborador - SUPERVISOR */}
                        {user && user.privilege_level === 'SUPERVISOR' && (
                            <div>
                                <label className="text-xs font-medium text-gray-600 mb-1 block">Colaborador</label>
                                <input
                                    type="text"
                                    value={filtroUsuario}
                                    onChange={(e) => setFiltroUsuario(e.target.value)}
                                    placeholder="ID colaborador"
                                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-slate-500 bg-white"
                                />
                            </div>
                        )}

                        {/* Colaborador ID - ADMIN */}
                        {user && user.privilege_level === 'ADMIN' && (
                            <div>
                                <label className="text-xs font-medium text-gray-600 mb-1 block">Colaborador ID</label>
                                <input
                                    type="text"
                                    value={filtroUsuario}
                                    onChange={(e) => setFiltroUsuario(e.target.value)}
                                    placeholder="ID colaborador"
                                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-slate-500 bg-white"
                                />
                            </div>
                        )}

                        {/* Status - SUPERVISOR ou ADMIN */}
                        {user && ['SUPERVISOR', 'ADMIN'].includes(user.privilege_level) && (
                            <div>
                                <label className="text-xs font-medium text-gray-600 mb-1 block">Status</label>
                                <select
                                    value={filtroStatus}
                                    onChange={(e) => setFiltroStatus(e.target.value)}
                                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-slate-500 bg-white"
                                >
                                    <option value="">Todos</option>
                                    <option value="EM_ANDAMENTO">Em Andamento</option>
                                    <option value="FINALIZADO">Finalizado</option>
                                    <option value="PAUSADO">Pausado</option>
                                </select>
                            </div>
                        )}
                    </div>

                    {/* Período compacto */}
                    {user && ['SUPERVISOR', 'ADMIN'].includes(user.privilege_level) && (
                        <div className="mt-2 pt-2 border-t border-gray-200">
                            <label className="text-xs font-medium text-gray-600 mb-1 block">Período</label>
                            <div className="flex items-center space-x-2">
                                <input
                                    type="date"
                                    value={dataInicio}
                                    onChange={(e) => setDataInicio(e.target.value)}
                                    className="px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-slate-500 bg-white"
                                />
                                <span className="text-xs text-gray-500">até</span>
                                <input
                                    type="date"
                                    value={dataFim}
                                    onChange={(e) => setDataFim(e.target.value)}
                                    className="px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-slate-500 bg-white"
                                />
                            </div>
                        </div>
                    )}
                </div>
                )}

                {/* Conteúdo baseado na aba ativa */}
                {activeInternalTab === 'apontamentos' && (
                <>
                {/* Resumo técnico */}
                <div className="px-4 py-2 bg-slate-50 border-b border-gray-200">
                    <h3 className="text-sm font-semibold text-gray-800 mb-2 uppercase tracking-wide">
                        Resumo do Período
                    </h3>
                    <div className="grid grid-cols-4 gap-2">
                        <div className="bg-white border-l-4 border-blue-500 px-3 py-2">
                            <div className="text-lg font-mono font-bold text-blue-700">{totalHours.toFixed(1)}h</div>
                            <div className="text-xs text-gray-600 uppercase">Horas</div>
                        </div>
                        <div className="bg-white border-l-4 border-indigo-500 px-3 py-2">
                            <div className="text-lg font-mono font-bold text-indigo-700">{apontamentos.length}</div>
                            <div className="text-xs text-gray-600 uppercase">OS</div>
                        </div>

                        {abstinencia > 0 && (
                            <div className="bg-white border-l-4 border-yellow-500 px-3 py-2">
                                <div className="text-lg font-mono font-bold text-yellow-700">{abstinencia.toFixed(1)}h</div>
                                <div className="text-xs text-gray-600 uppercase">Abstinência</div>
                            </div>
                        )}

                        {extraHours > 0 && (
                            <div className="bg-white border-l-4 border-green-500 px-3 py-2">
                                <div className="text-lg font-mono font-bold text-green-700">+{extraHours.toFixed(1)}h</div>
                                <div className="text-xs text-gray-600 uppercase">Extra</div>
                            </div>
                        )}

                        {/* Status compacto */}
                        <div className="bg-white border-l-4 border-purple-500 px-3 py-2">
                            <div className="text-sm font-bold text-purple-700">
                                {totalHours >= 8 ? 'Completo' : 'Pendente'}
                            </div>
                            <div className="text-xs text-gray-600 uppercase">Status</div>
                        </div>
                    </div>
                </div>

                {/* Botão técnico */}
                {apontamentos.length > 0 && user?.privilege_level === 'USER' && (
                    <div className="px-4 py-2 bg-red-50 border-b border-red-200">
                        <div className="flex items-center justify-center">
                            <button
                                onClick={handleDeleteLastOS}
                                className="px-3 py-1 bg-red-600 text-white rounded text-xs font-medium hover:bg-red-700 transition-colors"
                            >
                                Excluir Último
                            </button>
                        </div>
                        <p className="text-center text-red-600 text-xs mt-1">
                            Só é possível excluir se não aprovado
                        </p>
                    </div>
                )}
                {/* Lista compacta */}
                <div className="px-4 py-3">
                    {apontamentos.length === 0 ? (
                        <div className="text-center py-8">
                            <div className="text-4xl mb-3 opacity-50">📋</div>
                            <h3 className="text-sm font-bold text-gray-900 mb-2">Nenhum apontamento</h3>
                            <p className="text-gray-600 text-xs max-w-md mx-auto">
                                {user?.privilege_level === 'USER'
                                    ? 'Sem apontamentos para a data selecionada'
                                    : 'Ajuste os filtros de busca'
                                }
                            </p>
                            <div className="mt-4">
                                <button
                                    onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
                                    className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
                                >
                                    Ver Hoje
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {apontamentos.map((apontamento, index) => (
                                <div key={apontamento.id} className="bg-white border border-gray-300 rounded shadow-sm hover:shadow transition-shadow overflow-hidden">
                                    {/* Header técnico */}
                                    <div className="bg-slate-100 px-3 py-1 border-b border-gray-200">
                                        <div className="flex justify-between items-center">
                                            <div className="flex items-center space-x-2">
                                                <div className="bg-slate-700 text-white px-2 py-0.5 rounded text-xs font-mono">
                                                    OS {apontamento.numero_os}
                                                </div>
                                                <div className="flex items-center space-x-1">
                                                    <span className={`px-2 py-0.5 text-xs font-medium rounded ${getStatusColorClass(apontamento.status_apontamento)}`}>
                                                        {apontamento.status_apontamento ? apontamento.status_apontamento.replace('_', ' ') : 'N/A'}
                                                    </span>
                                                    {apontamento.aprovado_supervisor && <span className="w-2 h-2 bg-green-500 rounded-full"></span>}
                                                    {apontamento.foi_retrabalho && <span className="w-2 h-2 bg-orange-500 rounded-full"></span>}
                                                    {apontamento.servico_de_campo && <span className="w-2 h-2 bg-purple-500 rounded-full"></span>}
                                                </div>
                                            </div>
                                            <div className="text-xs text-gray-600 font-mono">
                                                {apontamento.data_hora_inicio ? formatDate(apontamento.data_hora_inicio) : 'N/A'}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Conteúdo técnico */}
                                    <div className="p-2">
                                        <div className="grid grid-cols-2 gap-2 text-xs">
                                            <div>
                                                <div className="text-gray-500 font-medium">Cliente</div>
                                                <div className="font-semibold text-gray-900 truncate">{apontamento.cliente}</div>
                                            </div>

                                            <div>
                                                <div className="text-gray-500 font-medium">Equipamento</div>
                                                <div className="font-semibold text-gray-900 truncate">{apontamento.equipamento}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-500 font-medium">Início</div>
                                                <div className="font-mono text-gray-900">{formatTime(apontamento.data_hora_inicio)}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-500 font-medium">Fim</div>
                                                <div className="font-mono text-gray-900">{formatTime(apontamento.data_hora_fim || '')}</div>
                                            </div>
                                            {apontamento.tempo_trabalhado && (
                                                <div>
                                                    <div className="text-gray-500 font-medium">Tempo</div>
                                                    <div className="font-mono font-bold text-blue-700">{apontamento.tempo_trabalhado.toFixed(1)}h</div>
                                                </div>
                                            )}
                                            <div>
                                                <div className="text-gray-500 font-medium">Atividade</div>
                                                <div className="font-semibold text-gray-900 truncate">{apontamento.tipo_atividade}</div>
                                            </div>
                                            <div>
                                                <div className="text-gray-500 font-medium">Técnico</div>
                                                <div className="font-semibold text-gray-900 truncate">{apontamento.nome_tecnico}</div>
                                            </div>
                                        </div>

                                        {/* Observações compactas */}
                                        {(apontamento.observacoes || apontamento.observacao_os || apontamento.causa_retrabalho) && (
                                            <div className="mt-2 pt-2 border-t border-gray-200">
                                                <div className="text-xs text-gray-500 font-medium mb-1">Observações</div>
                                                <div className="space-y-1 text-xs">
                                                    {apontamento.observacoes && (
                                                        <div className="text-gray-700 line-clamp-1">{apontamento.observacoes}</div>
                                                    )}
                                                    {apontamento.observacao_os && (
                                                        <div className="text-blue-700 line-clamp-1">{apontamento.observacao_os}</div>
                                                    )}
                                                    {apontamento.causa_retrabalho && (
                                                        <div className="text-orange-700 line-clamp-1">{apontamento.causa_retrabalho}</div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                </>
                )}

                {/* Seção de Programações */}
                {activeInternalTab === 'programacoes' && (
                <div className="px-4 py-3">
                    {loadingProgramacoes ? (
                        <div className="flex justify-center items-center h-32">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
                        </div>
                    ) : programacoes.length === 0 ? (
                        <div className="text-center py-8">
                            <div className="text-4xl mb-3">📋</div>
                            <h3 className="text-sm font-medium text-gray-900 mb-2">
                                Nenhuma programação
                            </h3>
                            <p className="text-xs text-gray-500">
                                Sem programações atribuídas
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {programacoes.map((programacao) => (
                                <div
                                    key={programacao.id}
                                    className="bg-white rounded border border-gray-300 p-3"
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
                                            <div className="text-sm text-blue-600 font-medium">
                                                🔄 Em andamento - Finalize via apontamento
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                )}
            </div>
        </div>
    );
};

export default MinhasOsTab;
