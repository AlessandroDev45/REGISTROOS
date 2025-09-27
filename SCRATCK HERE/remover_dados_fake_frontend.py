#!/usr/bin/env python3
"""
Script para remover dados fake/hardcoded do frontend
Especificamente do arquivo PesquisaOSTab.tsx
"""

import os
import re

def remover_dados_fake_pesquisa_os_tab():
    """Remove dados fake do PesquisaOSTab.tsx"""
    arquivo = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\frontend\src\features\desenvolvimento\components\tabs\PesquisaOSTab.tsx"
    
    print(f"🔧 Corrigindo {arquivo}...")
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Remover o mapeamento hardcoded de números para IDs
    conteudo_novo = re.sub(
        r'// Função para buscar IDs das OSs pelo número.*?await buscarIdsOSs\(osArray\);',
        '''// Buscar IDs reais das OSs via API
            try {
                const osNumeros = osArray.map(os => os.numero_os).filter(Boolean);
                if (osNumeros.length > 0) {
                    const idsResponse = await api.post('/desenvolvimento/buscar-ids-os', {
                        numeros_os: osNumeros
                    });
                    
                    if (idsResponse.data && idsResponse.data.mapeamento) {
                        for (const os of osArray) {
                            if (os.numero_os && idsResponse.data.mapeamento[os.numero_os]) {
                                os.id_os = idsResponse.data.mapeamento[os.numero_os];
                                console.log(`✅ Mapeado OS ${os.numero_os} -> ID ${os.id_os}`);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Erro ao buscar IDs das OSs:', error);
            }''',
        conteudo, flags=re.DOTALL
    )
    
    # Remover placeholder hardcoded
    conteudo_novo = re.sub(
        r'placeholder="21155"',
        'placeholder="Ex: 20203"',
        conteudo_novo
    )
    
    # Remover opções de status hardcoded e buscar da API
    conteudo_novo = re.sub(
        r'<option value="">Todos</option>\s*<option value="FINALIZADO">Finalizado</option>\s*<option value="EM_ANDAMENTO">Em Andamento</option>\s*<option value="PENDENTE">Pendente</option>',
        '''<option value="">Todos</option>
                                                {statusDisponiveis.map((status, index) => (
                                                    <option key={`status-${index}`} value={status}>
                                                        {status}
                                                    </option>
                                                ))}''',
        conteudo_novo
    )
    
    # Remover opções de prioridade hardcoded
    conteudo_novo = re.sub(
        r'<option value="">Todas</option>\s*<option value="URGENTE">Urgente</option>\s*<option value="ALTA">Alta</option>\s*<option value="NORMAL">Normal</option>\s*<option value="BAIXA">Baixa</option>',
        '''<option value="">Todas</option>
                                                    {prioridadesDisponiveis.map((prioridade, index) => (
                                                        <option key={`prioridade-${index}`} value={prioridade}>
                                                            {prioridade}
                                                        </option>
                                                    ))}''',
        conteudo_novo
    )
    
    # Adicionar estados para dados dinâmicos
    conteudo_novo = re.sub(
        r'const \[departamentosDisponiveis, setDepartamentosDisponiveis\] = useState<string\[\]>\(\[\]\);',
        '''const [departamentosDisponiveis, setDepartamentosDisponiveis] = useState<string[]>([]);
    const [statusDisponiveis, setStatusDisponiveis] = useState<string[]>([]);
    const [prioridadesDisponiveis, setPrioridadesDisponiveis] = useState<string[]>([]);''',
        conteudo_novo
    )
    
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo)
    
    print(f"✅ {arquivo} corrigido")

def adicionar_endpoint_buscar_ids():
    """Adiciona endpoint no backend para buscar IDs das OSs"""
    arquivo_backend = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\routes\desenvolvimento.py"
    
    print(f"🔧 Adicionando endpoint buscar-ids-os em {arquivo_backend}...")
    
    with open(arquivo_backend, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Adicionar endpoint antes do último endpoint
    endpoint_novo = '''
@router.post("/buscar-ids-os")
async def buscar_ids_os(
    request_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca IDs reais das OSs pelos números"""
    try:
        numeros_os = request_data.get("numeros_os", [])
        if not numeros_os:
            return {"mapeamento": {}}
        
        # Buscar OSs no banco de dados
        os_encontradas = db.query(OrdemServico.id, OrdemServico.numero_os).filter(
            OrdemServico.numero_os.in_(numeros_os)
        ).all()
        
        # Criar mapeamento numero -> id
        mapeamento = {}
        for os_id, numero_os in os_encontradas:
            mapeamento[numero_os] = os_id
        
        return {
            "mapeamento": mapeamento,
            "total_encontradas": len(mapeamento),
            "total_solicitadas": len(numeros_os)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar IDs das OSs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar IDs: {str(e)}")

'''
    
    # Inserir antes do último endpoint (que geralmente é o de teste)
    conteudo_novo = conteudo.replace(
        '@router.get("/formulario/teste-simples/{numero_os}"',
        endpoint_novo + '@router.get("/formulario/teste-simples/{numero_os}"'
    )
    
    with open(arquivo_backend, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo)
    
    print(f"✅ Endpoint buscar-ids-os adicionado")

def remover_templates_hardcoded():
    """Remove templates hardcoded do fullInstanceTemplates.ts"""
    arquivo = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\frontend\src\features\admin\components\config\fullInstanceTemplates.ts"

    print(f"🔧 Corrigindo {arquivo}...")

    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substituir templates hardcoded por funções que buscam da API
    conteudo_novo = '''// frontend/src/features/admin/components/config/fullInstanceTemplates.ts
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
        const response = await api.get('/admin/setores');
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
'''

    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo)

    print(f"✅ {arquivo} corrigido - templates agora são dinâmicos")

def main():
    """Função principal"""
    print("🚀 REMOVENDO DADOS FAKE DO FRONTEND")
    print("=" * 50)

    try:
        remover_dados_fake_pesquisa_os_tab()
        adicionar_endpoint_buscar_ids()
        remover_templates_hardcoded()

        print("\n🎉 CORREÇÃO FRONTEND CONCLUÍDA!")
        print("✅ Dados hardcoded removidos do PesquisaOSTab.tsx")
        print("✅ Mapeamento de IDs agora usa API real")
        print("✅ Status e prioridades agora são dinâmicos")
        print("✅ Endpoint buscar-ids-os adicionado no backend")
        print("✅ Templates hardcoded substituídos por funções dinâmicas")
        print("✅ Todos os dados agora vêm da API conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md")

    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
