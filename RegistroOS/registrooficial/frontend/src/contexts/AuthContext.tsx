import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useMemo } from 'react';
import api from '../services/api';
import { User } from '../pages/common/TiposApi'; // Use consolidated User interface
import { useCachedSetores } from '../hooks/useCachedSetores'; // Import the new hook

interface AuthContextType {
    user: User | null;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
    isLoading: boolean;
    selectedSector: string | null;
    setSelectedSector: (sector: string | null) => void;
    isAdmin: boolean;
    hasAccess: boolean;
    hasAccessFunction: (feature: string) => boolean;
    checkAccess: (sector: string) => Promise<boolean>;
    requiresPasswordChange: boolean;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [selectedSector, setSelectedSector] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [requiresPasswordChange, setRequiresPasswordChange] = useState(false);
    const [authInitialized, setAuthInitialized] = useState(false); // Flag para evitar execução dupla
    const { todosSetores, loading: setoresLoading, error: setoresError } = useCachedSetores();

    // Função para verificar se o usuário trabalha na produção baseado no campo do banco
    const trabalhaNaProducao = (user: User | null): boolean => {
        return user?.trabalha_producao === true;
    };

    // List of production sectors (normalized) - can be fetched from backend or defined here
    const setoresDeProducao = [
        'laboratorio de ensaios eletricos', // Ensure this matches exactly with your backend config names, normalized
        'mecanica',
        'montagem',
        'pintura',
        'bobinagem',
        'testes'
    ];

    const checkAuthStatus = useCallback(async () => {
        try {
            const response = await api.get('/me');
            const userData = response.data;
            // Ensure departamento is set for consistency
            if (!userData.departamento) {
                userData.departamento = 'MOTORES'; // Default value
            }
            setUser(userData);

            // Verificar se precisa trocar senha
            setRequiresPasswordChange(userData.primeiro_login || false);

            console.log('AuthContext checkAuthStatus - API user:', {
                setor: userData.setor,
                privilege_level: userData.privilege_level,
                trabalha_producao: userData.trabalha_producao,
                primeiro_login: userData.primeiro_login,
                isAdmin: userData.privilege_level === 'ADMIN' || userData.privilege_level === 'GESTAO'
            });
            // Only set selectedSector for regular users (USER, SUPERVISOR, PCP)
            // ADMIN and GESTAO users should choose their sector via selector
            if (['USER', 'SUPERVISOR', 'PCP'].includes(userData.privilege_level)) {
                setSelectedSector(userData.setor);
            } else {
                console.log('AuthContext checkAuthStatus - Not setting selectedSector for ADMIN/GESTAO user, will use selector');
            }
        } catch (error: any) {
            // Token is invalid, clear user data
            setUser(null);
            setSelectedSector(null);
            setRequiresPasswordChange(false);

            // Only log non-401 errors to avoid cluttering console with expected auth failures
            if (error.response?.status !== 401) {
                console.error('AuthContext checkAuthStatus - Unexpected error:', error);
            }
        } finally {
            setIsLoading(false);
        }
    }, []);

    const refreshUser = useCallback(async () => {
        try {
            console.log('🔄 Atualizando dados do usuário...');
            const response = await api.get('/me');
            const userData = response.data;
            if (!userData.departamento) {
                userData.departamento = 'MOTORES';
            }
            setUser(userData);
            setRequiresPasswordChange(userData.primeiro_login || false);
            console.log('✅ Dados do usuário atualizados:', {
                nome: userData.nome_completo,
                privilege: userData.privilege_level,
                setor: userData.setor,
                departamento: userData.departamento,
                trabalha_producao: userData.trabalha_producao
            });
        } catch (error: any) {
            // Se o erro for de autenticação, limpar o usuário
            if (error.response?.status === 401) {
                console.log('🔓 Sessão expirada, fazendo logout...');
                setUser(null);
            } else {
                console.error('❌ Erro ao atualizar dados do usuário:', error);
            }
        }
    }, []);

    const login = useCallback(async (email: string, password: string): Promise<boolean> => {
        try {
            console.log('🔐 Tentando login para:', email);
            console.log('🔑 Senha recebida - length:', password.length);
            console.log('🔑 Senha chars:', password.split('').map(c => c.charCodeAt(0)));

            // Limpar a senha de caracteres especiais
            const cleanPassword = password.trim();
            console.log('🧹 Senha limpa - length:', cleanPassword.length);

            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', cleanPassword);

            console.log('📤 Enviando requisição para /token');
            const response = await api.post('/token', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            console.log('✅ Resposta recebida:', response.status);
            console.log('📋 Dados do usuário:', response.data);

            // Token is now stored in HttpOnly cookie by the backend
            const userData = response.data.user;
            // Ensure departamento is set for consistency
            if (!userData.departamento) {
                userData.departamento = 'MOTORES'; // Default value
            }
            setUser(userData);

            // Verificar se precisa trocar senha
            setRequiresPasswordChange(response.data.requires_password_change || false);

            // Set selectedSector for regular users
            if (['USER', 'SUPERVISOR', 'PCP'].includes(userData.privilege_level)) {
                setSelectedSector(userData.setor);
            }

            console.log('🎉 Login bem-sucedido!');
            return true;
        } catch (error) {
            console.error('❌ Erro no login:', error);
            if (error.response) {
                console.error('📄 Resposta do erro:', error.response.data);
                console.error('🔢 Status do erro:', error.response.status);
            }
            return false;
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            console.log('AuthContext: Iniciando logout...');

            // Chamar API de logout para limpar cookie no servidor
            await api.post('/logout');
            console.log('AuthContext: Logout API call successful');
        } catch (error) {
            console.error('AuthContext: Logout error:', error);
            // Mesmo com erro na API, continuar com limpeza local
        }

        // Sempre limpar estado local
        console.log('AuthContext: Limpando estado local...');
        setUser(null);
        setSelectedSector(null);
        setRequiresPasswordChange(false);

        // Não precisamos limpar headers Authorization pois usamos cookies HttpOnly
        // O logout será feito via endpoint /logout que limpa o cookie

        // Limpar localStorage se houver algo
        localStorage.clear();
        sessionStorage.clear();

        console.log('AuthContext: Logout concluído - estado limpo');
    }, []);

    const checkAccess = useCallback(async (sector: string) => {
        console.log('AuthContext: checkAccess chamado para setor:', sector);

        // Normalizar o setor antes de fazer a chamada
        const setorNormalizado = sector.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "");
        console.log('AuthContext: Setor normalizado:', setorNormalizado);

        try {
            const response = await api.get(`/check-development-access/${setorNormalizado}`);
            const hasAccess = response.data.has_access;
            console.log('AuthContext: checkAccess para setor', setorNormalizado, 'resultado:', hasAccess, 'response:', response.data);
            return hasAccess;
        } catch (error) {
            console.error('AuthContext: Error checking access para setor', setorNormalizado, ':', error);
            return false;
        }
    }, []);

    // Usar useEffect com flag de controle para evitar execução dupla do StrictMode
    useEffect(() => {
        if (!authInitialized) {
            console.log('🔄 AuthContext: Executando checkAuthStatus inicial (primeira vez)');
            setAuthInitialized(true);
            checkAuthStatus(); // Check authentication status on mount
        }
    }, [authInitialized, checkAuthStatus]); // Dependência controlada

    // General access to development module
    const hasGeneralDevelopmentAccess = useCallback(() => {
        if (!user || setoresLoading) {
            return false;
        }

        const isAdminOrGestao = user.privilege_level === 'ADMIN' || user.privilege_level === 'GESTAO';
        if (isAdminOrGestao) return true; // Admins and Gestao have full access

        // For other roles, check if their *assigned* sector is a "production" sector
        const userSetorNormalizado = user.setor?.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "");
        const isProductionSector = setoresDeProducao.includes(userSetorNormalizado);

        // A user (USER or SUPERVISOR) has access if they work in production.
        // The `trabalha_producao` flag is the most explicit indicator.
        // Fallback: if `trabalha_producao` is not set, we can infer from sector list.
        const explicitlyWorksProduction = user.trabalha_producao === true;

        if (user.privilege_level === 'USER' || user.privilege_level === 'SUPERVISOR') {
            return explicitlyWorksProduction || isProductionSector;
        }

        return false;
    }, [user, setoresLoading, todosSetores]);

    const hasAccessFunction = useCallback((feature: string): boolean => {
        if (!user) return false;

        // Admin always has access to everything
        if (user.privilege_level === 'ADMIN') {
            return true;
        }

        // Feature-specific access rules
        switch (feature) {
            case 'desenvolvimento':
                // Check if the user is a production user (USER/SUPERVISOR) and their sector allows development work
                return hasGeneralDevelopmentAccess();

            case 'pcp':
                // PCP module access is for PCP, GESTAO, ADMIN
                return ['PCP', 'GESTAO', 'ADMIN'].includes(user.privilege_level);

            case 'gestao':
                // Management module access is for GESTAO, ADMIN
                return ['GESTAO', 'ADMIN'].includes(user.privilege_level);

            case 'admin':
                // Admin configuration module access is for ADMIN only
                return user.privilege_level === 'ADMIN';

            case 'dashboard':
            case 'consulta_os':
                // Dashboard and OS query are generally accessible to all logged-in users
                return true;

            default:
                return false;
        }
    }, [user, hasGeneralDevelopmentAccess]);

    // General access based on selectedSector, for the DevelopmentTemplate and other guards.
    // This is distinct from `hasAccessFunction` which checks module access.
    // `hasAccess` here is specifically about whether the *currently selected sector* allows general operations (e.g., development form).
    const isAdminOrGestao = user?.privilege_level === 'ADMIN' || user?.privilege_level === 'GESTAO';
    const hasAccessToSelectedSectorOperations = isAdminOrGestao || (user && selectedSector && setoresDeProducao.includes(selectedSector.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, "")));


    // Memoizar o valor do contexto para evitar re-renderizações desnecessárias
    const value: AuthContextType = useMemo(() => ({
        user,
        login,
        logout,
        isLoading,
        selectedSector,
        setSelectedSector,
        isAdmin: user?.privilege_level === 'ADMIN' || user?.privilege_level === 'GESTAO',
        hasAccess: hasGeneralDevelopmentAccess(), // This now represents access to the 'development' module
        hasAccessFunction,
        checkAccess,
        requiresPasswordChange,
        refreshUser
    }), [
        user,
        login,
        logout,
        isLoading,
        selectedSector,
        setSelectedSector,
        hasGeneralDevelopmentAccess,
        hasAccessFunction,
        checkAccess,
        requiresPasswordChange,
        refreshUser
    ]);

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth deve ser usado dentro de um AuthProvider');
    }
    return context;
};
