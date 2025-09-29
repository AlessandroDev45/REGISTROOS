// ============================================================================
// CONSTANTES CENTRALIZADAS DO SISTEMA REGISTROOS
// ============================================================================

// =============================================================================
// NÍVEIS DE PRIVILÉGIO (sincronizado com backend)
// =============================================================================
export const PRIVILEGE_LEVELS = {
  ADMIN: 'ADMIN',
  GESTAO: 'GESTAO', 
  PCP: 'PCP',
  SUPERVISOR: 'SUPERVISOR',
  USER: 'USER'
} as const;

export type PrivilegeLevel = typeof PRIVILEGE_LEVELS[keyof typeof PRIVILEGE_LEVELS];

// Ordem hierárquica dos privilégios (do maior para o menor)
export const PRIVILEGE_HIERARCHY = [
  PRIVILEGE_LEVELS.ADMIN,
  PRIVILEGE_LEVELS.GESTAO,
  PRIVILEGE_LEVELS.PCP,
  PRIVILEGE_LEVELS.SUPERVISOR,
  PRIVILEGE_LEVELS.USER
] as const;

// =============================================================================
// STATUS DE ORDEM DE SERVIÇO
// =============================================================================
export const STATUS_OS = {
  ABERTA: 'ABERTA',
  PROGRAMADA: 'PROGRAMADA',
  EM_ANDAMENTO: 'EM_ANDAMENTO',
  PENDENTE: 'PENDENTE',
  FINALIZADA: 'FINALIZADA',
  TERMINADA: 'TERMINADA',
  CANCELADA: 'CANCELADA'
} as const;

export type StatusOS = typeof STATUS_OS[keyof typeof STATUS_OS];

export const STATUS_OS_OPTIONS = Object.values(STATUS_OS);

// =============================================================================
// PRIORIDADES
// =============================================================================
export const PRIORIDADES = {
  URGENTE: 'URGENTE',
  ALTA: 'ALTA',
  NORMAL: 'NORMAL',
  BAIXA: 'BAIXA'
} as const;

export type Prioridade = typeof PRIORIDADES[keyof typeof PRIORIDADES];

export const PRIORIDADE_OPTIONS = Object.values(PRIORIDADES);

// =============================================================================
// TIPOS DE ATIVIDADE
// =============================================================================
export const TIPOS_ATIVIDADE = {
  MANUTENCAO: 'MANUTENÇÃO',
  REPARO: 'REPARO',
  INSTALACAO: 'INSTALAÇÃO',
  TESTE: 'TESTE',
  INSPECAO: 'INSPEÇÃO',
  CALIBRACAO: 'CALIBRAÇÃO',
  LIMPEZA: 'LIMPEZA',
  AJUSTE: 'AJUSTE'
} as const;

export type TipoAtividade = typeof TIPOS_ATIVIDADE[keyof typeof TIPOS_ATIVIDADE];

export const TIPOS_ATIVIDADE_OPTIONS = Object.values(TIPOS_ATIVIDADE);

// =============================================================================
// CORES DOS STATUS
// =============================================================================
export const STATUS_COLORS = {
  ABERTA: 'bg-blue-100 text-blue-800 border-blue-200',
  PROGRAMADA: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  EM_ANDAMENTO: 'bg-orange-100 text-orange-800 border-orange-200',
  PENDENTE: 'bg-red-100 text-red-800 border-red-200',
  FINALIZADA: 'bg-green-100 text-green-800 border-green-200',
  TERMINADA: 'bg-gray-100 text-gray-800 border-gray-200',
  CANCELADA: 'bg-gray-100 text-gray-600 border-gray-200'
} as const;

// =============================================================================
// CORES DAS PRIORIDADES
// =============================================================================
export const PRIORITY_COLORS = {
  URGENTE: 'bg-red-100 text-red-800 border-red-200',
  ALTA: 'bg-orange-100 text-orange-800 border-orange-200',
  NORMAL: 'bg-blue-100 text-blue-800 border-blue-200',
  BAIXA: 'bg-gray-100 text-gray-800 border-gray-200'
} as const;

// =============================================================================
// TIPOS DE ÁREA
// =============================================================================
export const TIPOS_AREA = {
  PRODUCAO: 'PRODUÇÃO',
  MANUTENCAO: 'MANUTENÇÃO',
  QUALIDADE: 'QUALIDADE',
  LOGISTICA: 'LOGÍSTICA',
  ADMINISTRATIVO: 'ADMINISTRATIVO',
  ENGENHARIA: 'ENGENHARIA'
} as const;

export type TipoArea = typeof TIPOS_AREA[keyof typeof TIPOS_AREA];

export const TIPOS_AREA_OPTIONS = Object.values(TIPOS_AREA);

// =============================================================================
// CONFIGURAÇÕES DE ACESSO POR FEATURE
// =============================================================================
export const FEATURE_ACCESS = {
  ADMIN_CONFIG: [PRIVILEGE_LEVELS.ADMIN],
  USER_MANAGEMENT: [PRIVILEGE_LEVELS.ADMIN, PRIVILEGE_LEVELS.GESTAO],
  PCP_DASHBOARD: [PRIVILEGE_LEVELS.ADMIN, PRIVILEGE_LEVELS.GESTAO, PRIVILEGE_LEVELS.PCP],
  GESTAO_DASHBOARD: [PRIVILEGE_LEVELS.ADMIN, PRIVILEGE_LEVELS.GESTAO],
  DESENVOLVIMENTO: [PRIVILEGE_LEVELS.ADMIN, PRIVILEGE_LEVELS.GESTAO, PRIVILEGE_LEVELS.PCP, PRIVILEGE_LEVELS.SUPERVISOR, PRIVILEGE_LEVELS.USER],
  CONSULTA_OS: [PRIVILEGE_LEVELS.ADMIN, PRIVILEGE_LEVELS.GESTAO, PRIVILEGE_LEVELS.PCP, PRIVILEGE_LEVELS.SUPERVISOR, PRIVILEGE_LEVELS.USER]
} as const;

// =============================================================================
// CONFIGURAÇÕES DE PAGINAÇÃO
// =============================================================================
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
  MAX_PAGE_SIZE: 100
} as const;

// =============================================================================
// CONFIGURAÇÕES DE VALIDAÇÃO
// =============================================================================
export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 6,
  MAX_TEXT_LENGTH: 255,
  MAX_DESCRIPTION_LENGTH: 1000,
  MIN_SEARCH_LENGTH: 2
} as const;

// =============================================================================
// CONFIGURAÇÕES DE TEMPO
// =============================================================================
export const TIME_CONFIG = {
  DEBOUNCE_DELAY: 300, // ms para debounce de busca
  TOAST_DURATION: 3000, // ms para duração de toasts
  POLLING_INTERVAL: 30000, // ms para polling de dados
  SESSION_TIMEOUT: 3600000 // ms para timeout de sessão (1 hora)
} as const;

// =============================================================================
// MENSAGENS PADRÃO
// =============================================================================
export const MESSAGES = {
  LOADING: 'Carregando...',
  NO_DATA: 'Nenhum dado encontrado',
  ERROR_GENERIC: 'Ocorreu um erro inesperado',
  ERROR_NETWORK: 'Erro de conexão. Verifique sua internet.',
  ERROR_UNAUTHORIZED: 'Acesso não autorizado',
  ERROR_FORBIDDEN: 'Você não tem permissão para esta ação',
  SUCCESS_SAVE: 'Dados salvos com sucesso!',
  SUCCESS_DELETE: 'Item removido com sucesso!',
  SUCCESS_UPDATE: 'Dados atualizados com sucesso!',
  CONFIRM_DELETE: 'Tem certeza que deseja remover este item?'
} as const;

// =============================================================================
// CONFIGURAÇÕES DE API
// =============================================================================
export const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 10000, // ms
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000 // ms
} as const;

// =============================================================================
// ROTAS DA APLICAÇÃO
// =============================================================================
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  ADMIN: '/admin',
  PCP: '/pcp',
  GESTAO: '/gestao',
  DESENVOLVIMENTO: '/desenvolvimento',
  CONSULTA_OS: '/consulta-os'
} as const;

// =============================================================================
// CONFIGURAÇÕES DE TEMA
// =============================================================================
export const THEME = {
  PRIMARY_COLOR: 'blue',
  SECONDARY_COLOR: 'gray',
  SUCCESS_COLOR: 'green',
  WARNING_COLOR: 'yellow',
  ERROR_COLOR: 'red',
  INFO_COLOR: 'blue'
} as const;

// =============================================================================
// UTILITÁRIOS DE VERIFICAÇÃO
// =============================================================================

/**
 * Verifica se o usuário tem privilégio suficiente para acessar uma feature
 */
export const hasFeatureAccess = (userPrivilege: PrivilegeLevel, feature: keyof typeof FEATURE_ACCESS): boolean => {
  return FEATURE_ACCESS[feature].includes(userPrivilege);
};

/**
 * Verifica se um privilégio é maior ou igual a outro
 */
export const hasPrivilegeLevel = (userPrivilege: PrivilegeLevel, requiredPrivilege: PrivilegeLevel): boolean => {
  const userIndex = PRIVILEGE_HIERARCHY.indexOf(userPrivilege);
  const requiredIndex = PRIVILEGE_HIERARCHY.indexOf(requiredPrivilege);
  return userIndex <= requiredIndex; // Menor índice = maior privilégio
};

/**
 * Obtém a cor CSS para um status
 */
export const getStatusColor = (status: StatusOS): string => {
  return STATUS_COLORS[status] || STATUS_COLORS.ABERTA;
};

/**
 * Obtém a cor CSS para uma prioridade
 */
export const getPriorityColor = (priority: Prioridade): string => {
  return PRIORITY_COLORS[priority] || PRIORITY_COLORS.NORMAL;
};
