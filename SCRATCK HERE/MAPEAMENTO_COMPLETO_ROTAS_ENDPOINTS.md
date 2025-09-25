# 📋 MAPEAMENTO COMPLETO DE ROTAS E ENDPOINTS - REGISTROOS

## 🎯 ESTRUTURA GERAL DO SISTEMA

### Frontend (React/TypeScript) - Páginas Principais:
1. **Dashboard** (`/dashboard`) - Página inicial com métricas gerais
2. **PCP** (`/pcp`) - Planejamento e Controle de Produção
3. **Consulta OS** (`/consulta-os`) - Consulta de Ordens de Serviço
4. **Administrador** (`/administrador`) - Administração do sistema
5. **Admin Config** (`/admin`) - Configurações administrativas
6. **Gestão** (`/gestao`) - Gestão de recursos e relatórios
7. **Desenvolvimento** (`/desenvolvimento`) - Apontamentos e desenvolvimento

---

## 🔗 BACKEND - MAPEAMENTO DE ROTAS E ENDPOINTS

### 1. **AUTH ROUTES** (`/api/auth`)
**Arquivo:** `routes/auth.py`
**Responsabilidade:** Autenticação e autorização
- `POST /api/token` - Login do usuário
- `POST /api/logout` - Logout do usuário
- `GET /api/me` - Dados do usuário atual
- `POST /api/register` - Registro de novo usuário

### 2. **PCP ROUTES** (`/api/pcp`)
**Arquivo:** `routes/pcp_routes.py`
**Responsabilidade:** Planejamento e Controle de Produção
- `GET /api/pcp/ordens-servico` - Ordens de serviço para PCP
- `GET /api/pcp/programacao-form-data` - **DADOS PARA FORMULÁRIO DE PROGRAMAÇÃO** ⚠️
- `POST /api/pcp/programacoes` - Criar nova programação
- `GET /api/pcp/programacoes` - Listar programações
- `GET /api/pcp/pendencias` - Listar pendências
- `GET /api/pcp/pendencias/dashboard` - Dashboard de pendências

### 3. **DESENVOLVIMENTO ROUTES** (`/api/desenvolvimento`)
**Arquivo:** `routes/desenvolvimento.py`
**Responsabilidade:** Apontamentos e desenvolvimento de OS
- `GET /api/desenvolvimento/ordens-servico` - OS para desenvolvimento
- `POST /api/desenvolvimento/apontamentos` - Criar apontamento
- `GET /api/desenvolvimento/apontamentos/{os_id}` - Apontamentos de uma OS
- `POST /api/desenvolvimento/programacoes` - Criar programação de desenvolvimento

### 4. **OS ROUTES** (`/api/os`)
**Arquivo:** `routes/os_routes_simple.py`
**Responsabilidade:** Ordens de Serviço
- `GET /api/os/` - Listar ordens de serviço
- `POST /api/os/` - Criar nova OS
- `GET /api/os/{os_id}` - Detalhes de uma OS
- `PUT /api/os/{os_id}` - Atualizar OS

### 5. **CATALOGS ROUTES** (`/api/catalogs`)
**Arquivo:** `routes/catalogs_validated.py`
**Responsabilidade:** Catálogos e estruturas hierárquicas
- `GET /api/catalogs/departamentos` - Listar departamentos
- `GET /api/catalogs/setores` - Listar setores
- `GET /api/catalogs/tipos-maquina` - Tipos de máquina
- `GET /api/catalogs/usuarios` - Usuários do sistema
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
