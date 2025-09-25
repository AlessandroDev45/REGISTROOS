# 📋 ANÁLISE COMPLETA DOS CAMPOS DOS FORMULÁRIOS

## 🎯 **CAMPOS PARA CRIAR NOVOS ELEMENTOS**

### **⚙️ 1. DEPARTAMENTO** (DepartamentoForm)
**CAMPOS:**
- `nome_tipo` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Todos campos são de entrada manual (é o nível mais alto da hierarquia)

---

### **🏭 2. SETORES** (SetorForm)
**CAMPOS:**
- `nome` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `descricao` (string) - **INPUT MANUAL** ✏️
- `area_tipo` (string) - **INPUT MANUAL** ✏️ (ex: PRODUCAO)
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento vem da DB, demais campos são manuais

---

### **🔧 3. TIPOS DE MÁQUINA** (TipoMaquinaForm)
**CAMPOS:**
- `nome_tipo` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `setor` (string) - **DROPDOWN DA DB** 🔽 (busca de setores do departamento)
- `categoria` (string) - **INPUT MANUAL** ✏️ (ex: MOTOR, GERADOR)
- `descricao_partes` (JSON) - **EDITOR VISUAL/JSON** 🎨 (estrutura hierárquica)
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento/Setor da DB, categoria e demais campos manuais

---

### **🧪 4. TIPOS DE TESTES** (TipoTesteForm)
**CAMPOS:**
- `nome` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `setor` (string) - **DROPDOWN DA DB** 🔽 (busca de setores do departamento)
- `tipo_teste` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `tipo_maquina` (string) - **DROPDOWN DA DB** 🔽 (busca de tipos_maquina)
- `categoria` (string) - **DROPDOWN DA DB** 🔽 (busca de tipos_maquina.categoria)
- `subcategoria` (number) - **DROPDOWN DA DB** 🔽 (busca subcategorias)
- `teste_exclusivo_setor` (boolean) - **CHECKBOX** ☑️
- `descricao_teste_exclusivo` (string) - **INPUT MANUAL** ✏️
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento/Setor/TipoMaquina/Categoria da DB, demais campos manuais

---

### **📋 5. ATIVIDADES** (TipoAtividadeForm)
**CAMPOS:**
- `nome_tipo` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `setor` (string) - **DROPDOWN DA DB** 🔽 (busca de setores do departamento)
- `categoria` (string) - **INPUT MANUAL** ✏️ (ex: MOTOR, GERADOR)
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento/Setor da DB, categoria e demais campos manuais

---

### **📄 6. DESCRIÇÃO DE ATIVIDADES** (DescricaoAtividadeForm)
**CAMPOS:**
- `codigo` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `setor` (string) - **DROPDOWN DA DB** 🔽 (busca de setores do departamento)
- `categoria` (string) - **DROPDOWN DA DB** 🔽 (busca de tipos_maquina.categoria)
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento/Setor/Categoria da DB, demais campos manuais

---

### **⚠️ 7. TIPOS DE FALHA** (TipoFalhaForm)
**CAMPOS:**
- `codigo` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `setor` (string) - **DROPDOWN DA DB** 🔽 (busca de setores do departamento)
- `categoria` (string) - **DROPDOWN DA DB** 🔽 (busca de tipos_maquina.categoria)
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento/Setor/Categoria da DB, demais campos manuais

---

### **🔄 8. CAUSAS DE RETRABALHO** (CausaRetrabalhoForm)
**CAMPOS:**
- `codigo` (string) - **INPUT MANUAL** ✏️
- `descricao` (string) - **INPUT MANUAL** ✏️
- `departamento` (string) - **DROPDOWN DA DB** 🔽 (busca de departamentos)
- `setor` (string) - **DROPDOWN DA DB** 🔽 (busca de setores do departamento)
- `ativo` (boolean) - **CHECKBOX** ☑️

**PADRÃO:** Departamento/Setor da DB, demais campos manuais

---

### **🌳 9. ESTRUTURA HIERÁRQUICA** (HierarchicalProcessForm)
**CAMPOS:**
- `id_setor` (number) - **DROPDOWN DA DB** 🔽 (busca de setores)
- `nome_setor` (string) - **READONLY** 👁️ (preenchido automaticamente)
- `id_tipo_maquina` (number) - **DROPDOWN DA DB** 🔽 (busca de tipos_maquina do setor)
- `nome_tipo_maquina` (string) - **READONLY** 👁️ (preenchido automaticamente)
- `id_tipo_teste` (number) - **DROPDOWN DA DB** 🔽 (busca de tipos_teste da máquina)
- `nome_tipo_teste` (string) - **READONLY** 👁️ (preenchido automaticamente)
- `id_atividade` (number) - **DROPDOWN DA DB** 🔽 (busca de atividades do teste)
- `nome_atividade` (string) - **READONLY** 👁️ (preenchido automaticamente)

**PADRÃO:** Todos campos são dropdowns hierárquicos da DB (formulário de relacionamento)

---

## 🎯 **RESUMO DO PADRÃO**

### **📝 INPUT MANUAL (onde criamos dados):**
- **Departamento**: nome_tipo, descricao
- **Tipos de Máquina**: categoria
- **Atividades**: categoria
- **Todos**: nome/codigo, descricao

### **🔽 DROPDOWN DA DB (onde usamos dados criados):**
- **Departamento**: usado por todos os outros
- **Setor**: usado por tipos de máquina, testes, atividades, etc.
- **Categoria de Máquina**: usado por descrição de atividades, tipos de falha, tipos de testes
- **Tipos de Máquina**: usado por tipos de testes
- **Hierárquica**: usa todos os níveis em cascata

### **✅ CAMPOS ESPECIAIS:**
- **Editor Visual**: Estrutura de partes (TipoMaquinaForm)
- **Checkboxes**: ativo, teste_exclusivo_setor
- **Readonly**: Nomes na estrutura hierárquica

---

## 🔍 **CAMPOS DE FILTROS PARA LISTAS**

### **⚙️ 1. DEPARTAMENTO** (DepartamentoList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: nome_tipo, descricao
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

---

### **🏭 2. SETORES** (SetorList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: nome, descricao
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Área Tipo**: Dropdown (PRODUCAO, ADMINISTRATIVO, etc.)
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

---

### **🔧 3. TIPOS DE MÁQUINA** (TipoMaquinaList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: nome_tipo, descricao
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Setor**: Dropdown (busca de setores do departamento)
- 🔽 **Categoria**: Dropdown (busca categorias únicas)
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

---

### **🧪 4. TIPOS DE TESTES** (TipoTesteList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: nome, descricao, tipo_teste
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Setor**: Dropdown (busca de setores do departamento)
- 🔽 **Tipo Máquina**: Dropdown (busca de tipos_maquina)
- 🔽 **Categoria**: Dropdown (busca de tipos_maquina.categoria)
- 🔽 **Tipo Teste**: Dropdown (valores únicos do campo tipo_teste)
- ☑️ **Status**: Ativo/Inativo/Todos
- ☑️ **Exclusivo Setor**: Sim/Não/Todos
- 📊 **Contador**: X de Y registros

---

### **📋 5. ATIVIDADES** (TipoAtividadeList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: nome_tipo, descricao
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Setor**: Dropdown (busca de setores do departamento)
- 🔽 **Categoria**: Dropdown (busca categorias únicas de tipo_atividade)
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

---

### **📄 6. DESCRIÇÃO DE ATIVIDADES** (DescricaoAtividadeList) ✅ **JÁ IMPLEMENTADO**
**FILTROS EXISTENTES:**
- 🔍 **Busca por texto**: codigo, descricao ✅
- 🔽 **Setor**: Dropdown (setores únicos) ✅
- ☑️ **Status**: Ativo/Inativo/Todos ✅
- 📊 **Contador**: X de Y registros ✅

**FILTROS A ADICIONAR:**
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Categoria**: Dropdown (busca de tipos_maquina.categoria)

---

### **⚠️ 7. TIPOS DE FALHA** (TipoFalhaList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: codigo, descricao
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Setor**: Dropdown (busca de setores do departamento)
- 🔽 **Categoria**: Dropdown (busca de tipos_maquina.categoria)
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

---

### **🔄 8. CAUSAS DE RETRABALHO** (CausaRetrabalhoList)
**FILTROS NECESSÁRIOS:**
- 🔍 **Busca por texto**: codigo, descricao
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Setor**: Dropdown (busca de setores do departamento)
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

---

### **🌳 9. ESTRUTURA HIERÁRQUICA** (HierarchicalProcessForm)
**FILTROS NECESSÁRIOS:**
- 🔽 **Departamento**: Dropdown (busca de departamentos)
- 🔽 **Setor**: Dropdown (busca de setores do departamento)
- 🔽 **Tipo Máquina**: Dropdown (busca de tipos_maquina do setor)
- 🔽 **Categoria**: Dropdown (busca de tipos_maquina.categoria)
- 🔽 **Tipo Teste**: Dropdown (busca de tipos_teste da máquina)
- 🔽 **Atividade**: Dropdown (busca de atividades do teste)
- 🔄 **Reset**: Botão para limpar todos os filtros
- 📊 **Visualização**: Árvore hierárquica filtrada

---

## 🎯 **PADRÃO DE FILTROS**

### **📋 FILTROS BÁSICOS (todos devem ter):**
- 🔍 **Busca por texto**: Campos principais (nome, codigo, descricao)
- ☑️ **Status**: Ativo/Inativo/Todos
- 📊 **Contador**: X de Y registros

### **🔽 FILTROS HIERÁRQUICOS (conforme dependência):**
- **Departamento** → **Setor** → **Categoria/Tipo Máquina** → **Outros**
- Filtros em cascata (setor depende de departamento, etc.)

### **🎨 LAYOUT PADRÃO:**
- Grid responsivo (1 coluna mobile, 3-4 colunas desktop)
- Fundo cinza claro para área de filtros
- Bordas e espaçamento consistentes
- Contador de resultados visível
