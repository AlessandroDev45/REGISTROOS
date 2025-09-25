# 🏭 RegistroOS - Sistema de Registro de Ordens de Serviço

Sistema inteligente para registro e acompanhamento de ordens de serviço em ambiente industrial.

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- npm ou yarn

### Instalação e Execução

1. **Clone o repositório**
```bash
git clone <repository-url>
cd RegistroOS
```

2. **Backend (Terminal 1)**
```bash
cd RegistroOS/registrooficial/backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend (Terminal 2)**
```bash
cd RegistroOS/registrooficial/frontend
npm install
npm start
```

4. **Acesse o sistema**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentação API: http://localhost:8000/docs

## 📁 Estrutura do Projeto

```
RegistroOS/
├── RegistroOS/registrooficial/          # Aplicação principal
│   ├── backend/                         # API FastAPI
│   │   ├── app/                        # Módulos da aplicação
│   │   ├── config/                     # Configurações
│   │   ├── routes/                     # Rotas da API
│   │   ├── utils/                      # Utilitários
│   │   ├── main.py                     # Ponto de entrada
│   │   └── requirements.txt            # Dependências Python
│   └── frontend/                       # Interface React
│       ├── src/                        # Código fonte
│       ├── public/                     # Arquivos públicos
│       └── package.json                # Dependências Node.js
├── Orientacoes/                        # Documentação essencial
│   ├── README.md                       # Guia principal
│   ├── DOCUMENTACAO_CONSOLIDADA.md     # Documentação completa
│   └── main.py                         # Servidor alternativo
└── SCRATCK HERE/                       # Arquivos de desenvolvimento/debug
```

## 🔧 Funcionalidades

- ✅ **Autenticação** - Login seguro com níveis de privilégio
- ✅ **Gestão de OS** - Criação e acompanhamento de ordens de serviço
- ✅ **Setores Dinâmicos** - Suporte a múltiplos setores (Laboratório, Mecânica, etc.)
- ✅ **Filtros Inteligentes** - Sistema de filtros otimizado
- ✅ **Dashboard** - Visão geral do sistema
- ✅ **Relatórios** - Geração de relatórios personalizados

## 👥 Níveis de Usuário

- **ADMIN** - Acesso total ao sistema
- **GESTAO** - Gestão de setores e relatórios
- **SUPERVISOR** - Supervisão de equipes
- **PCP** - Planejamento e controle de produção
- **USER** - Operação básica

## 🔍 Troubleshooting

### Problemas Comuns

1. **Erro de conexão com banco**
   - Verifique se o arquivo `registroos_oficial.db` existe
   - Execute as migrações se necessário

2. **Frontend não carrega**
   - Verifique se o backend está rodando na porta 8000
   - Confirme as configurações de proxy

3. **Logout não funciona**
   - Limpe o cache do navegador
   - Verifique os cookies HttpOnly

### Logs e Debug
- Backend: Logs aparecem no terminal do uvicorn
- Frontend: Use F12 → Console para debug
- Arquivos de teste: Pasta `SCRATCK HERE/`

## 📚 Documentação

- **Documentação Completa**: `Orientacoes/DOCUMENTACAO_CONSOLIDADA.md`
- **Guia de Desenvolvimento**: `Orientacoes/README.md`
- **Arquivos de Debug**: `SCRATCK HERE/`

## 🛠️ Desenvolvimento

### Estrutura Limpa
- **Código de produção**: `RegistroOS/registrooficial/`
- **Documentação**: `Orientacoes/`
- **Debug/Testes**: `SCRATCK HERE/`

### Scripts Úteis
```bash
# Iniciar ambos os serviços
./start_registroos.ps1

# Apenas backend
cd RegistroOS/registrooficial/backend && python main.py

# Apenas frontend  
cd RegistroOS/registrooficial/frontend && npm start
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Consulte a documentação em `Orientacoes/`
2. Verifique os arquivos de teste em `SCRATCK HERE/`
3. Execute os scripts de diagnóstico disponíveis

---

**Status**: ✅ **Sistema Limpo e Organizado**
**Última atualização**: Janeiro 2025
