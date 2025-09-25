# 📋 DOCUMENTAÇÃO COMPLETA DO SISTEMA REGISTROOS

## 🗄️ ESTRUTURA DO BANCO DE DADOS
**Última atualização:** 2025-01-18  
**Total de tabelas:** 22  
**Banco:** registroos_new.db

### 📊 TABELAS PRINCIPAIS

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
- privilege_level (VARCHAR(50)) NOT NULL -- USER, SUPERVISOR, ADMIN, GESTAO
- is_approved (BOOLEAN) NOT NULL
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- trabalha_producao (BOOLEAN) NOT NULL DEFAULT FALSE
- obs_reprovacao (TEXT)
- id_setor (INTEGER, FK → setores.id)
- id_departamento (INTEGER, FK → departamentos.id)
```

#### 2. **ordens_servico** (15 registros)
```sql
- id (INTEGER, PK) NOT NULL
- os_numero (VARCHAR(50)) NOT NULL
- id_cliente (INTEGER, FK → clientes.id)
- id_equipamento (INTEGER, FK → equipamentos.id)
- descricao_maquina (TEXT)
- status_os (VARCHAR(50)) -- ABERTA, EM ANDAMENTO, CONCLUIDA, AGUARDANDO
- id_responsavel_registro (INTEGER, FK → usuarios.id)
- id_responsavel_pcp (INTEGER, FK → usuarios.id)
- id_responsavel_final (INTEGER, FK → usuarios.id)
- data_inicio_prevista (DATETIME)
- data_fim_prevista (DATETIME)
- inicio_os (DATETIME)
- fim_os (DATETIME)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- criado_por (INTEGER, FK → usuarios.id)
- status_geral (VARCHAR(50)) DEFAULT 'ABERTA'
- prioridade (VARCHAR(20)) DEFAULT 'MEDIA'
- valor_total_previsto (DECIMAL(15,2))
- valor_total_real (DECIMAL(15,2))
- observacoes_gerais (TEXT)
- id_tipo_maquina (INTEGER, FK → tipos_maquina.id)
- custo_total_real (DECIMAL(15,2))
- horas_previstas (DECIMAL(10,2))
- horas_reais (DECIMAL(10,2))
- data_programacao (DATETIME)
- id_setor (INTEGER, FK → setores.id)
- id_departamento (INTEGER, FK → departamentos.id)
- horas_orcadas (DECIMAL(10,2)) DEFAULT 0 -- ⭐ CAMPO IMPORTANTE
- testes_iniciais_finalizados (BOOLEAN) DEFAULT 0
- testes_parciais_finalizados (BOOLEAN) DEFAULT 0
- testes_finais_finalizados (BOOLEAN) DEFAULT 0
- data_testes_iniciais_finalizados (DATETIME)
- data_testes_parciais_finalizados (DATETIME)
- data_testes_finais_finalizados (DATETIME)
- id_usuario_testes_iniciais (INTEGER, FK → usuarios.id)
- id_usuario_testes_parciais (INTEGER, FK → usuarios.id)
- id_usuario_testes_finais (INTEGER, FK → usuarios.id)
- teste_daimer (BOOLEAN) DEFAULT 0
- teste_carga (BOOLEAN) DEFAULT 0
```

#### 3. **apontamentos_detalhados** (27 registros) ⭐ TABELA CENTRAL
```sql
- id (INTEGER, PK) NOT NULL
- id_os (INTEGER, FK → ordens_servico.id) NOT NULL
- id_setor (INTEGER, FK → setores.id) NOT NULL
- id_usuario (INTEGER, FK → usuarios.id) NOT NULL
- id_atividade (INTEGER, FK → tipo_atividade.id) NOT NULL
- data_hora_inicio (DATETIME) NOT NULL
- data_hora_fim (DATETIME)
- status_apontamento (VARCHAR(50)) NOT NULL
- aprovado_supervisor (BOOLEAN)
- data_aprovacao_supervisor (DATETIME)
- foi_retrabalho (BOOLEAN)
- causa_retrabalho (VARCHAR(255))
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- observacao_os (TEXT)
- os_finalizada_em (DATETIME)
- servico_de_campo (BOOLEAN)
- observacoes_gerais (TEXT)
- criado_por (VARCHAR(255))
- criado_por_email (VARCHAR(255))
- setor (VARCHAR(100)) -- ⭐ CAMPO PARA IDENTIFICAR MOTORES/TRANSFORMADORES
- supervisor_aprovacao (VARCHAR(255))
```

#### 4. **programacoes** (4 registros)
```sql
- id (INTEGER, PK) NOT NULL
- id_ordem_servico (INTEGER, FK → ordens_servico.id)
- responsavel_id (INTEGER, FK → usuarios.id) NOT NULL
- inicio_previsto (DATETIME) NOT NULL
- fim_previsto (DATETIME) NOT NULL
- status (VARCHAR(50))
- criado_por_id (INTEGER, FK → usuarios.id)
- observacoes (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
- id_setor (INTEGER, FK → setores.id)
```

#### 5. **resultados_teste** (3 registros)
```sql
- id (INTEGER, PK) NOT NULL
- id_apontamento (INTEGER, FK → apontamentos_detalhados.id) NOT NULL
- id_teste (INTEGER, FK → tipos_teste.id) NOT NULL
- resultado (VARCHAR(20)) NOT NULL -- APROVADO, REPROVADO, PENDENTE
- observacao (TEXT)
- data_registro (DATETIME)
```

#### 6. **pendencias** (11 registros)
```sql
- id (INTEGER, PK) NOT NULL
- numero_os (VARCHAR(50)) NOT NULL
- cliente (VARCHAR(255)) NOT NULL
- data_inicio (DATETIME) NOT NULL
- id_responsavel_inicio (INTEGER, FK → usuarios.id) NOT NULL
- tipo_maquina (VARCHAR(100)) NOT NULL
- descricao_maquina (TEXT) NOT NULL
- descricao_pendencia (TEXT) NOT NULL
- status (VARCHAR(20)) NOT NULL
- prioridade (VARCHAR(20))
- data_fechamento (DATETIME)
- id_responsavel_fechamento (INTEGER, FK → usuarios.id)
- solucao_aplicada (TEXT)
- observacoes_fechamento (TEXT)
- id_apontamento_origem (INTEGER, FK → apontamentos_detalhados.id)
- id_apontamento_fechamento (INTEGER, FK → apontamentos_detalhados.id)
- tempo_aberto_horas (FLOAT)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
```

#### 7. **setores** (37 registros)
```sql
- id (INTEGER, PK) NOT NULL
- nome (VARCHAR(100)) NOT NULL
- departamento (VARCHAR(100)) NOT NULL -- ⭐ MOTORES/TRANSFORMADORES
- descricao (TEXT)
- ativo (BOOLEAN)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- id_departamento (INTEGER, FK → departamentos.id)
- area_tipo (VARCHAR(50)) NOT NULL DEFAULT 'PRODUCAO'
- supervisor_responsavel (INTEGER, FK → usuarios.id)
- permite_apontamento (BOOLEAN) DEFAULT 1
```

#### 8. **tipos_teste** (189 registros)
```sql
- id (INTEGER, PK) NOT NULL
- nome (VARCHAR(255)) NOT NULL
- departamento (VARCHAR(100)) NOT NULL
- tipo_maquina (VARCHAR(100))
- setor (VARCHAR(100))
- ativo (BOOLEAN)
- data_criacao (DATETIME)
- data_ultima_atualizacao (DATETIME)
- tipo_teste (VARCHAR(20)) DEFAULT 'ESTATICO'
- descricao (TEXT)
- exclusivo_setor (BOOLEAN) DEFAULT FALSE
- visivel_desenvolvimento (BOOLEAN) DEFAULT TRUE
- descricao_exclusiva (TEXT)
- teste_exclusivo_setor (BOOLEAN) DEFAULT FALSE
- descricao_teste_exclusivo (VARCHAR(255))
```

### 🔗 RELACIONAMENTOS PRINCIPAIS

1. **ordens_servico** ↔ **apontamentos_detalhados** (1:N)
2. **apontamentos_detalhados** ↔ **resultados_teste** (1:N)
3. **apontamentos_detalhados** ↔ **pendencias** (1:N)
4. **ordens_servico** ↔ **programacoes** (1:N)
5. **usuarios** ↔ **setores** (N:1)
6. **setores** ↔ **departamentos** (N:1)

### ⭐ CAMPOS IMPORTANTES PARA RELATÓRIO COMPLETO

#### **Identificação MOTORES vs TRANSFORMADORES:**
- `apontamentos_detalhados.setor` contém o setor do usuário
- Setores com "TRANSFORMADOR" = TRANSFORMADORES
- Outros setores = MOTORES

#### **Horas e Etapas:**
- `ordens_servico.horas_orcadas` = Total orçado
- Somar `apontamentos_detalhados` por etapas (Inicial, Parcial, Final)
- Calcular por setor e total geral

#### **Testes:**
- `resultados_teste` contém todos os resultados
- `tipos_teste` contém informações dos testes
- Filtrar por setor e tipo

#### **Retrabalhos:**
- `pendencias` contém retrabalhos e causas
- `apontamentos_detalhados.foi_retrabalho` = flag
- `causas_retrabalho` contém códigos e descrições
```
