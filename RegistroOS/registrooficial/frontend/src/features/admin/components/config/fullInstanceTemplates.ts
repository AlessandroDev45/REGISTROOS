// frontend/src/features/admin/components/config/fullInstanceTemplates.ts
// DADOS DINÂMICOS - BUSCAR DA API

import api from '../../../../services/api';

// Função para buscar departamentos reais da API
export const getDepartmentsTemplate = async () => {
    try {
        const response = await api.get('/admin/departamentos');
        return {
            "departamentos": response.data.map((dept: any) => ({
                "nome": dept.nome_tipo,
                "descricao": dept.descricao,
                "ativo": dept.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar departamentos:', error);
        return { "departamentos": [] };
    }
};

// Função para buscar setores reais da API
export const getSectorsByDepartmentTemplate = async () => {
    try {
        const response = await api.get('/setores');
        const setoresPorDepartamento: any = {};

        response.data.forEach((setor: any) => {
            const dept = setor.departamento;
            if (!setoresPorDepartamento[dept]) {
                setoresPorDepartamento[dept] = [];
            }
            setoresPorDepartamento[dept].push({
                "nome": setor.nome,
                "descricao": setor.descricao,
                "area_tipo": setor.area_tipo,
                "permite_apontamento": setor.permite_apontamento
            });
        });

        return {
            "setores_por_departamento": Object.keys(setoresPorDepartamento).map(dept => ({
                "departamento": dept,
                "setores": setoresPorDepartamento[dept]
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar setores:', error);
        return { "setores_por_departamento": [] };
    }
};

// Função para buscar tipos de máquina reais da API
export const getMachineTypesTemplate = async () => {
    try {
        const response = await api.get('/admin/tipos-maquina');
        return {
            "tipos_maquina_padrao": response.data.map((tipo: any) => ({
                "nome_tipo": tipo.nome_tipo,
                "categoria": tipo.categoria,
                "subcategoria": tipo.subcategoria,
                "descricao": tipo.descricao,
                "ativo": tipo.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar tipos de máquina:', error);
        return { "tipos_maquina_padrao": [] };
    }
};

// Função para buscar tipos de atividade reais da API
export const getActivityTypesTemplate = async () => {
    try {
        const response = await api.get('/admin/tipos-atividade');
        return {
            "tipos_atividade_padrao": response.data.map((tipo: any) => ({
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "ativo": tipo.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar tipos de atividade:', error);
        return { "tipos_atividade_padrao": [] };
    }
};

// Função para buscar descrições de atividade reais da API
export const getActivityDescriptionsTemplate = async () => {
    try {
        const response = await api.get('/admin/descricoes-atividade');
        return {
            "descricoes_atividade_padrao": response.data.map((desc: any) => ({
                "codigo": desc.codigo,
                "descricao": desc.descricao,
                "ativo": desc.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar descrições de atividade:', error);
        return { "descricoes_atividade_padrao": [] };
    }
};

// Função para buscar causas de retrabalho reais da API
export const getReworkCausesTemplate = async () => {
    try {
        const response = await api.get('/admin/causas-retrabalho');
        return {
            "causas_retrabalho_padrao": response.data.map((causa: any) => ({
                "codigo": causa.codigo,
                "descricao": causa.descricao,
                "ativo": causa.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar causas de retrabalho:', error);
        return { "causas_retrabalho_padrao": [] };
    }
};

// Função para buscar tipos de falha reais da API
export const getFailureTypesTemplate = async () => {
    try {
        const response = await api.get('/admin/tipos-falha');
        return {
            "tipos_falha_padrao": response.data.map((falha: any) => ({
                "codigo": falha.codigo,
                "descricao": falha.descricao,
                "ativo": falha.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar tipos de falha:', error);
        return { "tipos_falha_padrao": [] };
    }
};

// Função para buscar contextos de teste reais da API
export const getTestTypesContextTemplate = async () => {
    try {
        const response = await api.get('/admin/tipos-teste');
        return {
            "contextos_teste": response.data.map((teste: any) => ({
                "nome": teste.nome,
                "tipo_teste": teste.tipo_teste,
                "descricao": teste.descricao,
                "ativo": teste.ativo
            }))
        };
    } catch (error) {
        console.error('Erro ao buscar contextos de teste:', error);
        return { "contextos_teste": [] };
    }
};

// Templates legados removidos - agora tudo vem da API
export const DEPARTMENTS_TEMPLATE = null; // REMOVIDO - usar getDepartmentsTemplate()
export const SECTORS_BY_DEPARTMENT_TEMPLATE = null; // REMOVIDO - usar getSectorsByDepartmentTemplate()
export const MACHINE_TYPES_TEMPLATE = null; // REMOVIDO - usar getMachineTypesTemplate()
export const ACTIVITY_TYPES_TEMPLATE = null; // REMOVIDO - usar getActivityTypesTemplate()
export const ACTIVITY_DESCRIPTIONS_TEMPLATE = null; // REMOVIDO - usar getActivityDescriptionsTemplate()
export const REWORK_CAUSES_TEMPLATE = null; // REMOVIDO - usar getReworkCausesTemplate()
export const FAILURE_TYPES_TEMPLATE = null; // REMOVIDO - usar getFailureTypesTemplate()
export const TEST_TYPES_CONTEXT_TEMPLATE = null; // REMOVIDO - usar getTestTypesContextTemplate()
