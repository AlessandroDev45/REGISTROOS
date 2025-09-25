# 🔍 ANÁLISE DE CAMPOS DUPLICADOS E SIMILARES

## 📊 **CAMPOS PROBLEMÁTICOS IDENTIFICADOS**

### ⚠️ **1. TABELA `ordens_servico` - CAMPOS DE STATUS DUPLICADOS**

```sql
-- PROBLEMA: Dois campos de status com significados similares
status_os varchar           -- Status específico da OS
status_geral varchar        -- Status geral (redundante?)

-- RECOMENDAÇÃO: Manter apenas um campo de status
-- SOLUÇÃO: Usar apenas 'status_os' e remover 'status_geral'
```

### ⚠️ **2. TABELA `apontamentos_detalhados` - CAMPOS DE SETOR DUPLICADOS**

```sql
-- PROBLEMA: Setor referenciado de duas formas
id_setor integer [not null]  -- FK para tipo_setores (CORRETO)
setor varchar                -- Nome do setor em texto (REDUNDANTE)

-- RECOMENDAÇÃO: Usar apenas FK
-- SOLUÇÃO: Remover campo 'setor' e usar apenas 'id_setor'
```

### ⚠️ **3. TABELA `tipo_usuarios` - CAMPOS DE SETOR/DEPARTAMENTO DUPLICADOS**

```sql
-- PROBLEMA: Setor e departamento duplicados
setor varchar [not null]         -- Nome do setor em texto
departamento varchar [not null]  -- Nome do departamento em texto
id_setor integer                 -- FK para tipo_setores (CORRETO)
id_departamento integer          -- FK para tipo_departamentos (CORRETO)

-- RECOMENDAÇÃO: Usar apenas FKs
-- SOLUÇÃO: Remover 'setor' e 'departamento', manter apenas IDs
```

### ⚠️ **4. TABELA `tipo_setores` - CAMPOS DE DEPARTAMENTO DUPLICADOS**

```sql
-- PROBLEMA: Departamento referenciado de duas formas
departamento varchar [not null]  -- Nome do departamento em texto
id_departamento integer          -- FK para tipo_departamentos (CORRETO)

-- RECOMENDAÇÃO: Usar apenas FK
-- SOLUÇÃO: Remover 'departamento' e usar apenas 'id_departamento'
```

### ⚠️ **5. TABELA `tipos_maquina` - CAMPOS DE SETOR/DEPARTAMENTO DUPLICADOS**

```sql
-- PROBLEMA: Setor e departamento duplicados
setor varchar                -- Nome do setor em texto
departamento text            -- Nome do departamento em texto
id_departamento integer      -- FK para tipo_departamentos (CORRETO)

-- RECOMENDAÇÃO: Usar apenas FK
-- SOLUÇÃO: Remover 'setor' e 'departamento', manter apenas 'id_departamento'
```

### ⚠️ **6. TABELA `tipo_causas_retrabalho` - CAMPOS DUPLICADOS**

```sql
-- PROBLEMA: Departamento e setor duplicados
departamento text            -- Nome do departamento em texto
setor text                   -- Nome do setor em texto
id_departamento integer      -- FK para tipo_departamentos (CORRETO)

-- RECOMENDAÇÃO: Usar apenas FK
-- SOLUÇÃO: Remover 'departamento' e 'setor', manter apenas 'id_departamento'
```

### ⚠️ **7. TABELA `tipos_teste` - CAMPOS DUPLICADOS**

```sql
-- PROBLEMA: Departamento e setor duplicados + tipo_maquina
departamento varchar [not null]  -- Nome do departamento em texto
setor varchar                    -- Nome do setor em texto
tipo_maquina varchar             -- Nome do tipo de máquina em texto

-- RECOMENDAÇÃO: Usar FKs quando possível
-- SOLUÇÃO: Adicionar id_departamento, id_setor, id_tipo_maquina
```

### ⚠️ **8. TABELA `pendencias` - CAMPOS DUPLICADOS**

```sql
-- PROBLEMA: Cliente e tipo_maquina duplicados
cliente varchar [not null]      -- Nome do cliente em texto
tipo_maquina varchar [not null] -- Nome do tipo de máquina em texto

-- NOTA: Estes podem ser mantidos para performance em relatórios
-- MAS seria melhor usar FKs: id_cliente, id_tipo_maquina
```

---

## 🎯 **PLANO DE LIMPEZA RECOMENDADO**

### **FASE 1: REMOÇÕES SEGURAS (BAIXO RISCO)**

#### **1.1 Tabela `ordens_servico`**
```sql
-- Remover campo redundante
ALTER TABLE ordens_servico DROP COLUMN status_geral;
-- Manter apenas: status_os
```

#### **1.2 Tabela `apontamentos_detalhados`**
```sql
-- Remover campo redundante (já temos id_setor)
ALTER TABLE apontamentos_detalhados DROP COLUMN setor;
-- Usar apenas: id_setor (FK)
```

#### **1.3 Tabela `tipo_usuarios`**
```sql
-- Remover campos redundantes (já temos id_setor, id_departamento)
ALTER TABLE tipo_usuarios DROP COLUMN setor;
ALTER TABLE tipo_usuarios DROP COLUMN departamento;
-- Usar apenas: id_setor, id_departamento (FKs)
```

#### **1.4 Tabela `tipo_setores`**
```sql
-- Remover campo redundante (já temos id_departamento)
ALTER TABLE tipo_setores DROP COLUMN departamento;
-- Usar apenas: id_departamento (FK)
```

#### **1.5 Tabela `tipos_maquina`**
```sql
-- Remover campos redundantes
ALTER TABLE tipos_maquina DROP COLUMN setor;
ALTER TABLE tipos_maquina DROP COLUMN departamento;
-- Usar apenas: id_departamento (FK)
```

#### **1.6 Tabela `tipo_causas_retrabalho`**
```sql
-- Remover campos redundantes
ALTER TABLE tipo_causas_retrabalho DROP COLUMN departamento;
ALTER TABLE tipo_causas_retrabalho DROP COLUMN setor;
-- Usar apenas: id_departamento (FK)
```

### **FASE 2: MELHORIAS ESTRUTURAIS (MÉDIO RISCO)**

#### **2.1 Tabela `tipos_teste`**
```sql
-- Adicionar FKs para melhor normalização
ALTER TABLE tipos_teste ADD COLUMN id_departamento INTEGER;
ALTER TABLE tipos_teste ADD COLUMN id_setor INTEGER;
ALTER TABLE tipos_teste ADD COLUMN id_tipo_maquina INTEGER;

-- Migrar dados dos campos texto para FKs
-- Depois remover campos texto
ALTER TABLE tipos_teste DROP COLUMN departamento;
ALTER TABLE tipos_teste DROP COLUMN setor;
ALTER TABLE tipos_teste DROP COLUMN tipo_maquina;
```

#### **2.2 Tabela `pendencias`**
```sql
-- Adicionar FKs para melhor normalização
ALTER TABLE pendencias ADD COLUMN id_cliente INTEGER;
ALTER TABLE pendencias ADD COLUMN id_tipo_maquina INTEGER;

-- Migrar dados dos campos texto para FKs
-- Manter campos texto por compatibilidade (opcional)
```

---

## 📋 **ESTRUTURA FINAL LIMPA**

### **TABELA `ordens_servico` (LIMPA)**
```sql
Table ordens_servico {
  id integer [primary key]
  os_numero varchar [not null]
  status_os varchar                    -- ✅ ÚNICO CAMPO DE STATUS
  prioridade varchar [default: 'MEDIA']
  id_responsavel_registro integer
  id_responsavel_pcp integer
  id_responsavel_final integer
  data_inicio_prevista datetime
  data_fim_prevista datetime
  data_criacao datetime
  data_ultima_atualizacao datetime
  criado_por integer
  // status_geral varchar             -- ❌ REMOVIDO (duplicado)
  valor_total_previsto decimal
  valor_total_real decimal
  observacoes_gerais text
  id_tipo_maquina integer
  custo_total_real decimal
  horas_previstas decimal
  horas_reais decimal
  data_programacao datetime
  horas_orcadas decimal(10,2) [default: 0]
  testes_iniciais_finalizados boolean [default: 0]
  testes_parciais_finalizados boolean [default: 0]
  testes_finais_finalizados boolean [default: 0]
  data_testes_iniciais_finalizados datetime
  data_testes_parciais_finalizados datetime
  data_testes_finais_finalizados datetime
  id_usuario_testes_iniciais integer
  id_usuario_testes_parciais integer
  id_usuario_testes_finais integer
  testes_exclusivo_os text
  id_cliente integer
  id_equipamento integer
  id_setor integer
  id_departamento integer
  inicio_os datetime
  fim_os datetime
  descricao_maquina text
}
```

### **TABELA `apontamentos_detalhados` (LIMPA)**
```sql
Table apontamentos_detalhados {
  id integer [primary key]
  id_os integer [not null]
  id_usuario integer [not null]
  id_setor integer [not null]         -- ✅ ÚNICO CAMPO DE SETOR (FK)
  data_hora_inicio datetime [not null]
  data_hora_fim datetime
  status_apontamento varchar [not null]
  foi_retrabalho boolean [default: 0]
  causa_retrabalho varchar
  observacao_os text
  servico_de_campo boolean
  observacoes_gerais text
  aprovado_supervisor boolean
  data_aprovacao_supervisor datetime
  supervisor_aprovacao varchar
  criado_por varchar
  criado_por_email varchar
  data_processo_finalizado datetime
  // setor varchar                    -- ❌ REMOVIDO (duplicado com id_setor)
  horas_orcadas decimal(10,2) [default: 0]
  etapa_inicial boolean [default: 0]
  etapa_parcial boolean [default: 0]
  etapa_final boolean [default: 0]
  horas_etapa_inicial decimal [default: 0]
  horas_etapa_parcial decimal [default: 0]
  horas_etapa_final decimal [default: 0]
  observacoes_etapa_inicial text
  observacoes_etapa_parcial text
  observacoes_etapa_final text
  data_etapa_inicial datetime
  data_etapa_parcial datetime
  data_etapa_final datetime
  supervisor_etapa_inicial varchar
  supervisor_etapa_parcial varchar
  supervisor_etapa_final varchar
  tipo_maquina varchar
  tipo_atividade varchar
  descricao_atividade text
  categoria_maquina varchar
  subcategorias_maquina text
  subcategorias_finalizadas boolean [default: 0]
  data_finalizacao_subcategorias datetime
  emprestimo_setor varchar
  pendencia boolean [default: 0]
  pendencia_data datetime
}
```

### **TABELA `tipo_usuarios` (LIMPA)**
```sql
Table tipo_usuarios {
  id integer [primary key]
  nome_completo varchar [not null]
  nome_usuario varchar [not null]
  email varchar [not null]
  matricula varchar
  senha_hash varchar [not null]
  // setor varchar [not null]         -- ❌ REMOVIDO (usar id_setor)
  cargo varchar
  // departamento varchar [not null]  -- ❌ REMOVIDO (usar id_departamento)
  privilege_level varchar [not null]
  is_approved boolean [not null]
  data_criacao datetime
  data_ultima_atualizacao datetime
  trabalha_producao boolean [not null]
  obs_reprovacao text
  id_setor integer                     -- ✅ ÚNICO CAMPO DE SETOR (FK)
  id_departamento integer              -- ✅ ÚNICO CAMPO DE DEPARTAMENTO (FK)
  primeiro_login boolean [not null]
}
```

---

## ⚠️ **RISCOS E CONSIDERAÇÕES**

### **RISCOS BAIXOS:**
- Remoção de campos claramente duplicados (status_geral, setor quando há id_setor)
- Campos texto quando existem FKs equivalentes

### **RISCOS MÉDIOS:**
- Campos texto usados em relatórios (podem precisar de JOINs)
- Campos históricos que podem ter dados importantes

### **RECOMENDAÇÃO:**
1. **Começar com Fase 1** (remoções seguras)
2. **Testar aplicação** após cada remoção
3. **Validar relatórios** que usam campos removidos
4. **Implementar Fase 2** apenas após confirmação

---

## 🎯 **BENEFÍCIOS DA LIMPEZA**

### **ESTRUTURA MAIS LIMPA:**
- ✅ Eliminação de ambiguidades
- ✅ Padronização de relacionamentos
- ✅ Redução de redundâncias

### **MANUTENÇÃO MAIS FÁCIL:**
- ✅ Menos campos para manter sincronizados
- ✅ Relacionamentos mais claros
- ✅ Menos possibilidade de inconsistências

### **PERFORMANCE MELHORADA:**
- ✅ Tabelas menores
- ✅ Índices mais eficientes
- ✅ Queries mais simples
