# 🌳 Estrutura Completa do Banco de Dados REGISTROOS 🌳

Este documento apresenta a hierarquia e os relacionamentos do sistema REGISTROOS de forma visual e didática.

---

## 🏛️ 1. GESTÃO ORGANIZACIONAL & PESSOAS

A base da estrutura do sistema, definindo departamentos, setores e os usuários que os compõem.

*   **1.1. 🏢 Departamentos** (`tipo_departamentos`)
    *   `id` (🔑 PK)
    *   `nome_tipo`
    *   `descricao`
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`

*   **1.2. 🏗️ Setores** (`tipo_setores`)
    *   `id` (🔑 PK)
    *   `nome`
    *   `descricao`
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `area_tipo`
    *   `supervisor_responsável`
    *   `permite_apontamento`
    *   `departamento` (compatibilidade)
    *   `departamento_obj` (Relacionamento)
    *   **LÓGICA:** Um `Setor` **pertence a** um `Departamento`.

*   **1.3. 👤 Usuários** (`tipo_usuarios`)
    *   `id` (🔑 PK)
    *   `nome_completo`
    *   `nome_usuario`
    *   `email`
    *   `matricula`
    *   `senha_hash`
    *   `cargo`
    *   `privilege_level`
    *   `is_approved`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `trabalha_producao`
    *   `obs_reprovacao`
    *   `id_setor` (🔗 FK para `tipo_setores.id`)
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `primeiro_login`
    *   `setor_obj` (Relacionamento)
    *   `departamento_obj` (Relacionamento)
    *   **LÓGICA:** Um `Usuário` **pertence a** um `Setor` e, consequentemente, a um `Departamento`.

---

## 🛠️ 2. INFRAESTRUTURA OPERACIONAL & RECURSOS DO SETOR

Detalha os ativos, testes e procedimentos que são gerenciados e utilizados pelos setores.

*   **2.1. ⚙️ Tipos de Máquinas** (`tipos_maquina`)
    *   `id` (🔑 PK)
    *   `nome_tipo` (Ex: MAQUINA ROTATIVA CA)
    *   `categoria` 🎯 (Ex: MOTOR, GERADOR)
    *   `subcategoria` (JSON array, Ex: ESTATOR, ROTOR)
    *   `descricao`
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `especificacoes_tecnicas`
    *   `campos_teste_resultado`
    *   `setor` (compatibilidade)
    *   `departamento` (compatibilidade)
    *   `departamento_obj` (Relacionamento)
    *   **LÓGICA:** `Tipos de Máquinas` são gerenciados por um `Departamento` e associados a um `Setor`. Sua `Categoria` é vital para outras entidades.

*   **2.2. 🧪 Tipos de Teste** (`tipos_teste`)
    *   `id` (🔑 PK)
    *   `nome` (Ex: Ensaio Elétrico)
    *   `departamento` (depende do `Departamento` do `Setor`)
    *   `setor` (depende do `Setor` que o gerencia)
    *   `tipo_teste` (Ex: ESTÁTICO, DINÂMICO)
    *   `descricao`
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `tipo_maquina` (🔗 FK para `tipos_maquina.id` - **Depende do Tipo de Máquina**)
    *   `teste_exclusivo_setor`
    *   `descricao_teste_exclusivo` (Ex: Teste Daimer)
    *   `categoria` (Ex: Visual)
    *   `subcategoria` (Ex: Padrão)
    *   **LÓGICA:** `Tipos de Teste` são específicos para um `Departamento`, `Setor` e, crucialmente, para um `Tipo de Máquina` específico.

*   **2.3. 📋 Tipos de Atividade** (`tipo_atividade`)
    *   `id` (🔑 PK)
    *   `nome_tipo`
    *   `descricao`
    *   `categoria` 🎯 (Depende da **Categoria da Máquina** selecionada)
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `id_tipo_maquina` (🔗 FK para `tipos_maquina.id` - **Conceptual: Pode ser filtrado por Tipo de Máquina e Categoria**)
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `departamento`
    *   `setor`
    *   **LÓGICA:** `Tipos de Atividade` são contextualizados pela `Categoria da Máquina`, gerenciados por `Departamento` e `Setor`.

*   **2.4. 📄 Descrições de Atividade** (`tipo_descricao_atividade`)
    *   `id` (🔑 PK)
    *   `codigo`
    *   `descricao`
    *   `categoria` 🎯 (Depende da **Categoria da Máquina** selecionada)
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `setor`
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `departamento`
    *   `tipo_maquina` (🔗 FK para `tipos_maquina.id` - **Conceptual: Pode ser filtrado por Tipo de Máquina e Categoria**)
    *   **LÓGICA:** Similar aos `Tipos de Atividade`, as `Descrições` são filtradas pela `Categoria da Máquina` e vinculadas a `Departamento` e `Setor`.

*   **2.5. ⚠️ Tipos de Falha** (`tipo_falha`)
    *   `id` (🔑 PK)
    *   `codigo`
    *   `descricao`
    *   `categoria` 🎯 (Depende da **Categoria da Máquina** selecionada)
    *   `severidade` (BAIXA, MEDIA, ALTA, CRITICA)
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `setor`
    *   `observacoes`
    *   `departamento`
    *   **LÓGICA:** `Tipos de Falha` são associados a `Departamento`, `Setor` e, novamente, à `Categoria da Máquina`.

*   **2.6. 🔄 Causas de Retrabalho** (`tipo_causas_retrabalho`)
    *   `id` (🔑 PK)
    *   `codigo`
    *   `descricao`
    *   `ativo`
    *   `data_criacao`
    *   `data_ultima_atualizacao`
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `departamento`
    *   `setor`
    *   **LÓGICA:** As `Causas de Retrabalho` são identificadas e gerenciadas por `Departamento` e `Setor`, frequentemente ligadas a `Tipos de Falha` ou processos.

---

## 💼 3. GESTÃO DE CLIENTES E ATIVOS

Entidades primárias que definem quem e o que é o objeto de serviço.

*   **3.1. 🤝 Clientes** (`clientes`)
    *   `id` (🔑 PK)
    *   `razao_social`
    *   `nome_fantasia`
    *   `cnpj_cpf`
    *   `contato_principal`
    *   `telefone_contato`
    *   `email_contato`
    *   `endereco`
    *   `data_criacao`
    *   `data_ultima_atualizacao`

*   **3.2. 🛠️ Equipamentos** (`equipamentos`)
    *   `id` (🔑 PK)
    *   `descricao`
    *   `tipo`
    *   `fabricante`
    *   `modelo`
    *   `numero_serie`
    *   `data_criacao`
    *   `data_ultima_atualizacao`

---

## 📝 4. FLUXO CENTRAL: ORDEM DE SERVIÇO (OS) & EXECUÇÃO

O coração do sistema, detalhando a jornada de uma OS desde sua criação até a finalização, incluindo programações, apontamentos, testes e pendências.

*   **4.1. 📑 Ordens de Serviço (OS)** (`ordens_servico`)
    *   `id` (🔑 PK)
    *   `os_numero`
    *   `status_os`, `prioridade`, `status_geral`
    *   `id_responsavel_registro` (🔗 FK para `tipo_usuarios.id`)
    *   `id_responsavel_pcp` (🔗 FK para `tipo_usuarios.id`)
    *   `id_responsavel_final` (🔗 FK para `tipo_usuarios.id`)
    *   `data_inicio_prevista`, `data_fim_prevista`, `data_criacao`, `data_ultima_atualizacao`
    *   `criado_por`
    *   `valor_total_previsto`, `valor_total_real`, `custo_total_real`
    *   `observacoes_gerais`
    *   `id_tipo_maquina` (🔗 FK para `tipos_maquina.id`)
    *   `horas_previstas`, `horas_reais`, `horas_orcadas`
    *   `data_programacao`
    *   `testes_iniciais_finalizados`, `testes_parciais_finalizados`, `testes_finais_finalizados`
    *   `data_testes_iniciais_finalizados`, `data_testes_parciais_finalizados`, `data_testes_finais_finalizados`
    *   `id_usuario_testes_iniciais` (🔗 FK para `tipo_usuarios.id`)
    *   `id_usuario_testes_parciais` (🔗 FK para `tipo_usuarios.id`)
    *   `id_usuario_testes_finais` (🔗 FK para `tipo_usuarios.id`)
    *   `testes_exclusivo_os`
    *   `id_cliente` (🔗 FK para `clientes.id`)
    *   `id_equipamento` (🔗 FK para `equipamentos.id`)
    *   `id_setor` (🔗 FK para `tipo_setores.id`)
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `inicio_os`, `fim_os`
    *   `descricao_maquina`
    *   **LÓGICA:** A `OS` é a principal transação, **vinculando** um `Cliente` e um `Equipamento` a um `Tipo de Máquina`, `Setor` e `Departamento`, com responsáveis definidos.

*   **4.2. 📅 Programações** (`programacoes`)
    *   `id` (🔑 PK)
    *   `id_ordem_servico` (🔗 FK para `ordens_servico.id`)
    *   `criado_por_id` (🔗 FK para `tipo_usuarios.id`)
    *   `responsavel_id` (🔗 FK para `tipo_usuarios.id`)
    *   `observacoes`
    *   `status`
    *   `inicio_previsto`, `fim_previsto`
    *   `created_at`, `updated_at`
    *   `id_setor` (🔗 FK para `tipo_setores.id`)
    *   **LÓGICA:** Uma `OS` pode ter uma ou muitas `Programações`, indicando períodos e responsáveis pelo trabalho.

*   **4.3. ⏳ Apontamentos Detalhados** (`apontamentos_detalhados`)
    *   `id` (🔑 PK)
    *   `id_os` (🔗 FK para `ordens_servico.id` - **Depende dos dados da OS**)
        *   *(Isso implica acesso a: `Número da OS`, `Status OS`, `Cliente`, `Equipamento`, `Tipo de Máquina` da OS)*
    *   `id_usuario` (🔗 FK para `tipo_usuarios.id`)
    *   `id_setor` (🔗 FK para `tipo_setores.id`)
    *   `data_hora_inicio`
    *   `data_hora_fim`
    *   `status_apontamento`
    *   `foi_retrabalho` (🔄 Sim/Não)
    *   `causa_retrabalho` (🔗 FK para `tipo_causas_retrabalho.id` - se `foi_retrabalho` for verdadeiro)
    *   `observacao_os`
    *   `servico_de_campo`
    *   `observacoes_gerais`
    *   `aprovado_supervisor`
    *   `data_aprovacao_supervisor`
    *   `supervisor_aprovacao` (🔗 FK para `tipo_usuarios.id`)
    *   `criado_por`, `criado_por_email`
    *   `data_processo_finalizado`
    *   `setor` (compatibilidade)
    *   `horas_orcadas`
    *   **Etapas de Finalização:**
        *   `etapa_inicial`, `horas_etapa_inicial`, `observacoes_etapa_inicial`, `data_etapa_inicial`, `supervisor_etapa_inicial` (🔗 FK para `tipo_usuarios.id`)
        *   `etapa_parcial`, `horas_etapa_parcial`, `observacoes_etapa_parcial`, `data_etapa_parcial`, `supervisor_etapa_parcial` (🔗 FK para `tipo_usuarios.id`)
        *   `etapa_final`, `horas_etapa_final`, `observacoes_etapa_final`, `data_etapa_final`, `supervisor_etapa_final` (🔗 FK para `tipo_usuarios.id`)
    *   `tipo_maquina` (🔗 FK para `tipos_maquina.id` - **Depende do Tipo de Máquina**)
    *   `tipo_atividade` (🔗 FK para `tipo_atividade.id` - **Depende do Tipo de Atividade**)
    *   `descricao_atividade` (🔗 FK para `tipo_descricao_atividade.id` - **Depende da Descrição da Atividade**)
    *   `categoria_maquina`
    *   `subcategorias_maquina`, `subcategorias_finalizadas`, `data_finalizacao_subcategorias`
    *   `emprestimo_setor`
    *   `pendencia` (flag/status - **PODE ou NÃO GERAR uma PENDÊNCIA**)
    *   `pendencia_data`
    *   **LÓGICA:** Os `Apontamentos Detalhados` registram o trabalho executado em uma `OS`. Podem ser criados:
        *   **Diretamente** (sem programação prévia).
        *   **Através de uma Programação**.
        *   Eles capturam informações detalhadas sobre a atividade, quem a fez, quando, se foi retrabalho, e o progresso por etapas, além de serem o ponto de entrada para `Resultados de Testes` e `Pendências`.

*   **4.4. 🛑 Pendências** (`pendencias`)
    *   `id` (🔑 PK)
    *   `numero_os` (🔗 FK para `ordens_servico.os_numero`)
    *   `cliente`, `data_inicio`
    *   `id_responsavel_inicio` (🔗 FK para `tipo_usuarios.id`)
    *   `tipo_maquina`, `descricao_maquina`
    *   `descricao_pendencia`, `status`, `prioridade`
    *   `data_fechamento`
    *   `id_responsavel_fechamento` (🔗 FK para `tipo_usuarios.id`)
    *   `solucao_aplicada`, `observacoes_fechamento`
    *   `id_apontamento_origem` (🔗 FK para `apontamentos_detalhados.id` - **Pode ser gerada por um Apontamento**)
    *   `id_apontamento_fechamento` (🔗 FK para `apontamentos_detalhados.id`)
    *   `tempo_aberto_horas`, `data_criacao`, `data_ultima_atualizacao`
    *   **LÓGICA:** `Pendências` surgem de uma `OS` e podem ser originadas ou resolvidas a partir de um `Apontamento Detalhado`.

*   **4.5. ✅ Resultados de Testes** (`resultados_teste`)
    *   `id` (🔑 PK)
    *   `id_apontamento` (🔗 FK para `apontamentos_detalhados.id`)
    *   `id_teste` (🔗 FK para `tipos_teste.id`)
    *   `resultado`
    *   `observacao`
    *   `data_registro`
    *   **LÓGICA:** Registra os resultados de `Tipos de Teste` executados durante um `Apontamento Detalhado`.

*   **4.6. 📝 OS Testes Exclusivos Finalizados** (`os_testes_exclusivos_finalizados`)
    *   `id` (🔑 PK)
    *   `numero_os` (🔗 FK para `ordens_servico.os_numero`)
    *   `id_teste_exclusivo` (🔗 FK para `tipos_teste.id`)
    *   `nome_teste`, `descricao_teste`
    *   `usuario_finalizacao`
    *   `departamento`, `setor`
    *   `data_finalizacao`, `hora_finalizacao`
    *   `descricao_atividade`
    *   `observacoes`, `data_criacao`
    *   **LÓGICA:** Registra a conclusão de `Tipos de Teste` que são exclusivos de uma `OS`.

---

## ⚙️ 5. GESTÃO DO SISTEMA

Entidades para configuração e auditoria internas do sistema.

*   **5.1. 🗓️ Feriados** (`tipo_feriados`)
    *   `id` (🔑 PK)
    *   `nome`, `data_feriado`
    *   `tipo` (Nacional, Estadual, Municipal)
    *   `ativo`
    *   `data_criacao`, `data_ultima_atualizacao`
    *   `observacoes`

*   **5.2. ⚠️ Tipos de Falha** (`tipo_falha`)
    *   `id` (🔑 PK)
    *   `codigo`, `descricao`
    *   `categoria`
    *   `severidade` (BAIXA, MEDIA, ALTA, CRITICA)
    *   `ativo`
    *   `data_criacao`, `data_ultima_atualizacao`
    *   `id_departamento` (🔗 FK para `tipo_departamentos.id`)
    *   `setor`, `observacoes`, `departamento`
    *   **LÓGICA:** Tipos de falha para categorizar problemas, com vínculos organizacionais.

*   **5.3. 📜 Logs de Migração** (`migration_log`)
    *   `id` (🔑 PK)
    *   `fase`, `acao`
    *   `tabela_afetada`, `registros_afetados`
    *   `data_execucao`, `observacoes`

---

### 🔑 Legenda do Mapa Visual

*   `[Nome da Seção]` : Título principal do grupo de entidades.
*   `[Nome da Entidade]` (`nome_da_tabela`) : Título da tabela e seu nome técnico.
*   `id` (🔑 PK) : **Primary Key** (Chave Primária), identificador único da tabela.
*   `{FK: Tabela Destino}` : **Foreign Key** (Chave Estrangeira), aponta para a PK de outra tabela.
*   `🔗` : Indica um relacionamento de Chave Estrangeira explícito.
*   `🎯 **categoria**` : Destaca a **Categoria da Máquina** como um atributo crucial para contextualização e filtragem em várias entidades.
*   **LÓGICA:** : Explica o principal relacionamento ou dependência da entidade.

---

## 🌐 6. MAPEAMENTO COMPLETO DE ROTAS E ENDPOINTS

Esta seção documenta todas as rotas e endpoints do sistema RegistroOS, organizados por módulo funcional e alinhados com a hierarquia do banco de dados.

### 📊 **6.1. DASHBOARD** (`/api/dashboard`)

#### **Frontend Routes:**
- **Dashboard Principal** - Visão geral do sistema
- **Métricas em Tempo Real** - KPIs e indicadores
- **Gráficos de Performance** - Análises visuais

#### **Backend Endpoints:**
- `GET /api/general/health` - Status do sistema
- `GET /api/pcp/dashboard` - Dashboard PCP
- `GET /api/pcp/pendencias/dashboard` - Dashboard de pendências

---

### 📝 **6.2. PCP (PLANEJAMENTO E CONTROLE DE PRODUÇÃO)** (`/api/pcp`)

#### **Frontend Routes:**
- **PCP Principal** - Interface de planejamento
- **Programação** - Criação e gestão de programações
- **Pendências** - Gestão de pendências

#### **Backend Endpoints:**
```
GET    /api/pcp/ordens-servico           # Ordens de serviço para PCP
GET    /api/pcp/programacao-form-data    # Dados para formulário de programação
POST   /api/pcp/programacoes             # Criar nova programação
GET    /api/pcp/programacoes             # Listar programações
PUT    /api/pcp/programacoes/{id}        # Atualizar programação
DELETE /api/pcp/programacoes/{id}        # Excluir programação
GET    /api/pcp/pendencias               # Listar pendências
GET    /api/pcp/pendencias/dashboard     # Dashboard de pendências
POST   /api/pcp/pendencias               # Criar pendência
PUT    /api/pcp/pendencias/{id}          # Atualizar pendência
GET    /api/pcp/dashboard                # Dashboard PCP
```

---

### 🔍 **6.3. CONSULTA OS** (`/api/os`)

#### **Frontend Routes:**
- **Consulta OS** - Busca e visualização de ordens de serviço
- **Detalhes OS** - Visualização detalhada de uma OS
- **Histórico OS** - Histórico de alterações

#### **Backend Endpoints:**
```
GET    /api/os/                         # Listar ordens de serviço
POST   /api/os/                         # Criar nova OS
GET    /api/os/{os_id}                  # Detalhes de uma OS
PUT    /api/os/{os_id}                  # Atualizar OS
DELETE /api/os/{os_id}                  # Excluir OS
GET    /api/os/search                   # Buscar OS por critérios
GET    /api/os/{os_id}/apontamentos     # Apontamentos de uma OS
GET    /api/os/{os_id}/pendencias       # Pendências de uma OS
GET    /api/os/{os_id}/programacoes     # Programações de uma OS
```

---

### 👨‍💼 **6.4. ADMINISTRADOR** (`/api/admin`)

#### **Frontend Routes:**
- **Administrador** - Interface administrativa principal
- **Gestão de Usuários** - CRUD de usuários
- **Configurações** - Configurações do sistema

#### **Backend Endpoints:**
```
GET    /api/admin/status                # Status do sistema
GET    /api/admin/departamentos         # Listar departamentos
POST   /api/admin/departamentos         # Criar departamento
PUT    /api/admin/departamentos/{id}    # Atualizar departamento
DELETE /api/admin/departamentos/{id}    # Excluir departamento
GET    /api/admin/setores               # Listar setores
POST   /api/admin/setores               # Criar setor
PUT    /api/admin/setores/{id}          # Atualizar setor
DELETE /api/admin/setores/{id}          # Excluir setor
GET    /api/admin/tipos-maquina         # Listar tipos de máquina
POST   /api/admin/tipos-maquina         # Criar tipo de máquina
PUT    /api/admin/tipos-maquina/{id}    # Atualizar tipo de máquina
DELETE /api/admin/tipos-maquina/{id}    # Excluir tipo de máquina
GET    /api/admin/tipos-teste           # Listar tipos de teste
POST   /api/admin/tipos-teste           # Criar tipo de teste
PUT    /api/admin/tipos-teste/{id}      # Atualizar tipo de teste
DELETE /api/admin/tipos-teste/{id}      # Excluir tipo de teste
```

---

### ⚙️ **6.5. ADMIN CONFIG** (`/api/admin/config`)

#### **Frontend Routes:**
- **Configurações Avançadas** - Configurações técnicas
- **Backup/Restore** - Gestão de backups
- **Logs do Sistema** - Visualização de logs

#### **Backend Endpoints:**
```
GET    /api/admin/config/sistema        # Configurações do sistema
PUT    /api/admin/config/sistema        # Atualizar configurações
GET    /api/admin/config/backup         # Criar backup
POST   /api/admin/config/restore        # Restaurar backup
GET    /api/admin/config/logs           # Logs do sistema
DELETE /api/admin/config/logs           # Limpar logs
```

---

### 📈 **6.6. GESTÃO** (`/api/gestao`)

#### **Frontend Routes:**
- **Gestão Principal** - Interface de gestão
- **Relatórios** - Relatórios gerenciais
- **Análises** - Análises de performance

#### **Backend Endpoints:**
```
GET    /api/gestao/dashboard            # Dashboard de gestão
GET    /api/gestao/relatorios           # Relatórios gerenciais
GET    /api/gestao/metricas             # Métricas de performance
GET    /api/gestao/usuarios             # Usuários para gestão
GET    /api/gestao/setores              # Setores para gestão
GET    /api/gestao/departamentos        # Departamentos para gestão
GET    /api/gestao/ordens-servico       # OS para gestão
GET    /api/gestao/apontamentos         # Apontamentos para gestão
GET    /api/gestao/pendencias           # Pendências para gestão
```

---

### 🛠️ **6.7. DESENVOLVIMENTO** (`/api/desenvolvimento`)

#### **Frontend Routes:**
- **Desenvolvimento Principal** - Interface de desenvolvimento
- **Formulários Dinâmicos** - Formulários inteligentes
- **Seleção de Setores** - Seleção dinâmica de setores

#### **Backend Endpoints:**
```
GET    /api/desenvolvimento/ordens-servico        # OS para desenvolvimento
POST   /api/desenvolvimento/apontamentos          # Criar apontamento
GET    /api/desenvolvimento/apontamentos/{os_id}  # Apontamentos de uma OS
PUT    /api/desenvolvimento/apontamentos/{id}     # Atualizar apontamento
DELETE /api/desenvolvimento/apontamentos/{id}     # Excluir apontamento
POST   /api/desenvolvimento/programacoes          # Criar programação
GET    /api/desenvolvimento/formulario/dados      # Dados para formulário
GET    /api/desenvolvimento/setores               # Setores disponíveis
GET    /api/desenvolvimento/tipos-maquina         # Tipos de máquina
GET    /api/desenvolvimento/tipos-atividade       # Tipos de atividade
GET    /api/desenvolvimento/descricoes-atividade  # Descrições de atividade
GET    /api/desenvolvimento/causas-retrabalho     # Causas de retrabalho
GET    /api/desenvolvimento/colaboradores         # Colaboradores
```

#### **Subseções do Desenvolvimento:**

##### **📊 6.7.1. Dashboard**
```
GET    /api/desenvolvimento/dashboard             # Dashboard de desenvolvimento
GET    /api/desenvolvimento/dashboard/metricas    # Métricas do dashboard
GET    /api/desenvolvimento/dashboard/graficos    # Dados para gráficos
```

##### **📝 6.7.2. Apontamento**
```
POST   /api/desenvolvimento/apontamentos          # Criar novo apontamento
GET    /api/desenvolvimento/apontamentos/form     # Dados para formulário
POST   /api/desenvolvimento/apontamentos/validar  # Validar apontamento
```

##### **📋 6.7.3. Meus Apontamentos**
```
GET    /api/desenvolvimento/meus-apontamentos     # Apontamentos do usuário
GET    /api/desenvolvimento/meus-apontamentos/{id} # Detalhes do apontamento
PUT    /api/desenvolvimento/meus-apontamentos/{id} # Editar apontamento
```

##### **🔍 6.7.4. Pesquisa Apontamentos**
```
GET    /api/desenvolvimento/apontamentos/search   # Buscar apontamentos
POST   /api/desenvolvimento/apontamentos/filtros  # Aplicar filtros
GET    /api/desenvolvimento/apontamentos/export   # Exportar resultados
```

##### **📅 6.7.5. Programação** (Conversa com PCP e Gestão)
```
GET    /api/desenvolvimento/programacao           # Programações do setor
POST   /api/desenvolvimento/programacao           # Criar programação
PUT    /api/desenvolvimento/programacao/{id}      # Atualizar programação
GET    /api/desenvolvimento/programacao/pcp       # Dados do PCP
GET    /api/desenvolvimento/programacao/gestao    # Dados da Gestão
```

##### **⚠️ 6.7.6. Pendências** (Conversa com PCP e Gestão)
```
GET    /api/desenvolvimento/pendencias            # Pendências do setor
POST   /api/desenvolvimento/pendencias            # Criar pendência
PUT    /api/desenvolvimento/pendencias/{id}       # Atualizar pendência
GET    /api/desenvolvimento/pendencias/pcp        # Pendências do PCP
GET    /api/desenvolvimento/pendencias/gestao     # Pendências da Gestão
```

##### **⚙️ 6.7.7. Gerenciar**
```
GET    /api/desenvolvimento/gerenciar             # Interface de gerenciamento
GET    /api/desenvolvimento/gerenciar/setores     # Gerenciar setores
GET    /api/desenvolvimento/gerenciar/usuarios    # Gerenciar usuários do setor
```

##### **👥 6.7.8. Aprovação Usuários**
```
GET    /api/desenvolvimento/aprovacao-usuarios    # Usuários pendentes
POST   /api/desenvolvimento/aprovacao-usuarios/{id}/aprovar  # Aprovar usuário
POST   /api/desenvolvimento/aprovacao-usuarios/{id}/rejeitar # Rejeitar usuário
```

---

### 🔐 **6.8. AUTENTICAÇÃO** (`/api/auth`)

#### **Backend Endpoints:**
```
POST   /api/login                       # Login de usuário
POST   /api/logout                      # Logout de usuário
POST   /api/register                    # Registro de usuário
POST   /api/change-password             # Alterar senha
GET    /api/me                          # Dados do usuário atual
POST   /api/refresh-token               # Renovar token
```

---

### 👥 **6.9. USUÁRIOS** (`/api/users`)

#### **Backend Endpoints:**
```
GET    /api/users/                      # Listar usuários
POST   /api/users/                      # Criar usuário
GET    /api/users/{user_id}             # Detalhes do usuário
PUT    /api/users/{user_id}             # Atualizar usuário
DELETE /api/users/{user_id}             # Excluir usuário
POST   /api/users/{user_id}/approve     # Aprovar usuário
POST   /api/users/{user_id}/reject      # Rejeitar usuário
```

---

### 📚 **6.10. CATÁLOGOS** (`/api/catalogs`)

#### **Backend Endpoints:**
```
GET    /api/catalogs/departamentos      # Catálogo de departamentos
GET    /api/catalogs/setores            # Catálogo de setores
GET    /api/catalogs/tipos-maquina      # Catálogo de tipos de máquina
GET    /api/catalogs/tipos-teste        # Catálogo de tipos de teste
GET    /api/catalogs/clientes           # Catálogo de clientes
GET    /api/catalogs/equipamentos       # Catálogo de equipamentos
GET    /api/catalogs/usuarios           # Catálogo de usuários
GET    /api/catalogs/tipo-atividade     # Catálogo de tipos de atividade
GET    /api/catalogs/descricao-atividade # Catálogo de descrições de atividade
GET    /api/catalogs/tipo-falha         # Catálogo de tipos de falha
GET    /api/catalogs/causas-retrabalho  # Catálogo de causas de retrabalho
GET    /api/catalogs/status             # Status dos catálogos
```

---

### 📊 **6.11. RELATÓRIOS** (`/api/relatorio`)

#### **Backend Endpoints:**
```
GET    /api/relatorio/completo          # Relatório completo
GET    /api/relatorio/os                # Relatório de OS
GET    /api/relatorio/apontamentos      # Relatório de apontamentos
GET    /api/relatorio/pendencias        # Relatório de pendências
GET    /api/relatorio/usuarios          # Relatório de usuários
POST   /api/relatorio/personalizado     # Relatório personalizado
GET    /api/relatorio/export/{tipo}     # Exportar relatório
```

---

### 🔧 **6.12. GERAL** (`/api/general`)

#### **Backend Endpoints:**
```
GET    /api/health                      # Health check
GET    /api/test-endpoint               # Endpoint de teste
GET    /api/version                     # Versão da API
GET    /api/status                      # Status geral do sistema
```

---

### 🔄 **6.13. INTEGRAÇÃO ENTRE MÓDULOS**

#### **Comunicação PCP ↔ Desenvolvimento:**
- Programações criadas no PCP são visíveis no Desenvolvimento
- Apontamentos do Desenvolvimento atualizam status no PCP
- Pendências são compartilhadas entre ambos os módulos

#### **Comunicação Gestão ↔ Desenvolvimento:**
- Relatórios de gestão incluem dados do Desenvolvimento
- Aprovações de usuários passam pela Gestão
- Métricas de performance são compartilhadas

#### **Comunicação PCP ↔ Gestão:**
- Dashboard de gestão inclui métricas do PCP
- Relatórios gerenciais incluem dados de programação
- Pendências críticas são escaladas para a Gestão

---

### 📋 **6.14. RESUMO DE ENDPOINTS POR MÓDULO**

| **Módulo** | **Prefix** | **Endpoints** | **Funcionalidade Principal** |
|------------|------------|---------------|------------------------------|
| **Dashboard** | `/api/general` | 4 | Visão geral e métricas |
| **PCP** | `/api/pcp` | 12 | Planejamento e controle |
| **Consulta OS** | `/api/os` | 8 | Gestão de ordens de serviço |
| **Administrador** | `/api/admin` | 16 | Administração do sistema |
| **Admin Config** | `/api/admin/config` | 6 | Configurações avançadas |
| **Gestão** | `/api/gestao` | 8 | Gestão e relatórios |
| **Desenvolvimento** | `/api/desenvolvimento` | 25+ | Apontamentos e desenvolvimento |
| **Autenticação** | `/api` | 6 | Login e segurança |
| **Usuários** | `/api/users` | 6 | Gestão de usuários |
| **Catálogos** | `/api/catalogs` | 12 | Dados de referência |
| **Relatórios** | `/api/relatorio` | 7 | Relatórios e exportações |
| **Geral** | `/api` | 4 | Utilitários gerais |

**Total de Endpoints:** **114+**

---

## 🔐 7. DADOS DE ADMIN E CONFIGURAÇÕES

### 📋 **7.1. CREDENCIAIS DE ADMIN PADRÃO**

#### **Login Administrativo:**
```
Email: admin@registroos.com
Senha: 123456
Privilege Level: ADMIN
Nome: Administrador do Sistema
Matricula: ADMIN001
```

#### **Características do Admin:**
- **Acesso Total**: Todos os módulos e funcionalidades
- **Criação de Entidades**: Pode criar departamentos, setores, tipos de máquina, etc.
- **Gestão de Usuários**: Aprovar, rejeitar e gerenciar usuários
- **Configurações do Sistema**: Acesso a configurações avançadas
- **Backup/Restore**: Gestão de backups do sistema

---

### ⚙️ **7.2. ADMIN CONFIG - CRIAÇÃO DE ENTIDADES** (`/api/admin/config`)

#### **Endpoints para Criação de Entidades:**
```
POST   /api/admin/config/departamentos      # Criar departamento
POST   /api/admin/config/setores            # Criar setor
POST   /api/admin/config/tipos-maquina      # Criar tipo de máquina
POST   /api/admin/config/tipos-teste        # Criar tipo de teste
POST   /api/admin/config/tipos-atividade    # Criar tipo de atividade
POST   /api/admin/config/descricoes-atividade # Criar descrição de atividade
POST   /api/admin/config/causas-retrabalho  # Criar causa de retrabalho
POST   /api/admin/config/tipos-falha        # Criar tipo de falha
POST   /api/admin/config/clientes           # Criar cliente
POST   /api/admin/config/equipamentos       # Criar equipamento
```

#### **Endpoints de Configuração do Sistema:**
```
GET    /api/admin/config/sistema            # Configurações do sistema
PUT    /api/admin/config/sistema            # Atualizar configurações
GET    /api/admin/config/backup             # Criar backup
POST   /api/admin/config/restore            # Restaurar backup
GET    /api/admin/config/logs               # Logs do sistema
DELETE /api/admin/config/logs               # Limpar logs
GET    /api/admin/config/status             # Status das configurações
```

---

### 🏗️ **7.3. ENTIDADES PADRÃO CRIADAS**

#### **Departamentos Padrão:**
- **MOTORES** - Departamento de Motores Elétricos
- **GERADORES** - Departamento de Geradores
- **TRANSFORMADORES** - Departamento de Transformadores
- **ADMINISTRAÇÃO** - Departamento Administrativo

#### **Setores Padrão:**
- **BOBINAGEM** (MOTORES) - Setor de Bobinagem de Motores
- **MONTAGEM** (MOTORES) - Setor de Montagem de Motores
- **TESTE** (MOTORES) - Setor de Testes de Motores
- **ADMINISTRAÇÃO** (ADMINISTRAÇÃO) - Setor Administrativo

#### **Tipos de Máquina Padrão:**
- **MOTOR TRIFÁSICO** - Motor elétrico trifásico
  - Categoria: MOTOR
  - Subcategorias: ESTATOR, ROTOR, CARCAÇA
- **MOTOR MONOFÁSICO** - Motor elétrico monofásico
  - Categoria: MOTOR
  - Subcategorias: ESTATOR, ROTOR

---

### 🔧 **7.4. SCRIPT DE CONFIGURAÇÃO**

#### **Setup Automático:**
```bash
# Executar setup completo
python scripts/setup_admin_config.py
```

#### **Funcionalidades do Script:**
1. ✅ Verificar/Criar usuário admin padrão
2. ✅ Criar departamentos padrão
3. ✅ Criar setores padrão
4. ✅ Criar tipos de máquina padrão
5. ✅ Criar tipos de teste padrão
6. ✅ Criar tipos de atividade padrão
7. ✅ Criar descrições de atividade padrão
8. ✅ Criar causas de retrabalho padrão
9. ✅ Criar tipos de falha padrão
10. ✅ Criar cliente padrão
11. ✅ Criar equipamento padrão

---

### 🛡️ **7.5. NÍVEIS DE PRIVILÉGIO**

#### **Hierarquia de Privilégios:**
```
ADMIN       # Acesso total ao sistema
├── GESTAO  # Gestão e relatórios
├── PCP     # Planejamento e controle
├── SUPERVISOR # Supervisão de setores
└── USER    # Usuário padrão
```

#### **Permissões por Nível:**
- **ADMIN**: Todas as funcionalidades + Admin Config
- **GESTAO**: Dashboard, relatórios, gestão de usuários
- **PCP**: Programação, pendências, ordens de serviço
- **SUPERVISOR**: Aprovação de apontamentos, gestão do setor
- **USER**: Apontamentos, consulta de OS

---

### 📊 **7.6. CONFIGURAÇÕES DO SISTEMA**

#### **Informações do Sistema:**
```json
{
  "sistema": {
    "nome": "RegistroOS",
    "versao": "1.9.0",
    "banco_dados": "registroos_new.db"
  },
  "configuracoes": {
    "privilege_levels": ["ADMIN", "GESTAO", "PCP", "SUPERVISOR", "USER"],
    "status_os": ["ABERTA", "EM_ANDAMENTO", "FINALIZADA", "CANCELADA"],
    "tipos_area": ["PRODUÇÃO", "QUALIDADE", "ADMINISTRATIVO"]
  }
}
```

#### **Estatísticas do Sistema:**
- Total de usuários
- Total de departamentos
- Total de setores
- Total de tipos de máquina
- Total de clientes

---

### 🚀 **7.7. ACESSO AO SISTEMA**

#### **URLs de Acesso:**
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Admin Interface**: http://localhost:3001/admin

#### **Primeiro Acesso:**
1. Acesse http://localhost:3001
2. Faça login com as credenciais admin
3. Navegue para a seção Admin Config
4. Configure as entidades necessárias
5. Crie usuários para os setores

---

## 🔄 8. COMUNICAÇÃO ADMIN ↔ SUPERVISOR (FLUXO REAL)

### 📋 **8.1. FLUXOS DE CRIAÇÃO DE USUÁRIOS**

#### **Cenário 1: Admin cria usuário diretamente**
```
ADMIN → Admin Routes → Usuário criado automaticamente
```
- **Endpoint**: `POST /api/admin/usuarios`
- **Resultado**: Usuário aprovado automaticamente (`is_approved: True`)
- **Senha**: Gerada automaticamente e informada ao admin
- **Primeiro Login**: Usuário deve alterar senha no primeiro acesso

#### **Cenário 2: Auto-registro de usuário**
```
USUÁRIO → Registra-se → SUPERVISOR/ADMIN → Aprova → Usuário ativado
```
- **Endpoint Registro**: `POST /api/register`
- **Endpoint Aprovação**: `PUT /api/usuarios/{id}/approve`
- **Fluxo**:
  1. Usuário se registra no sistema
  2. Conta criada com `is_approved: False`
  3. Supervisor do setor ou Admin aprova
  4. Usuário pode fazer login

---

### ⚙️ **8.2. FLUXOS DE CRIAÇÃO DE ENTIDADES (REAL)**

#### **Admin cria entidades básicas diretamente**
```
ADMIN → Admin Config → Entidade criada imediatamente
```
- **Endpoints**: `/api/admin/config/{tipo-entidade}`
- **Tipos**: departamentos, setores, tipos-maquina, tipos-teste
- **Resultado**: Entidade disponível imediatamente no sistema

#### **Clientes e Equipamentos via Scraping**
```
Sistema Externo → Scraping → Dados extraídos → Cliente/Equipamento criado automaticamente
```
- **Script**: `scrape_os_data.py`
- **Processo**:
  1. OS é consultada no sistema externo
  2. Dados do cliente são extraídos automaticamente
  3. Cliente é criado se não existir
  4. Equipamento é relacionado via descrição da OS
  5. OS é criada com relacionamentos corretos

---

### 📢 **8.3. COMUNICAÇÃO REAL ENTRE ADMIN E SUPERVISOR**

#### **Endpoints Reais para Admin**
```
POST   /api/admin/usuarios         # Criar usuário diretamente
GET    /api/usuarios/              # Ver todos os usuários
PUT    /api/usuarios/{id}/approve  # Aprovar usuário pendente
POST   /api/admin/config/*         # Criar entidades básicas
```

#### **Endpoints Reais para Supervisor**
```
GET    /api/usuarios/              # Ver usuários do setor
PUT    /api/usuarios/{id}/approve  # Aprovar usuário do setor
GET    /api/pcp/*                  # Acessar funcionalidades PCP
GET    /api/gestao/*               # Acessar funcionalidades Gestão
```

#### **Dados de Criação de Usuário (Admin)**
```json
{
  "nome_completo": "João Silva",
  "email": "joao.silva@empresa.com",
  "matricula": "123456",
  "setor": "BOBINAGEM",
  "departamento": "MOTORES",
  "cargo": "Técnico",
  "privilege_level": "USER",
  "trabalha_producao": true
}
```

#### **Dados de Scraping de OS**
```json
{
  "OS": "12345",
  "CLIENTE": "Empresa ABC Ltda",
  "CNPJ": "12.345.678/0001-90",
  "CLASSIFICACAO DO EQUIPAMENTO": "MOTOR TRIFÁSICO",
  "DESCRIÇÃO": "Motor 10CV para bomba",
  "DEPARTAMENTO": "MOTORES"
}
```

---

### 🛡️ **8.4. PERMISSÕES E RESTRIÇÕES REAIS**

#### **Supervisor pode:**
- ✅ Aprovar usuários do seu setor (auto-registro)
- ✅ Acessar funcionalidades PCP e Gestão
- ✅ Ver usuários do seu setor
- ✅ Gerenciar apontamentos e programações
- ❌ Criar usuários diretamente
- ❌ Criar entidades básicas
- ❌ Aprovar usuários de outros setores

#### **Admin pode:**
- ✅ Criar usuários diretamente
- ✅ Criar entidades básicas (departamentos, setores, tipos)
- ✅ Aprovar usuários de qualquer setor
- ✅ Gerenciar configurações do sistema
- ✅ Acessar todos os módulos
- ✅ Executar scripts de configuração

---

### 📊 **8.5. RELACIONAMENTOS E DEPENDÊNCIAS**

#### **Fluxo de Dados Real**
```
Sistema Externo → Scraping → Cliente/Equipamento → OS → Apontamentos/Programações
```

#### **Dependências de Criação**
1. **Departamentos** → Criados pelo Admin
2. **Setores** → Dependem de Departamentos
3. **Usuários** → Dependem de Setores/Departamentos
4. **Clientes** → Criados via scraping de OS
5. **Equipamentos** → Relacionados via descrição da OS
6. **OS** → Dependem de Cliente, Equipamento, Setor, Departamento
7. **Apontamentos** → Dependem de OS e Usuário

---

## 🔧 9. CORREÇÕES IMPLEMENTADAS - FORMULÁRIO APONTAMENTO

### ✅ **9.1. PROBLEMA RESOLVIDO: Campos Observação e Resultado Global**

#### **Problema Identificado:**
- Campos **Observação Geral** e **Resultado Global** não estavam visíveis no formulário
- Erro 404 no endpoint `/api/tipos-maquina/categorias`
- Campo `resultado_global` não existia na tabela do banco de dados

#### **Correções Aplicadas:**

##### **A. Frontend (ApontamentoFormTab.tsx):**
- ✅ **Visibilidade dos campos**: Removida condição que escondia os campos quando OS estava bloqueada
- ✅ **Campos sempre visíveis**: Agora aparecem sempre, mas ficam desabilitados se OS estiver finalizada
- ✅ **Mapeamento correto**:
  - `formData.observacao` → `observacao_geral` (backend)
  - `formData.resultadoGlobal` → `resultado_global` (backend)

##### **B. Backend (routes/general.py):**
- ✅ **Endpoint categorias**: Implementado `/api/tipos-maquina/categorias`
- ✅ **Campos no apontamento**: Adicionados `observacoes_gerais` e `resultado_global`
- ✅ **Conflito datetime**: Resolvido usando alias `datetime as dt`

##### **C. Banco de Dados:**
- ✅ **Campo resultado_global**: Adicionado na tabela `apontamentos_detalhados`
- ✅ **Migração**: Script criado para adicionar o campo sem perder dados
- ✅ **Valores padrão**: Registros existentes atualizados com 'PENDENTE'

#### **Campos Implementados no Formulário:**

##### **📝 Observação Geral:**
- **Tipo**: Textarea (3 linhas)
- **Validação**: Texto em maiúsculas, formatação automática
- **Placeholder**: "OBSERVAÇÕES GERAIS SOBRE O APONTAMENTO..."
- **Estado**: Desabilitado se OS finalizada

##### **🎯 Resultado Global:**
- **Tipo**: Select dropdown
- **Opções**:
  - ✅ Aprovado
  - ❌ Reprovado
  - ⚠️ Aprovado com Restrição
  - 🔄 Pendente
  - 🔍 Em Análise
- **Estado**: Desabilitado se OS finalizada

#### **Status de Bloqueio da OS:**
OSs são bloqueadas para apontamento quando têm status:
- `RECUSADA - CONFERIDA`
- `TERMINADA - CONFERIDA`
- `TERMINADA - EXPEDIDA`
- `OS CANCELADA`

#### **Testes Realizados:**
- ✅ Login admin funcionando
- ✅ Endpoint categorias funcionando
- ✅ Criação de apontamento com observação e resultado
- ✅ Campos visíveis no formulário
- ✅ Dados salvos corretamente no banco

---

### 🗂️ **9.2. ESTRUTURA ATUALIZADA DA TABELA APONTAMENTOS_DETALHADOS**

#### **Campos Adicionados:**
```sql
-- Campo adicionado via migração
ALTER TABLE apontamentos_detalhados
ADD COLUMN resultado_global TEXT;
```

#### **Estrutura Completa (46 campos):**
1. `id` (PK)
2. `id_os` (FK → ordens_servico.id)
3. `id_usuario` (FK → tipo_usuarios.id)
4. `id_setor` (FK → tipo_setores.id)
5. `data_hora_inicio`
6. `data_hora_fim`
7. `status_apontamento`
8. `foi_retrabalho`
9. `causa_retrabalho`
10. `observacao_os`
11. `servico_de_campo`
12. **`observacoes_gerais`** ✅ (Campo para observação geral)
13. `aprovado_supervisor`
14. `data_aprovacao_supervisor`
15. `supervisor_aprovacao`
16. `criado_por`
17. `criado_por_email`
18. `data_processo_finalizado`
19. `setor`
20. `horas_orcadas`
21. `etapa_inicial`
22. `etapa_parcial`
23. `etapa_final`
24. `horas_etapa_inicial`
25. `horas_etapa_parcial`
26. `horas_etapa_final`
27. `observacoes_etapa_inicial`
28. `observacoes_etapa_parcial`
29. `observacoes_etapa_final`
30. `data_etapa_inicial`
31. `data_etapa_parcial`
32. `data_etapa_final`
33. `supervisor_etapa_inicial`
34. `supervisor_etapa_parcial`
35. `supervisor_etapa_final`
36. `tipo_maquina`
37. `tipo_atividade`
38. `descricao_atividade`
39. `categoria_maquina`
40. `subcategorias_maquina`
41. `subcategorias_finalizadas`
42. `data_finalizacao_subcategorias`
43. `emprestimo_setor`
44. `pendencia`
45. `pendencia_data`
46. **`resultado_global`** ✅ (Campo para resultado global)

---

### 📊 **9.3. ENDPOINTS ATUALIZADOS**

#### **Endpoint de Categorias (Novo):**
```
GET /api/tipos-maquina/categorias?departamento={dept}&setor={setor}
```
- **Função**: Retorna categorias de máquina filtradas por departamento e setor
- **Resposta**: Array de categorias únicas
- **Exemplo**: `['GERADOR CA', 'MOTOR', 'MOTOR CA', 'MOTOR CC', 'OPERACIONAL', 'TRANSFORMADOR']`

#### **Endpoint de Apontamento (Atualizado):**
```
POST /api/save-apontamento
```
- **Campos Novos**:
  - `observacao_geral`: Observação geral do apontamento
  - `resultado_global`: Resultado global (APROVADO, REPROVADO, etc.)

#### **Payload de Exemplo:**
```json
{
  "inpNumOS": "12345",
  "inpCliente": "EMPRESA ABC",
  "inpEquipamento": "MOTOR 10CV",
  "inpData": "2025-01-16",
  "inpDataFim": "2025-01-16",
  "observacao": "OBSERVAÇÃO GERAL DE TESTE",
  "resultadoGlobal": "APROVADO",
  "testes": {
    "1": "APROVADO",
    "2": "REPROVADO"
  },
  "observacoes_testes": {
    "1": "Teste passou",
    "2": "Falha detectada"
  }
}
```

---

### 📊 **9.4. CORREÇÕES FINAIS APLICADAS**

#### **9.4.1 Problema dos Componentes React**
- **Warning**: "A component is changing an uncontrolled input to be controlled"
- **Causa**: Campos sendo inicializados como `undefined` e depois mudando para valores definidos
- **Solução**: Todos os campos de input agora garantem valor padrão com `|| ''`

#### **9.4.2 Campos Corrigidos:**
- ✅ `formData.statusOS || ''` (campo readonly)
- ✅ `formData.inpDataFim || ''` (data fim)
- ✅ `formData.inpHoraFim || ''` (hora fim)
- ✅ `formData.observacao || ''` (observação geral)
- ✅ `formData.resultadoGlobal || ''` (resultado global)

#### **9.4.3 Inicialização do FormData Corrigida:**
```typescript
// ApontamentoContext.tsx - Inicialização completa
const [formData, setFormData] = useState<any>({
    // Campos básicos da OS
    inpNumOS: '',
    statusOS: '',
    inpCliente: '',
    inpEquipamento: '',

    // Campos de seleção
    selMaq: '',
    selAtiv: '',
    selDescAtiv: '',

    // Campos de data/hora
    inpData: '',
    inpHora: '',
    inpDataFim: '',
    inpHoraFim: '',

    // Campos de observação e resultado - CORRIGIDO
    observacao: '',
    resultadoGlobal: '',

    // Demais campos...
});
```

### 📊 **9.5. STATUS FINAL**

✅ **SISTEMA 100% ALINHADO COM A HIERARQUIA**
- Todos os campos implementados
- Relacionamentos corretos
- Endpoints funcionando
- Frontend atualizado
- **Warnings React corrigidos**
- Testes executados com sucesso

---

## 10. DEPARTAMENTO TESTE CRIADO

### 10.1 Novo Departamento e Hierarquia Completa

#### **10.1.1 Departamento TESTE (ID: 5)**
- ✅ **Nome**: TESTE
- ✅ **Descrição**: Departamento de Testes e Validação
- ✅ **Status**: Ativo
- ✅ **Data Criação**: 2025-09-23

#### **10.1.2 Setor TESTES (ID: 47)**
- ✅ **Nome**: TESTES
- ✅ **Departamento**: TESTE
- ✅ **Área Tipo**: TESTE
- ✅ **Permite Apontamento**: Sim
- ✅ **Supervisor**: Admin (ID: 1)

### 10.2 Componentes da Hierarquia

#### **10.2.1 🔧 Tipos de Máquina (3 criados)**
1. **EQUIPAMENTO TESTE A**
   - Categoria: CATEGORIA_A
   - Subcategorias: SUB_A1, SUB_A2, SUB_A3

2. **EQUIPAMENTO TESTE B**
   - Categoria: CATEGORIA_B
   - Subcategorias: SUB_B1, SUB_B2

3. **EQUIPAMENTO TESTE C**
   - Categoria: CATEGORIA_C
   - Subcategorias: SUB_C1, SUB_C2, SUB_C3, SUB_C4

#### **10.2.2 🧪 Tipos de Teste (5 criados)**
1. **TESTE FUNCIONAL BÁSICO** (FUNCIONAL)
2. **TESTE DE PERFORMANCE** (PERFORMANCE)
3. **TESTE DE SEGURANÇA** (SEGURANCA)
4. **TESTE DE DURABILIDADE** (DURABILIDADE)
5. **TESTE DE CALIBRAÇÃO** (CALIBRACAO)

#### **10.2.3 📋 Atividades (4 criadas)**
1. **PREPARAÇÃO DE TESTE** (PREPARACAO)
2. **EXECUÇÃO DE TESTE** (EXECUCAO)
3. **ANÁLISE DE RESULTADOS** (ANALISE)
4. **DOCUMENTAÇÃO** (DOCUMENTACAO)

#### **10.2.4 📄 Descrições de Atividade (8 criadas)**
1. **PREP_001**: Preparação inicial - Setup básico
2. **PREP_002**: Preparação avançada - Configuração completa
3. **EXEC_001**: Execução básica - Testes funcionais simples
4. **EXEC_002**: Execução avançada - Testes complexos
5. **ANAL_001**: Análise preliminar - Verificação inicial
6. **ANAL_002**: Análise detalhada - Estudo completo
7. **DOC_001**: Documentação básica - Relatório simples
8. **DOC_002**: Documentação completa - Relatório detalhado

#### **10.2.5 ⚠️ Tipos de Falha (6 criados)**
1. **FALHA_001**: Falha de comunicação (MEDIA)
2. **FALHA_002**: Falha elétrica (ALTA)
3. **FALHA_003**: Falha mecânica (ALTA)
4. **FALHA_004**: Falha de software (MEDIA)
5. **FALHA_005**: Falha de calibração (BAIXA)
6. **FALHA_006**: Falha crítica (CRITICA)

#### **10.2.6 🔄 Causas de Retrabalho (6 criadas)**
1. **RETR_001**: Erro na preparação
2. **RETR_002**: Falha no equipamento
3. **RETR_003**: Erro humano
4. **RETR_004**: Condições ambientais
5. **RETR_005**: Material defeituoso
6. **RETR_006**: Procedimento incorreto

### 10.3 Sistema de Programação de Testes

#### **10.3.1 Nova Tabela: `programacao_testes`**
- ✅ **Tabela criada** com 25 campos
- ✅ **4 programações de exemplo** criadas
- ✅ **Endpoints de exemplo** gerados

#### **10.3.2 Programações Criadas:**
1. **PROG_TESTE_001**: Teste Completo - Equipamento A (ALTA prioridade)
2. **PROG_TESTE_002**: Teste de Durabilidade - Equipamento B (NORMAL)
3. **PROG_TESTE_003**: Validação Rápida - Equipamento C (URGENTE)
4. **PROG_TESTE_004**: Bateria Completa - Todos Equipamentos (ALTA)

#### **10.3.3 Campos da Tabela `programacao_testes`:**
- `id`, `codigo_programacao`, `titulo`, `descricao`
- `id_departamento`, `id_setor`, `id_tipo_maquina`
- `data_inicio_programada`, `hora_inicio_programada`
- `data_fim_programada`, `hora_fim_programada`
- `status`, `prioridade`
- `id_responsavel_programacao`, `id_responsavel_execucao`
- `testes_programados` (JSON)
- `observacoes_programacao`, `observacoes_execucao`
- `criado_por`, `data_criacao`, `data_ultima_atualizacao`
- `data_inicio_real`, `data_fim_real`, `tempo_execucao_minutos`
- `resultado_geral`, `percentual_aprovacao`

### 10.4 Status Final

✅ **DEPARTAMENTO TESTE 100% FUNCIONAL**
- Hierarquia completa implementada
- Sistema de programação funcionando
- Todos os componentes integrados
- Pronto para apontamentos e testes
- Endpoints funcionando
- Documentação completa

---

## 11. FORMULÁRIO DE PROGRAMAÇÃO PCP CORRIGIDO

### 11.1 Problema Identificado e Resolvido

#### **11.1.1 Erro no Endpoint `/api/pcp/programacao-form-data`**
- ❌ **Problema**: Query SQL incorreta na tabela `clientes`
- ❌ **Erro**: `no such column: c.nome`
- ✅ **Solução**: Corrigido para usar `c.razao_social`

#### **11.1.2 Correção Aplicada**
```sql
-- ANTES (INCORRETO):
SELECT os.id, os.os_numero, os.descricao_maquina, os.status_os,
       c.nome as cliente_nome, 'N/A' as tipo_maquina_nome,
       s.nome as setor_nome
FROM ordens_servico os
LEFT JOIN clientes c ON os.id_cliente = c.id

-- DEPOIS (CORRETO):
SELECT os.id, os.os_numero, os.descricao_maquina, os.status_os,
       c.razao_social as cliente_nome, 'N/A' as tipo_maquina_nome,
       s.nome as setor_nome
FROM ordens_servico os
LEFT JOIN clientes c ON os.id_cliente = c.id
```

### 11.2 Formulário Funcionando Completamente

#### **11.2.1 ✅ Dados Disponíveis no Formulário**
- 🏢 **Departamentos**: 5 disponíveis (incluindo TESTE)
- 🏭 **Setores**: 40 disponíveis (incluindo TESTES)
- 👥 **Supervisores**: 4 usuários (ADMIN e SUPERVISOR)
- 📋 **Ordens de Serviço**: 6 disponíveis

#### **11.2.2 ✅ Departamento TESTE Integrado**
- **ID**: 5
- **Nome**: TESTE
- **Setor**: TESTES (ID: 47)
- **Status**: Totalmente funcional

#### **11.2.3 ✅ Funcionalidades Testadas**
1. **Seleção de Departamento**: ✅ Funcionando
2. **Seleção de Setor**: ✅ Funcionando (filtrado por departamento)
3. **Seleção de Supervisor**: ✅ Funcionando
4. **Criação de Programação**: ✅ Funcionando
5. **Listagem de Programações**: ✅ Funcionando

### 11.3 Teste de Programação Criada

#### **11.3.1 Programação de Teste Criada**
- **ID**: 1
- **OS**: TEST003
- **Departamento**: TESTE (ID: 5)
- **Setor**: TESTES (ID: 47)
- **Supervisor**: SUPERVISOR LABORATORIO DE ENSAIOS ELETRICOS
- **Status**: PROGRAMADA
- **Data**: 2025-01-20 08:00:00 até 17:00:00

#### **11.3.2 Endpoints Funcionando**
- ✅ `GET /api/pcp/programacao-form-data` - Dados do formulário
- ✅ `POST /api/pcp/programacoes` - Criar programação
- ✅ `GET /api/pcp/programacoes` - Listar programações
- ✅ `PUT /api/pcp/programacoes/{id}/status` - Atualizar status

### 11.4 Status Final do Sistema

✅ **SISTEMA COMPLETO 100% FUNCIONAL**
- Departamento TESTE operacional
- Setor TESTES configurado
- Formulário de programação funcionando
- Apontamentos sendo criados
- Relatórios completos disponíveis
- Sistema de programação ativo
- Pendências sendo gerenciadas
- Hierarquia completa implementada

---