import React, { Suspense } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { SetorProvider } from './contexts/SetorContext';
import { ApontamentoProvider } from './contexts/ApontamentoContext'; // Provider para o formulário
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastContainer } from 'react-toastify'; // Import ToastContainer
import 'react-toastify/dist/ReactToastify.css'; // Import CSS for toasts

// Sistema dinâmico de setores - não precisa mais importar lista estática

// Importe as páginas
import LoginPage from './features/autenticacao/LoginPage';
import RegisterPage from './features/autenticacao/RegisterPage';
import DashboardPage from './features/dashboard/DashboardPage';
import PCPPage from './features/pcp/PCPPage';
import AdministradorPage from './features/admin/administrador';
import AdminPage from './features/admin/AdminPage';
import GestaoPage from './features/gestao/gestao';
import ConsultaOsPage from './pages/common/consulta-os';
import UniversalSectorPage from './features/desenvolvimento/UniversalSectorPage'; // Nossa página inteligente
import SetorSelectionPage from './features/desenvolvimento/SetorSelectionPage'; // Página de seleção de setores
// ... importe outras páginas como PCP, ConsultaOs, etc.

const queryClient = new QueryClient();

// Componente para proteger rotas
const PrivateRoute = ({ children }: { children: JSX.Element }) => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
        return <div>Carregando sessão...</div>;
    }

    if (!user) {
        console.log('PrivateRoute: Usuário não autenticado, redirecionando para login');
        return <Navigate to="/login" replace />;
    }

    return children;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <SetorProvider>
          <ApontamentoProvider> {/* Provider do formulário envolvendo as rotas de desenvolvimento */}
            <Router>
              <Suspense fallback={<div>Carregando página...</div>}>
                <Routes>
                  {/* Rotas Públicas */}
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />

                  {/* Rotas Privadas */}
                  <Route path="/pcp" element={<PrivateRoute><PCPPage /></PrivateRoute>} />
                  <Route path="/administrador" element={<PrivateRoute><AdministradorPage /></PrivateRoute>} />
                  <Route path="/admin" element={<PrivateRoute><AdminPage /></PrivateRoute>} />
                  <Route path="/gestao" element={<PrivateRoute><GestaoPage /></PrivateRoute>} />
                  <Route path="/consulta-os" element={<PrivateRoute><ConsultaOsPage /></PrivateRoute>} />
                  <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />

                  {/* Rota de Desenvolvimento Dinâmica */}
                  <Route
                    path="/desenvolvimento/:setor"
                    element={<PrivateRoute><UniversalSectorPage /></PrivateRoute>}
                  />
                  {/* Rota de fallback para desenvolvimento - página de seleção */}
                  <Route
                    path="/desenvolvimento"
                    element={<PrivateRoute><SetorSelectionPage /></PrivateRoute>}
                  />

                  {/* Adicione outras rotas privadas aqui (PCP, etc.) */}

                  {/* Rotas de Fallback */}
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                  <Route path="*" element={<Navigate to="/dashboard" />} />
                </Routes>
              </Suspense>
              {/* Add ToastContainer here for global toast notifications */}
              <ToastContainer
                position="bottom-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
              />
            </Router>
          </ApontamentoProvider>
        </SetorProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;