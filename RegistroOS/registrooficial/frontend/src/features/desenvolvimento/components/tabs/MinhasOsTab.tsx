import React, { useState, useEffect } from 'react';
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

const MinhasOsTab: React.FC = () => {
    const { setorAtivo } = useSetor();
    const { user } = useAuth();
    const [apontamentos, setApontamentos] = useState<Apontamento[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
    const [filtroUsuario, setFiltroUsuario] = useState<string>('');
    const [dataInicio, setDataInicio] = useState<string>('');
    const [dataFim, setDataFim] = useState<string>('');
    const [filtroStatus, setFiltroStatus] = useState<string>('');

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
                    data_hora_inicio: apt.data_hora_inicio,
                    data_hora_fim: apt.data_hora_fim,
                    tempo_trabalhado: apt.tempo_trabalhado,
                    tipo_atividade: apt.tipo_atividade || 'N/A',
                    descricao_atividade: apt.descricao_atividade || 'N/A',
                    status_apontamento: apt.status_apontamento || 'N/A',
                    setor: apt.setor || 'N/A',
                    departamento: apt.departamento || 'N/A',
                    nome_tecnico: apt.nome_tecnico || 'N/A',
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
            await api.delete(`/apontamentos/${lastApontamento.id}`);
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
        <div className="w-full p-4">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                {/* Header Compacto */}
                <div className="bg-gradient-to-r from-blue-600 to-indigo-700 px-4 py-3">
                    <div className="flex justify-between items-center">
                        <div>
                            <h2 className="text-2xl font-bold text-white mb-1 flex items-center">
                                📋 {user?.privilege_level === 'USER' ? 'Meus Apontamentos' :
                                  user?.privilege_level === 'SUPERVISOR' ? `Apontamentos do Setor` :
                                  'Todos os Apontamentos'}
                            </h2>
                            <p className="text-blue-100 text-sm">
                                {user?.privilege_level === 'USER' ? 'Visualize seus apontamentos diários e controle de horas' :
                                  user?.privilege_level === 'SUPERVISOR' ? `Gerencie apontamentos do setor ${user.setor} - ${user.departamento}` :
                                  'Visualize e gerencie apontamentos de todos os setores e departamentos'}
                            </p>
                        </div>
                        <div className="text-right">
                            <div className="text-blue-100 text-xs font-medium">Total</div>
                            <div className="text-3xl font-bold text-white">{apontamentos.length}</div>
                        </div>
                    </div>
                </div>

                {/* Filtros Compactos */}
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Data */}
                        <div className="flex flex-col space-y-2">
                            <label className="text-sm font-semibold text-gray-700">📅 Data</label>
                            <input
                                type="date"
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                            />
                        </div>

                        {/* Colaborador - SUPERVISOR */}
                        {user && user.privilege_level === 'SUPERVISOR' && (
                            <div className="flex flex-col space-y-2">
                                <label className="text-sm font-semibold text-gray-700">👤 Colaborador</label>
                                <input
                                    type="text"
                                    value={filtroUsuario}
                                    onChange={(e) => setFiltroUsuario(e.target.value)}
                                    placeholder="ID do colaborador do setor"
                                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                                    title="Filtrar por colaborador específico do seu setor"
                                />
                            </div>
                        )}

                        {/* Colaborador ID - ADMIN */}
                        {user && user.privilege_level === 'ADMIN' && (
                            <div className="flex flex-col space-y-2">
                                <label className="text-sm font-semibold text-gray-700">👤 Colaborador ID</label>
                                <input
                                    type="text"
                                    value={filtroUsuario}
                                    onChange={(e) => setFiltroUsuario(e.target.value)}
                                    placeholder="ID do colaborador"
                                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                                />
                            </div>
                        )}

                        {/* Status - SUPERVISOR ou ADMIN */}
                        {user && ['SUPERVISOR', 'ADMIN'].includes(user.privilege_level) && (
                            <div className="flex flex-col space-y-2">
                                <label className="text-sm font-semibold text-gray-700">📊 Status</label>
                                <select
                                    value={filtroStatus}
                                    onChange={(e) => setFiltroStatus(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                                >
                                    <option value="">Todos os Status</option>
                                    <option value="EM_ANDAMENTO">Em Andamento</option>
                                    <option value="FINALIZADO">Finalizado</option>
                                    <option value="PAUSADO">Pausado</option>
                                </select>
                            </div>
                        )}
                    </div>

                    {/* Filtros de período para SUPERVISOR e ADMIN */}
                    {/* Filtros de período para SUPERVISOR e ADMIN */}
                    {user && ['SUPERVISOR', 'ADMIN'].includes(user.privilege_level) && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                            <div className="flex flex-col space-y-1">
                                <label className="text-sm font-semibold text-gray-700">📅 Período</label>
                                <div className="flex items-center space-x-2">
                                    <input
                                        type="date"
                                        value={dataInicio}
                                        onChange={(e) => setDataInicio(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                                        title="Data início"
                                    />
                                    <span className="text-gray-500 font-medium">até</span>
                                    <input
                                        type="date"
                                        value={dataFim}
                                        onChange={(e) => setDataFim(e.target.value)}
                                        className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                                        title="Data fim"
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>
                {/* Cards de Resumo Compactos */}
                <div className="px-4 py-3 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
                    <h3 className="text-base font-semibold text-gray-900 mb-3 flex items-center">
                        📊 Resumo do Período
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-2xl font-bold">{totalHours.toFixed(1)}h</div>
                                    <div className="text-blue-100 text-sm font-medium">Horas Trabalhadas</div>
                                </div>
                                <div className="text-3xl opacity-80">⏰</div>
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg p-4 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-2xl font-bold">{apontamentos.length}</div>
                                    <div className="text-indigo-100 text-sm font-medium">OS Trabalhadas</div>
                                </div>
                                <div className="text-3xl opacity-80">📋</div>
                            </div>
                        </div>

                        {abstinencia > 0 && (
                            <div className="bg-gradient-to-br from-yellow-500 to-orange-500 rounded-lg p-4 text-white shadow-lg">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-2xl font-bold">{abstinencia.toFixed(1)}h</div>
                                        <div className="text-yellow-100 text-sm font-medium">Abstinência</div>
                                    </div>
                                    <div className="text-3xl opacity-80">⚠️</div>
                                </div>
                            </div>
                        )}

                        {extraHours > 0 && (
                            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white shadow-lg">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-2xl font-bold">+{extraHours.toFixed(1)}h</div>
                                        <div className="text-green-100 text-sm font-medium">Hora Extra</div>
                                    </div>
                                    <div className="text-3xl opacity-80">🚀</div>
                                </div>
                            </div>
                        )}

                        {/* Card de Status Geral */}
                        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white shadow-lg">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-base font-bold">
                                        {totalHours >= 8 ? 'Completo' : 'Pendente'}
                                    </div>
                                    <div className="text-purple-100 text-sm font-medium">Status do Dia</div>
                                </div>
                                <div className="text-3xl opacity-80">
                                    {totalHours >= 8 ? '✅' : '⏳'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Botão de Ação Compacto */}
                {apontamentos.length > 0 && user?.privilege_level === 'USER' && (
                    <div className="px-4 py-3 bg-red-50 border-b border-red-200">
                        <div className="flex items-center justify-center">
                            <button
                                onClick={handleDeleteLastOS}
                                className="px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 shadow-lg flex items-center space-x-2"
                            >
                                <span className="text-sm">🗑️</span>
                                <span className="font-semibold text-sm">Excluir Último</span>
                            </button>
                        </div>
                        <p className="text-center text-red-600 text-xs mt-1">
                            ⚠️ Só é possível excluir se o supervisor ainda não aprovou
                        </p>
                    </div>
                )}
                {/* Lista de Apontamentos Compacta */}
                <div className="px-4 py-4">
                    {apontamentos.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4 opacity-50">📋</div>
                            <h3 className="text-xl font-bold text-gray-900 mb-3">Nenhum apontamento encontrado</h3>
                            <p className="text-gray-600 text-base max-w-md mx-auto">
                                {user?.privilege_level === 'USER'
                                    ? 'Você ainda não possui apontamentos para a data selecionada. Comece criando um novo apontamento!'
                                    : 'Não há apontamentos para os filtros aplicados. Tente ajustar os critérios de busca.'
                                }
                            </p>
                            <div className="mt-6">
                                <button
                                    onClick={() => setSelectedDate(new Date().toISOString().split('T')[0])}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                                >
                                    📅 Ver Hoje
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {apontamentos.map((apontamento, index) => (
                                <div key={apontamento.id} className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden">
                                    {/* Header Compacto */}
                                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-3 py-2 border-b border-gray-100">
                                        <div className="flex justify-between items-center">
                                            <div className="flex items-center space-x-2">
                                                <div className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-semibold">
                                                    OS {apontamento.numero_os}
                                                </div>
                                                <div className="flex items-center space-x-1">
                                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColorClass(apontamento.status_apontamento)}`}>
                                                        {apontamento.status_apontamento ? apontamento.status_apontamento.replace('_', ' ') : 'N/A'}
                                                    </span>
                                                    {apontamento.aprovado_supervisor && <span className="px-1 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-700">✅</span>}
                                                    {apontamento.foi_retrabalho && <span className="px-1 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-700">🔄</span>}
                                                    {apontamento.servico_de_campo && <span className="px-1 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-700">🏗️</span>}
                                                </div>
                                            </div>
                                            <div className="text-xs text-gray-600 font-medium">
                                                📅 {apontamento.data_hora_inicio ? formatDate(apontamento.data_hora_inicio) : 'N/A'}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Conteúdo Compacto */}
                                    <div className="p-3">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                            {/* Coluna Esquerda Compacta */}
                                            <div className="space-y-2">
                                                {/* Cliente e Equipamento Compactos */}
                                                <div className="grid grid-cols-1 gap-2">
                                                    <div className="bg-blue-50 rounded p-2 border border-blue-100">
                                                        <div className="flex items-center space-x-1 mb-1">
                                                            <span className="text-blue-600 text-xs">🏢</span>
                                                            <span className="text-xs font-semibold text-blue-800">Cliente</span>
                                                        </div>
                                                        <p className="text-gray-900 text-xs font-medium leading-tight">{apontamento.cliente}</p>
                                                    </div>

                                                    <div className="bg-green-50 rounded p-2 border border-green-100">
                                                        <div className="flex items-center space-x-1 mb-1">
                                                            <span className="text-green-600 text-xs">⚙️</span>
                                                            <span className="text-xs font-semibold text-green-800">Equipamento</span>
                                                        </div>
                                                        <p className="text-gray-900 text-xs font-medium leading-tight">{apontamento.equipamento}</p>
                                                    </div>
                                                </div>

                                                {/* Horários Compactos */}
                                                <div className="bg-purple-50 rounded p-2 border border-purple-100">
                                                    <div className="flex items-center space-x-1 mb-1">
                                                        <span className="text-purple-600 text-xs">⏰</span>
                                                        <span className="text-xs font-semibold text-purple-800">Horários</span>
                                                    </div>
                                                    <div className="flex items-center space-x-3">
                                                        <div>
                                                            <div className="text-xs text-purple-600 font-medium">Início</div>
                                                            <div className="text-gray-900 text-sm font-semibold">{formatTime(apontamento.data_hora_inicio)}</div>
                                                        </div>
                                                        <div>
                                                            <div className="text-xs text-purple-600 font-medium">Fim</div>
                                                            <div className="text-gray-900 text-sm font-semibold">{formatTime(apontamento.data_hora_fim || '')}</div>
                                                        </div>
                                                        {apontamento.tempo_trabalhado && (
                                                            <div className="ml-3 pl-3 border-l border-purple-200">
                                                                <div className="text-xs text-purple-600 font-medium">Tempo</div>
                                                                <div className="text-sm font-bold text-purple-800">{apontamento.tempo_trabalhado.toFixed(1)}h</div>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Coluna Direita Compacta */}
                                            <div className="space-y-2">
                                                {/* Atividades Compactas */}
                                                <div className="bg-orange-50 rounded p-2 border border-orange-100">
                                                    <div className="flex items-center space-x-1 mb-1">
                                                        <span className="text-orange-600 text-xs">📋</span>
                                                        <span className="text-xs font-semibold text-orange-800">Atividades</span>
                                                    </div>
                                                    <div className="space-y-1">
                                                        <div>
                                                            <div className="text-xs text-orange-600 font-medium">Tipo</div>
                                                            <div className="text-gray-900 text-xs font-medium">{apontamento.tipo_atividade}</div>
                                                        </div>
                                                        <div>
                                                            <div className="text-xs text-orange-600 font-medium">Descrição</div>
                                                            <div className="text-gray-900 text-xs font-medium">{apontamento.descricao_atividade}</div>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* Técnico Compacto */}
                                                <div className="bg-indigo-50 rounded p-2 border border-indigo-100">
                                                    <div className="flex items-center space-x-1 mb-1">
                                                        <span className="text-indigo-600 text-xs">👤</span>
                                                        <span className="text-xs font-semibold text-indigo-800">Técnico</span>
                                                    </div>
                                                    <div className="space-y-1">
                                                        <div>
                                                            <div className="text-xs text-indigo-600 font-medium">Nome</div>
                                                            <div className="text-gray-900 text-xs font-medium">{apontamento.nome_tecnico}</div>
                                                        </div>
                                                        <div className="flex items-center space-x-3">
                                                            <div>
                                                                <div className="text-xs text-indigo-600 font-medium">Setor</div>
                                                                <div className="text-gray-900 text-xs font-medium">{apontamento.setor}</div>
                                                            </div>
                                                            <div>
                                                                <div className="text-xs text-indigo-600 font-medium">Depto</div>
                                                                <div className="text-gray-900 text-xs font-medium">{apontamento.departamento}</div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Observações Compactas */}
                                        {(apontamento.observacoes || apontamento.observacao_os || apontamento.causa_retrabalho) && (
                                            <div className="mt-2 pt-2 border-t border-gray-200">
                                                <div className="flex items-center space-x-1 mb-2">
                                                    <span className="text-gray-600 text-xs">📝</span>
                                                    <span className="text-xs font-semibold text-gray-800">Observações</span>
                                                </div>
                                                <div className="space-y-1">
                                                    {apontamento.observacoes && (
                                                        <div className="bg-gray-50 rounded p-1">
                                                            <div className="text-xs text-gray-600 font-medium mb-1">Gerais</div>
                                                            <p className="text-gray-900 text-xs">{apontamento.observacoes}</p>
                                                        </div>
                                                    )}
                                                    {apontamento.observacao_os && (
                                                        <div className="bg-blue-50 rounded p-1">
                                                            <div className="text-xs text-blue-600 font-medium mb-1">OS</div>
                                                            <p className="text-gray-900 text-xs">{apontamento.observacao_os}</p>
                                                        </div>
                                                    )}
                                                    {apontamento.causa_retrabalho && (
                                                        <div className="bg-orange-50 rounded p-1">
                                                            <div className="text-xs text-orange-600 font-medium mb-1">Retrabalho</div>
                                                            <p className="text-gray-900 text-xs">{apontamento.causa_retrabalho}</p>
                                                        </div>
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
            </div>
        </div>
    );
};

export default MinhasOsTab;
