import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getOrdensServico,
  getOrdemServicoById,
  criarApontamentoSetor,
  listarApontamentosOS,
  registrarTesteSetor,
  listarTestesOS,
  createApontamento,
  getPendencias,
  updatePendencia,
  getProgramacoes,
  createProgramacao,
  getOsDisponiveisForPcp,
  fetchAtividadeTipos,
  fetchDescricaoAtividades,
  fetchFalhaLaboratorioTipos,
  fetchMaquinaSubTipos
} from '../services/api';
import { fetchTestesPorSetor, fetchAtividadesPorSetor } from '../services/catalogApi';
import {
    AtividadeTipoData, DescricaoAtividadeData, FalhaTipoData, TipoMaquinaData, TipoTesteData, CausaRetrabalhoData, SetorData, DepartamentoData,
    setorService, tipoMaquinaService, atividadeTipoService, descricaoAtividadeService, falhaTipoService, causaRetrabalhoService, tipoTesteService, departamentoService
} from '../services/adminApi';

// Ordem de Serviço queries
export const useOrdensServico = (filters?: any) => {
  return useQuery({
    queryKey: ['ordens-servico', filters],
    queryFn: () => getOrdensServico(filters),
  });
};

export const useOrdemServico = (osId: number) => {
  return useQuery({
    queryKey: ['ordem-servico', osId],
    queryFn: () => getOrdemServicoById(osId),
    enabled: !!osId,
  });
};

// Apontamentos queries and mutations
export const useApontamentosOS = (osId: number, setor?: string) => {
  return useQuery({
    queryKey: ['apontamentos', osId, setor],
    queryFn: () => listarApontamentosOS(osId, setor),
    enabled: !!osId,
  });
};

export const useCreateApontamentoSetor = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ osId, apontamentoData }: { osId: number; apontamentoData: any }) =>
      criarApontamentoSetor(osId, apontamentoData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['apontamentos', variables.osId] });
      queryClient.invalidateQueries({ queryKey: ['ordem-servico', variables.osId] });
    },
  });
};

export const useCreateApontamento = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createApontamento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ordens-servico'] });
      queryClient.invalidateQueries({ queryKey: ['apontamentos'] });
    },
  });
};

// Testes queries and mutations
export const useTestesOS = (osId: number, setor?: string) => {
  return useQuery({
    queryKey: ['testes', osId, setor],
    queryFn: () => listarTestesOS(osId, setor),
    enabled: !!osId,
  });
};

export const useRegistrarTesteSetor = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ osId, testeData }: { osId: number; testeData: any }) =>
      registrarTesteSetor(osId, testeData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['testes', variables.osId] });
      queryClient.invalidateQueries({ queryKey: ['ordem-servico', variables.osId] });
    },
  });
};

// Pendências queries and mutations
export const usePendencias = (filters?: any) => {
  return useQuery({
    queryKey: ['pendencias', filters],
    queryFn: () => getPendencias(filters),
  });
};

export const useUpdatePendencia = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, pendenciaData }: { id: number; pendenciaData: any }) =>
      updatePendencia(id, pendenciaData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendencias'] });
    },
  });
};

// PCP queries and mutations
export const useProgramacoes = (filters?: any) => {
  return useQuery({
    queryKey: ['programacoes', filters],
    queryFn: () => getProgramacoes(filters),
  });
};

export const useCreateProgramacao = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createProgramacao,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programacoes'] });
    },
  });
};

export const useOsDisponiveisForPcp = () => {
  return useQuery({
    queryKey: ['os-disponiveis-pcp'],
    queryFn: getOsDisponiveisForPcp,
  });
};

// Catálogos queries (using types from adminApi)
export const useAtividadeTipos = (setor?: string) => {
  return useQuery<AtividadeTipoData[]>({
    queryKey: ['atividade-tipos', setor],
    queryFn: () => fetchAtividadeTipos(setor),
  });
};

export const useDescricaoAtividades = (setor?: string) => {
  return useQuery<DescricaoAtividadeData[]>({
    queryKey: ['descricao-atividades', setor],
    queryFn: () => fetchDescricaoAtividades(setor),
  });
};

export const useFalhaLaboratorioTipos = (setor?: string) => {
  return useQuery<FalhaTipoData[]>({
    queryKey: ['falha-laboratorio-tipos', setor],
    queryFn: () => fetchFalhaLaboratorioTipos(setor),
  });
};

export const useMaquinaSubTipos = (setor?: string) => {
  return useQuery<TipoMaquinaData[]>({
    queryKey: ['maquina-subtipos', setor],
    queryFn: () => fetchMaquinaSubTipos(setor),
  });
};

export const useTestesPorSetor = (setor: string) => {
    return useQuery<TipoTesteData[]>({
      queryKey: ['testes-por-setor', setor],
      queryFn: () => fetchTestesPorSetor(setor),
      enabled: !!setor,
    });
  };

export const useAtividadesPorSetor = (setor: string) => {
    return useQuery<AtividadeTipoData[]>({ // Assuming it returns AtividadeTipoData
      queryKey: ['atividades-por-setor', setor],
      queryFn: () => fetchAtividadesPorSetor(setor),
      enabled: !!setor,
    });
};
// Admin API hooks
// Add hooks for adminApi services here, similar to the existing ones
export const useSetoresAdmin = () => {
    return useQuery<SetorData[]>({
        queryKey: ['admin-setores'],
        queryFn: setorService.getSetores,
    });
};

export const useCreateSetor = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: setorService.createSetor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-setores'] });
            queryClient.invalidateQueries({ queryKey: ['setores-cache'] }); // Invalidate global cache too
        },
    });
};

export const useUpdateSetor = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: SetorData }) => setorService.updateSetor(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-setores'] });
            queryClient.invalidateQueries({ queryKey: ['setores-cache'] });
        },
    });
};

export const useDeleteSetor = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => setorService.deleteSetor(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-setores'] });
            queryClient.invalidateQueries({ queryKey: ['setores-cache'] });
        },
    });
};

export const useTiposMaquinaAdmin = () => {
    return useQuery<TipoMaquinaData[]>({
        queryKey: ['admin-tipos-maquina'],
        queryFn: tipoMaquinaService.getTiposMaquina,
    });
};

export const useCreateTipoMaquina = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: tipoMaquinaService.createTipoMaquina,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-maquina'] });
        },
    });
};

export const useUpdateTipoMaquina = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: TipoMaquinaData }) => tipoMaquinaService.updateTipoMaquina(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-maquina'] });
        },
    });
};

export const useDeleteTipoMaquina = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => tipoMaquinaService.deleteTipoMaquina(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-maquina'] });
        },
    });
};

export const useAtividadesTipoAdmin = () => {
    return useQuery<AtividadeTipoData[]>({
        queryKey: ['admin-tipos-atividade'],
        queryFn: atividadeTipoService.getAtividadesTipo,
    });
};

export const useCreateAtividadeTipo = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: atividadeTipoService.createAtividadeTipo,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-atividade'] });
        },
    });
};

export const useUpdateAtividadeTipo = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: AtividadeTipoData }) => atividadeTipoService.updateAtividadeTipo(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-atividade'] });
        },
    });
};

export const useDeleteAtividadeTipo = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => atividadeTipoService.deleteAtividadeTipo(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-atividade'] });
        },
    });
};

export const useDescricoesAtividadeAdmin = () => {
    return useQuery<DescricaoAtividadeData[]>({
        queryKey: ['admin-descricoes-atividade'],
        queryFn: descricaoAtividadeService.getDescricoesAtividade,
    });
};

export const useCreateDescricaoAtividade = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: descricaoAtividadeService.createDescricaoAtividade,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-descricoes-atividade'] });
        },
    });
};

export const useUpdateDescricaoAtividade = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: DescricaoAtividadeData }) => descricaoAtividadeService.updateDescricaoAtividade(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-descricoes-atividade'] });
        },
    });
};

export const useDeleteDescricaoAtividade = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => descricaoAtividadeService.deleteDescricaoAtividade(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-descricoes-atividade'] });
        },
    });
};

export const useFalhasTipoAdmin = () => {
    return useQuery<FalhaTipoData[]>({
        queryKey: ['admin-tipos-falha'],
        queryFn: falhaTipoService.getFalhasTipo,
    });
};

export const useCreateFalhaTipo = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: falhaTipoService.createFalhaTipo,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-falha'] });
        },
    });
};

export const useUpdateFalhaTipo = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: FalhaTipoData }) => falhaTipoService.updateFalhaTipo(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-falha'] });
        },
    });
};

export const useDeleteFalhaTipo = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => falhaTipoService.deleteFalhaTipo(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-falha'] });
        },
    });
};

export const useCausasRetrabalhoAdmin = () => {
    return useQuery<CausaRetrabalhoData[]>({
        queryKey: ['admin-causas-retrabalho'],
        queryFn: causaRetrabalhoService.getCausasRetrabalho,
    });
};

export const useCreateCausaRetrabalho = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: causaRetrabalhoService.createCausaRetrabalho,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-causas-retrabalho'] });
        },
    });
};

export const useUpdateCausaRetrabalho = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: CausaRetrabalhoData }) => causaRetrabalhoService.updateCausaRetrabalho(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-causas-retrabalho'] });
        },
    });
};

export const useDeleteCausaRetrabalho = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => causaRetrabalhoService.deleteCausaRetrabalho(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-causas-retrabalho'] });
        },
    });
};

export const useTiposTesteAdmin = () => {
    return useQuery<TipoTesteData[]>({
        queryKey: ['admin-tipos-teste'],
        queryFn: () => tipoTesteService.getTiposTeste(),
    });
};

export const useCreateTipoTeste = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: tipoTesteService.createTipoTeste,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-teste'] });
        },
    });
};

export const useUpdateTipoTeste = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: TipoTesteData }) => tipoTesteService.updateTipoTeste(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-teste'] });
        },
    });
};

export const useDeleteTipoTeste = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => tipoTesteService.deleteTipoTeste(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-tipos-teste'] });
        },
    });
};

export const useDepartamentosAdmin = () => {
    return useQuery<DepartamentoData[]>({
        queryKey: ['admin-departamentos'],
        queryFn: departamentoService.getDepartamentos,
    });
};

export const useCreateDepartamento = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: departamentoService.createDepartamento,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-departamentos'] });
        },
    });
};

export const useUpdateDepartamento = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, data }: { id: number, data: DepartamentoData }) => departamentoService.updateDepartamento(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-departamentos'] });
        },
    });
};

export const useDeleteDepartamento = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (id: number) => departamentoService.deleteDepartamento(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin-departamentos'] });
        },
    });
};