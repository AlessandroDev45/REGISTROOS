import React, { useState, useEffect } from 'react';
import api from '../../../../services/api';
import useAuth from '../../../../hooks/useAuth';

interface PendingUser {
  id: number;
  nome_completo: string;
  email: string;
  setor: string;
  status: string;
  privilege_level: string;
  trabalha_producao: boolean;
}

const AprovacaoColaboradoresTab = () => {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const fetchPending = async () => {
      try {
        const response = await api.get('/users/pending-approval');
        const users = response.data;
        setPendingUsers(users);
        setPendingCount(users.length);
        console.log('Pendentes para admin:', users);
      } catch (error) {
        console.error('Erro ao buscar pendentes:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user && user.privilege_level === 'ADMIN') {
      fetchPending();
    }
  }, [user]);

  const approveUser = async (id: number) => {
    try {
      await api.put(`/users/usuarios/${id}/approve`, { privilege_level: 'USER', trabalha_producao: true });
      setPendingUsers(prev => {
        const updated = prev.filter(u => u.id !== id);
        setPendingCount(updated.length);
        return updated;
      });
      console.log('Usuário aprovado:', id);
    } catch (error) {
      console.error('Erro ao aprovar:', error);
    }
  };

  const rejectUser = async (id: number) => {
    try {
      await api.put(`/users/usuarios/${id}/reject`);
      setPendingUsers(prev => {
        const updated = prev.filter(u => u.id !== id);
        setPendingCount(updated.length);
        return updated;
      });
      console.log('Usuário rejeitado:', id);
    } catch (error) {
      console.error('Erro ao rejeitar:', error);
    }
  };

  if (loading) return <p>Carregando colaboradores pendentes...</p>;

  return (
    <div className="p-4">
      <div className="mb-4">
        <h2 className="text-xl font-bold">📋 Aprovação de Colaboradores</h2>
        <p className="text-gray-600">Administração de Colaboradores - Gerencie usuários, aprovações e cadastros</p>
        {pendingCount > 0 && (
          <div className="mt-2 p-3 bg-yellow-100 border border-yellow-400 rounded text-yellow-800">
            ⚠️ Atenção! Você tem {pendingCount} colaborador(es) pendente(s) de aprovação.
          </div>
        )}
      </div>
      <div className="mb-4 space-y-1">
        <h3 className="font-medium">Colaboradores Pendentes de Aprovação</h3>
        {pendingUsers.length === 0 ? (
          <p className="text-gray-500">Não há colaboradores pendentes de aprovação.</p>
        ) : (
          <table className="min-w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-gray-50">
                <th className="border border-gray-300 px-4 py-2 text-left">Nome</th>
                <th className="border border-gray-300 px-4 py-2 text-left">E-mail</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Setor</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Status</th>
                <th className="border border-gray-300 px-4 py-2 text-left">Ações</th>
              </tr>
            </thead>
            <tbody>
              {pendingUsers.map((pendingUser: PendingUser) => (
                <tr key={pendingUser.id} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2">{pendingUser.nome_completo}</td>
                  <td className="border border-gray-300 px-4 py-2">{pendingUser.email}</td>
                  <td className="border border-gray-300 px-4 py-2">{pendingUser.setor || '-'}</td>
                  <td className="border border-gray-300 px-4 py-2">
                    <span className="bg-yellow-200 text-yellow-800 px-2 py-1 rounded text-sm">Pendente</span>
                  </td>
                  <td className="border border-gray-300 px-4 py-2">
                    <button
                      onClick={() => approveUser(pendingUser.id)}
                      className="mr-2 bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                    >
                      Aprovar
                    </button>
                    <button
                      onClick={() => rejectUser(pendingUser.id)}
                      className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                    >
                      Rejeitar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default AprovacaoColaboradoresTab;
