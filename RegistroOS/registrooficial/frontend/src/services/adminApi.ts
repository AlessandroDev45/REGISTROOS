import api from './api';
import { Atividade } from '../pages/common/TiposApi'; // Import the consolidated Atividade type

export interface SetorData {
    id?: number;
    nome: string; // Frontend usa 'nome', backend recebe como 'nome' via alias
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    descricao: string;
    ativo: boolean;
    area_tipo?: string;
    supervisor_responsavel?: string;
    permite_apontamento?: boolean;
}

export interface TipoMaquinaData {
    id?: number;
    nome: string; // Frontend usa 'nome', backend recebe como 'nome' via alias (nome_tipo na DB)
    categoria: string;
    subcategoria?: string[]; // Lista de strings (JSON no backend)
    descricao: string;
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    ativo: boolean;
}

export interface AtividadeTipoData { // Renamed from TipoAtividadeData to avoid confusion with Atividade interface
    id?: number;
    nome: string; // Frontend usa 'nome', backend recebe como 'nome' via alias (nome_tipo na DB)
    descricao: string;
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    setor: string; // Nome do setor (para exibição)
    id_setor?: number; // ID do setor (para envio ao backend)
    categoria: string;
    ativo: boolean;
}

export interface DescricaoAtividadeData {
    id?: number;
    codigo: string;
    descricao: string;
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    setor: string; // Nome do setor (para exibição)
    id_setor?: number; // ID do setor (para envio ao backend)
    categoria?: string; // Categoria da descrição
    ativo: boolean;
}

export interface FalhaTipoData {
    id?: number;
    codigo: string;
    descricao: string;
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    setor: string; // Nome do setor (para exibição)
    id_setor?: number; // ID do setor (para envio ao backend)
    categoria?: string; // Categoria da falha
    ativo: boolean;
}

export interface CausaRetrabalhoData {
    id?: number;
    codigo: string;
    descricao: string;
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    setor: string; // Nome do setor (para exibição)
    id_setor?: number; // ID do setor (para envio ao backend)
    categoria?: string; // Categoria da causa
    ativo: boolean;
}

export interface TipoTesteData {
    id?: number;
    nome: string;
    departamento: string; // Nome do departamento (para exibição)
    id_departamento?: number; // ID do departamento (para envio ao backend)
    setor: string; // Nome do setor (para exibição) - OBRIGATÓRIO
    id_setor?: number; // ID do setor (para envio ao backend)
    tipo_teste: string; // Campo tipo_teste conforme database
    descricao: string;
    ativo: boolean;
    tipo_maquina?: string; // Adicionado campo tipo_maquina para compatibilidade
    categoria?: string; // Novo campo categoria: Visual, Elétricos, Mecânicos
    subcategoria?: number; // Novo campo subcategoria: 0 = Padrão, 1 = Especiais
}

export interface DepartamentoData {
    id?: number;
    nome: string; // Frontend usa 'nome', backend recebe como 'nome' via alias (nome_tipo na DB)
    descricao: string;
    ativo: boolean;
}

// CentroCustoData é um alias para DepartamentoData (mesma tabela)
export interface CentroCustoData {
    id?: number;
    nome: string;  // Mapeia para nome_tipo na tabela departamentos
    codigo?: string;  // Campo opcional para compatibilidade
    departamento?: string;  // Campo opcional para compatibilidade
    descricao: string;
    ativo: boolean;
}


// Services atualizados para usar as rotas corretas do backend
export const setorService = {
    getSetores: () => api.get<SetorData[]>('/admin/setores').then(res => res.data),  // CORRIGIDO: usar rota admin
    getSetorById: (id: number) => api.get<SetorData>(`/admin/setores/${id}`).then(res => res.data),
    createSetor: (data: SetorData) => api.post<SetorData>('/admin/setores', data).then(res => res.data),
    updateSetor: (id: number, data: SetorData) => api.put<SetorData>(`/admin/setores/${id}`, data).then(res => res.data),
    deleteSetor: (id: number) => api.delete(`/admin/setores/${id}`).then(res => res.data),
};

export const tipoMaquinaService = {
    getTiposMaquina: () => api.get<TipoMaquinaData[]>('/admin/tipos-maquina').then(res => res.data),
    getTipoMaquinaById: (id: number) => api.get<TipoMaquinaData>(`/admin/tipos-maquina/${id}`).then(res => res.data),
    createTipoMaquina: (data: TipoMaquinaData) => api.post<TipoMaquinaData>('/admin/tipos-maquina', data).then(res => res.data),
    updateTipoMaquina: (id: number, data: TipoMaquinaData) => api.put<TipoMaquinaData>(`/admin/tipos-maquina/${id}`, data).then(res => res.data),
    deleteTipoMaquina: (id: number) => api.delete(`/admin/tipos-maquina/${id}`).then(res => res.data),
};

// Serviço para buscar categorias de máquinas (para uso em formulários)
export const categoriaService = {
    getCategoriasMaquina: () => api.get<string[]>('/admin/categorias-maquina/').then(res => res.data),
};

// ... Adicione outros serviços conforme necessário

export const atividadeTipoService = {
    getAtividadesTipo: () => api.get<AtividadeTipoData[]>('/admin/tipos-atividade').then(res => res.data),
    getAtividadesPorTipoMaquina: (tipoMaquina: string) => api.get<AtividadeTipoData[]>(`/admin/tipos-atividade?tipo_maquina=${encodeURIComponent(tipoMaquina)}`).then(res => res.data),
    getAtividadeTipoById: (id: number) => api.get<AtividadeTipoData>(`/admin/tipos-atividade/${id}`).then(res => res.data),
    createAtividadeTipo: (data: AtividadeTipoData) => api.post<AtividadeTipoData>('/admin/tipos-atividade', data).then(res => res.data),
    updateAtividadeTipo: (id: number, data: AtividadeTipoData) => api.put<AtividadeTipoData>(`/admin/tipos-atividade/${id}`, data).then(res => res.data),
    deleteAtividadeTipo: (id: number) => api.delete(`/admin/tipos-atividade/${id}`).then(res => res.data),
};

// ... Adicione outros serviços conforme necessário

export const descricaoAtividadeService = {
    getDescricoesAtividade: () => api.get<DescricaoAtividadeData[]>('/admin/descricoes-atividade').then(res => res.data),
    getDescricaoAtividadeById: (id: number) => api.get<DescricaoAtividadeData>(`/admin/descricoes-atividade/${id}`).then(res => res.data),
    createDescricaoAtividade: (data: DescricaoAtividadeData) => api.post<DescricaoAtividadeData>('/admin/descricoes-atividade', data).then(res => res.data),
    updateDescricaoAtividade: (id: number, data: DescricaoAtividadeData) => api.put<DescricaoAtividadeData>(`/admin/descricoes-atividade/${id}`, data).then(res => res.data),
    deleteDescricaoAtividade: (id: number) => api.delete(`/admin/descricoes-atividade/${id}`).then(res => res.data),
};

// ... Adicione outros serviços conforme necessário

export const falhaTipoService = {
    getFalhasTipo: () => api.get<FalhaTipoData[]>('/admin/tipos-falha').then(res => res.data),
    getFalhaTipoById: (id: number) => api.get<FalhaTipoData>(`/admin/tipos-falha/${id}`).then(res => res.data),
    createFalhaTipo: (data: FalhaTipoData) => api.post<FalhaTipoData>('/admin/tipos-falha', data).then(res => res.data),
    updateFalhaTipo: (id: number, data: FalhaTipoData) => api.put<FalhaTipoData>(`/admin/tipos-falha/${id}`, data).then(res => res.data),
    deleteFalhaTipo: (id: number) => api.delete(`/admin/tipos-falha/${id}`).then(res => res.data),
};

export const tipoTesteService = {
    getTiposTeste: () => api.get<TipoTesteData[]>('/admin/tipos-teste').then(res => res.data),
    getTipoTesteById: (id: number) => api.get<TipoTesteData>(`/admin/tipos-teste/${id}`).then(res => res.data),
    createTipoTeste: (data: TipoTesteData) => api.post<TipoTesteData>('/admin/tipos-teste', data).then(res => res.data),
    updateTipoTeste: (id: number, data: TipoTesteData) => api.put<TipoTesteData>(`/admin/tipos-teste/${id}`, data).then(res => res.data),
    deleteTipoTeste: (id: number) => api.delete(`/admin/tipos-teste/${id}`).then(res => res.data),
};

export const causaRetrabalhoService = {
    getCausasRetrabalho: () => api.get<CausaRetrabalhoData[]>('/admin/causas-retrabalho').then(res => res.data),
    getCausaRetrabalhoById: (id: number) => api.get<CausaRetrabalhoData>(`/admin/causas-retrabalho/${id}`).then(res => res.data),
    createCausaRetrabalho: (data: CausaRetrabalhoData) => api.post<CausaRetrabalhoData>('/admin/causas-retrabalho', data).then(res => res.data),
    updateCausaRetrabalho: (id: number, data: CausaRetrabalhoData) => api.put<CausaRetrabalhoData>(`/admin/causas-retrabalho/${id}`, data).then(res => res.data),
    deleteCausaRetrabalho: (id: number) => api.delete(`/admin/causas-retrabalho/${id}`).then(res => res.data),
};

// ... Adicione outros serviços conforme necessário

export const departamentoService = { // Serviço para Departamentos
    getDepartamentos: () => api.get<DepartamentoData[]>('/admin/departamentos').then(res => res.data),
    getDepartamentoById: (id: number) => api.get<DepartamentoData>(`/admin/departamentos/${id}`).then(res => res.data),
    createDepartamento: (data: DepartamentoData) => api.post<DepartamentoData>('/admin/departamentos', data).then(res => res.data),
    updateDepartamento: (id: number, data: DepartamentoData) => api.put<DepartamentoData>(`/admin/departamentos/${id}`, data).then(res => res.data),
    deleteDepartamento: (id: number) => api.delete(`/admin/departamentos/${id}`).then(res => res.data),
};

// CentroCustoService usa a mesma API de departamentos mas mapeia os dados
export const centroCustoService = {
    getCentrosCusto: async (): Promise<CentroCustoData[]> => {
        const departamentos = await api.get<DepartamentoData[]>('/admin/departamentos').then(res => res.data);
        return departamentos.map(dept => ({
            id: dept.id,
            nome: dept.nome_tipo,  // Mapear nome_tipo para nome
            codigo: `DEPT-${dept.id}`,  // Gerar código baseado no ID
            departamento: dept.nome_tipo,  // Para compatibilidade
            descricao: dept.descricao,
            ativo: dept.ativo
        }));
    },
    getCentroCustoById: async (id: number): Promise<CentroCustoData> => {
        const dept = await api.get<DepartamentoData>(`/admin/departamentos/${id}`).then(res => res.data);
        return {
            id: dept.id,
            nome: dept.nome_tipo,
            codigo: `DEPT-${dept.id}`,
            departamento: dept.nome_tipo,
            descricao: dept.descricao,
            ativo: dept.ativo
        };
    },
    createCentroCusto: async (data: CentroCustoData): Promise<CentroCustoData> => {
        const deptData = {
            nome_tipo: data.nome,
            descricao: data.descricao,
            ativo: data.ativo
        };
        const result = await api.post<DepartamentoData>('/admin/departamentos', deptData).then(res => res.data);
        return {
            id: result.id,
            nome: result.nome_tipo,
            codigo: `DEPT-${result.id}`,
            departamento: result.nome_tipo,
            descricao: result.descricao,
            ativo: result.ativo
        };
    },
    updateCentroCusto: async (id: number, data: CentroCustoData): Promise<CentroCustoData> => {
        const deptData: DepartamentoData = {
            id: id,
            nome_tipo: data.nome,
            descricao: data.descricao,
            ativo: data.ativo
        };
        const result = await api.put<DepartamentoData>(`/admin/departamentos/${id}`, deptData).then(res => res.data);
        return {
            id: result.id,
            nome: result.nome_tipo,
            codigo: `DEPT-${result.id}`,
            departamento: result.nome_tipo,
            descricao: result.descricao,
            ativo: result.ativo
        };
    },
    deleteCentroCusto: (id: number) => api.delete(`/admin/departamentos/${id}`).then(res => res.data),
};

// ... Adicione outros serviços conforme necessário</search>


// Renamed from getAll to a more specific name, it was used by AdminPage previously
// The original `getAll` calls in `AdminPage` were custom for each type, so I'm leaving
// the specific services as is and will adjust `AdminPage` to use them directly.
// If you need a generic `getAll` that fetches *all* types of entities, it would be a separate, more complex function.

// Note: The previous `setorService.getDepartamentos()` was a quick fix in SetorForm.tsx.
// Services properly exported above
