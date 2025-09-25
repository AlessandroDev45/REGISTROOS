# 📋 DOCUMENTAÇÃO CONSOLIDADA - RegistroOS

## 🎯 VISÃO GERAL DO SISTEMA

O RegistroOS é um sistema de gestão de ordens de serviço para laboratórios de ensaios elétricos e mecânicos, com controle de usuários, aprovações e apontamentos específicos por setor.

---

## 🏗️ ESTRUTURA DO PROJETO

### 📁 Módulos Principais
```
RegistroOS/
├── backend/                 # API FastAPI
├── frontend/               # Interface React/TypeScript
└── database/              # Estrutura do banco SQLite
```

### 🔧 Tecnologias
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, TypeScript, Tailwind CSS
- **Autenticação**: JWT com HttpOnly cookies

---

## 🚨 PROBLEMAS CRÍTICOS RESOLVIDOS

### ✅ Login e Autenticação
**Problema**: Falha no login com "Email ou senha inválidos"
**Solução**: 
- Corrigidos hashes de senha corrompidos
- Configurado proxy Vite para redirecionamento `/api/*`
- Implementado HttpOnly cookies para segurança

### ✅ Estrutura do Banco de Dados
**Problema**: 41 tabelas desnecessárias sendo criadas
**Solução**: 
- Identificadas 10 tabelas essenciais
- Removidas 31 tabelas redundantes
- Implementada relação 1:1 entre OS e Equipamento

---

## 👥 GESTÃO DE USUÁRIOS

### 🔐 Níveis de Privilégio
- **USER**: Acesso básico ao setor
- **SUPERVISOR**: Aprovação de usuários do próprio laboratório
- **PCP**: Planejamento e controle de produção
- **GESTAO**: Gestão geral
- **ADMIN**: Acesso total ao sistema

### 📝 Processo de Aprovação
1. **Cadastro**: Usuário se registra no sistema
2. **Pendência**: Conta fica pendente de aprovação
3. **Aprovação**: Supervisor/Admin aprova a conta
4. **Ativação**: Usuário pode fazer login

**Regras de Aprovação**:
- **Supervisor**: Pode aprovar apenas usuários do seu laboratório
- **Admin**: Pode aprovar qualquer usuário do sistema

---

## 🔧 FUNCIONALIDADES IMPLEMENTADAS

### ⚡ Laboratório de Ensaios Elétricos
- Formulário de apontamento completo
- Testes específicos por tipo de máquina:
  - Máquinas Rotativas CA/CC
  - Máquinas Estáticas (Transformadores)
- Controle de pendências elétricas
- Validação rigorosa de dados

### 🔩 Setor de Mecânica
- Apontamentos mecânicos
- Controle de retrabalho
- Gestão de causas de falha

### 📊 Recursos Gerais
- Múltiplas pendências por OS
- Múltiplas programações por OS
- Dados completos do usuário salvos automaticamente
- Campos específicos: Daimer, Carga, Horas Orçadas

---

## 🛠️ CONFIGURAÇÃO E INSTALAÇÃO

### Backend
```bash
cd RegistroOS/registrooficial/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd RegistroOS/registrooficial/frontend
npm install
npm run dev
```

### Proxy Configuration (vite.config.ts)
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

---

## 🔍 TROUBLESHOOTING

### Problema: Logout não funciona
**Diagnóstico**: Verificar se o endpoint `/logout` está sendo chamado corretamente
**Solução**: 
1. Verificar se o cookie HttpOnly está sendo removido
2. Confirmar redirecionamento para `/login`
3. Limpar estado do usuário no frontend

### Problema: Usuário não consegue fazer login
**Verificações**:
1. Conta está aprovada (`is_approved = True`)
2. Senha não foi corrompida por scripts de limpeza
3. Proxy está configurado corretamente

---

## 📋 ESTRUTURA DO BANCO DE DADOS

### Tabelas Essenciais (10)
1. **usuarios** - Dados dos usuários
2. **ordem_servico** - Ordens de serviço
3. **equipamentos** - Equipamentos (relação 1:1 com OS)
4. **apontamentos** - Apontamentos de trabalho
5. **pendencias** - Pendências por OS
6. **programacoes** - Programações por OS
7. **setores** - Setores do sistema
8. **departamentos** - Departamentos
9. **tipos_teste** - Tipos de teste por setor
10. **causas_retrabalho** - Causas de retrabalho

### Relacionamentos Principais
```
OS (1:1) Equipamento
OS (1:N) Apontamentos
OS (1:N) Pendências
OS (1:N) Programações
Usuario (1:N) Apontamentos
```

---

## 🚀 PRÓXIMOS PASSOS

1. **Otimização**: Remover tabelas desnecessárias definitivamente
2. **Testes**: Implementar testes automatizados
3. **Documentação**: Manter documentação atualizada
4. **Segurança**: Implementar HTTPS em produção
5. **Performance**: Otimizar consultas do banco de dados

---

## 📞 SUPORTE

Para problemas técnicos:
1. Verificar logs do backend
2. Verificar console do navegador
3. Confirmar configuração do proxy
4. Validar estrutura do banco de dados
