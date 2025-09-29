import { STATUS_COLORS, STATUS_OS, PRIORITY_COLORS, PRIORIDADES, TIPOS_ATIVIDADE } from './constants';

export const getStatusColorClass = (status: string): string => {
    switch (status?.toUpperCase()) {
        case STATUS_OS.FINALIZADA:
        case 'CONCLUIDO':
        case 'APROVADO':
            return STATUS_COLORS.SUCCESS;
        case STATUS_OS.EM_ANDAMENTO:
        case 'EXECUTANDO':
        case 'EM_ANALISE':
        case 'AGENDADO':
            return STATUS_COLORS.INFO;
        case STATUS_OS.PENDENTE:
        case 'AGUARDANDO':
        case 'PAUSADO':
        case 'AGUARDANDO_APROVACAO':
            return STATUS_COLORS.WARNING;
        case 'ATRASADA':
        case 'ATRASADO':
        case 'REJEITADO':
        case STATUS_OS.CANCELADA:
            return STATUS_COLORS.ERROR;
        default:
            return STATUS_COLORS.DEFAULT;
    }
};

export const getPriorityColorClass = (prioridade: string): string => {
    switch (prioridade?.toUpperCase()) {
        case PRIORIDADES.URGENTE:
            return STATUS_COLORS.ERROR;
        case PRIORIDADES.ALTA:
            return 'bg-orange-100 text-orange-800';
        case PRIORIDADES.MEDIA:
        case PRIORIDADES.NORMAL:
            return STATUS_COLORS.INFO;
        case PRIORIDADES.BAIXA:
            return STATUS_COLORS.DEFAULT;
        default:
            return STATUS_COLORS.DEFAULT;
    }
};

export const getPriorityTextColorClass = (prioridade: string): string => {
    switch (prioridade?.toUpperCase()) {
        case PRIORIDADES.URGENTE: return 'text-red-600';
        case PRIORIDADES.ALTA: return 'text-orange-600';
        case PRIORIDADES.MEDIA:
        case PRIORIDADES.NORMAL: return 'text-blue-600';
        case PRIORIDADES.BAIXA: return 'text-gray-600';
        default: return 'text-gray-600';
    }
};

export const getPriorityBorderColorClass = (prioridade: string): string => {
    const prioridadeUpper = prioridade?.toUpperCase() as keyof typeof PRIORITY_COLORS;
    return PRIORITY_COLORS[prioridadeUpper] || PRIORITY_COLORS[PRIORIDADES.BAIXA];
};

export const getTipoColorClass = (tipo: string): string => {
    switch (tipo?.toUpperCase()) {
      case TIPOS_ATIVIDADE.MANUTENCAO: return STATUS_COLORS.INFO;
      case TIPOS_ATIVIDADE.TESTE: return 'bg-purple-100 text-purple-800';
      case TIPOS_ATIVIDADE.MONTAGEM: return STATUS_COLORS.SUCCESS;
      case TIPOS_ATIVIDADE.DESMONTAGEM: return 'bg-orange-100 text-orange-800';
      case TIPOS_ATIVIDADE.INSPECAO: return STATUS_COLORS.WARNING;
      case TIPOS_ATIVIDADE.REPARO: return STATUS_COLORS.ERROR;
      default: return STATUS_COLORS.DEFAULT;
    }
};