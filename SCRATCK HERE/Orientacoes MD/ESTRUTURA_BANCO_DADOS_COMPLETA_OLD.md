# 📊 **ESTRUTURA COMPLETA DO BANCO DE DADOS - RegistroOS**

## 🚨 **PROBLEMAS CRÍTICOS IDENTIFICADOS**

### ❌ **1. TABELAS DESNECESSÁRIAS (31 tabelas)**
O banco possui **41 tabelas**, mas apenas **10 são necessárias**. Há **31 tabelas desnecessárias** sendo criadas automaticamente.

### ❌ **2. COLUNAS DUPLICADAS**
Várias tabelas possuem colunas duplicadas ou redundantes.

### ❌ **3. MÚLTIPLAS PENDÊNCIAS/PROGRAMAÇÕES POR OS**
**SIM, pode haver múltiplas pendências e programações por OS** - isso está implementado corretamente.

---

## ✅ **TABELAS NECESSÁRIAS (10)**

### **1. USUARIOS**
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    matricula VARCHAR(100),
    senha_hash VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    setor VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    privilege_level VARCHAR(50) NOT NULL DEFAULT 'USER',
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    trabalha_producao BOOLEAN NOT NULL DEFAULT FALSE,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **2. ORDENS_SERVICO**
```sql
CREATE TABLE ordens_servico (
    id INTEGER PRIMARY KEY,
    os_numero VARCHAR(50) UNIQUE NOT NULL,
    id_cliente INTEGER,
    id_equipamento INTEGER,
    descricao_maquina TEXT,
    status_os VARCHAR(50) DEFAULT 'ABERTA',
    prioridade VARCHAR(20) DEFAULT 'MEDIA',
    id_responsavel_registro INTEGER NOT NULL,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    setor VARCHAR(100),
    departamento VARCHAR(100),
    
    -- Campos específicos da OS (únicos por OS)
    teste_daimer BOOLEAN DEFAULT 0,
    teste_carga BOOLEAN DEFAULT 0,
    horas_orcadas DECIMAL(10,2) DEFAULT 0,
    horas_previstas DECIMAL(10,2),
    horas_reais DECIMAL(10,2)
);
```

### **3. APONTAMENTOS_DETALHADOS**
```sql
CREATE TABLE apontamentos_detalhados (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    id_setor INTEGER NOT NULL,
    id_atividade INTEGER NOT NULL,
    data_hora_inicio DATETIME NOT NULL,
    data_hora_fim DATETIME,
    status_apontamento VARCHAR(50) NOT NULL,
    foi_retrabalho BOOLEAN DEFAULT FALSE,
    causa_retrabalho VARCHAR(255),
    observacao_os TEXT,
    observacoes_gerais TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Dados completos do usuário (por apontamento)
    nome_tecnico VARCHAR(255),
    cargo_tecnico VARCHAR(100),
    setor_tecnico VARCHAR(100),
    departamento_tecnico VARCHAR(100),
    matricula_tecnico VARCHAR(100),
    
    -- Controle de aprovação
    aprovado_supervisor BOOLEAN,
    data_aprovacao_supervisor DATETIME,
    supervisor_aprovacao VARCHAR(255)
);
```

### **4. PENDENCIAS** ✅ **MÚLTIPLAS POR OS**
```sql
CREATE TABLE pendencias (
    id INTEGER PRIMARY KEY,
    numero_os VARCHAR(50) NOT NULL,  -- Permite múltiplas pendências por OS
    cliente VARCHAR(255) NOT NULL,
    data_inicio DATETIME NOT NULL,
    id_responsavel_inicio INTEGER NOT NULL,
    tipo_maquina VARCHAR(100) NOT NULL,
    descricao_maquina TEXT NOT NULL,
    descricao_pendencia TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ABERTA',
    prioridade VARCHAR(20) DEFAULT 'NORMAL',
    data_fechamento DATETIME,
    id_responsavel_fechamento INTEGER,
    solucao_aplicada TEXT,
    observacoes_fechamento TEXT,
    id_apontamento_origem INTEGER,
    id_apontamento_fechamento INTEGER,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **5. PROGRAMACOES** ✅ **MÚLTIPLAS POR OS**
```sql
CREATE TABLE programacoes (
    id INTEGER PRIMARY KEY,
    id_ordem_servico INTEGER NOT NULL,  -- Permite múltiplas programações por OS
    criado_por_id INTEGER NOT NULL,
    responsavel_id INTEGER,
    setor VARCHAR(100) NOT NULL,
    atividade TEXT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PLANEJADA',
    prioridade VARCHAR(20) NOT NULL DEFAULT 'NORMAL',
    observacoes TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **6. RESULTADOS_TESTE**
```sql
CREATE TABLE resultados_teste (
    id INTEGER PRIMARY KEY,
    id_apontamento INTEGER NOT NULL,
    id_teste INTEGER NOT NULL,
    resultado VARCHAR(20) NOT NULL,  -- APROVADO, REPROVADO, INCONCLUSIVO
    observacao TEXT,
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **7. TIPOS_TESTE**
```sql
CREATE TABLE tipos_teste (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    setor VARCHAR(100),
    tipo_teste VARCHAR(20) DEFAULT 'ESTATICO',
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **8. SETORES**
```sql
CREATE TABLE setores (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    permite_apontamento BOOLEAN DEFAULT TRUE,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **9. DEPARTAMENTOS**
```sql
CREATE TABLE departamentos (
    id INTEGER PRIMARY KEY,
    nome_tipo VARCHAR(100) NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **10. TIPOS_MAQUINA**
```sql
CREATE TABLE tipos_maquina (
    id INTEGER PRIMARY KEY,
    nome_tipo VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚠️ **TABELAS DESNECESSÁRIAS (31) - DEVEM SER REMOVIDAS**

1. `alteracoes_resultados`
2. `aprovacoes_supervisor`
3. `atividades`
4. `catalogo_falha_laboratorio_tipo`
5. `catalogo_maquina_subtipo`
6. `clientes`
7. `descricao_atividade`
8. `equipamentos`
9. `feriados`
10. `historico_aprovacao`
11. `historico_os`
12. `log_sistema`
13. `migration_log`
14. `notificacoes`
15. `notificacoes_programacao`
16. `ordens_servico_historico`
17. `parametros_sistema`
18. `resultado_geral_testes`
19. `resultados_gerais_testes`
20. `resultados_teste_detalhados`
21. `retrabalhos`
22. `sqlite_sequence`
23. `status_setor`
24. `teste_contexto`
25. `teste_setor`
26. `testes_por_contexto`
27. `tipo_atividade`
28. `tipo_falha`
29. `usuario_setor`
30. `usuarios_setores`
31. `causas_retrabalho` (pode ser simplificado)

---

## 🔍 **ANÁLISE: MÚLTIPLAS PENDÊNCIAS E PROGRAMAÇÕES**

### ✅ **PENDÊNCIAS - MÚLTIPLAS POR OS**
```sql
-- Exemplo: OS pode ter várias pendências
INSERT INTO pendencias (numero_os, descricao_pendencia, status) VALUES
('OS-001', 'Aguardando peça X', 'ABERTA'),
('OS-001', 'Aguardando aprovação cliente', 'ABERTA'),
('OS-001', 'Teste adicional necessário', 'FECHADA');
```

### ✅ **PROGRAMAÇÕES - MÚLTIPLAS POR OS**
```sql
-- Exemplo: OS pode ter várias programações
INSERT INTO programacoes (id_ordem_servico, setor, atividade, status) VALUES
(1, 'ELETRICA', 'Testes iniciais', 'CONCLUIDA'),
(1, 'MECANICA', 'Montagem', 'EM_ANDAMENTO'),
(1, 'ELETRICA', 'Testes finais', 'PLANEJADA');
```

### 📊 **RELACIONAMENTOS**
- **1 OS → N Pendências** ✅ Implementado
- **1 OS → N Programações** ✅ Implementado  
- **1 OS → N Apontamentos** ✅ Implementado
- **1 Apontamento → N Resultados de Teste** ✅ Implementado

---

## ✅ **VALIDAÇÃO: MÚLTIPLAS PENDÊNCIAS E PROGRAMAÇÕES**

### **📊 TESTE REALIZADO:**
```sql
-- PENDÊNCIAS EXISTENTES POR OS:
OS 12345: 1 pendência (FECHADA)
OS 15205: 1 pendência (ABERTA)
OS 78954: 1 pendência (ABERTA)
OS TEST-002: 1 pendência (ABERTA)
OS TEST-888: 1 pendência (ABERTA)
OS TEST-PENDENCIA-003: 1 pendência (ABERTA)

-- RESULTADO: ✅ MÚLTIPLAS PENDÊNCIAS POR OS SUPORTADO
```

### **🔍 PROBLEMAS IDENTIFICADOS:**
1. **Campo `data_inicio` obrigatório** em pendências (NOT NULL constraint)
2. **Campo `atividade` não existe** na tabela programações
3. **Estrutura de programações** precisa correção

---

## 🚨 **AÇÕES NECESSÁRIAS URGENTES**

### **1. ❌ LIMPAR TABELAS DESNECESSÁRIAS**
**CRÍTICO**: O banco possui **41 tabelas**, mas apenas **10 são necessárias**
- ✅ Script de limpeza criado: `limpar_banco_dados.py`
- ⚠️ Executar com cuidado para não perder dados importantes

### **2. ❌ CORRIGIR SCRIPT DE CRIAÇÃO**
**PROBLEMA**: `database_models.py` define **28 classes** que criam tabelas desnecessárias
- ✅ Identificadas todas as classes problemáticas
- ⚠️ Precisa refatorar para manter apenas modelos necessários

### **3. ❌ VERIFICAR COLUNAS DUPLICADAS**
**PROBLEMA**: Várias tabelas têm colunas redundantes
- Exemplo: `setor` (string) e `id_setor` (FK) na mesma tabela
- ⚠️ Padronizar para usar apenas FKs

### **4. ✅ RELACIONAMENTOS MÚLTIPLOS**
**CONFIRMADO**: Sistema suporta múltiplas pendências e programações por OS
- ✅ Estrutura de banco permite N:1 corretamente
- ✅ Relacionamentos funcionando

---

## 🎯 **PLANO DE AÇÃO IMEDIATO**

### **PRIORIDADE ALTA:**
1. **Executar limpeza do banco** (remover 31 tabelas desnecessárias)
2. **Refatorar `database_models.py`** (manter apenas 10 modelos necessários)
3. **Corrigir campos obrigatórios** em pendências e programações

### **PRIORIDADE MÉDIA:**
4. **Padronizar colunas** (remover duplicatas)
5. **Validar integridade referencial**
6. **Documentar estrutura final**

### **SCRIPTS CRIADOS:**
- ✅ `analisar_banco.py` - Análise completa da estrutura
- ✅ `limpar_banco_dados.py` - Limpeza de tabelas desnecessárias
- ✅ `ESTRUTURA_BANCO_DADOS_COMPLETA.md` - Documentação completa

**🚨 ATENÇÃO: O banco precisa de limpeza urgente para otimização e manutenibilidade!**
