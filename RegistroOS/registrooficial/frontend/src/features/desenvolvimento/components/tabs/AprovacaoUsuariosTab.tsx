import React, { useState, useEffect } from 'react';
import { useSetor } from '../../../../contexts/SetorContext';
import { useAuth } from '../../../../contexts/AuthContext';
import { getStatusColorClass } from '../../../../utils/statusColors'; // Import centralized utility

interface UsuarioPendente {
    id: number;
    nome_completo: string;
    email: string;
    setor: string;
    cargo?: string;
    telefone?: string;
    data_solicitacao: string;
    status: 'PENDENTE' | 'APROVADO' | 'REJEITADO';
    motivo_solicitacao?: string;
    supervisor_solicitante?: string;
}

const AprovacaoUsuariosTab: React.FC = () => {
    const { setorAtivo } = useSetor();
    const { user } = useAuth();
    const [usuariosPendentes, setUsuariosPendentes] = useState<UsuarioPendente[]>([]);
    const [loading, setLoading] = useState(true);
    const [processando, setProcessando] = useState<number | null>(null);
    const [filtroStatus, setFiltroStatus] = useState<string>('PENDENTE');

    useEffect(() => {
        const fetchUsuariosPendentes = async () => {
            if (!setorAtivo) return;

            try {
                setLoading(true);
                // Buscar usuários pendentes de aprovação via API
                const response = await fetch('/api/users/pending-approval', {
                    credentials: 'include'
                });

                if (response.ok) {
                    const usuarios = await response.json();
                    setUsuariosPendentes(usuarios);
                } else {
                    console.error('Erro ao buscar usuários pendentes:', response.status);
                    setUsuariosPendentes([]);
                }
            } catch (error) {
                console.error('Erro ao buscar usuários pendentes:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchUsuariosPendentes();
    }, [setorAtivo]);

    const handleAprovarUsuario = async (usuarioId: number) => {
        setProcessando(usuarioId);
        try {
            // TODO: Implement real API call for approval
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
            
            setUsuariosPendentes(prev =>
                prev.map(usuario =>
                    usuario.id === usuarioId
                        ? { ...usuario, status: 'APROVADO' as const }
                        : usuario
                )
            );
            
            alert('Usuário aprovado com sucesso!');
        } catch (error) {
            console.error('Erro ao aprovar usuário:', error);
            alert('Erro ao aprovar usuário');
        } finally {
            setProcessando(null);
        }
    };

    const handleRejeitarUsuario = async (usuarioId: number) => {
        const motivo = prompt('Digite o motivo da rejeição (opcional):');
        
        setProcessando(usuarioId);
        try {
            // TODO: Implement real API call for rejection
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
            
            setUsuariosPendentes(prev =>
                prev.map(usuario =>
                    usuario.id === usuarioId
                        ? { ...usuario, status: 'REJEITADO' as const }
                        : usuario
                )
            );
            
            alert('Usuário rejeitado.');
        } catch (error) {
            console.error('Erro ao rejeitar usuário:', error);
            alert('Erro ao rejeitar usuário');
        } finally {
            setProcessando(null);
        }
    };


    // Filtrar usuários baseado no privilégio do usuário logado
    const usuariosFiltrados = usuariosPendentes.filter(usuario => {
        // Filtro por status
        if (filtroStatus && usuario.status !== filtroStatus) {
            return false;
        }

        // SUPERVISOR só pode ver usuários do mesmo setor
        if (user?.privilege_level === 'SUPERVISOR') {
            return usuario.setor === user.setor;
        }

        // ADMIN e GESTAO podem ver todos
        return true;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span className="ml-2">Carregando usuários pendentes...</span>
            </div>
        );
    }

    // Check if user has permission to approve users
    const canApproveUsers = user && ['ADMIN', 'GESTAO', 'SUPERVISOR'].includes(user.privilege_level);

    if (!canApproveUsers) {
        return (
            <div className="max-w-6xl mx-auto p-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                    <div className="text-yellow-400 text-5xl mb-3">🔒</div>
                    <h3 className="text-lg font-medium text-yellow-800 mb-2">
                        Acesso Restrito
                    </h3>
                    <p className="text-yellow-700">
                        Você não possui permissão para aprovar usuários. Esta funcionalidade está disponível apenas para Supervisores, Gestores e Administradores.
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
                    Aprovação de Colaboradores - {setorAtivo?.nome}
                </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Gerencie solicitações de acesso ao sistema
                        {user?.privilege_level === 'SUPERVISOR' && (
                            <span className="text-orange-600 font-medium"> (Filtrado por setor: {user.setor})</span>
                        )}
                    </p>
                </div>

                {/* Filtros */}
                <div className="p-6 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Filtrar por Status
                                </label>
                                <select
                                    value={filtroStatus}
                                    onChange={(e) => setFiltroStatus(e.target.value)}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Todos</option>
                                    <option value="PENDENTE">Pendentes</option>
                                    <option value="APROVADO">Aprovados</option>
                                    <option value="REJEITADO">Rejeitados</option>
                                </select>
                            </div>
                        </div>
                        <div className="text-sm text-gray-500">
                            {usuariosFiltrados.length} colaborador(es) encontrado(s)
                        </div>
                    </div>
                </div>

                {/* Lista de Usuários */}
                <div className="p-6">
                    {usuariosFiltrados.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-gray-400 text-6xl mb-4">👥</div>
                            <h3 className="text-lg font-medium text-gray-900 mb-2">
                                Nenhum colaborador encontrado
                            </h3>
                            <p className="text-gray-500">
                                {filtroStatus ? `Não há colaboradores com status "${filtroStatus}"` : 'Não há solicitações de colaboradores pendentes'}
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {usuariosFiltrados.map((usuario) => (
                                <div key={usuario.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex-1">
                                            <div className="flex items-center space-x-3 mb-2">
                                                <h3 className="text-lg font-medium text-gray-900">
                                                    {usuario.nome_completo}
                                                </h3>
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColorClass(usuario.status)}`}>
                                                    {usuario.status}
                                                </span>
                                            </div>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                                                <div>
                                                    <p><span className="font-medium">Email:</span> {usuario.email}</p>
                                                    <p><span className="font-medium">Setor:</span> {usuario.setor}</p>
                                                    <p><span className="font-medium">Cargo:</span> {usuario.cargo || 'Não informado'}</p>
                                                </div>
                                                <div>
                                                    <p><span className="font-medium">Telefone:</span> {usuario.telefone || 'Não informado'}</p>
                                                    <p><span className="font-medium">Data Solicitação:</span> {new Date(usuario.data_solicitacao).toLocaleDateString('pt-BR')}</p>
                                                    <p><span className="font-medium">Solicitante:</span> {usuario.supervisor_solicitante || 'Não informado'}</p>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        {usuario.status === 'PENDENTE' && (
                                            <div className="ml-6 flex space-x-2">
                                                <button
                                                    onClick={() => handleAprovarUsuario(usuario.id)}
                                                    disabled={processando === usuario.id}
                                                    className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
                                                >
                                                    {processando === usuario.id ? '⏳' : '✅'} Aprovar
                                                </button>
                                                <button
                                                    onClick={() => handleRejeitarUsuario(usuario.id)}
                                                    disabled={processando === usuario.id}
                                                    className="px-4 py-2 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 disabled:opacity-50 transition-colors"
                                                >
                                                    {processando === usuario.id ? '⏳' : '❌'} Rejeitar
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                    
                                    {usuario.motivo_solicitacao && (
                                        <div className="border-t border-gray-100 pt-4">
                                            <p className="text-sm">
                                                <span className="font-medium text-gray-700">Motivo da solicitação:</span>
                                                <span className="text-gray-600 ml-1">{usuario.motivo_solicitacao}</span>
                                            </p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AprovacaoUsuariosTab;