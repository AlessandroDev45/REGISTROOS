// Teste das rotas administrativas corrigidas
// Execute este arquivo no console do navegador para testar as rotas

const API_BASE = 'http://localhost:3001/api';

// Função para testar uma rota POST
async function testarRotaPOST(endpoint, dados) {
    try {
        console.log(`🧪 Testando POST ${endpoint}...`);
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}` // Se necessário
            },
            credentials: 'include',
            body: JSON.stringify(dados)
        });
        
        console.log(`📊 Status: ${response.status}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ Sucesso:`, data);
            return { success: true, data };
        } else {
            const error = await response.text();
            console.log(`❌ Erro:`, error);
            return { success: false, error, status: response.status };
        }
    } catch (error) {
        console.log(`💥 Erro de rede:`, error);
        return { success: false, error: error.message };
    }
}

// Função para testar uma rota GET
async function testarRotaGET(endpoint) {
    try {
        console.log(`🧪 Testando GET ${endpoint}...`);
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}` // Se necessário
            },
            credentials: 'include'
        });
        
        console.log(`📊 Status: ${response.status}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ Sucesso:`, data);
            return { success: true, data };
        } else {
            const error = await response.text();
            console.log(`❌ Erro:`, error);
            return { success: false, error, status: response.status };
        }
    } catch (error) {
        console.log(`💥 Erro de rede:`, error);
        return { success: false, error: error.message };
    }
}

// Dados de teste
const dadosTesteTipoAtividade = {
    nome_tipo: "TESTE_ATIVIDADE_" + Date.now(),
    descricao: "Atividade de teste criada automaticamente",
    departamento: "MOTORES",
    setor: "MONTAGEM",
    categoria: "MOTOR",
    ativo: true
};

const dadosTesteTipoMaquina = {
    nome_tipo: "TESTE_MAQUINA_" + Date.now(),
    descricao: "Máquina de teste criada automaticamente",
    departamento: "MOTORES",
    setor: "MONTAGEM",
    categoria: "MOTOR",
    ativo: true
};

const dadosTesteSetor = {
    nome: "TESTE_SETOR_" + Date.now(),
    descricao: "Setor de teste criado automaticamente",
    departamento: "MOTORES",
    ativo: true
};

const dadosTesteTipoFalha = {
    codigo: "TF" + Date.now(),
    descricao: "Tipo de falha de teste criado automaticamente",
    departamento: "MOTORES",
    setor: "MONTAGEM",
    ativo: true
};

const dadosTesteDescricaoAtividade = {
    codigo: "DA" + Date.now(),
    descricao: "Descrição de atividade de teste criada automaticamente",
    setor: "MONTAGEM",
    ativo: true
};

// Função principal de teste
async function executarTestes() {
    console.log("🚀 Iniciando testes das rotas administrativas...\n");
    
    // Testar rotas GET primeiro
    console.log("=== TESTANDO ROTAS GET ===");
    await testarRotaGET('/admin/setores/');
    await testarRotaGET('/admin/tipos-maquina/');
    await testarRotaGET('/admin/tipos-atividade/');
    await testarRotaGET('/admin/tipos-falha/');
    await testarRotaGET('/admin/descricoes-atividade/');
    await testarRotaGET('/api/categorias-maquina');
    
    console.log("\n=== TESTANDO ROTAS POST ===");
    
    // Testar rotas POST
    await testarRotaPOST('/admin/setores/', dadosTesteSetor);
    await testarRotaPOST('/admin/tipos-maquina/', dadosTesteTipoMaquina);
    await testarRotaPOST('/admin/tipos-atividade/', dadosTesteTipoAtividade);
    await testarRotaPOST('/admin/tipos-falha/', dadosTesteTipoFalha);
    await testarRotaPOST('/admin/descricoes-atividade/', dadosTesteDescricaoAtividade);
    
    console.log("\n✨ Testes concluídos!");
}

// Executar os testes
console.log("Para executar os testes, chame: executarTestes()");

// Exportar funções para uso manual
window.testarRotasAdmin = {
    executarTestes,
    testarRotaPOST,
    testarRotaGET,
    dadosTesteTipoAtividade,
    dadosTesteTipoMaquina,
    dadosTesteSetor,
    dadosTesteTipoFalha,
    dadosTesteDescricaoAtividade
};
