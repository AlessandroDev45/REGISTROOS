import React, { useState, useEffect } from 'react';
import api from '../../../../services/api';
import useAuth from '../../../../hooks/useAuth';
import { useSetor } from '../../../../contexts/SetorContext';

interface PendingUser {
  id: number;
  nome_completo: string;
  email: string;
  setor: string;
  privilege_level: string;
  trabalha_producao: boolean;
}

const AprovacaoUsuariosTab = () => {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { configuracaoAtual } = useSetor();

  useEffect(() => {
    const fetchPending = async () => {
      try {
        const response = await api.get('/users/pending-approval');
        setPendingUsers(response.data);
        console.log('Pendentes:', response.data); // Debug
      } catch (error) {
        console.error('Erro:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user && user.privilege_level === 'SUPERVISOR') {
      fetchPending();
    }
  }, [user]);

  const approveUser = async (id: number) => {
    try {
      await api.put(`/users/usuarios/${id}/approve`, { privilege_level: 'USER', trabalha_producao: true });
      setPendingUsers(prev => prev.filter((u: PendingUser) => u.id !== id));
    } catch (error) {
      console.error('Erro aprovar:', error);
    }
  };

  const rejectUser = async (id: number) => {
    try {
      await api.put(`/users/usuarios/${id}/reject`);
      setPendingUsers(prev => prev.filter((u: PendingUser) => u.id !== id));
    } catch (error) {
      console.error('Erro rejeitar:', error);
    }
  };

  if (loading) return <p>Carregando...</p>;

  return (
    <div className="p-4">
      <h2>Aprovação de Colaboradores - {configuracaoAtual?.NomeSetor}</h2>
      <p>Gerencie solicitações (Filtrado por setor: {configuracaoAtual?.NomeSetor})</p>
      {pendingUsers.length === 0 ? (
        <div className="p-4 bg-gray-100 rounded">
          <p>0 colaborador(es) encontrado(s)</p>
          <p>Nenhum colaborador encontrado</p>
          <p>Não há solicitações de colaboradores pendentes</p>
        </div>
      ) : (
        <table className="min-w-full border">
          <thead>
            <tr>
              <th className="border px-4 py-2">Nome</th>
              <th className="border px-4 py-2">Email</th>
              <th className="border px-4 py-2">Setor</th>
              <th className="border px-4 py-2">Ações</th>
            </tr>
          </thead>
          <tbody>
            {pendingUsers.map((user: PendingUser) => (
              <tr key={user.id}>
                <td className="border px-4 py-2">{user.nome_completo}</td>
                <td className="border px-4 py-2">{user.email}</td>
                <td className="border px-4 py-2">{user.setor || 'N/A'}</td>
                <td className="border px-4 py-2">
                  <button onClick={() => approveUser(user.id)} className="mr-2 bg-green-500 text-white p-2 rounded">Aprovar</button>
                  <button onClick={() => rejectUser(user.id)} className="bg-red-500 text-white p-2 rounded">Rejeitar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AprovacaoUsuariosTab;
