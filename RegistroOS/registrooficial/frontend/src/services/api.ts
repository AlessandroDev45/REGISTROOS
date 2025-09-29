import axios from 'axios';
import { AtividadeTipoData, DescricaoAtividadeData, FalhaTipoData, TipoMaquinaData } from './adminApi'; // Import specific types from adminApi

const api = axios.create({
  baseURL: '/api', // URL do backend FastAPI via proxy
  withCredentials: true, // Send cookies with requests (IMPORTANTE para HttpOnly cookies)
});

// Interceptor para garantir que cookies sejam sempre enviados
api.interceptors.request.use(config => {
  // Garantir que withCredentials está sempre true para enviar cookies HttpOnly
  config.withCredentials = true;
  console.log('🔐 [API] Enviando requisição com cookies:', config.url);
  return config;
});

// Interceptor para tratar respostas de erro de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.log('🚫 [API] Erro 401 - Token inválido ou expirado');
      // Não redirecionar automaticamente, deixar o AuthContext tratar
    }
    return Promise.reject(error);
  }
);

// Catalog Endpoints
export const fetchAtividadeTipos = async (setor?: string) => {
  try {
    const params = setor ? { setor } : {};
    const response = await api.get<AtividadeTipoData[]>('/tipos-atividade', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar tipos de atividade:", error);
    return [];
  }
};

export const fetchDescricaoAtividades = async (setor?: string) => {
  try {
    const params = setor ? { setor } : {};
    const response = await api.get<DescricaoAtividadeData[]>('/descricoes-atividade', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar descrições de atividade:", error);
    return [];
  }
};

export const fetchFalhaLaboratorioTipos = async (setor?: string) => {
  try {
    const params = setor ? { setor } : {};
    const response = await api.get<FalhaTipoData[]>('/catalogos/tipo-falha-laboratorio', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar tipos de falha do laboratório:", error);
    return [];
  }
};

export const fetchMaquinaSubTipos = async (setor?: string) => {
  try {
    const params = setor ? { setor } : {};
    const response = await api.get<TipoMaquinaData[]>('/catalogos/maquina-subtipo', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar subtipos de máquina:", error);
    return [];
  }
};

// PCP Endpoints
export const getProgramacoes = async (filters?: any) => {
  try {
    const response = await api.get('/pcp/programacoes', { params: filters });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar programações:", error);
    return [];
  }
};

export const createProgramacao = async (programacaoData: any) => {
  try {
    const response = await api.post('/pcp/programacoes', programacaoData);
    return response.data;
  } catch (error) {
    console.error("Erro ao criar programação:", error);
    throw error;
  }
};

export const updateProgramacao = async (id: number, programacaoData: any) => {
  try {
    // Enviar apenas os campos que o backend espera para atualização de status
    const updatePayload = {
      status: programacaoData.status
    };
    
    const response = await api.patch(`/pcp/programacoes/${id}/status`, updatePayload);
    return response.data;
  } catch (error) {
    console.error("Erro ao atualizar programação:", error);
    throw error;
  }
};

export const deleteProgramacao = async (id: number) => {
  try {
    const response = await api.delete(`/pcp/programacoes/${id}`);
    return response.data;
  } catch (error) {
    console.error("Erro ao cancelar programação:", error);
    throw error;
  }
};

export const enviarProgramacaoSetor = async (programacaoId: number, setorId: number) => {
  try {
    const response = await api.post(`/pcp/programacoes/${programacaoId}/enviar-setor`, { setor_id: setorId });
    return response.data;
  } catch (error) {
    console.error("Erro ao enviar programação para setor:", error);
    throw error;
  }
};

export const getProgramacoesDashboard = async (periodoDias?: number) => {
  try {
    const params = periodoDias ? { periodo_dias: periodoDias } : {};
    const response = await api.get('/pcp/programacoes/dashboard', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar dashboard de programações:", error);
    return {};
  }
};

export const getProgramacaoFormData = async () => {
  try {
    const response = await api.get('/pcp/programacao-form-data');
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar dados do formulário de programação:", error);
    // Retornar estrutura vazia - dados devem vir apenas da API
    throw error; // Propagar erro para que o frontend saiba que houve falha
  }
};

export const getOsDisponiveisForPcp = async () => {
  try {
    const response = await api.get('/pcp/ordens-servico');
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar OS disponíveis para PCP:", error);
    // Não retornar array vazio - propagar erro para que o frontend saiba que houve falha
    throw error;
  }
};

// Catalog Data Endpoints
export const getClientes = async () => {
  try {
    const response = await api.get('/clientes');
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar clientes:", error);
    return [];
  }
};

export const getEquipamentos = async () => {
  try {
    const response = await api.get('/equipamentos');
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar equipamentos:", error);
    return [];
  }
};

export const getTiposAtividade = async (departamento?: string) => {
  try {
    const params = departamento ? { departamento } : {};
    const response = await api.get('/tipos-atividade', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar tipos de atividade:", error);
    return [];
  }
};

export const getDescricoesAtividade = async (departamento?: string, setor?: string) => {
  try {
    const params: any = {};
    if (departamento) params.departamento = departamento;
    if (setor) params.setor = setor;
    const response = await api.get('/descricoes-atividade', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar descrições de atividade:", error);
    return [];
  }
};

// Pendências Endpoints
export const getPendencias = async (filters?: any) => {
  try {
    const response = await api.get('/pcp/pendencias', { params: filters });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar pendências:", error);
    return [];
  }
};

export const getPendenciaDetalhes = async (id: number) => {
  try {
    const response = await api.get(`/pcp/pendencias/${id}`);
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar detalhes da pendência:", error);
    throw error;
  }
};

export const getPendenciasDashboard = async (periodoDias?: number) => {
  try {
    const params = periodoDias ? { periodo_dias: periodoDias } : {};
    const response = await api.get('/pcp/pendencias/dashboard', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar dashboard de pendências:", error);
    return {};
  }
};

export const updatePendencia = async (id: number, pendenciaData: any) => {
  try {
    const response = await api.put(`/pendencias/${id}`, pendenciaData);
    return response.data;
  } catch (error) {
    console.error("Erro ao atualizar pendência:", error);
    throw error;
  }
};

// Dashboard PCP Avançado
export const getDashboardAvancado = async (periodoDias?: number, setorId?: number) => {
  try {
    const params: any = {};
    if (periodoDias) params.periodo_dias = periodoDias;
    if (setorId) params.setor_id = setorId;
    const response = await api.get('/pcp/dashboard/avancado', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar dashboard avançado:", error);
    return {};
  }
};

export const getRelatorioEficiencia = async (periodoDias?: number, setorId?: number) => {
  try {
    const params: any = {};
    if (periodoDias) params.periodo_dias = periodoDias;
    if (setorId) params.setor_id = setorId;
    const response = await api.get('/pcp/relatorios/eficiencia-setores', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar relatório de eficiência:", error);
    return {};
  }
};

export const getAlertasPCP = async () => {
  try {
    const response = await api.get('/pcp/alertas');
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar alertas PCP:", error);
    return { alertas: [], total_alertas: 0 };
  }
};

// Apontamento Endpoints
export const createApontamento = async (apontamentoData: any) => {
  try {
    const response = await api.post('/save-apontamento', apontamentoData);
    return response.data;
  } catch (error: any) {
    console.error("Erro ao criar apontamento:", error);
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail);
    }
    throw new Error("Ocorreu um erro desconhecido ao salvar o apontamento.");
  }
};

export const getApontamentosDetalhados = async (filters?: any) => {
  try {
    const response = await api.get('/desenvolvimento/apontamentos-detalhados', { params: filters });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar apontamentos detalhados:", error);
    return [];
  }
};

// Dashboard Endpoints
export const getDashboardMetrics = async (departamento?: string) => {
  try {
    const params = departamento ? { departamento } : {};
    const response = await api.get('/dashboard-metrics', { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar métricas do dashboard:", error);
    return {
      osAbertas: 0,
      osEmAndamento: 0,
      osConcluidas: 0,
      pendencias: 0,
      performanceSetores: [],
      osRecentes: []
    };
  }
};
// =============================================================================
// NOVAS FUNÇÕES PARA ESTRUTURA SETORIZADA DA OS
// =============================================================================

// OS Endpoints - Estrutura Setorizada
export const getOrdensServico = async (filters?: any) => {
  try {
    const response = await api.get('/os/', { params: filters });
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar ordens de serviço:", error);
    return [];
  }
};

export const getOrdemServicoById = async (osId: number) => {
  try {
    const response = await api.get(`/os/${osId}`);
    return response.data;
  } catch (error: any) {
    console.error("Erro ao buscar ordem de serviço:", error);
    throw error;
  }
};

export const adicionarSetorParticipante = async (osId: number, setorData: any) => {
  try {
    const response = await api.post(`/os/${osId}/setores`, setorData);
    return response.data;
  } catch (error: any) {
    console.error("Erro ao adicionar setor participante:", error);
    throw error;
  }
};

// Apontamentos por Setor
export const criarApontamentoSetor = async (osId: number, apontamentoData: any) => {
  try {
    const response = await api.post(`/os/${osId}/apontamentos`, apontamentoData);
    return response.data;
  } catch (error: any) {
    console.error("Erro ao criar apontamento por setor:", error);
    throw error;
  }
};

export const listarApontamentosOS = async (osId: number, setor?: string) => {
  try {
    const params = setor ? { setor } : {};
    const response = await api.get(`/os/${osId}/apontamentos`, { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao listar apontamentos da OS:", error);
    return [];
  }
};

// Testes por Setor
export const registrarTesteSetor = async (osId: number, testeData: any) => {
  try {
    const response = await api.post(`/os/${osId}/testes`, testeData);
    return response.data;
  } catch (error: any) {
    console.error("Erro ao registrar teste por setor:", error);
    throw error;
  }
};

export const listarTestesOS = async (osId: number, setor?: string) => {
  try {
    const params = setor ? { setor } : {};
    const response = await api.get(`/os/${osId}/testes`, { params });
    return response.data;
  } catch (error) {
    console.error("Erro ao listar testes da OS:", error);
    return [];
  }
};

export default api;
