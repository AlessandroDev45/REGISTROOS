# Plano de Separação de Responsabilidades - RegistroOS

## 📋 Análise das Sobreposições Identificadas

### 🚨 Problemas Encontrados:
- **27 sobreposições de paths** entre módulos
- Endpoints duplicados entre desenvolvimento, admin e config
- Falta de clareza sobre qual módulo é responsável por cada funcionalidade

## 🎯 Definição de Responsabilidades por Módulo

### 🔧 **DESENVOLVIMENTO** (`/api/`)
**Responsabilidade:** Operações do dia a dia dos setores de produção
- ✅ Apontamentos de produção
- ✅ Consulta de dados para formulários (tipos-maquina, tipos-atividade, etc.)
- ✅ Programações operacionais
- ✅ Pendências operacionais
- ✅ Dashboard operacional

**Endpoints que devem permanecer:**
- `/api/tipos-maquina` (GET) - Consulta para formulários
- `/api/tipos-atividade` (GET) - Consulta para formulários  
- `/api/descricoes-atividade` (GET) - Consulta para formulários
- `/api/causas-retrabalho` (GET) - Consulta para formulários
- `/api/apontamentos/*` - Todas as operações de apontamento
- `/api/programacao/*` - Programações operacionais
- `/api/pendencias/*` - Gestão de pendências
- `/api/dashboard/*` - Dashboard operacional

### 🛠️ **ADMIN** (`/api/admin/`)
**Responsabilidade:** Administração e configuração do sistema
- ✅ CRUD completo de entidades do sistema
- ✅ Gestão de usuários
- ✅ Configurações avançadas

**Endpoints que devem permanecer:**
- `/api/admin/departamentos/*` - CRUD departamentos
- `/api/admin/setores/*` - CRUD setores
- `/api/admin/tipos-maquina/*` - CRUD tipos de máquina
- `/api/admin/tipos-atividade/*` - CRUD tipos de atividade
- `/api/admin/tipos-falha/*` - CRUD tipos de falha
- `/api/admin/tipos-teste/*` - CRUD tipos de teste
- `/api/admin/causas-retrabalho/*` - CRUD causas de retrabalho
- `/api/admin/descricoes-atividade/*` - CRUD descrições de atividade
- `/api/admin/usuarios/*` - Gestão de usuários
- `/api/admin/status` - Status do sistema

### 🏭 **PCP** (`/api/pcp/`)
**Responsabilidade:** Planejamento e Controle de Produção
- ✅ Programação automática de ordens
- ✅ Gestão de programações em lote
- ✅ Relatórios de programação
- ✅ Controle de setores de produção

**Endpoints atuais (manter todos):**
- `/api/pcp/programacoes-gerar`
- `/api/pcp/ordens-disponiveis`
- `/api/pcp/programacoes-manuais`
- `/api/pcp/setores-producao`
- `/api/pcp/programacoes-enviadas`
- `/api/pcp/programacoes/{id}/status`
- `/api/pcp/relatorio-programacoes`

### 📊 **GESTÃO** (`/api/gestao/`)
**Responsabilidade:** Relatórios gerenciais e métricas
- ✅ Métricas e KPIs
- ✅ Relatórios gerenciais
- ✅ Análises de eficiência

**Endpoints atuais (manter todos):**
- `/api/gestao/metricas-gerais`
- `/api/gestao/ordens-por-setor`
- `/api/gestao/eficiencia-setores`

### ⚙️ **CONFIG** (`/api/config/`)
**Responsabilidade:** Configurações básicas do sistema
- ❌ **REMOVER ESTE MÓDULO** - Funcionalidades duplicadas com ADMIN
- Migrar funcionalidades para ADMIN se necessário

## 🔄 Ações Necessárias

### 1. **Remover Módulo CONFIG**
- Remover `app/config_routes_simple.py`
- Remover import e include_router do main.py
- Todas as funcionalidades já estão no ADMIN

### 2. **Limpar Endpoints Duplicados no DESENVOLVIMENTO**
- Manter apenas endpoints GET para consulta (formulários)
- Remover endpoints de CRUD que pertencem ao ADMIN

### 3. **Garantir Separação Clara**
- DESENVOLVIMENTO: Operações (GET para consulta, POST/PUT para apontamentos)
- ADMIN: Configuração (CRUD completo)
- PCP: Planejamento (programações em lote)
- GESTÃO: Relatórios (métricas e análises)

## 📈 Resultado Esperado

Após as correções:
- ✅ 0 sobreposições de paths
- ✅ Responsabilidades claras por módulo
- ✅ Endpoints organizados por função
- ✅ Facilidade de manutenção
- ✅ Escalabilidade melhorada
