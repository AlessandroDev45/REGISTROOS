// frontend/src/features/admin/components/config/fullInstanceTemplates.ts

export const DEPARTMENTS_TEMPLATE = {
    "departamentos": [
        {
            "nome": "MOTORES",
            "descricao": "Departamento de Motores Elétricos",
            "ativo": true
        },
        {
            "nome": "TRANSFORMADORES",
            "descricao": "Departamento de Transformadores",
            "ativo": true
        }
    ]
};

export const SECTORS_BY_DEPARTMENT_TEMPLATE = {
    "setores_por_departamento": [
        {
            "departamento": "MOTORES",
            "setores": [
                {
                    "nome": "LAB",
                    "descricao": "Laboratório de Ensaios Elétricos",
                    "area_tipo": "PRODUCAO",
                    "permite_apontamento": true,
                },
                {
                    "nome": "MECANICA",
                    "descricao": "Setor de Mecânica e Produção",
                    "area_tipo": "PRODUCAO",
                    "permite_apontamento": true,
                },
                {
                    "nome": "PCP",
                    "descricao": "Planejamento e Controle da Produção",
                    "area_tipo": "ADMINISTRATIVA",
                    "permite_apontamento": false,
                },
                {
                    "nome": "GESTAO",
                    "descricao": "Gestão e Administração",
                    "area_tipo": "ADMINISTRATIVA",
                    "permite_apontamento": false,
                }
            ]
        },
        {
            "departamento": "TRANSFORMADORES",
            "setores": [
                {
                    "nome": "LAB",
                    "descricao": "Laboratório de Ensaios Elétricos",
                    "area_tipo": "PRODUCAO",
                    "permite_apontamento": true,
                },
                {
                    "nome": "MECANICA",
                    "descricao": "Setor de Mecânica e Produção",
                    "area_tipo": "PRODUCAO",
                    "permite_apontamento": true,
                },
                {
                    "nome": "PCP",
                    "descricao": "Planejamento e Controle da Produção",
                    "area_tipo": "ADMINISTRATIVA",
                    "permite_apontamento": false,
                },
                {
                    "nome": "GESTAO",
                    "descricao": "Gestão e Administração",
                    "area_tipo": "ADMINISTRATIVA",
                    "permite_apontamento": false,
                }
            ]
        }
    ]
};

export const MACHINE_TYPES_TEMPLATE = {
    "tipos_maquina_padrao": [
        {
            "nome": "Motor Trifásico",
            "categoria": "MOTOR", // Mapped to 'departamento' in backend
            "descricao": "Motor elétrico trifásico de indução",
            "ativo": true // Default active
        },
        {
            "nome": "Motor Monofásico",
            "categoria": "MOTOR",
            "descricao": "Motor elétrico monofásico",
            "ativo": true
        },
        {
            "nome": "Transformador Distribuição",
            "categoria": "TRANSFORMADOR",
            "descricao": "Transformador de distribuição",
            "ativo": true
        },
        {
            "nome": "Transformador Potência",
            "categoria": "TRANSFORMADOR",
            "descricao": "Transformador de potência",
            "ativo": true
        }
    ]
};

export const ACTIVITY_TYPES_TEMPLATE = {
    "tipos_atividade_padrao": [
        {"nome_tipo": "Inspeção", "descricao": "Inspeção visual e dimensional", "ativo": true},
        {"nome_tipo": "Teste Elétrico", "descricao": "Ensaios elétricos de rotina", "ativo": true},
        {"nome_tipo": "Montagem", "descricao": "Montagem de componentes", "ativo": true},
        {"nome_tipo": "Desmontagem", "descricao": "Desmontagem para inspeção/reparo", "ativo": true},
        {"nome_tipo": "Reparo", "descricao": "Reparo ou substituição de peças", "ativo": true},
        {"nome_tipo": "Pintura", "descricao": "Processo de pintura e acabamento", "ativo": true},
        {"nome_tipo": "Embalagem", "descricao": "Preparação para expedição", "ativo": true}
    ]
};

export const ACTIVITY_DESCRIPTIONS_TEMPLATE = {
    "descricoes_atividade_padrao": [
        // LAB
        {"codigo": "LAB-001", "descricao": "Verificação de Resistência de Isolamento", "setor": "LAB", "ativo": true},
        {"codigo": "LAB-002", "descricao": "Teste de Hipot (Rigidez Dielétrica)", "setor": "LAB", "ativo": true},
        {"codigo": "LAB-003", "descricao": "Medição de Perdas em Vazio", "setor": "LAB", "ativo": true},
        // MECANICA
        {"codigo": "MEC-001", "descricao": "Inspeção Visual Componentes Mecânicos", "setor": "MECANICA", "ativo": true},
        {"codigo": "MEC-002", "descricao": "Substituição de Rolamentos", "setor": "MECANICA", "ativo": true},
        {"codigo": "MEC-003", "descricao": "Alinhamento de Eixo", "setor": "MECANICA", "ativo": true},
        // PCP
        {"codigo": "PCP-001", "descricao": "Emissão de Ordem de Produção", "setor": "PCP", "ativo": true},
        {"codigo": "PCP-002", "descricao": "Acompanhamento de Prazos", "setor": "PCP", "ativo": true},
        // GESTAO
        {"codigo": "GES-001", "descricao": "Análise de Relatórios de Produção", "setor": "GESTAO", "ativo": true}
    ]
};


export const FAULT_TYPES_TEMPLATE = {
    "tipos_falha_padrao": [
        // For LAB
        {"codigo": "FAL-LAB-001", "descricao": "Falha no Isolamento (Baixa Resistência)", "setor": "LAB", "ativo": true},
        {"codigo": "FAL-LAB-002", "descricao": "Curto-circuito Interno", "setor": "LAB", "ativo": true},
        {"codigo": "FAL-LAB-003", "descricao": "Valores Elétricos Fora de Tolerância", "setor": "LAB", "ativo": true},
        // For MECANICA
        {"codigo": "FAL-MEC-001", "descricao": "Desgaste Excessivo de Rolamento", "setor": "MECANICA", "ativo": true},
        {"codigo": "FAL-MEC-002", "descricao": "Desalinhamento Mecânico", "setor": "MECANICA", "ativo": true},
        {"codigo": "FAL-MEC-003", "descricao": "Componente Quebrado/Trincado", "setor": "MECANICA", "ativo": true}
    ]
};

export const REWORK_CAUSES_TEMPLATE = {
    "causas_retrabalho_padrao": [
        // For MOTORES department
        {"codigo": "CRM-001", "descricao": "Erro de Montagem - Eixo", "departamento": "MOTORES", "ativo": true},
        {"codigo": "CRM-002", "descricao": "Material com Defeito - Enrolamento", "departamento": "MOTORES", "ativo": true},
        {"codigo": "CRM-003", "descricao": "Falha de Processo - Teste Elétrico", "departamento": "MOTORES", "ativo": true},
        // For TRANSFORMADORES department
        {"codigo": "CRT-001", "descricao": "Erro de Fabricação - Núcleo", "departamento": "TRANSFORMADORES", "ativo": true},
        {"codigo": "CRT-002", "descricao": "Contaminação do Óleo", "departamento": "TRANSFORMADORES", "ativo": true},
        {"codigo": "CRT-003", "descricao": "Problema de Soldagem - Buchas", "departamento": "TRANSFORMADORES", "ativo": true}
    ]
};

// Placeholder for TesteContexto as it's more complex, requiring specific mappings
// This data will be created via specific logic in handleCreateFullInstance
export const TEST_TYPES_CONTEXT_TEMPLATE = {
    // This is a simplified representation. Actual creation logic will need to map
    // `setor`, `tipo_maquina`, `classificacao_temporal` from IDs.
    // The previous prompt had detailed structure, which indicates this is not a flat catalog.
    // It should be created in the `handleCreateFullInstance` based on the previously created entities.
};

// Placeholder for Atividade (Hierarchical, linking to Sector and possibly others)
export const ACTIVITIES_HIERARCHICAL_TEMPLATE = {
    // Similar to Test_Types_Context_Template, this is not a flat catalog.
    // It depends on Sector ID.
};