import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import api from '../../../../services/api';
import { getStatusColorClass } from '../../../../utils/statusColors'; // Import centralized utility

interface RegistroApontamento {
    id: number;
    numero_os: string;
    funcionario: string;
    tipo_atividade: string;
    data: string;
    hora_inicio: string;
    hora_fim: string;
    horas_trabalhadas: number;
    status: 'PENDENTE_APROVACAO' | 'APROVADO' | 'REJEITADO' | 'EM_ANDAMENTO' | 'CONCLUIDO';
    setor: string;
    cliente: string;
    equipamento: string;
}

const GerenciarTab: React.FC = () => {
    const { setorAtivo } = useSetor();
    const { user } = useAuth();
    const [registros, setRegistros] = useState<RegistroApontamento[]>([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'general' | 'byEmployee'>('general');
    const [selectedEmployee, setSelectedEmployee] = useState<string>('');
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [activeSubTab, setActiveSubTab] = useState<'aprovacao' | 'edicao'>('aprovacao');
    const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
    const [currentRecordForEdit, setCurrentRecordForEdit] = useState<RegistroApontamento | null>(null);
    const [editFormData, setEditFormData] = useState<any>({});
    const [colaboradores, setColaboradores] = useState<any[]>([]);

    // Função para definir cores do status
    const getStatusColorClass = (status: string) => {
        switch (status) {
            case 'APROVADO':
                return 'bg-green-100 text-green-800';
            case 'PENDENTE':
                return 'bg-yellow-100 text-yellow-800';
            case 'REJEITADO':
                return 'bg-red-100 text-red-800';
            case 'FINALIZADO':
                return 'bg-blue-100 text-blue-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    };

    useEffect(() => {
        const fetchRegistros = async () => {
            if (!setorAtivo || !user) return;

            try {
                setLoading(true);

                // Construir parâmetros da consulta
                const params: any = {};

                // Filtros baseados no privilégio do usuário
                if (user.privilege_level === 'SUPERVISOR') {
                    params.setor = user.setor;
                    params.departamento = user.departamento;
                } else if (user.privilege_level === 'GESTAO') {
                    params.departamento = user.departamento;
                }
                // ADMIN pode ver todos os registros (sem filtros)

                // Filtros de data
                if (startDate) params.data_inicio = startDate;
                if (endDate) params.data_fim = endDate;

                // Filtro por funcionário específico
                if (viewMode === 'byEmployee' && selectedEmployee) {
                    params.usuario_id = selectedEmployee;
                }

                console.log('🔍 Buscando apontamentos com parâmetros:', params);

                // Fazer chamada real para a API
                const response = await api.get('/apontamentos-detalhados', { params });

                // Converter dados para o formato esperado
                const registrosConvertidos = response.data.map((apt: any) => ({
                    id: apt.id,
                    numero_os: apt.numero_os || `APT-${apt.id}`,
                    funcionario: apt.nome_tecnico || 'N/A',
                    cliente: apt.cliente || 'Cliente não informado',
                    equipamento: apt.equipamento || 'Equipamento não informado',
                    data: apt.data_hora_inicio ? apt.data_hora_inicio.split('T')[0] : new Date().toISOString().split('T')[0],
                    hora_inicio: apt.data_hora_inicio ? new Date(apt.data_hora_inicio).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : '--',
                    hora_fim: apt.data_fim ? new Date(apt.data_fim).toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}) : '--',
                    horas_trabalhadas: apt.tempo_trabalhado || 0,
                    tipo_atividade: apt.tipo_atividade || 'N/A',
                    descricao_atividade: apt.descricao_atividade || 'N/A',
                    status: apt.aprovado_supervisor ? 'APROVADO' : 'PENDENTE',
                    observacoes: apt.observacoes || apt.observacao_os || '',
                    foi_retrabalho: apt.foi_retrabalho || false,
                    servico_de_campo: apt.servico_de_campo || false,
                    setor: apt.setor || user.setor,
                    departamento: apt.departamento || user.departamento
                }));

                console.log('✅ Registros carregados:', registrosConvertidos.length);
                setRegistros(registrosConvertidos);
            } catch (error) {
                console.error('❌ Erro ao buscar registros:', error);
                setRegistros([]);
            } finally {
                setLoading(false);
            }
        };

        fetchRegistros();
    }, [setorAtivo, user, startDate, endDate, viewMode, selectedEmployee]);

    // Buscar colaboradores baseado no privilégio do usuário
    useEffect(() => {
        const fetchColaboradores = async () => {
            if (!user) return;

            try {
                console.log('🔍 Buscando colaboradores...');

                // Buscar usuários baseado no privilégio
                const response = await api.get('/users/usuarios/');

                // Filtrar colaboradores baseado no privilégio do usuário
                let colaboradoresFiltrados = response.data;

                if (user.privilege_level === 'SUPERVISOR') {
                    // Supervisor vê apenas do seu setor
                    colaboradoresFiltrados = response.data.filter((colab: any) =>
                        colab.setor === user.setor && colab.departamento === user.departamento
                    );
                } else if (user.privilege_level === 'GESTAO') {
                    // Gestão vê apenas do seu departamento
                    colaboradoresFiltrados = response.data.filter((colab: any) =>
                        colab.departamento === user.departamento
                    );
                }
                // ADMIN vê todos (sem filtro)

                console.log('✅ Colaboradores carregados:', colaboradoresFiltrados.length);
                setColaboradores(colaboradoresFiltrados);
            } catch (error) {
                console.error('❌ Erro ao buscar colaboradores:', error);
                setColaboradores([]);
            }
        };

        fetchColaboradores();
    }, [user]);

    const handleApproveRecord = async (recordId: number) => {
        try {
            console.log('🔍 Aprovando registro:', recordId);

            // Fazer chamada real para a API de aprovação
            const response = await api.put(`/desenvolvimento/apontamentos/${recordId}/aprovar`, {
                aprovado_supervisor: true,
                data_aprovacao_supervisor: new Date().toISOString(),
                supervisor_aprovacao: user?.nome_completo || user?.primeiro_nome
            });

            // Atualizar estado local
            setRegistros(prev =>
                prev.map(record =>
                    record.id === recordId
                        ? { ...record, status: 'APROVADO' as const }
                        : record
                )
            );

            console.log('✅ Registro aprovado com sucesso');

            // Verificar se houve aprovação automática de programação
            let mensagem = 'Apontamento aprovado com sucesso!';
            if (response.data.programacao_aprovada) {
                mensagem += `\n🎯 Programação OS ${response.data.programacao_aprovada.os_numero} aprovada automaticamente!`;
            }

            alert(mensagem);
        } catch (error) {
            console.error('❌ Erro ao aprovar registro:', error);
            alert('Erro ao aprovar registro. Verifique suas permissões.');
        }
    };

    const handleRejectRecord = async (recordId: number) => {
        const motivo = prompt('Digite o motivo da rejeição (opcional):');

        try {
            console.log('🔍 Rejeitando registro:', recordId, 'Motivo:', motivo);

            // Fazer chamada real para a API de rejeição
            await api.put(`/desenvolvimento/apontamentos/${recordId}/rejeitar`, {
                aprovado_supervisor: false,
                motivo_rejeicao: motivo || 'Rejeitado pelo supervisor',
                supervisor_aprovacao: user?.nome_completo || user?.primeiro_nome
            });

            // Atualizar estado local
            setRegistros(prev =>
                prev.map(record =>
                    record.id === recordId
                        ? { ...record, status: 'REJEITADO' as const }
                        : record
                )
            );

            console.log('✅ Registro rejeitado com sucesso');
            alert('Registro rejeitado.');
        } catch (error) {
            console.error('❌ Erro ao rejeitar registro:', error);
            alert('Erro ao rejeitar registro. Verifique suas permissões.');
        }
    };

    const handleEditRecord = (record: RegistroApontamento) => {
        setCurrentRecordForEdit(record);
        setEditFormData({
            numero_os: record.numero_os,
            funcionario: record.funcionario,
            tipo_atividade: record.tipo_atividade,
            data: record.data,
            hora_inicio: record.hora_inicio,
            hora_fim: record.hora_fim,
            cliente: record.cliente,
            equipamento: record.equipamento
        });
        setIsEditModalOpen(true);
    };

    const handleSaveEditedRecord = async () => {
        if (!currentRecordForEdit) return;

        try {
            console.log('🔍 Salvando edição do registro:', currentRecordForEdit.id);

            // Calcular horas trabalhadas
            const inicio = new Date(`2025-01-01T${editFormData.hora_inicio}`);
            const fim = new Date(`2025-01-01T${editFormData.hora_fim}`);
            const horasTrabalhadas = (fim.getTime() - inicio.getTime()) / (1000 * 60 * 60);

            // Preparar dados para envio
            const updateData = {
                data_hora_inicio: `${editFormData.data}T${editFormData.hora_inicio}:00`,
                data_hora_fim: editFormData.hora_fim ? `${editFormData.data}T${editFormData.hora_fim}:00` : null,
                tempo_trabalhado: horasTrabalhadas,
                observacoes: editFormData.observacoes || '',
                tipo_atividade: editFormData.tipo_atividade || '',
                descricao_atividade: editFormData.descricao_atividade || ''
            };

            console.log('📤 Dados para atualização:', updateData);

            // Fazer chamada real para a API
            await api.put(`/desenvolvimento/apontamentos/${currentRecordForEdit.id}/editar`, updateData);

            // Atualizar estado local
            setRegistros(prev =>
                prev.map(record =>
                    record.id === currentRecordForEdit.id
                        ? {
                            ...record,
                            ...editFormData,
                            horas_trabalhadas: horasTrabalhadas,
                            hora_inicio: editFormData.hora_inicio,
                            hora_fim: editFormData.hora_fim || '--'
                        }
                        : record
                )
            );

            setIsEditModalOpen(false);
            setCurrentRecordForEdit(null);
            setEditFormData({});

            console.log('✅ Registro atualizado com sucesso');
            alert('Registro atualizado com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao salvar registro:', error);
            alert('Erro ao salvar registro. Verifique suas permissões.');
        }
    };


    // Filter records
    const filteredRecords = registros.filter(record => {
        let matches = true;

        // Filter by employee
        if (viewMode === 'byEmployee' && selectedEmployee) {
            matches = matches && record.funcionario === selectedEmployee;
        }

        // Filter by date range
        if (startDate && endDate) {
            const recordDate = new Date(record.data);
            const filterStartDate = new Date(startDate);
            const filterEndDate = new Date(endDate);
            matches = matches && recordDate >= filterStartDate && recordDate <= filterEndDate;
        }

        return matches;
    });

    const totalHours = filteredRecords.reduce((sum, record) => sum + record.horas_trabalhadas, 0);
    const completedTasks = filteredRecords.filter(record => ['APROVADO', 'CONCLUIDO'].includes(record.status)).length;
    const avgHoursPerTask = filteredRecords.length > 0 ? (totalHours / filteredRecords.length).toFixed(1) : '0';

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2">Carregando registros...</span>
            </div>
        );
    }

    // Check if user can manage records
    const canManageRecords = user && ['ADMIN', 'GESTAO', 'SUPERVISOR'].includes(user.privilege_level);

    if (!canManageRecords) {
        return (
            <div className="max-w-6xl mx-auto p-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                    <div className="text-yellow-400 text-5xl mb-3">🔒</div>
                    <h3 className="text-lg font-medium text-yellow-800 mb-2">
                        Acesso Restrito
                    </h3>
                    <p className="text-yellow-700">
                        Você não possui permissão para gerenciar registros. Esta funcionalidade está disponível apenas para Supervisores, Gestores e Administradores.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full p-6">
            <div className="bg-white rounded-lg shadow-sm">
                <div className="p-6 border-b border-gray-200">
                    <h2 className="text-xl font-semibold text-gray-900">
                        Gerenciar Registros - {setorAtivo?.nome}
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Visualize e gerencie registros de apontamentos por período e colaborador
                    </p>
                </div>

                {/* Sub-tabs */}
                <div className="border-b border-gray-200">
                    <nav className="flex space-x-8 px-6">
                        <button
                            onClick={() => setActiveSubTab('aprovacao')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                activeSubTab === 'aprovacao'
                                    ? 'border-green-500 text-green-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            ✅ Aprovação
                        </button>
                        <button
                            onClick={() => setActiveSubTab('edicao')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm ${
                                activeSubTab === 'edicao'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            ✏️ Edição
                        </button>
                    </nav>
                </div>

                {/* Filters */}
                <div className="p-6 border-b border-gray-200 bg-gray-50">
                    <h4 className="font-medium text-gray-900 mb-4">Filtros</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Data Início</label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Data Fim</label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Modo de Visualização</label>
                            <select
                                value={viewMode}
                                onChange={(e) => setViewMode(e.target.value as 'general' | 'byEmployee')}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="general">Geral por Setor</option>
                                <option value="byEmployee">Por Colaborador</option>
                            </select>
                        </div>
                        {viewMode === 'byEmployee' && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Colaborador</label>
                                <select
                                    value={selectedEmployee}
                                    onChange={(e) => setSelectedEmployee(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Selecionar Colaborador</option>
                                    {colaboradores.map(colaborador => (
                                        <option key={colaborador.id} value={colaborador.id}>
                                            {colaborador.nome_completo || colaborador.primeiro_nome} - {colaborador.setor}
                                        </option>
                                    ))}
                                </select>
                                <p className="text-xs text-gray-500 mt-1">
                                    {colaboradores.length} colaborador(es) disponível(eis)
                                </p>
                            </div>
                        )}
                    </div>
                    <div className="flex items-center justify-between">
                        <button
                            onClick={() => {
                                setStartDate('');
                                setEndDate('');
                                setSelectedEmployee('');
                            }}
                            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                        >
                            Limpar Filtros
                        </button>
                        <div className="text-sm text-gray-500">
                            {filteredRecords.length} registro(s) encontrado(s)
                        </div>
                    </div>
                </div>

                {/* Statistics */}
                <div className="p-6 border-b border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <h4 className="font-medium text-blue-900">Total de Horas</h4>
                            <div className="text-2xl font-bold text-blue-600">{totalHours.toFixed(1)}h</div>
                            <p className="text-sm text-blue-700">Período filtrado</p>
                        </div>
                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <h4 className="font-medium text-green-900">Tarefas Aprovadas</h4>
                            <div className="text-2xl font-bold text-green-600">{completedTasks}</div>
                            <p className="text-sm text-green-700">De {filteredRecords.length} registros</p>
                        </div>
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <h4 className="font-medium text-purple-900">Média por Tarefa</h4>
                            <div className="text-2xl font-bold text-purple-600">{avgHoursPerTask}h</div>
                            <p className="text-sm text-purple-700">Horas trabalhadas</p>
                        </div>
                    </div>
                </div>

                {/* Records Table */}
                <div className="p-6">
                    {filteredRecords.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">📋</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                Nenhum registro encontrado
                            </h3>
                            <p className="text-gray-500">
                                Ajuste os filtros para ver os registros disponíveis
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OS</th>
                                        {viewMode === 'general' && <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Funcionário</th>}
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Atividade</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Início</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fim</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Horas</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {filteredRecords.map((record) => (
                                        <tr key={record.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {record.numero_os}
                                            </td>
                                            {viewMode === 'general' && (
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {record.funcionario}
                                                </td>
                                            )}
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 max-w-xs truncate" title={record.cliente}>
                                                {record.cliente}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                <div className="max-w-xs truncate" title={record.descricao_atividade}>
                                                    <div className="font-medium">{record.tipo_atividade}</div>
                                                    <div className="text-xs text-gray-500">{record.descricao_atividade}</div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {new Date(record.data).toLocaleDateString('pt-BR')}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                <span className="font-mono text-xs bg-blue-50 px-2 py-1 rounded">
                                                    {record.hora_inicio}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                <span className="font-mono text-xs bg-blue-50 px-2 py-1 rounded">
                                                    {record.hora_fim}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                <span className="font-semibold text-blue-600">
                                                    {record.horas_trabalhadas.toFixed(1)}h
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColorClass(record.status)}`}>
                                                    {record.status.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <div className="flex space-x-2">
                                                    {activeSubTab === 'aprovacao' && record.status === 'PENDENTE' && (
                                                        <>
                                                            <button
                                                                onClick={() => handleApproveRecord(record.id)}
                                                                className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 text-xs font-medium transition-colors"
                                                                title="Aprovar apontamento"
                                                            >
                                                                ✅ Aprovar
                                                            </button>
                                                            <button
                                                                onClick={() => handleRejectRecord(record.id)}
                                                                className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 text-xs font-medium transition-colors"
                                                                title="Rejeitar apontamento"
                                                            >
                                                                ❌ Rejeitar
                                                            </button>
                                                        </>
                                                    )}
                                                    {activeSubTab === 'edicao' && record.status !== 'APROVADO' && (
                                                        <button
                                                            onClick={() => handleEditRecord(record)}
                                                            className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-xs font-medium transition-colors"
                                                            title="Editar apontamento"
                                                        >
                                                            ✏️ Editar
                                                        </button>
                                                    )}
                                                    {activeSubTab === 'edicao' && record.status === 'APROVADO' && (
                                                        <span className="px-3 py-1 text-xs bg-gray-100 text-gray-500 rounded cursor-not-allowed" title="Apontamento aprovado não pode ser editado">
                                                            🔒 Aprovado
                                                        </span>
                                                    )}
                                                    {record.foi_retrabalho && (
                                                        <span className="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full">
                                                            🔄 Retrabalho
                                                        </span>
                                                    )}
                                                    {record.servico_de_campo && (
                                                        <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded-full">
                                                            🏗️ Campo
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            {/* Edit Modal */}
            {isEditModalOpen && currentRecordForEdit && (
                <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center">
                    <div className="bg-white p-8 rounded-lg shadow-xl max-w-2xl w-full mx-4">
                        <h3 className="text-lg font-semibold mb-4">Editar Apontamento - {setorAtivo?.nome}</h3>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Número OS</label>
                                <input
                                    type="text"
                                    value={editFormData.numero_os || ''}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
                                    disabled
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    ⚠️ O número da OS não pode ser alterado
                                </p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Funcionário</label>
                                <select
                                    value={editFormData.funcionario || ''}
                                    onChange={(e) => setEditFormData({...editFormData, funcionario: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    disabled
                                >
                                    <option value={editFormData.funcionario || ''}>
                                        {editFormData.funcionario || 'Funcionário não informado'}
                                    </option>
                                </select>
                                <p className="text-xs text-gray-500 mt-1">
                                    ⚠️ O funcionário não pode ser alterado
                                </p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Data</label>
                                <input
                                    type="date"
                                    value={editFormData.data || ''}
                                    onChange={(e) => setEditFormData({...editFormData, data: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Atividade</label>
                                <input
                                    type="text"
                                    value={editFormData.tipo_atividade || ''}
                                    onChange={(e) => setEditFormData({...editFormData, tipo_atividade: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Hora Início</label>
                                <input
                                    type="time"
                                    value={editFormData.hora_inicio || ''}
                                    onChange={(e) => setEditFormData({...editFormData, hora_inicio: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Hora Fim</label>
                                <input
                                    type="time"
                                    value={editFormData.hora_fim || ''}
                                    onChange={(e) => setEditFormData({...editFormData, hora_fim: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Descrição da Atividade</label>
                                <input
                                    type="text"
                                    value={editFormData.descricao_atividade || ''}
                                    onChange={(e) => setEditFormData({...editFormData, descricao_atividade: e.target.value})}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Ex: SVC - SERVICO DE CAMPO"
                                />
                            </div>
                        </div>

                        {/* Observações */}
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Observações</label>
                            <textarea
                                value={editFormData.observacoes || ''}
                                onChange={(e) => setEditFormData({...editFormData, observacoes: e.target.value})}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                rows={3}
                                placeholder="Observações sobre o apontamento..."
                            />
                        </div>

                        {/* Informações calculadas */}
                        <div className="bg-gray-50 rounded-lg p-4 mb-4">
                            <h4 className="text-sm font-medium text-gray-700 mb-2">Informações Calculadas</h4>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-600">Horas Trabalhadas:</span>
                                    <span className="ml-2 font-semibold text-blue-600">
                                        {editFormData.hora_inicio && editFormData.hora_fim ?
                                            (() => {
                                                const inicio = new Date(`2025-01-01T${editFormData.hora_inicio}`);
                                                const fim = new Date(`2025-01-01T${editFormData.hora_fim}`);
                                                const horas = (fim.getTime() - inicio.getTime()) / (1000 * 60 * 60);
                                                return `${horas.toFixed(1)}h`;
                                            })() : '--'
                                        }
                                    </span>
                                </div>
                                <div>
                                    <span className="text-gray-600">Serviço de Campo:</span>
                                    <span className="ml-2 font-semibold">
                                        {editFormData.descricao_atividade &&
                                         (editFormData.descricao_atividade.toUpperCase().includes('SERVICO DE CAMPO') ||
                                          editFormData.descricao_atividade.toUpperCase().includes('SVC')) ?
                                            <span className="text-purple-600">✅ Sim</span> :
                                            <span className="text-gray-500">❌ Não</span>
                                        }
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={() => setIsEditModalOpen(false)}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleSaveEditedRecord}
                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                            >
                                Salvar Alterações
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GerenciarTab;
