# ✅ ANÁLISE DETALHADA DE ROTAS - CONTEXTOS ESPECÍFICOS

## ANÁLISE CORRIGIDA: Rotas com Propósitos Diferentes

### 1. ROTAS QUE **NÃO SÃO CONFLITOS** - Contextos Específicos

#### 1.1 Programações - Contextos Diferentes

**✅ CORRETO - Não há conflito real:**

1. **PCP Routes** (`/api/pcp/programacoes`):
   - **Propósito:** Planejamento e Controle de Produção
   - **Usuários:** Supervisores/Admin para criar programações
   - **Funcionalidade:** Criar, editar, atribuir programações
   - **Contexto:** Visão gerencial do PCP

2. **Desenvolvimento Routes** (`/api/desenvolvimento/programacao`):
   - **Propósito:** Consulta de programações para desenvolvimento
   - **Usuários:** Técnicos para ver suas programações
   - **Funcionalidade:** Visualizar programações atribuídas
   - **Contexto:** Visão operacional do técnico

**CONCLUSÃO:** Manter ambas - servem propósitos diferentes

#### 1.2 Apontamentos - Contextos Diferentes

**✅ CORRETO - Não há conflito real:**

1. **Desenvolvimento Routes** (`/api/desenvolvimento/os/apontamentos`):
   - **Propósito:** Criação de apontamentos detalhados
   - **Funcionalidade:** Apontamentos com testes, validações, programações
   - **Contexto:** Interface principal de desenvolvimento

2. **General Routes** (`/api/save-apontamento`):
   - **Propósito:** Salvamento rápido/alternativo
   - **Funcionalidade:** Apontamentos simples com pendências
   - **Contexto:** Interface simplificada

3. **Main.py** (`/api/apontamentos-detalhados`):
   - **Propósito:** Consulta de apontamentos para dashboard
   - **Funcionalidade:** Listagem com filtros avançados
   - **Contexto:** Relatórios e dashboards

**CONCLUSÃO:** Manter todas - servem propósitos diferentes

#### 1.4 Catálogos - Níveis de Acesso Diferentes

**⚠️ CONFLITO PARCIAL - Precisa ajuste:**

1. **Catalogs Validated Clean** (`/api/catalogs/departamentos`):
   - **Propósito:** Listagem geral para formulários
   - **Acesso:** Usuários autenticados
   - **Funcionalidade:** GET apenas (somente leitura)
   - **Filtros:** Apenas ativos

2. **Admin Config Routes** (`/api/admin/departamentos`):
   - **Propósito:** CRUD completo para administração
   - **Acesso:** Apenas ADMIN
   - **Funcionalidade:** GET, POST, PUT, DELETE
   - **Filtros:** Todos os registros

**CONCLUSÃO:** Manter ambas - níveis de acesso diferentes

### 2. CONFLITOS REAIS IDENTIFICADOS E RESOLVIDOS

#### 2.1 ✅ Arquivos Removidos (Duplicatas Reais)

**Removidos com sucesso:**
- `admin_routes_simple.py` - Duplicava admin_config_routes.py
- `catalogs_simple.py` - Versão antiga dos catálogos
- `catalogs_validated.py` - Versão intermediária dos catálogos
- `pcp_routes_backup.py` - Backup desnecessário

#### 2.2 ✅ Main.py Atualizado

**Estrutura consolidada:**
- `/api/auth` - Autenticação
- `/api/catalogs` - Catálogos gerais
- `/api/os` - Ordens de serviço
- `/api/desenvolvimento` - Apontamentos e desenvolvimento
- `/api/pcp` - Planejamento e controle
- `/api/gestao` - Gestão e relatórios
- `/api/admin` - Administração
- `/api/users` - Usuários
- `/api/reports` - Relatórios
- `/api` - Endpoints gerais

### 3. MAPEAMENTO DE CAMPOS DO DATABASE_MODELS.PY

#### 3.1 Inconsistências de Nomenclatura Identificadas

**Departamento (tipo_departamentos):**
- DB: `nome_tipo` (String)
- Frontend esperado: `nome`
- **Ação:** Usar alias no Pydantic

**Setor (tipo_setores):**
- DB: `nome` (String)
- DB: `departamento` (String) + `id_departamento` (FK)
- **Ação:** Padronizar uso de FK

**TipoMaquina (tipos_maquina):**
- DB: `nome_tipo` (String)
- DB: `subcategoria` (JSON)
- **Ação:** Tratar JSON corretamente

**Usuario (tipo_usuarios):**
- DB: `setor` (String) + `id_setor` (FK)
- DB: `departamento` (String) + `id_departamento` (FK)
- **Ação:** Migrar para uso exclusivo de FKs
- `GET /api/catalogs/estrutura-hierarquica` - Estrutura hierárquica completa

### 6. **ADMIN ROUTES** (`/api/admin`)
**Arquivo:** `app/admin_routes_simple.py`
**Responsabilidade:** Administração do sistema
- `GET /api/admin/setores/` - Gerenciar setores
- `GET /api/admin/tipos-maquina/` - Gerenciar tipos de máquina
- `GET /api/admin/tipos-atividade/` - Gerenciar tipos de atividade
- `GET /api/admin/usuarios/` - Gerenciar usuários

### 7. **GESTÃO ROUTES** (`/api/gestao`)
**Arquivo:** `app/gestao_routes.py`
**Responsabilidade:** Gestão de recursos e relatórios
- `GET /api/gestao/dashboard` - Dashboard de gestão
- `GET /api/gestao/relatorios` - Relatórios de gestão

### 8. **USERS ROUTES** (`/api/users`)
**Arquivo:** `routes/users.py`
**Responsabilidade:** Gerenciamento de usuários
- `GET /api/users/` - Listar usuários
- `POST /api/users/` - Criar usuário
- `PUT /api/users/{user_id}` - Atualizar usuário

### 9. **GENERAL ROUTES** (`/api/general`)
**Arquivo:** `routes/general.py`
**Responsabilidade:** Endpoints gerais
- `GET /api/general/status` - Status do sistema

### 10. **RELATÓRIO ROUTES** (`/api/relatorio`)
**Arquivo:** `routes/relatorio_completo.py`
**Responsabilidade:** Relatórios completos
- `GET /api/relatorio/completo` - Relatório completo

---

## ⚠️ PROBLEMA IDENTIFICADO: PROGRAMAÇÃO PCP

### **ENDPOINT PROBLEMÁTICO:**
`GET /api/pcp/programacao-form-data`

### **FUNÇÃO:**
Retornar dados para o formulário de Nova Programação:
- Setores de produção
- Supervisores que trabalham na produção
- Departamentos (MOTORES, TRANSFORMADORES)
- Ordens de serviço disponíveis

### **PROBLEMA ATUAL:**
- Endpoint retorna arrays vazios
- Consultas SQL não executam corretamente
- Frontend não consegue preencher dropdowns

### **IMPACTO:**
- Seção "Programação" no PCP não funciona
- Não é possível criar novas programações
- Formulários ficam vazios

---

## 🎯 PRÓXIMA AÇÃO ESPECÍFICA

**FOCO EXCLUSIVO:** Corrigir o endpoint `/api/pcp/programacao-form-data` no arquivo `routes/pcp_routes.py` para que retorne os dados corretos do banco de dados.
