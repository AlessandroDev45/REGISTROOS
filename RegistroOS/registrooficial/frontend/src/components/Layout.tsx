/* frontend/src/components/Layout.tsx */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Logo from '../logo/assets/logo.png';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api'; // Certifique-se de que o caminho está correto
import { FormValidationProvider } from './FormValidationProvider';
import ChangePasswordModal from '../features/auth/ChangePasswordModal';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, logout, hasAccessFunction, isLoading: authLoading, requiresPasswordChange, refreshUser } = useAuth();
    const [saudacao, setSaudacao] = useState<string>('');
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);

    // Logs removidos para reduzir ruído - apenas em desenvolvimento se necessário
    // console.log('🏗️ Layout renderizado - showUserMenu:', showUserMenu);
    // console.log('👤 User:', user);
    // console.log('🔐 Requires password change:', requiresPasswordChange);

    // Memoizar saudação para evitar recálculos desnecessários
    const saudacaoMemo = useMemo(() => {
        const now = new Date();
        const hour = now.getHours();
        if (hour >= 6 && hour < 12) return 'Bom dia';
        if (hour >= 12 && hour < 18) return 'Boa tarde';
        return 'Boa noite';
    }, []);

    useEffect(() => {
        setSaudacao(saudacaoMemo);
    }, [saudacaoMemo]);

    // Mostrar modal de troca de senha se necessário
    useEffect(() => {
        if (requiresPasswordChange && user) {
            setShowChangePasswordModal(true);
        }
    }, [requiresPasswordChange, user]);

    // Otimizar handler de clique fora com useCallback
    const handleClickOutside = useCallback((event: MouseEvent) => {
        const target = event.target as Element;
        if (showUserMenu && !target.closest('.user-menu-container')) {
            console.log('🔍 Clique fora do menu - fechando');
            setShowUserMenu(false);
        }
    }, [showUserMenu]);

    // Fechar menu quando clicar fora (useEffect único otimizado)
    useEffect(() => {
        if (showUserMenu) {
            document.addEventListener('mousedown', handleClickOutside);
            return () => {
                document.removeEventListener('mousedown', handleClickOutside);
            };
        }
    }, [showUserMenu, handleClickOutside]);

    const handleLogout = async () => {
        console.log('🚪 Layout: BOTÃO LOGOUT CLICADO!');

        // Fechar menu imediatamente
        setShowUserMenu(false);

        try {
            // Tentar logout via AuthContext
            console.log('🔄 Tentando logout via AuthContext...');
            await logout();
            console.log('✅ Logout AuthContext OK');
        } catch (error) {
            console.error('❌ Erro no AuthContext logout:', error);
        }

        try {
            // Logout direto via API como backup
            console.log('🔄 Fazendo logout direto via API...');
            await api.post('/logout');
            console.log('✅ Logout API OK');
        } catch (error) {
            console.error('❌ Erro no logout API:', error);
        }

        // Limpar tudo manualmente
        console.log('🧹 Limpando estado manualmente...');
        localStorage.clear();
        sessionStorage.clear();

        // Redirecionar SEMPRE
        console.log('🔄 Redirecionando para login...');
        window.location.href = '/login';
    };

    const handlePasswordChangeSuccess = async () => {
        setShowChangePasswordModal(false);
        await refreshUser(); // Atualizar dados do usuário
    };

    const handlePasswordChangeClose = () => {
        // Se é primeiro login, não permitir fechar o modal
        if (!requiresPasswordChange) {
            setShowChangePasswordModal(false);
        }
    };

    // Memoize user-related data to prevent unnecessary re-renders
    const userData = useMemo(() => {
        return {
            userName: user?.nome_completo || 'Usuário',
            userSetor: user?.setor || 'Setor não definido',
            userPrivilege: user?.privilege_level || 'USER',
            isLoggedIn: !!user
        };
    }, [user]);

    const menuRoutes = useMemo(() => [
        { path: '/dashboard', label: 'Dashboard', feature: 'dashboard' },
        { path: '/pcp', label: 'PCP', feature: 'pcp' },
        { path: '/consulta-os', label: 'Consulta OS', feature: 'consulta_os' },
        { path: '/administrador', label: 'Administrador', feature: 'admin' },
        { path: '/admin', label: 'Admin Config', feature: 'admin' }, // Assuming 'admin' feature covers this too
        { path: '/gestao', label: 'Gestão', feature: 'gestao' },
        { path: '/desenvolvimento', label: 'Desenvolvimento', feature: 'desenvolvimento' },
    ], []); // Empty dependency array as menuRoutes are static

    if (authLoading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Carregando dados do usuário...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <nav className="bg-white shadow-lg">
                <div className="w-full px-4">
                    <div className="flex justify-between h-16">
                        <div className="flex flex-col md:flex-row md:items-center md:flex-1">
                            <div className="shrink-0 flex items-center">
                                <img src={Logo} alt="RegistroOS Logo" className="h-8 w-auto" />
                            </div>
                            <div className="hidden md:ml-6 md:flex md:space-x-8 flex-1 justify-center">
                                {menuRoutes.map(route => {
                                    const hasAccess = hasAccessFunction(route.feature);
                                    return (
                                        <React.Fragment key={route.path}>
                                            {hasAccess ? (
                                                <Link
                                                    to={route.path}
                                                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                                                        location.pathname.startsWith(route.path)
                                                            ? 'border-indigo-500 text-gray-900'
                                                            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                                                    }`}
                                                    title={`${userData.userPrivilege.toUpperCase()} possui acesso para este módulo.`}
                                                >
                                                    {route.label}
                                                </Link>
                                            ) : (
                                                <span
                                                    className="inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium border-transparent text-gray-400 cursor-not-allowed"
                                                    title={`${userData.userPrivilege.toUpperCase()} não possui acesso para este módulo.`}
                                                >
                                                    {route.label} 🔒
                                                </span>
                                            )}
                                        </React.Fragment>
                                    );
                                })}
                            </div>
                            <div className="md:ml-auto flex flex-col items-end md:items-center">
                                {userData.isLoggedIn ? (
                                    <div className="text-sm text-gray-600 mb-1 md:hidden md:mb-0">
                                        {saudacao}, {userData.userName} ({userData.userSetor})
                                    </div>
                                ) : (
                                    <div className="text-sm text-gray-600 mb-1 md:hidden md:mb-0">
                                        Bem-vindo, Faça login
                                    </div>
                                )}

                                {userData.isLoggedIn ? (
                                    <div className="relative user-menu-container">
                                        <button
                                            onClick={() => {
                                                console.log('👤 CLIQUE NO MENU DO USUÁRIO!');
                                                console.log('showUserMenu antes:', showUserMenu);
                                                setShowUserMenu(!showUserMenu);
                                                console.log('showUserMenu depois:', !showUserMenu);
                                            }}
                                            className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <span>👤</span>
                                            <span className="hidden md:inline">{userData.userName.split(' ')[0]}</span>
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>

                                        {showUserMenu && (
                                            <div
                                                className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200"
                                                onClick={(e) => {
                                                    console.log('🔍 Clique no menu dropdown detectado');
                                                    e.stopPropagation();
                                                }}
                                            >
                                                <button
                                                    onClick={() => {
                                                        setShowChangePasswordModal(true);
                                                        setShowUserMenu(false);
                                                    }}
                                                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                >
                                                    🔐 Alterar Senha
                                                </button>
                                                <hr className="my-1" />
                                                <button
                                                    onMouseDown={(e) => {
                                                        console.log('🚪 LOGOUT CLICADO!');
                                                        e.preventDefault();
                                                        e.stopPropagation();
                                                        localStorage.clear();
                                                        sessionStorage.clear();
                                                        window.location.href = '/login';
                                                    }}
                                                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                                    style={{ cursor: 'pointer' }}
                                                >
                                                    🚪 Logout
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <button
                                        onClick={handleLogout}
                                        className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700"
                                        disabled={!userData.isLoggedIn}
                                    >
                                        Acesso Restrito
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                    {userData.isLoggedIn && (
                        <div className="hidden md:block text-sm text-gray-600 text-center py-2 bg-gray-50 border-t border-b border-gray-200">
                            {saudacao}, <span className="font-medium">{userData.userName}</span> | Setor: <span className="font-medium">{userData.userSetor}</span>
                        </div>
                    )}
                    {!userData.isLoggedIn && (
                         <div className="hidden md:block text-sm text-gray-600 text-center py-2 bg-gray-50 border-t border-b border-gray-200">
                            Por favor, faça login para acessar o sistema.
                        </div>
                    )}
                </div>
            </nav>

            <main className="flex-grow">
                <div className="w-full py-6 sm:px-6 lg:px-8">
                    <FormValidationProvider>
                        {children}
                    </FormValidationProvider>
                </div>
            </main>

            {/* Modal de Mudança de Senha */}
            <ChangePasswordModal
                isOpen={showChangePasswordModal}
                onClose={handlePasswordChangeClose}
                onSuccess={handlePasswordChangeSuccess}
                isFirstLogin={requiresPasswordChange}
            />
        </div>
    );
};

export default Layout;
