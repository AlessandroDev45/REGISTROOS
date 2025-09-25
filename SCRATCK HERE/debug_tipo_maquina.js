// Script para debugar o problema do erro 500 em tipos de máquina
// Execute no console do navegador

const API_BASE = 'http://localhost:3001/api';

// Dados de teste mínimos
const dadosMinimos = {
    nome_tipo: "TESTE_DEBUG_" + Date.now(),
    categoria: "MOTOR",
    descricao: "Teste de debug",
    departamento: "MOTORES",
    setor: "MONTAGEM",
    ativo: true
};

// Dados completos com todos os campos possíveis
const dadosCompletos = {
    nome_tipo: "TESTE_COMPLETO_" + Date.now(),
    categoria: "MOTOR",
    descricao: "Teste completo com todos os campos",
    departamento: "MOTORES",
    setor: "MONTAGEM",
    ativo: true,
    campos_teste_resultado: "",
    especificacoes_tecnicas: "",
    id_departamento: null,
    data_criacao: null,
    data_ultima_atualizacao: null
};

async function testarCriacaoTipoMaquina(dados, nome) {
    try {
        console.log(`🧪 Testando criação de tipo de máquina: ${nome}`);
        console.log('📤 Dados enviados:', JSON.stringify(dados, null, 2));
        
        const response = await fetch(`${API_BASE}/admin/tipos-maquina/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
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
            const errorText = await response.text();
            console.log(`❌ Erro ${response.status}:`, errorText);
            
            // Tentar parsear como JSON se possível
            try {
                const errorJson = JSON.parse(errorText);
                console.log(`📋 Detalhes do erro:`, errorJson);
            } catch (e) {
                console.log(`📋 Erro como texto:`, errorText);
            }
            
            return { success: false, error: errorText, status: response.status };
        }
    } catch (error) {
        console.log(`💥 Erro de rede:`, error);
        return { success: false, error: error.message };
    }
}

async function testarGetTiposMaquina() {
    try {
        console.log('🧪 Testando GET tipos de máquina...');
        
        const response = await fetch(`${API_BASE}/admin/tipos-maquina/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            credentials: 'include'
        });
        
        console.log(`📊 Status: ${response.status}`);
        
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ GET Sucesso:`, data);
            
            if (data.length > 0) {
                console.log(`📋 Exemplo de tipo de máquina existente:`, data[0]);
            }
            
            return { success: true, data };
        } else {
            const error = await response.text();
            console.log(`❌ GET Erro:`, error);
            return { success: false, error };
        }
    } catch (error) {
        console.log(`💥 GET Erro de rede:`, error);
        return { success: false, error: error.message };
    }
}

async function executarDebug() {
    console.log("🚀 Iniciando debug do erro 500 em tipos de máquina...\n");
    
    // Primeiro, testar GET para ver a estrutura dos dados existentes
    console.log("=== TESTANDO GET PARA VER ESTRUTURA ===");
    await testarGetTiposMaquina();
    
    console.log("\n=== TESTANDO POST COM DADOS MÍNIMOS ===");
    await testarCriacaoTipoMaquina(dadosMinimos, "Dados Mínimos");
    
    console.log("\n=== TESTANDO POST COM DADOS COMPLETOS ===");
    await testarCriacaoTipoMaquina(dadosCompletos, "Dados Completos");
    
    console.log("\n✨ Debug concluído!");
}

// Função para testar campos individuais
async function testarCampoIndividual(campo, valor) {
    const dadosBase = {
        nome_tipo: `TESTE_${campo.toUpperCase()}_` + Date.now(),
        categoria: "MOTOR",
        descricao: "Teste de campo individual",
        departamento: "MOTORES",
        setor: "MONTAGEM",
        ativo: true
    };
    
    dadosBase[campo] = valor;
    
    console.log(`🧪 Testando campo: ${campo} = ${valor}`);
    return await testarCriacaoTipoMaquina(dadosBase, `Campo ${campo}`);
}

// Exportar funções para uso manual
window.debugTipoMaquina = {
    executarDebug,
    testarCriacaoTipoMaquina,
    testarGetTiposMaquina,
    testarCampoIndividual,
    dadosMinimos,
    dadosCompletos
};

console.log("Para executar o debug, chame: debugTipoMaquina.executarDebug()");
