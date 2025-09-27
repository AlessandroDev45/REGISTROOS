import React, { useState, useEffect } from 'react';
import { useSetor } from 'contexts/SetorContext';
import { useAuth } from 'contexts/AuthContext';
import api from '../../services/api';
import Layout from '../../components/Layout';
import { useCachedSetores } from '../../hooks/useCachedSetores';
import { getStatusColorClass } from '../../utils/statusColors';
import { formatarTextoInput, criarHandlerTextoValidado } from '../../utils/textValidation';
import EditUserModal from './components/EditUserModal';

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
   privilege_level?: string;
}

interface Usuario {
    id: number;
    nome_completo: string;
    email: string;
    matricula?: string;
    cargo?: string;
    setor: string;
    departamento: string;
    privilege_level: string;
    trabalha_producao: boolean;
    is_approved: boolean;
    status?: string;
}

interface NovoUsuario {
   nome_completo: string;
   email: string;
   senha: string;
   matricula?: string;
   setor: string;
   departamento?: string;
   cargo?: string;
   privilege_level: string;
   trabalha_producao: boolean;
}

interface Setor {
    id: number;
    nome: string;
    descricao: string;
    id_departamento: number;
    ativo: boolean;
    data_criacao: string;
}

const Administrador: React.FC = () => {
   const [setores, setSetores] = useState<Setor[]>([]);
   const [loadingSetores, setLoadingSetores] = useState(false);
   const { setorAtivo } = useSetor();
   const { user } = useAuth();
   const [usuariosPendentes, setUsuariosPendentes] = useState<UsuarioPendente[]>([]);
   const [todosUsuarios, setTodosUsuarios] = useState<Usuario[]>([]);
   const [loading, setLoading] = useState(true);
   const [processando, setProcessando] = useState<number | null>(null);
   const [activeTab, setActiveTab] = useState<'aprovacao' | 'gerenciar' | 'novo'>('aprovacao');
   const [showForm, setShowForm] = useState(false);
   const [showEditModal, setShowEditModal] = useState(false);
   const [editingUser, setEditingUser] = useState<Usuario | null>(null);
   const [savingUser, setSavingUser] = useState(false);
   const [novoUsuario, setNovoUsuario] = useState<NovoUsuario>({
       nome_completo: '',
       email: '',
       senha: '',
       matricula: '',
       setor: '',
       departamento: 'MOTORES',
       cargo: '',
       privilege_level: 'USER',
       trabalha_producao: false
   });

   const carregarSetores = async (departamento: string) => {
       try {
           setLoadingSetores(true);
           const response = await api.get('/setores', {
               params: { departamento }
           });
           setSetores(response.data);
       } catch (error: any) {
           console.error('Erro ao carregar setores:', error);
           setSetores([]);
       } finally {
           setLoadingSetores(false);
       }
   };

   useEffect(() => {
       if (novoUsuario.departamento) {
           carregarSetores(novoUsuario.departamento);
       }
   }, [novoUsuario.departamento]);

   useEffect(() => {
       const fetchData = async () => {
           try {
               setLoading(true);
               console.log('🔍 Buscando dados de colaboradores...');

               // Fetch pending users
               console.log('📋 Buscando usuários pendentes...');
               const pendingResponse = await api.get('/users/pending-approval');
               console.log('✅ Usuários pendentes encontrados:', pendingResponse.data.length);
               setUsuariosPendentes(pendingResponse.data);

               // Fetch all users
               console.log('👥 Buscando todos os usuários...');
               const allResponse = await api.get('/users/usuarios/');
               console.log('✅ Todos os usuários encontrados:', allResponse.data.length);
               setTodosUsuarios(allResponse.data);

           } catch (error: any) {
               console.error('❌ Erro ao buscar dados:', error);
               // Tentar endpoints alternativos se o principal falhar
               try {
                   console.log('🔄 Tentando endpoint alternativo para usuários pendentes...');
                   const altPendingResponse = await api.get('/admin/usuarios-pendentes');
                   setUsuariosPendentes(altPendingResponse.data);
                   console.log('✅ Usuários pendentes encontrados via endpoint alternativo:', altPendingResponse.data.length);
               } catch (altError: any) {
                   console.error('❌ Erro no endpoint alternativo:', altError);
               }
           } finally {
               setLoading(false);
           }
       };

       fetchData();
   }, []); // Removido setorAtivo da dependência para sempre executar

   const handleAprovarUsuario = async (usuario: UsuarioPendente) => {
       setProcessando(usuario.id);
       try {
           const response = await api.put(`/users/usuarios/${usuario.id}/approve`, {
               privilege_level: usuario.privilege_level || 'USER',
               trabalha_producao: false
           });

           setUsuariosPendentes(prev =>
               prev.filter(u => u.id !== usuario.id)
           );

           // Update all users list
           setTodosUsuarios(prev =>
               prev.map(u =>
                   u.id === usuario.id
                       ? { ...u, status: 'APROVADO' as const, privilege_level: usuario.privilege_level || 'USER' }
                       : u
               )
           );

           alert('Usuário aprovado com sucesso!');
       } catch (error: any) {
           console.error('Erro ao aprovar usuário:', error);
           alert('Erro ao aprovar usuário');
       } finally {
           setProcessando(null);
       }
   };

   const handleReprovarUsuario = async (usuarioId: number) => {
       const motivo = prompt('Digite o motivo da reprovação (opcional):');

       setProcessando(usuarioId);
       try {
           const response = await api.put(`/users/usuarios/${usuarioId}/reject`, {
               motivo: motivo || 'Reprovado por administrador'
           });

           setUsuariosPendentes(prev =>
               prev.filter(u => u.id !== usuarioId)
           );

           setTodosUsuarios(prev =>
               prev.map(u =>
                   u.id === usuarioId
                       ? { ...u, status: 'REJEITADO' as const }
                       : u
               )
           );

           alert('Usuário reprovado.');
       } catch (error: any) {
           console.error('Erro ao reprovar usuário:', error);
           alert('Erro ao reprovar usuário');
       } finally {
           setProcessando(null);
       }
   };

   const handleCreateUser = async () => {
       try {
           // Preparar dados para o endpoint correto
           const userData = {
               nome_completo: novoUsuario.nome_completo,
               email: novoUsuario.email,
               matricula: novoUsuario.matricula || '',
               setor: novoUsuario.setor,
               departamento: novoUsuario.departamento || 'MOTORES', // Valor padrão
               cargo: novoUsuario.cargo || '',
               privilege_level: novoUsuario.privilege_level,
               trabalha_producao: novoUsuario.trabalha_producao
           };

           const response = await api.post('/admin/usuarios', userData);

           // Mostrar senha temporária gerada
           if (response.data.senha_temporaria) {
               alert(`Usuário criado com sucesso!\nSenha temporária: ${response.data.senha_temporaria}\n${response.data.instrucoes}`);
           } else {
               alert('Usuário criado com sucesso!');
           }

           // Refresh users list
           const allResponse = await api.get('/users/usuarios/');
           setTodosUsuarios(allResponse.data);

           // Reset form
           setNovoUsuario({
               nome_completo: '',
               email: '',
               senha: '',
               matricula: '',
               setor: '',
               departamento: 'MOTORES',
               cargo: '',
               privilege_level: 'USER',
               trabalha_producao: false
           });
           setShowForm(false);

       } catch (error: any) {
           console.error('Erro ao criar usuário:', error);
           const errorMessage = error.response?.data?.detail || 'Erro ao criar usuário';
           alert(errorMessage);
       }
   };

   const handleEditUser = (usuario: Usuario) => {
       setEditingUser(usuario);
       setShowEditModal(true);
   };

   const handleSaveUser = async (userData: Partial<Usuario>) => {
       if (!editingUser) return;

       setSavingUser(true);
       try {
           const response = await api.put(`/admin/usuarios/${editingUser.id}`, userData);

           // Update the user in the list
           setTodosUsuarios(prev =>
               prev.map(u =>
                   u.id === editingUser.id
                       ? { ...u, ...userData }
                       : u
               )
           );

           alert('Usuário atualizado com sucesso!');
       } catch (error: any) {
           console.error('Erro ao atualizar usuário:', error);
           const errorMessage = error.response?.data?.detail || 'Erro ao atualizar usuário';
           alert(errorMessage);
           throw error; // Re-throw to let modal handle it
       } finally {
           setSavingUser(false);
       }
   };

   const getStatusColor = (status: string) => {
       switch (status) {
           case 'PENDENTE': return 'bg-yellow-100 text-yellow-800';
           case 'APROVADO': return 'bg-green-100 text-green-800';
           case 'REJEITADO': return 'bg-red-100 text-red-800';
           default: return 'bg-gray-100 text-gray-800';
       }
   };

   if (loading) {
       return (
           <Layout>
               <div className="flex items-center justify-center p-8">
                   <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                   <span className="ml-2">Carregando dados...</span>
               </div>
           </Layout>
       );
   }

   // Check if user has permission to approve users
   const canApproveUsers = user && ['ADMIN', 'GESTAO', 'SUPERVISOR'].includes(user.privilege_level || '');

   if (!canApproveUsers) {
       return (
           <Layout>
               <div className="max-w-6xl mx-auto p-4 md:p-6 lg:p-8">
                   <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                       <div className="text-yellow-400 text-5xl mb-3">🔒</div>
                       <h3 className="text-lg font-medium text-yellow-800 mb-2">
                           Acesso Restrito
                       </h3>
                       <p className="text-yellow-700">
                           Você não possui permissão para gerenciar usuários. Esta funcionalidade está disponível apenas para Administradores, Supervisores e Gestores.
                       </p>
                   </div>
               </div>
           </Layout>
       );
   }

   return (
       <Layout>
            <div className="w-full p-4 md:p-6 lg:p-8">
                <h1 className="text-2xl font-bold text-gray-800 mb-6">Sistema de Administração de Colaboradores</h1>

               {/* Sistema de Notificações */}
               {usuariosPendentes.length > 0 && (
                   <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-r-lg">
                       <div className="flex">
                           <div className="flex-shrink-0">
                               <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                   <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                               </svg>
                           </div>
                           <div className="ml-3">
                               <p className="text-sm text-yellow-700">
                                   <strong>⚠️ Atenção!</strong> Você tem <span className="font-bold">{usuariosPendentes.length}</span> colaborador(es) pendente(s) de aprovação.
                                   <button
                                       onClick={() => setActiveTab('aprovacao')}
                                       className="ml-2 font-medium underline hover:text-yellow-800 transition-colors"
                                   >
                                       Ver usuários pendentes →
                                   </button>
                               </p>
                           </div>
                       </div>
                   </div>
               )}

               <div className="bg-white rounded-lg shadow-sm">
                   <div className="p-6 border-b border-gray-200">
                       <h2 className="text-xl font-semibold text-gray-900">
                           Administração de Colaboradores - {setorAtivo?.nome}
                       </h2>
                       <p className="text-sm text-gray-600 mt-1">
                           Gerencie usuários, aprovações e cadastros
                       </p>
                   </div>

                   {/* Tabs */}
                   <div className="border-b border-gray-200">
                       <nav className="-mb-px flex">
                           <button
                               onClick={() => setActiveTab('aprovacao')}
                               className={`py-4 px-6 border-b-2 font-medium text-sm ${
                                   activeTab === 'aprovacao'
                                       ? 'border-blue-500 text-blue-600'
                                       : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                               }`}
                           >
                               📋 Aprovação de Colaboradores
                           </button>
                           <button
                               onClick={() => setActiveTab('gerenciar')}
                               className={`py-4 px-6 border-b-2 font-medium text-sm ${
                                   activeTab === 'gerenciar'
                                       ? 'border-blue-500 text-blue-600'
                                       : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                               }`}
                           >
                               👥 Gerenciar Colaboradores
                           </button>
                           <button
                               onClick={() => setActiveTab('novo')}
                               className={`py-4 px-6 border-b-2 font-medium text-sm ${
                                   activeTab === 'novo'
                                       ? 'border-blue-500 text-blue-600'
                                       : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                               }`}
                           >
                               ➕ Novo Colaborador
                           </button>
                       </nav>
                   </div>

                   <div className="p-6">
                       {activeTab === 'aprovacao' && (
                           <>
                               <h3 className="text-lg font-medium text-gray-900 mb-4">Colaboradores Pendentes de Aprovação</h3>
                               {usuariosPendentes.length === 0 ? (
                                   <div className="text-center py-12">
                                       <div className="text-gray-400 text-6xl mb-4">✅</div>
                                       <h3 className="text-lg font-medium text-gray-900 mb-2">
                                           Nenhum colaborador pendente
                                       </h3>
                                       <p className="text-gray-500">
                                           Todos os usuários foram processados
                                       </p>
                                   </div>
                               ) : (
                                   <table className="min-w-full divide-y divide-gray-200">
                                       <thead className="bg-gray-50">
                                           <tr>
                                               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                                               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">E-mail</th>
                                               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Setor</th>
                                               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                                           </tr>
                                       </thead>
                                       <tbody className="bg-white divide-y divide-gray-200">
                                           {usuariosPendentes.map((usuario) => (
                                               <tr key={usuario.id}>
                                                   <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{usuario.nome_completo}</td>
                                                   <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.email}</td>
                                                   <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.setor || '-'}</td>
                                                   <td className="px-6 py-4 whitespace-nowrap">
                                                       <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(usuario.status)}`}>
                                                           {usuario.status}
                                                       </span>
                                                   </td>
                                                   <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                       {usuario.status === 'PENDENTE' && (
                                                           <div className="flex space-x-2">
                                                               <button
                                                                   onClick={() => handleAprovarUsuario(usuario)}
                                                                   disabled={processando === usuario.id}
                                                                   className="text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50"
                                                               >
                                                                   {processando === usuario.id ? '⏳' : 'Aprovar'}
                                                               </button>
                                                               <button
                                                                   onClick={() => handleReprovarUsuario(usuario.id)}
                                                                   disabled={processando === usuario.id}
                                                                   className="text-xs bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 disabled:opacity-50"
                                                               >
                                                                   {processando === usuario.id ? '⏳' : 'Reprovar'}
                                                               </button>
                                                           </div>
                                                       )}
                                                   </td>
                                               </tr>
                                           ))}
                                       </tbody>
                                   </table>
                               )}
                           </>
                       )}

                       {activeTab === 'gerenciar' && (
                           <>
                               <h3 className="text-lg font-medium text-gray-900 mb-4">Todos os Colaboradores</h3>
                               <table className="min-w-full divide-y divide-gray-200">
                                   <thead className="bg-gray-50">
                                       <tr>
                                           <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                                           <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">E-mail</th>
                                           <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Setor</th>
                                           <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Privilégio</th>
                                           <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                           <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                                       </tr>
                                   </thead>
                                   <tbody className="bg-white divide-y divide-gray-200">
                                       {todosUsuarios.map((usuario) => (
                                           <tr key={usuario.id}>
                                               <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{usuario.nome_completo}</td>
                                               <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.email}</td>
                                               <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.setor || '-'}</td>
                                               <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.privilege_level || 'USER'}</td>
                                               <td className="px-6 py-4 whitespace-nowrap">
                                                   <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(usuario.status || 'PENDENTE')}`}>
                                                       {usuario.status || 'PENDENTE'}
                                                   </span>
                                               </td>
                                               <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                   <button
                                                       onClick={() => handleEditUser(usuario)}
                                                       className="text-indigo-600 hover:text-indigo-900 mr-2"
                                                   >
                                                       Editar
                                                   </button>
                                               </td>
                                           </tr>
                                       ))}
                                   </tbody>
                               </table>
                           </>
                       )}

                       {activeTab === 'novo' && (
                           <div className="max-w-md">
                               <h3 className="text-lg font-medium text-gray-900 mb-4">Criar Novo Colaborador</h3>
                               <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
                                   <p className="text-sm text-blue-800">
                                       <strong>Nota:</strong> Uma senha temporária será gerada automaticamente e exibida após a criação do usuário.
                                   </p>
                               </div>
                               <div className="space-y-4">
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">Nome Completo</label>
                                       <input
                                           type="text"
                                           value={novoUsuario.nome_completo}
                                           onChange={criarHandlerTextoValidado((valor) => setNovoUsuario({...novoUsuario, nome_completo: valor}))}
                                           onPaste={(e) => {
                                               e.preventDefault();
                                               const texto = e.clipboardData.getData('text');
                                               const textoLimpo = formatarTextoInput(texto);
                                               setNovoUsuario({...novoUsuario, nome_completo: textoLimpo});
                                           }}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                           placeholder="NOME COMPLETO EM MAIÚSCULAS"
                                           style={{ textTransform: 'uppercase' }}
                                       />
                                   </div>
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">E-mail</label>
                                       <input
                                           type="email"
                                           value={novoUsuario.email}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, email: e.target.value})}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                           required
                                       />
                                   </div>
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">Matrícula (opcional)</label>
                                       <input
                                           type="text"
                                           value={novoUsuario.matricula || ''}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, matricula: e.target.value})}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                       />
                                   </div>
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">Setor</label>
                                       <select
                                           value={novoUsuario.setor}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, setor: e.target.value})}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                           required
                                       >
                                           <option value="">Selecione um setor</option>
                                           {setores.map((setor) => (
                                               <option key={setor.id} value={setor.nome}>
                                                   {setor.nome}
                                               </option>
                                           ))}
                                       </select>
                                   </div>
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">Departamento</label>
                                       <select
                                           value={novoUsuario.departamento || 'MOTORES'}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, departamento: e.target.value})}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                       >
                                           <option value="MOTORES">MOTORES</option>
                                           <option value="TRANSFORMADORES">TRANSFORMADORES</option>
                                       </select>
                                   </div>
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">Cargo (opcional)</label>
                                       <input
                                           type="text"
                                           value={novoUsuario.cargo || ''}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, cargo: e.target.value})}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                       />
                                   </div>
                                   <div>
                                       <label className="block text-sm font-medium text-gray-700">Privilégio</label>
                                       <select
                                           value={novoUsuario.privilege_level}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, privilege_level: e.target.value})}
                                           className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                       >
                                           <option value="USER">USER</option>
                                           <option value="SUPERVISOR">SUPERVISOR</option>
                                           <option value="GESTAO">GESTAO</option>
                                           <option value="ADMIN">ADMIN</option>
                                       </select>
                                   </div>
                                   <div className="flex items-center">
                                       <input
                                           id="trabalha_producao"
                                           type="checkbox"
                                           checked={novoUsuario.trabalha_producao}
                                           onChange={(e) => setNovoUsuario({...novoUsuario, trabalha_producao: e.target.checked})}
                                           className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                       />
                                       <label htmlFor="trabalha_producao" className="ml-2 block text-sm text-gray-900">
                                           Trabalha na produção
                                       </label>
                                   </div>
                                   <div className="flex space-x-2">
                                       <button
                                           onClick={handleCreateUser}
                                           className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                                       >
                                           Criar Colaborador
                                       </button>
                                       <button
                                           onClick={() => setShowForm(false)}
                                           className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
                                       >
                                           Cancelar
                                       </button>
                                   </div>
                               </div>
                           </div>
                       )}
                   </div>
               </div>
           </div>

           {/* Edit User Modal */}
           <EditUserModal
               isOpen={showEditModal}
               onClose={() => setShowEditModal(false)}
               user={editingUser}
               setores={setores}
               onSave={handleSaveUser}
               loading={savingUser}
           />
       </Layout>
   );
};

export default Administrador;
