export const getStatusColorClass = (status: string): string => {
    switch (status?.toUpperCase()) {
        case 'FINALIZADA':
        case 'CONCLUIDO':
        case 'APROVADO':
            return 'bg-green-100 text-green-800';
        case 'EM_ANDAMENTO':
        case 'EXECUTANDO':
        case 'EM_ANALISE':
        case 'AGENDADO':
            return 'bg-blue-100 text-blue-800';
        case 'PENDENTE':
        case 'AGUARDANDO':
        case 'PAUSADO':
        case 'AGUARDANDO_APROVACAO':
            return 'bg-yellow-100 text-yellow-800';
        case 'ATRASADA':
        case 'ATRASADO':
        case 'REJEITADO':
        case 'CANCELADO':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
};

export const getPriorityColorClass = (prioridade: string): string => {
    switch (prioridade?.toUpperCase()) {
        case 'URGENTE':
            return 'bg-red-500 text-white'; // Or a lighter red if it's border
        case 'ALTA':
            return 'bg-orange-500 text-white'; // Or lighter orange
        case 'MEDIA':
        case 'NORMAL':
            return 'bg-yellow-500 text-white'; // Or lighter yellow
        case 'BAIXA':
            return 'bg-green-500 text-white'; // Or lighter green
        default:
            return 'bg-gray-500 text-white';
    }
};

export const getPriorityBorderColorClass = (prioridade: string): string => {
    switch (prioridade?.toUpperCase()) {
        case 'URGENTE':
            return 'border-red-200';
        case 'ALTA':
            return 'border-orange-200';
        case 'MEDIA':
        case 'NORMAL':
            return 'border-blue-200';
        case 'BAIXA':
            return 'border-gray-200';
        default:
            return 'border-gray-200';
    }
};

export const getTipoColorClass = (tipo: string): string => {
    switch (tipo?.toUpperCase()) {
      case 'MANUTENCAO': return 'bg-blue-100 text-blue-800';
      case 'TESTE': return 'bg-purple-100 text-purple-800';
      case 'MONTAGEM': return 'bg-green-100 text-green-800';
      case 'DESMONTAGEM': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
};