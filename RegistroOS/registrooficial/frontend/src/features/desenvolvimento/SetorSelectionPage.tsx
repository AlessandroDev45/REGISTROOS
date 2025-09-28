import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../services/api';
import logo from '../../logo/assets/logo.png';

interface Setor {
  id: number;
  nome: string;
  descricao?: string;
  departamento?: string;
  ativo: boolean;
}

const SetorSelectionPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [setores, setSetores] = useState<Setor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const initializeAccess = async () => {
      // Verificar se o usuário tem acesso ao desenvolvimento
      if (!user) {
        setLoading(false);
        return;
      }

      console.log('🔍 Verificando acesso ao desenvolvimento para:', user.nome_completo);
      console.log('🔍 Privilege level:', user.privilege_level);
      console.log('🔍 Trabalha produção:', user.trabalha_producao);

      // Verificar acesso: ADMIN, SUPERVISOR ou trabalha_producao = true
      const temAcesso = user.privilege_level === 'ADMIN' ||
                       user.privilege_level === 'SUPERVISOR' ||
                       user.trabalha_producao === true;

      console.log('🔍 Resultado da verificação de acesso:', temAcesso);

      if (!temAcesso) {
        setError('Acesso negado. Apenas usuários de produção, supervisores ou administradores podem acessar o desenvolvimento.');
        setLoading(false);
        return;
      }

      console.log('✅ Usuário tem acesso ao desenvolvimento:', user);
      console.log('📊 Dados detalhados do usuário:', {
        privilege_level: user.privilege_level,
        trabalha_producao: user.trabalha_producao,
        setor: user.setor,
        departamento: user.departamento
      });

      // Se não for ADMIN, redirecionar automaticamente para o setor do usuário
      if (user.privilege_level !== 'ADMIN' && user.setor) {
        const setorKey = user.setor.toLowerCase().replace(/\s+/g, '-');
        console.log('🔄 Redirecionando usuário para seu setor:', setorKey);
        navigate(`/desenvolvimento/${setorKey}`);
        return;
      }

      // Só carregar setores se for ADMIN
      if (user.privilege_level === 'ADMIN') {
        loadSetores();
      } else {
        setLoading(false);
      }
    };

    // Só executar se user existir e não estivermos já carregando
    if (user && loading) {
      initializeAccess();
    }
  }, [user?.id, user?.privilege_level, user?.trabalha_producao, navigate]); // Dependências específicas para evitar loop

  const loadSetores = async () => {
    try {
      setLoading(true);
      const response = await api.get('/setores');
      const setoresData = response.data || [];

      // Filtrar setores baseado no nível de privilégio do usuário
      let setoresFiltrados = setoresData.filter((setor: Setor) => setor.ativo !== false);

      // Se não for ADMIN, mostrar apenas setores do departamento/setor do usuário
      if (user?.privilege_level !== 'ADMIN') {
        setoresFiltrados = setoresFiltrados.filter((setor: Setor) => {
          // Verificar se o usuário pertence ao departamento do setor
          const pertenceAoDepartamento = user?.departamento === setor.departamento;
          // Verificar se o usuário pertence ao setor específico
          const pertenceAoSetor = user?.setor === setor.nome;

          return pertenceAoDepartamento || pertenceAoSetor;
        });

        // Se não encontrou setores e não trabalha na produção, negar acesso
        if (setoresFiltrados.length === 0 && !user?.trabalha_producao) {
          console.error('❌ Nenhum setor encontrado após filtro:', {
            user_departamento: user?.departamento,
            user_setor: user?.setor,
            trabalha_producao: user?.trabalha_producao,
            total_setores: setoresData.length,
            setores_sample: setoresData.slice(0, 3).map(s => ({
              nome: s.nome,
              departamento: s.departamento
            }))
          });
          setError('Acesso negado. Você não tem acesso a nenhum setor de desenvolvimento.');
          return;
        }
      }

      setSetores(setoresFiltrados);
      console.log('Setores carregados para usuário:', setoresFiltrados);
      console.log('Usuário:', user);
    } catch (error) {
      console.error('Erro ao carregar setores:', error);
      setError('Erro ao carregar setores. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleSetorSelect = (setor: Setor) => {
    const setorKey = setor.nome.toLowerCase().replace(/\s+/g, '-');
    navigate(`/desenvolvimento/${setorKey}`);
  };

  const filteredSetores = setores.filter(setor =>
    setor.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (setor.descricao && setor.descricao.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (setor.departamento && setor.departamento.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando setores...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">❌</div>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={loadSetores}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors mr-2"
                title="Voltar ao Dashboard"
              >
                ← Dashboard
              </button>
              <img src={logo} alt="RegistroOS Logo" className="h-8 w-auto" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Sistema de Desenvolvimento
                </h1>
                <p className="text-sm text-gray-500">
                  {user?.primeiro_nome || (user?.nome_completo ? user.nome_completo.split(' ')[0] : 'Usuário')} | Selecione um setor para continuar
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {setores.length} setores disponíveis
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Debug Info */}
      <div className="w-full px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-blue-50 rounded-lg p-4 mb-4">
          <div className="text-sm text-blue-800 mb-2">
            <strong>Debug Info:</strong> {user?.nome_completo} ({user?.privilege_level}) -
            Setor: {user?.setor || 'N/A'} - Dept: {user?.departamento || 'N/A'} -
            Produção: {user?.trabalha_producao ? 'Sim' : 'Não'}
          </div>
          <button
            onClick={async () => {
              setLoading(true);
              await refreshUser();
              loadSetores();
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
          >
            🔄 Atualizar Dados
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="w-full px-4 sm:px-6 lg:px-8 py-6">
        {/* Search */}
        <div className="mb-6">
          <div className="max-w-md">
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Buscar Setor
            </label>
            <input
              type="text"
              id="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Digite o nome do setor..."
            />
          </div>
        </div>

        {/* Setores Grid */}
        {filteredSetores.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm ? 'Nenhum setor encontrado' : 'Nenhum setor disponível'}
            </h3>
            <p className="text-gray-500">
              {searchTerm 
                ? 'Tente ajustar os termos de busca.' 
                : 'Entre em contato com o administrador para configurar setores.'
              }
            </p>
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Limpar Busca
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredSetores.map((setor) => (
              <div
                key={setor.id}
                onClick={() => handleSetorSelect(setor)}
                className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 hover:border-blue-300"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-2xl">🏭</div>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      ID: {setor.id}
                    </span>
                  </div>
                  
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {setor.nome}
                  </h3>
                  
                  {setor.departamento && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Departamento:</span> {setor.departamento}
                    </p>
                  )}
                  
                  {setor.descricao && (
                    <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                      {setor.descricao}
                    </p>
                  )}
                  
                  <div className="flex justify-between items-center">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Ativo
                    </span>
                    <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      Acessar →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Footer */}
        <div className="mt-12 bg-blue-50 rounded-lg p-6">
          <div className="flex items-start">
            <div className="text-blue-400 text-xl mr-3">ℹ️</div>
            <div>
              <h3 className="text-lg font-medium text-blue-900 mb-2">
                Sistema Dinâmico de Setores
              </h3>
              <p className="text-blue-700 text-sm">
                {user?.privilege_level === 'ADMIN'
                  ? 'Como administrador, você tem acesso a todos os setores do sistema. Cada setor possui suas próprias configurações e funcionalidades.'
                  : 'Você tem acesso aos setores do seu departamento. Cada setor possui suas próprias atividades, testes e formulários personalizados.'
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SetorSelectionPage;
