# 🚀 RegistroOS - Inicialização Automática

Este documento explica como iniciar automaticamente tanto o **backend** quanto o **frontend** do RegistroOS com um único comando.

## 📋 Pré-requisitos

- ✅ **Python 3.8+** instalado
- ✅ **Node.js 16+** e **npm** instalados
- ✅ Dependências do backend instaladas (`pip install -r requirements.txt`)
- ✅ Dependências do frontend instaladas (`npm install` no diretório frontend)

## 🎯 Opções de Inicialização

### **Opção 1: Script Python (Recomendado)**
```bash
python start_app.py
```

### **Opção 2: Arquivo Batch (Windows)**
Duplo clique em: `start_registroos.bat`

### **Opção 3: Script PowerShell (Windows)**
```powershell
.\start_registroos.ps1
```

### **Opção 4: Main.py Modificado**
```bash
cd backend
python main.py
```

## 🌐 URLs de Acesso

Após a inicialização, o sistema estará disponível em:

- **🖥️ Frontend (Interface)**: http://localhost:3001
- **⚙️ Backend (API)**: http://localhost:8000
- **📚 Documentação da API**: http://localhost:8000/docs

## 🛑 Como Parar o Sistema

Para parar todos os serviços:
- Pressione **Ctrl+C** no terminal
- Os processos do backend e frontend serão encerrados automaticamente

## 🔧 Funcionalidades

### ✅ **O que o sistema faz automaticamente:**

1. **Verifica diretórios** necessários
2. **Inicia o backend** FastAPI na porta 8000
3. **Aguarda 3 segundos** para o backend estabilizar
4. **Inicia o frontend** React/Vite na porta 3001
5. **Monitora os processos** e exibe status
6. **Encerra graciosamente** com Ctrl+C

### 🖥️ **Comportamento no Windows:**

- Cada serviço abre em **janela separada** do console
- Facilita o monitoramento individual de logs
- Permite fechar serviços individualmente se necessário

### 🐧 **Comportamento no Linux/Mac:**

- Processos executam em **background**
- Logs são exibidos no terminal principal
- Encerramento conjunto com Ctrl+C

## 🚨 Solução de Problemas

### **Erro: "Porta já em uso"**
```bash
# Verificar processos usando as portas
netstat -ano | findstr :8000
netstat -ano | findstr :3001

# Matar processos se necessário
taskkill /PID <PID_NUMBER> /F
```

### **Erro: "Python não encontrado"**
- Verifique se Python está no PATH
- Reinstale Python marcando "Add to PATH"

### **Erro: "npm não encontrado"**
- Verifique se Node.js está instalado
- Reinstale Node.js incluindo npm

### **Erro: "Diretório não encontrado"**
- Execute o script a partir do diretório `registrooficial`
- Verifique se as pastas `backend` e `frontend` existem

## 📁 Estrutura de Arquivos

```
registrooficial/
├── start_app.py              # Script principal Python
├── start_registroos.bat      # Script Windows Batch
├── start_registroos.ps1      # Script Windows PowerShell
├── INICIALIZACAO.md          # Este arquivo
├── backend/
│   ├── main.py              # Backend modificado (também funciona)
│   └── ...
└── frontend/
    ├── package.json
    └── ...
```

## 🎉 Vantagens

- ✅ **Um único comando** inicia tudo
- ✅ **Monitoramento automático** dos processos
- ✅ **Encerramento gracioso** com Ctrl+C
- ✅ **Multiplataforma** (Windows, Linux, Mac)
- ✅ **Janelas separadas** no Windows para melhor visualização
- ✅ **Verificações automáticas** de dependências e diretórios

## 💡 Dicas

1. **Para desenvolvimento**: Use `start_app.py` para ter controle total
2. **Para usuários finais**: Use `start_registroos.bat` (duplo clique)
3. **Para automação**: Use scripts PowerShell ou Batch em tarefas agendadas
4. **Para produção**: Configure como serviços do sistema operacional

---

**🎯 Agora você pode iniciar todo o RegistroOS com apenas um comando!**
