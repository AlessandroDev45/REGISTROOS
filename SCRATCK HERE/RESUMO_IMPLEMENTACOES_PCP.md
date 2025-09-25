Com base na minha análise do banco de dados SQLite `registroos_new.db`, aqui está uma lista completa de todas as tabelas, suas colunas e relacionamentos:

## **📊 VISÃO GERAL DO SCHEMA DO BANCO DE DADOS**

### **🏗️ Tabelas Principais de Negócio**

#### **1. `ordens_servico` (Ordens de Serviço)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `os_numero` (VARCHAR(50), NOT NULL)
- `id_cliente` (INTEGER)
- `id_equipamento` (INTEGER)
- `descricao_maquina` (TEXT)
- `status_os` (VARCHAR(50))
- `id_responsavel_registro` (INTEGER)
- `id_responsavel_pcp` (INTEGER)
- `id_responsavel_final` (INTEGER)
- `data_inicio_prevista` (DATETIME)
- `data_fim_prevista` (DATETIME)
- `inicio_os` (DATETIME)
- `fim_os` (DATETIME)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `criado_por` (INTEGER)
- `status_geral` (VARCHAR(50), DEFAULT 'ABERTA')
- `prioridade` (VARCHAR(20), DEFAULT 'MEDIA')
- `valor_total_previsto` (DECIMAL(15,2))
- `valor_total_real` (DECIMAL(15,2))
- `observacoes_gerais` (TEXT)
- `id_tipo_maquina` (INTEGER)
- `custo_total_real` (DECIMAL(15,2))
- `horas_previstas` (DECIMAL(10,2))
- `horas_reais` (DECIMAL(10,2))
- `data_programacao` (DATETIME)
- `id_setor` (INTEGER)
- `id_departamento` (INTEGER)
- `horas_orcadas` (DECIMAL(10,2), DEFAULT 0)
- `testes_iniciais_finalizados` (BOOLEAN, DEFAULT 0)
- `testes_parciais_finalizados` (BOOLEAN, DEFAULT 0)
- `testes_finais_finalizados` (BOOLEAN, DEFAULT 0)
- `data_testes_iniciais_finalizados` (DATETIME)
- `data_testes_parciais_finalizados` (DATETIME)
- `data_testes_finais_finalizados` (DATETIME)
- `id_usuario_testes_iniciais` (INTEGER)
- `id_usuario_testes_parciais` (INTEGER)
- `id_usuario_testes_finais` (INTEGER)
- `testes_exclusivo` (TEXT)

#### **2. `apontamentos_detalhados` (Apontamentos Detalhados/Lançamentos de Tempo)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `id_os` (INTEGER, NOT NULL)
- `id_setor` (INTEGER, NOT NULL)
- `id_usuario` (INTEGER, NOT NULL)
- `data_hora_inicio` (DATETIME, NOT NULL)
- `data_hora_fim` (DATETIME)
- `status_apontamento` (VARCHAR(50), NOT NULL)
- `aprovado_supervisor` (BOOLEAN)
- `data_aprovacao_supervisor` (DATETIME)
- `foi_retrabalho` (BOOLEAN)
- `causa_retrabalho` (VARCHAR(255))
- `observacao_os` (TEXT)
- `servico_de_campo` (BOOLEAN)
- `observacoes_gerais` (TEXT)
- `criado_por` (VARCHAR(255))
- `criado_por_email` (VARCHAR(255))
- `setor` (VARCHAR(100))
- `supervisor_aprovacao` (VARCHAR(255))
- `horas_orcadas` (DECIMAL(10,2), DEFAULT 0)
- `etapa_inicial` (BOOLEAN, DEFAULT 0)
- `etapa_parcial` (BOOLEAN, DEFAULT 0)
- `etapa_final` (BOOLEAN, DEFAULT 0)
- `horas_etapa_inicial` (DECIMAL(10,2), DEFAULT 0)
- `horas_etapa_parcial` (DECIMAL(10,2), DEFAULT 0)
- `horas_etapa_final` (DECIMAL(10,2), DEFAULT 0)
- `observacoes_etapa_inicial` (TEXT)
- `observacoes_etapa_parcial` (TEXT)
- `observacoes_etapa_final` (TEXT)
- `data_etapa_inicial` (DATETIME)
- `data_etapa_parcial` (DATETIME)
- `data_etapa_final` (DATETIME)
- `supervisor_etapa_inicial` (VARCHAR(255))
- `supervisor_etapa_parcial` (VARCHAR(255))
- `supervisor_etapa_final` (VARCHAR(255))
- `data_processo_finalizado` (DATETIME)
- `tipo_maquina` (VARCHAR(100))
- `tipo_atividade` (VARCHAR(100))
- `descricao_atividade` (TEXT)
- `categoria_maquina` (VARCHAR(50))
- `subcategorias_maquina` (TEXT)
- `subcategorias_finalizadas` (BOOLEAN, DEFAULT 0)
- `data_finalizacao_subcategorias` (DATETIME)

#### **3. `pendencias` (Pendências)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `numero_os` (VARCHAR(50), NOT NULL)
- `cliente` (VARCHAR(255), NOT NULL)
- `data_inicio` (DATETIME, NOT NULL)
- `id_responsavel_inicio` (INTEGER, NOT NULL)
- `tipo_maquina` (VARCHAR(100), NOT NULL)
- `descricao_maquina` (TEXT, NOT NULL)
- `descricao_pendencia` (TEXT, NOT NULL)
- `status` (VARCHAR(20), NOT NULL)
- `prioridade` (VARCHAR(20))
- `data_fechamento` (DATETIME)
- `id_responsavel_fechamento` (INTEGER)
- `solucao_aplicada` (TEXT)
- `observacoes_fechamento` (TEXT)
- `id_apontamento_origem` (INTEGER)
- `id_apontamento_fechamento` (INTEGER)
- `tempo_aberto_horas` (FLOAT)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)

#### **4. `programacoes` (Programações/Agendamentos)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `id_ordem_servico` (INTEGER)
- `responsavel_id` (INTEGER, NOT NULL)
- `inicio_previsto` (DATETIME, NOT NULL)
- `fim_previsto` (DATETIME, NOT NULL)
- `status` (VARCHAR(50))
- `criado_por_id` (INTEGER)
- `observacoes` (TEXT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)
- `id_setor` (INTEGER)

#### **5. `resultados_teste` (Resultados de Teste)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `id_apontamento` (INTEGER, NOT NULL)
- `id_teste` (INTEGER, NOT NULL)
- `resultado` (VARCHAR(20), NOT NULL)
- `observacao` (TEXT)
- `data_registro` (DATETIME)

### **🏢 Tabelas Mestre/Referenciais**

#### **6. `clientes` (Clientes)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `razao_social` (VARCHAR(255), NOT NULL)
- `nome_fantasia` (VARCHAR(255))
- `cnpj_cpf` (VARCHAR(20))
- `contato_principal` (VARCHAR(255))
- `telefone_contato` (VARCHAR(20))
- `email_contato` (VARCHAR(255))
- `endereco` (TEXT)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)

#### **7. `equipamentos` (Equipamentos)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `descricao` (TEXT, NOT NULL)
- `tipo` (VARCHAR(100))
- `fabricante` (VARCHAR(100))
- `modelo` (VARCHAR(100))
- `numero_serie` (VARCHAR(100))
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)

#### **8. `tipo_usuarios` (Tipos de Usuários)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `nome_completo` (VARCHAR(255), NOT NULL)
- `nome_usuario` (VARCHAR(100), NOT NULL)
- `email` (VARCHAR(255), NOT NULL)
- `matricula` (VARCHAR(100))
- `senha_hash` (VARCHAR(255), NOT NULL)
- `setor` (VARCHAR(100), NOT NULL)
- `cargo` (VARCHAR(100))
- `departamento` (VARCHAR(100), NOT NULL)
- `privilege_level` (VARCHAR(50), NOT NULL)
- `is_approved` (BOOLEAN, NOT NULL)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `trabalha_producao` (BOOLEAN, NOT NULL, DEFAULT FALSE)
- `obs_reprovacao` (TEXT)
- `id_setor` (INTEGER)
- `id_departamento` (INTEGER)
- `primeiro_login` (BOOLEAN, NOT NULL, DEFAULT 0)

#### **9. `tipo_setores` (Tipos de Setores)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `nome` (VARCHAR(100), NOT NULL)
- `departamento` (VARCHAR(100), NOT NULL)
- `descricao` (TEXT)
- `ativo` (BOOLEAN)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `id_departamento` (INTEGER)
- `area_tipo` (VARCHAR(50), NOT NULL, DEFAULT 'PRODUCAO')
- `supervisor_responsavel` (INTEGER)
- `permite_apontamento` (BOOLEAN, DEFAULT 1)

#### **10. `tipo_departamentos` (Tipos de Departamentos)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `nome_tipo` (VARCHAR(100))
- `descricao` (TEXT)
- `ativo` (BOOLEAN, DEFAULT 1)
- `data_criacao` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- `data_ultima_atualizacao` (DATETIME, DEFAULT CURRENT_TIMESTAMP)

#### **11. `tipos_maquina` (Tipos de Máquina)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `nome_tipo` (VARCHAR(100), NOT NULL)
- `descricao` (TEXT)
- `data_criacao` (DATETIME)
- `categoria` (VARCHAR(50))
- `id_departamento` (INTEGER)
- `especificacoes_tecnicas` (TEXT)
- `ativo` (BOOLEAN, DEFAULT 1)
- `data_ultima_atualizacao` (DATETIME)
- `campos_teste_resultado` (TEXT)
- `setor` (VARCHAR(100))
- `departamento` (TEXT)
- `descricao_partes` (TEXT)

#### **12. `tipo_atividade` (Tipos de Atividade)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `nome_tipo` (VARCHAR(255), NOT NULL)
- `descricao` (TEXT)
- `ativo` (BOOLEAN)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `id_tipo_maquina` (INTEGER)
- `categoria` (VARCHAR(50))

#### **13. `tipo_descricao_atividade` (Tipos de Descrição de Atividade)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `codigo` (VARCHAR(50), NOT NULL)
- `descricao` (TEXT, NOT NULL)
- `ativo` (BOOLEAN)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `setor` (VARCHAR(100))
- `categoria` (VARCHAR(50))

#### **14. `tipo_causas_retrabalho` (Tipos de Causas de Retrabalho)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `codigo` (VARCHAR(50), NOT NULL)
- `descricao` (VARCHAR(255), NOT NULL)
- `ativo` (BOOLEAN)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `id_departamento` (INTEGER)
- `departamento` (TEXT)
- `setor` (TEXT)

#### **15. `tipos_teste` (Tipos de Teste)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY)
- `nome` (VARCHAR(255), NOT NULL)
- `departamento` (VARCHAR(100), NOT NULL)
- `tipo_maquina` (VARCHAR(100))
- `setor` (VARCHAR(100))
- `ativo` (BOOLEAN)
- `data_criacao` (DATETIME)
- `data_ultima_atualizacao` (DATETIME)
- `tipo_teste` (VARCHAR(20), DEFAULT 'ESTATICO')
- `descricao` (TEXT)
- `exclusivo_setor` (BOOLEAN, DEFAULT FALSE)
- `visivel_desenvolvimento` (BOOLEAN, DEFAULT TRUE)
- `descricao_exclusiva` (TEXT)
- `teste_exclusivo_setor` (BOOLEAN, DEFAULT FALSE)
- `descricao_teste_exclusivo` (VARCHAR(255))
- `categoria` (VARCHAR(50), DEFAULT 'Visual')
- `subcategoria` (INTEGER, DEFAULT 0)

### **📊 Tabelas do Sistema/Utilitárias**

#### **16. `os_testes_exclusivos_finalizados` (Testes Exclusivos Finalizados)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
- `numero_os` (VARCHAR(50), NOT NULL)
- `id_teste_exclusivo` (INTEGER, NOT NULL)
- `nome_teste` (VARCHAR(255), NOT NULL)
- `descricao_teste` (VARCHAR(255))
- `usuario_finalizacao` (VARCHAR(100), NOT NULL)
- `departamento` (VARCHAR(100), NOT NULL)
- `setor` (VARCHAR(100), NOT NULL)
- `data_finalizacao` (DATE, NOT NULL)
- `hora_finalizacao` (TIME, NOT NULL)
- `descricao_atividade` (TEXT)
- `observacoes` (TEXT)
- `data_criacao` (DATETIME, DEFAULT CURRENT_TIMESTAMP)

#### **17. `migration_log` (Log de Migração)**
**Colunas:**
- `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
- `fase` (TEXT, NOT NULL)
- `acao` (TEXT, NOT NULL)
- `tabela_afetada` (TEXT)
- `registros_afetados` (INTEGER)
- `data_execucao` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- `observacoes` (TEXT)

---

## **🔗 RELACIONAMENTOS E CHAVES ESTRANGEIRAS**

### **Relacionamentos Principais de Negócio:**

1. **`ordens_servico` → `clientes`**
   - `ordens_servico.id_cliente` → `clientes.id`
   - **Explicação:** Cada ordem de serviço pertence a um cliente específico

2. **`ordens_servico` → `equipamentos`**
   - `ordens_servico.id_equipamento` → `equipamentos.id`
   - **Explicação:** Cada ordem de serviço está associada a um equipamento específico

3. **`ordens_servico` → `tipo_usuarios`** (Múltiplos relacionamentos)
   - `ordens_servico.id_responsavel_registro` → `tipo_usuarios.id`
   - `ordens_servico.id_responsavel_pcp` → `tipo_usuarios.id`
   - `ordens_servico.id_responsavel_final` → `tipo_usuarios.id`
   - `ordens_servico.criado_por` → `tipo_usuarios.id`
   - **Explicação:** Ordens de serviço têm múltiplas responsabilidades de usuário (registro, PCP, final, criador)

4. **`ordens_servico` → `tipo_setores`**
   - `ordens_servico.id_setor` → `tipo_setores.id`
   - **Explicação:** Ordens de serviço são atribuídas a setores específicos

5. **`ordens_servico` → `tipo_departamentos`**
   - `ordens_servico.id_departamento` → `tipo_departamentos.id`
   - **Explicação:** Ordens de serviço pertencem a departamentos específicos

6. **`ordens_servico` → `tipos_maquina`**
   - `ordens_servico.id_tipo_maquina` → `tipos_maquina.id`
   - **Explicação:** Ordens de serviço especificam tipos de máquina

### **Relacionamentos de Apontamentos/Lançamentos:**

7. **`apontamentos_detalhados` → `ordens_servico`**
   - `apontamentos_detalhados.id_os` → `ordens_servico.id`
   - **Explicação:** Cada apontamento pertence a uma ordem de serviço específica

8. **`apontamentos_detalhados` → `tipo_usuarios`**
   - `apontamentos_detalhados.id_usuario` → `tipo_usuarios.id`
   - **Explicação:** Apontamentos são feitos por usuários específicos

9. **`apontamentos_detalhados` → `tipo_setores`**
   - `apontamentos_detalhados.id_setor` → `tipo_setores.id`
   - **Explicação:** Apontamentos são atribuídos a setores

### **Relacionamentos de Testes e Resultados:**

10. **`resultados_teste` → `apontamentos_detalhados`**
    - `resultados_teste.id_apontamento` → `apontamentos_detalhados.id`
    - **Explicação:** Resultados de teste pertencem a apontamentos específicos

11. **`resultados_teste` → `tipos_teste`**
    - `resultados_teste.id_teste` → `tipos_teste.id`
    - **Explicação:** Resultados de teste referenciam tipos de teste específicos

12. **`os_testes_exclusivos_finalizados` → `tipos_teste`**
    - `os_testes_exclusivos_finalizados.id_teste_exclusivo` → `tipos_teste.id`
    - **Explicação:** Testes exclusivos finalizados referenciam tipos de teste

### **Relacionamentos de Pendências:**

13. **`pendencias` → `tipo_usuarios`** (Múltiplos relacionamentos)
    - `pendencias.id_responsavel_inicio` → `tipo_usuarios.id`
    - `pendencias.id_responsavel_fechamento` → `tipo_usuarios.id`
    - **Explicação:** Pendências têm usuários responsáveis pela criação e fechamento

14. **`pendencias` → `apontamentos_detalhados`** (Múltiplos relacionamentos)
    - `pendencias.id_apontamento_origem` → `apontamentos_detalhados.id`
    - `pendencias.id_apontamento_fechamento` → `apontamentos_detalhados.id`
    - **Explicação:** Pendências estão vinculadas a apontamentos que as criaram e fecharam

### **Relacionamentos de Programação:**

15. **`programacoes` → `ordens_servico`**
    - `programacoes.id_ordem_servico` → `ordens_servico.id`
    - **Explicação:** Programações pertencem a ordens de serviço específicas

16. **`programacoes` → `tipo_usuarios`** (Múltiplos relacionamentos)
    - `programacoes.responsavel_id` → `tipo_usuarios.id`
    - `programacoes.criado_por_id` → `tipo_usuarios.id`
    - **Explicação:** Programações têm usuários responsáveis e criadores

17. **`programacoes` → `tipo_setores`**
    - `programacoes.id_setor` → `tipo_setores.id`
    - **Explicação:** Programações são atribuídas a setores

### **Relacionamentos de Tabelas Referenciais:**

18. **`tipo_usuarios` → `tipo_setores`**
    - `tipo_usuarios.id_setor` → `tipo_setores.id`
    - **Explicação:** Usuários pertencem a setores específicos

19. **`tipo_usuarios` → `tipo_departamentos`**
    - `tipo_usuarios.id_departamento` → `tipo_departamentos.id`
    - **Explicação:** Usuários pertencem a departamentos específicos

20. **`tipo_setores` → `tipo_departamentos`**
    - `tipo_setores.id_departamento` → `tipo_departamentos.id`
    - **Explicação:** Setores pertencem a departamentos

21. **`tipo_setores` → `tipo_usuarios`**
    - `tipo_setores.supervisor_responsavel` → `tipo_usuarios.id`
    - **Explicação:** Setores têm supervisores responsáveis

22. **`tipos_maquina` → `tipo_departamentos`**
    - `tipos_maquina.id_departamento` → `tipo_departamentos.id`
    - **Explicação:** Tipos de máquina pertencem a departamentos

23. **`tipo_atividade` → `tipos_maquina`**
    - `tipo_atividade.id_tipo_maquina` → `tipos_maquina.id`
    - **Explicação:** Tipos de atividade estão associados a tipos de máquina

24. **`tipo_causas_retrabalho` → `tipo_departamentos`**
    - `tipo_causas_retrabalho.id_departamento` → `tipo_departamentos.id`
    - **Explicação:** Causas de retrabalho estão associadas a departamentos

---

## **📝 NOTAS ADICIONAIS**

- **Triggers:** Muitas tabelas têm triggers de conversão para MAIÚSCULO nos campos de texto
- **Índices:** Indexação abrangente para performance em campos consultados frequentemente
- **Tabelas de Backup:** Tabelas terminando com 'X' parecem ser versões de backup/legado
- **Tipos de Dados:** Usa tipos de dados SQLite com restrições apropriadas
- **Relacionamentos:** Usa principalmente restrições de chave estrangeira para integridade referencial
- **Campos de Auditoria:** A maioria das tabelas inclui `data_criacao` e `data_ultima_atualizacao` para auditoria

Este schema suporta um sistema abrangente de gerenciamento de ordens de serviço com rastreamento detalhado de apontamentos, testes, programação e gerenciamento de problemas em múltiplos departamentos e setores.