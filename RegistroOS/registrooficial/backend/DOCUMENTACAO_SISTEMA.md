# 📋 DOCUMENTAÇÃO COMPLETA DO SISTEMA REGISTROOS

## 🗄️ ESTRUTURA DO BANCO DE DADOS
**Última atualização:** 2025-01-19
**Total de tabelas:** 21 (removida os_testes_exclusivos)
**Banco:** registroos_new.db

### 📊 TABELAS E COLUNAS

#### 1. **usuarios** (9 registros)
```sql
- id (INTEGER, PK) NOT NULL
- nome_completo (VARCHAR(255)) NOT NULL
- nome_usuario (VARCHAR(100)) NOT NULL
- email (VARCHAR(255)) NOT NULL
- matricula (VARCHAR(100))
- senha_hash (VARCHAR(255)) NOT NULL
- setor (VARCHAR(100)) NOT NULL
- cargo (VARCHAR(100))
- departamento (VARCHAR(100)) NOT NULL
- privilege_level (VARCHAR(50)) NOT NULL -- USER, SUPERVISOR, ADMIN
- is_approved (BOOLEAN) NOT NULL
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- trabalha_producao (BOOLEAN) NOT NULL DEFAULT FALSE
- obs_reprovacao (TEXT)
- id_setor (INTEGER, FK)
- id_departamento (INTEGER, FK)
```

#### 2. **ordens_servico**
```sql
- id (INTEGER, PK)
- os_numero (TEXT, UNIQUE)
- id_cliente (INTEGER, FK)
- id_equipamento (INTEGER, FK)
- descricao_maquina (TEXT)
- status_os (TEXT) -- ABERTA, EM ANDAMENTO, CONCLUIDA, AGUARDANDO
- id_responsavel_registro (INTEGER, FK)
- id_responsavel_pcp (INTEGER, FK)
- id_responsavel_final (INTEGER, FK)
- data_inicio_prevista (DATETIME)
- data_fim_prevista (DATETIME)
- inicio_os (DATETIME)
- fim_os (DATETIME)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- criado_por (INTEGER, FK)
- status_geral (TEXT)
- prioridade (TEXT) -- BAIXA, NORMAL, MEDIA, ALTA, URGENTE
- valor_total_previsto (REAL)
- valor_total_real (REAL)
- observacoes_gerais (TEXT)
- id_tipo_maquina (INTEGER, FK)
- custo_total_real (REAL)
- horas_previstas (REAL)
- horas_reais (REAL)
- data_programacao (DATETIME)
- id_setor (INTEGER, FK)
- id_departamento (INTEGER, FK)
- horas_orcadas (REAL)
- testes_iniciais_finalizados (BOOLEAN)
- testes_parciais_finalizados (BOOLEAN)
- testes_finais_finalizados (BOOLEAN)
- data_testes_iniciais_finalizados (DATETIME)
- data_testes_parciais_finalizados (DATETIME)
- data_testes_finais_finalizados (DATETIME)
- id_usuario_testes_iniciais (INTEGER, FK)
- id_usuario_testes_parciais (INTEGER, FK)
- id_usuario_testes_finais (INTEGER, FK)
- testes_exclusivo (TEXT) -- JSON com dados dos testes exclusivos selecionados
```

#### 3. **programacoes**
```sql
- id (INTEGER, PK)
- id_ordem_servico (INTEGER, FK)
- responsavel_id (INTEGER, FK)
- inicio_previsto (DATETIME)
- fim_previsto (DATETIME)
- status (TEXT) -- PROGRAMADA, EM_ANDAMENTO, CONCLUIDA, CANCELADA
- criado_por_id (INTEGER, FK)
- observacoes (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
- id_setor (INTEGER, FK)
```

#### 4. **apontamentos_detalhados**
```sql
- id (INTEGER, PK)
- id_os (INTEGER, FK)
- id_setor (INTEGER, FK)
- id_usuario (INTEGER, FK)
- id_atividade (INTEGER, FK)
- data_hora_inicio (DATETIME)
- data_hora_fim (DATETIME)
- status_apontamento (TEXT) -- PENDENTE, CONCLUIDO, CANCELADO
- aprovado_supervisor (BOOLEAN)
- data_aprovacao_supervisor (DATETIME)
- foi_retrabalho (BOOLEAN)
- causa_retrabalho (TEXT)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- observacao_os (TEXT)
- os_finalizada_em (DATETIME)
- servico_de_campo (BOOLEAN)
- observacoes_gerais (TEXT)
- criado_por (TEXT)
- criado_por_email (TEXT)
- setor (TEXT)
- supervisor_aprovacao (TEXT)
```

#### 5. **pendencias**
```sql
- id (INTEGER, PK)
- numero_os (TEXT)
- cliente (TEXT)
- data_inicio (DATETIME)
- id_responsavel_inicio (INTEGER, FK)
- tipo_maquina (TEXT)
- descricao_maquina (TEXT)
- descricao_pendencia (TEXT)
- status (TEXT) -- ABERTA, FECHADA, EM_ANDAMENTO
- prioridade (TEXT) -- BAIXA, NORMAL, ALTA, URGENTE
- data_fechamento (DATETIME)
- id_responsavel_fechamento (INTEGER, FK)
- solucao_aplicada (TEXT)
- observacoes_fechamento (TEXT)
- id_apontamento_origem (INTEGER, FK)
- id_apontamento_fechamento (INTEGER, FK)
- tempo_aberto_horas (REAL)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
```

#### 6. **causas_retrabalho**
```sql
- id (INTEGER, PK)
- codigo (TEXT, UNIQUE)
- descricao (TEXT)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- id_departamento (INTEGER, FK)
- departamento (TEXT)
- setor (TEXT)
```

#### 7. **setores**
```sql
- id (INTEGER, PK)
- nome (TEXT, UNIQUE)
- descricao (TEXT)
- ativo (BOOLEAN)
- id_departamento (INTEGER, FK)
- data_criacao (DATETIME)
```

#### 8. **departamentos**
```sql
- id (INTEGER, PK)
- nome (TEXT, UNIQUE)
- descricao (TEXT)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
```

#### 9. **tipos_maquina**
```sql
- id (INTEGER, PK)
- nome (TEXT, UNIQUE)
- descricao (TEXT)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
```

#### 10. **clientes**
```sql
- id (INTEGER, PK)
- nome (TEXT)
- cnpj (TEXT, UNIQUE)
- email (TEXT)
- telefone (TEXT)
- endereco (TEXT)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
```

#### 11. **equipamentos**
```sql
- id (INTEGER, PK)
- nome (TEXT)
- modelo (TEXT)
- numero_serie (TEXT, UNIQUE)
- id_cliente (INTEGER, FK)
- id_tipo_maquina (INTEGER, FK)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
```

#### 12. **atividades**
```sql
- id (INTEGER, PK)
- nome (TEXT, UNIQUE)
- descricao (TEXT)
- tempo_estimado_horas (REAL)
- id_setor (INTEGER, FK)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
```

---

## 🧪 TESTES EXCLUSIVOS POR OS

### **Sistema de Testes Exclusivos**
- **Campo:** `testes_exclusivo` (TEXT - JSON)
- **Descrição:** Sistema flexível para armazenar testes exclusivos selecionados por supervisores
- **Aplicação:** Filtrados por departamento e setor do usuário
- **Controle:** Definido no momento do apontamento pelos supervisores

### **Estrutura JSON dos Testes Exclusivos:**
```json
{
  "testes": [
    {
      "id": 1,
      "nome": "Teste Daimer",
      "descricao": "Teste de isolamento Daimer",
      "usuario": "João Silva",
      "setor": "LABORATORIO_ENSAIOS_ELETRICOS",
      "departamento": "MOTORES",
      "data": "2025-01-19",
      "hora": "14:30:00"
    }
  ]
}
```

### **Regras de Negócio dos Testes Exclusivos:**
1. Aparecem apenas na seção "Etapas" para supervisores e administradores
2. São filtrados automaticamente por departamento e setor do usuário
3. Múltiplos testes podem ser selecionados por OS
4. Dados completos de auditoria são salvos (usuário, data, hora, setor)
5. Sistema permite marcar/desmarcar testes em diferentes apontamentos
6. Baseados na tabela `tipos_teste` com `teste_exclusivo_setor = 1`

---

## 🎯 DASHBOARDS E FUNCIONALIDADES

### 📊 **PCP (Planejamento e Controle de Produção)**

#### **Dashboard PCP**
- **Endpoint Base:** `/api/pcp/`
- **Funcionalidades:**
  - 📊 Métricas de produção em tempo real
  - 📈 Gráficos de performance por setor
  - ⏱️ Indicadores de prazo e atraso
  - 📋 Resumo de programações ativas

#### **Ordens de Serviço**
- **Endpoint:** `/api/pcp/ordens-servico`
- **Campos Enviados/Recebidos:**
  ```json
  {
    "id": "INTEGER",
    "os_numero": "TEXT",
    "status_os": "TEXT",
    "prioridade": "TEXT",
    "data_criacao": "DATETIME",
    "id_setor": "INTEGER",
    "responsavel_pcp": "INTEGER"
  }
  ```

#### **Programação**
- **Endpoint:** `/api/pcp/programacoes-enviadas`
- **Campos Enviados/Recebidos:**
  ```json
  {
    "id": "INTEGER",
    "id_ordem_servico": "INTEGER",
    "responsavel_id": "INTEGER",
    "inicio_previsto": "DATETIME",
    "fim_previsto": "DATETIME",
    "status": "TEXT",
    "observacoes": "TEXT"
  }
  ```

#### **Calendário**
- **Endpoint:** `/api/pcp/calendario`
- **Funcionalidade:** Visualização temporal das programações

### 🔍 **Consulta OS**

#### **Consulta Dados**
- **Endpoint:** `/api/consulta/dados`
- **Funcionalidade:** Busca geral de ordens de serviço

#### **Pesquisa Por OS**
- **Endpoint:** `/api/consulta/os/{numero_os}`
- **Funcionalidade:** Busca específica por número da OS

### 👥 **Administrador**

#### **Aprovação de Colaboradores**
- **Endpoint:** `/api/admin/aprovacao-colaboradores`
- **Funcionalidade:** Aprovar novos usuários

#### **Gerenciar Colaboradores**
- **Endpoint:** `/api/admin/colaboradores`
- **Campos Enviados/Recebidos:**
  ```json
  {
    "id": "INTEGER",
    "nome_completo": "TEXT",
    "email": "TEXT",
    "privilege_level": "TEXT",
    "id_setor": "INTEGER",
    "ativo": "BOOLEAN"
  }
  ```

#### **Novo Colaborador**
- **Endpoint:** `POST /api/admin/colaboradores`
- **Funcionalidade:** Criar novo usuário

### 📊 **Gestão**

#### **Relatórios**
- **Endpoint:** `/api/gestao/relatorio-producao`
- **Funcionalidade:** Relatórios executivos de produção

#### **Usuários**
- **Endpoint:** `/api/gestao/usuarios`
- **Funcionalidade:** Gestão de usuários do sistema

#### **OS**
- **Endpoint:** `/api/gestao/ordens-servico`
- **Funcionalidade:** Visão gerencial das ordens

#### **Configurações**
- **Endpoint:** `/api/gestao/configuracoes`
- **Funcionalidade:** Configurações do sistema

### 🔧 **Desenvolvimento**

#### **Dashboard**
- **Endpoint:** `/api/dashboard-desenvolvimento`
- **Funcionalidade:** Métricas operacionais do setor

#### **Apontamento**
- **Endpoint:** `/api/apontamentos`
- **Campos Enviados/Recebidos:**
  ```json
  {
    "id": "INTEGER",
    "id_os": "INTEGER",
    "id_usuario": "INTEGER",
    "data_hora_inicio": "DATETIME",
    "data_hora_fim": "DATETIME",
    "status_apontamento": "TEXT",
    "observacoes_gerais": "TEXT"
  }
  ```

#### **Minhas OS**
- **Endpoint:** `/api/ordens-lista`
- **Funcionalidade:** Ordens atribuídas ao usuário
- **Campos de Teste Retornados:**
  ```json
  {
    "testes_exclusivo": null  // JSON string com testes exclusivos ou null
  }
  ```

#### **Pesquisa OS**
- **Endpoint:** `/api/pesquisa-os`
- **Funcionalidade:** Busca de ordens de serviço

#### **Programação**
- **Endpoint:** `/api/programacoes-lista`
- **Funcionalidade:** Visualizar programações

#### **Pendências**
- **Endpoint:** `/api/pendencias`
- **Campos Enviados/Recebidos:**
  ```json
  {
    "id": "INTEGER",
    "numero_os": "TEXT",
    "descricao_pendencia": "TEXT",
    "status": "TEXT",
    "prioridade": "TEXT",
    "id_apontamento_origem": "INTEGER"
  }
  ```

#### **Gerenciar**
- **Endpoint:** `/api/gerenciar`
- **Funcionalidade:** Gestão de registros do setor

#### **Aprovação Usuários**
- **Endpoint:** `/api/aprovacao-usuarios`
- **Funcionalidade:** Aprovar apontamentos e registros

---

## 🔗 RELACIONAMENTOS ENTRE TABELAS

1. **usuarios** ↔ **setores** (id_setor)
2. **usuarios** ↔ **departamentos** (id_departamento)
3. **ordens_servico** ↔ **clientes** (id_cliente)
4. **ordens_servico** ↔ **equipamentos** (id_equipamento)
5. **programacoes** ↔ **ordens_servico** (id_ordem_servico)
6. **apontamentos_detalhados** ↔ **ordens_servico** (id_os)
7. **pendencias** ↔ **apontamentos_detalhados** (id_apontamento_origem)
8. **equipamentos** ↔ **tipos_maquina** (id_tipo_maquina)

---

## 📋 PADRÕES DE RESPOSTA API

### ✅ Sucesso (200)
```json
{
  "data": [...],
  "total": 0,
  "page": 1,
  "limit": 50
}
```

### ❌ Erro (500)
```json
{
  "detail": "Mensagem de erro detalhada"
}
```

### 🔒 Não Autorizado (401)
```json
{
  "detail": "Token inválido ou expirado"
}
```

### 🚫 Não Encontrado (404)
```json
{
  "detail": "Recurso não encontrado"
}
```

---

## 🔄 ATUALIZAÇÕES RECENTES (2025-01-19)

### ✅ **Correções Implementadas:**

1. **Sistema de Testes Exclusivos Reformulado:**
   - ❌ Removida tabela `os_testes_exclusivos`
   - ❌ Removidas colunas `teste_daimer` e `teste_carga` de `ordens_servico`
   - ✅ Adicionada coluna `testes_exclusivo` (TEXT/JSON) em `ordens_servico`
   - ✅ Sistema agora baseado em `tipos_teste` com filtro por setor/departamento

2. **Campo Horas Orçadas Desbloqueado:**
   - ✅ Corrigido tipo de `supervisor_horas_orcadas` de boolean para number
   - ✅ Campo agora funcional para supervisores e administradores

3. **Busca de Departamentos no Admin Config:**
   - ✅ Adicionada rota `/admin/departamentos` (sem barra final)
   - ✅ Mantida compatibilidade com `/admin/departamentos/`
   - ✅ Corrigidos dropdowns em todos os formulários Admin Config

4. **Processamento de Testes Exclusivos no Backend:**
   - ✅ Implementado processamento de `testes_exclusivos_selecionados`
   - ✅ Dados salvos como JSON na coluna `testes_exclusivo`
   - ✅ Inclui informações de auditoria (usuário, setor, data, hora)

### 🎯 **Funcionalidades Ativas:**

- **Testes Exclusivos:** Aparecem na seção Etapas para supervisores
- **Filtro Automático:** Por departamento e setor do usuário
- **Dados de Auditoria:** Completos para controle e rastreabilidade
- **Admin Config:** Todos os formulários funcionando corretamente
- **Campo Horas Orçadas:** Editável para supervisores

---

**Última atualização:** 2025-01-19
**Versão do Sistema:** 1.1
**Responsável:** Equipe de Desenvolvimento
