# Regras de Negócio - Sistema RegistroOS

## 1. Estrutura da Ordem de Serviço (OS)

### 1.1 Unicidade da OS
- **Regra Principal**: Cada `os_numero` é **único** no sistema
- **Relação 1:1**: Uma OS está relacionada a **um único equipamento**
- **Dados Fixos**: Cliente, CNPJ, endereço, telefone e outras informações são fixas por OS
- **Status do Sankhya**: Campo `status_sankhya` recebe status do ERP Sankhya e impede lançamentos em OS terminadas

### 1.2 Estrutura da OS no Banco de Dados
```sql
CREATE TABLE ordens_servico (
    id INTEGER PRIMARY KEY,
    os_numero VARCHAR(50) NOT NULL UNIQUE,  -- CAMPO ÚNICO
    id_cliente INTEGER,                     -- 1 cliente por OS
    id_equipamento INTEGER,                 -- 1 equipamento por OS
    status_sankhya VARCHAR(50),             -- Status do ERP Sankhya
    status_os VARCHAR(50) DEFAULT 'Em Andamento',
    -- ... outros campos fixos da OS
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_equipamento) REFERENCES equipamentos(id)
);
```

## 2. Sistema de Apontamentos

### 2.1 Múltiplos Apontamentos por OS
- **Regra**: Uma mesma OS (`os_numero`) pode ter **múltiplos registros de apontamento**
- **Responsáveis**: Apontamentos podem ser feitos por **um ou vários colaboradores simultaneamente**
- **Setores**: Apontamentos podem ser realizados em **um ou mais setores**:
  - Mecânica, Laboratório Elétrico, PCP, Gestão (Motores)
  - Mecânica, Laboratório Elétrico, PCP, Gestão (Transformadores)
- **Sem Hierarquia**: Não há dependência entre setores - qualquer um pode iniciar primeiro
- **Sem Limites**: Não há limite para número de apontamentos, desde que não sejam duplicados

### 2.2 Estrutura dos Apontamentos
```sql
CREATE TABLE apontamentos_detalhados (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,                    -- FK para ordens_servico
    setor_responsavel VARCHAR(100) NOT NULL,   -- Setor que fez o apontamento
    id_tecnico_responsavel INTEGER NOT NULL,   -- Técnico responsável
    data_inicio DATETIME,
    hora_inicio VARCHAR(10),
    data_fim DATETIME,
    hora_fim VARCHAR(10),
    tempo_gasto_horas REAL,
    descricao_atividade VARCHAR(255),
    resultado_final VARCHAR(100),
    foi_retrabalho BOOLEAN DEFAULT FALSE,
    matricula_tecnico VARCHAR(100),
    -- ... outros campos do apontamento
    FOREIGN KEY (id_os) REFERENCES ordens_servico(id),
    FOREIGN KEY (id_tecnico_responsavel) REFERENCES usuarios(id)
);
```

### 2.3 Status por Setor
```sql
CREATE TABLE status_setor (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,
    setor VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDENTE',
    data_inicio DATETIME,
    data_conclusao DATETIME,
    responsavel_atualizacao INTEGER,
    observacoes TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_os) REFERENCES ordens_servico(id),
    FOREIGN KEY (responsavel_atualizacao) REFERENCES usuarios(id),
    UNIQUE(id_os, setor)
);
```

## 3. Relacionamentos e Restrições

### 3.1 Relacionamento OS ↔ Equipamento
- **Tipo**: Um-para-um (1:1) efetivo
- **Restrição**: Cada OS tem exatamente um equipamento
- **Implicação**: Um equipamento pode estar associado a múltiplas OS, mas cada OS específica um equipamento único

### 3.2 Relacionamento OS ↔ Apontamentos
- **Tipo**: Um-para-muitos (1:N)
- **Restrição**: Uma OS pode ter múltiplos apontamentos
- **Implicação**: Apontamentos são "filhos" da OS e herdam suas características fixas

### 3.3 Relacionamento Apontamentos ↔ Colaboradores
- **Tipo**: Muitos-para-um (N:1)
- **Restrição**: Múltiplos apontamentos podem ser feitos pelo mesmo colaborador
- **Implicação**: Um colaborador pode fazer apontamentos em múltiplas OS

### 3.4 Relacionamento OS ↔ Status por Setor
- **Tipo**: Um-para-muitos (1:N)
- **Restrição**: Uma OS pode ter status para múltiplos setores
- **Implicação**: Cada setor mantém seu próprio status independentemente

## 4. Fluxo Operacional

### 4.1 Criação da OS
1. PCP pode criar OS 15205 para MOTOR VILLARES 650 dentro da pag PCP que deve ser direcionada para o setor escolhido
2. Lab/Mecânica podem iniciar sem programação do PCP
3. Sistema recebe OS via API do Sankhya
4. OS fica disponível para apontamentos em qualquer setor

### 4.2 Processo de Apontamento
1. Colaborador seleciona OS pelo `os_numero`
2. Sistema valida se OS não está terminada (status_sankhya)
2.1 Se existir no sankhia o sistema preenche os campos cliente e descricao do equipamento com os dados do sankhia
2.2 Se nao existir gera se um aviso que nao encontrou e o user deve preencher os campos cliente e descricao do equipamento manualmente
3. Sistema carrega dados fixos (equipamento, cliente, etc.)
4. Colaborador registra apontamento no seu setor
5. Sistema valida conflitos de horário e duplicatas
6. Apontamento é salvo mantendo referência à OS original
7. Status do setor é atualizado automaticamente

### 4.3 Cenários de Uso

#### Cenário: Múltiplos Colaboradores Simultâneos
```
OS 15205 - MOTOR VILLARES 650
├── Apontamento 1: Maria (Mecânica) - 14:00 às 16:00
├── Apontamento 2: João (Laboratório) - 14:00 às 16:00 ✓ (Setores diferentes)
├── Apontamento 3: João (Laboratório) - 16:00 às 17:00 ✓ (Continuação válida)
```

#### Cenário: Status por Setor vs Status Geral
```
OS 15205 - Status Geral: "EM_ANDAMENTO" (do Sankhya)
├── Mecânica: "CONCLUÍDO"
├── Elétrica: "EM_ANDAMENTO"
├── PCP: "PENDENTE"
├── Gestão: "AGUARDANDO"
```

### 4.4 Setores de Atuação

#### MOTORES:
- **Mecânica**: Faz lançamentos de apontamentos e testes específicos
- **Laboratório de Ensaios Elétricos**: Faz lançamentos de apontamentos e testes específicos
- **PCP (Planejamento e Controle da Produção)**: Cria OS e programações, NÃO faz lançamentos de tempo
- **Gestão**: Faz lançamentos de apontamentos para acompanhamento e fechamento

#### TRANSFORMADORES:
- **Mecânica**: Faz lançamentos de apontamentos e testes específicos
- **Laboratório de Ensaios Elétricos**: Faz lançamentos de apontamentos e testes específicos
- **PCP (Planejamento e Controle da Produção)**: Cria OS e programações, NÃO faz lançamentos de tempo
- **Gestão**: Faz lançamentos de apontamentos para acompanhamento e fechamento

## 5. Sistema de Testes Dinâmicos

### 5.1 Estrutura dos Testes
```sql
CREATE TABLE testes_setor (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,
    setor VARCHAR(100) NOT NULL,
    id_teste VARCHAR(255) NOT NULL,
    grupo_ensaio VARCHAR(100),
    parametros_teste TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_os) REFERENCES ordens_servico(id)
);
```

### 5.2 Testes por Setor

#### Mecânica:
- `inspecao_visual`: Inspeção Visual com componentes específicos
- `teste_balanceamento`: Teste de Balanceamento com tolerâncias configuráveis
- `teste_dimensional`: Teste Dimensional com dimensões críticas

#### Laboratório Elétrico:
- `ensaio_isolamento`: Ensaio de Isolamento com tensão e resistência
- `teste_carga`: Teste de Carga com potência e duração
- `analise_vibracional`: Análise Vibracional com frequências e sensibilidade

#### PCP:
- `planejamento_programacao`: Planejamento e Controle da Produção

#### Gestão:
- `avaliacao_final`: Avaliação Final e documentação

## 6. Regras de Integridade e Validação

### 6.1 Validações de Negócio
- **Unicidade OS**: Não permitir duplicação de `os_numero`
- **Status Sankhya**: Impedir lançamentos em OS com status "TERMINADA", "FINALIZADA", "CANCELADA"
- **Conflito de Horário**: Validar sobreposição de horários para mesmo técnico
- **Duplicatas**: Evitar apontamentos idênticos (mesmo técnico, setor, horário)
- **Permissões**: Validar que usuário pertence ao setor do apontamento
- **Consistência**: Todos os apontamentos devem referenciar OS válida

### 6.2 Restrições Técnicas
- **FK Constraints**: Garantir integridade referencial
- **Unique Constraints**: Evitar status duplicados por setor/OS
- **Triggers**: Validar regras de negócio na inserção
- **Índices**: Otimizar consultas por `os_numero`, setores e status

## 7. Dashboard e Métricas

### 7.1 Métricas Principais
- **Tempo médio por setor**: Cálculo automático das horas trabalhadas
- **Taxa de retrabalho**: Percentual de apontamentos marcados como retrabalho
- **Produtividade por colaborador**: Horas trabalhadas nos últimos 30 dias
- **Status atual**: Visão geral do status de todas as OS ativas
- **Distribuição por setor**: Análise da carga de trabalho por setor

### 7.2 Relatórios Disponíveis
- **OS por status**: Agrupamento por status geral e por setor
- **Produtividade individual**: Métricas por colaborador
- **Análise de retrabalho**: Causas e frequência de retrabalhos
- **Tempo de ciclo**: Do início ao fim da OS por setor

## 8. Considerações de Design

### 8.1 Vantagens desta Arquitetura
- **Flexibilidade**: Múltiplos colaboradores trabalhando simultaneamente
- **Sem Hierarquia**: Qualquer setor pode iniciar o trabalho primeiro
- **Rastreabilidade**: Histórico completo de intervenções por setor
- **Especialização**: Cada setor registra seus apontamentos específicos
- **Integração**: Status automático do ERP Sankhya
- **Escalabilidade**: Suporte a testes dinâmicos e configuráveis

### 8.2 Cenários Complexos Suportados
- Manutenção preventiva em múltiplos setores simultaneamente
- Retrabalho e revisões na mesma OS com rastreamento
- Colaboração entre diferentes especialidades sem dependências
- Acompanhamento longitudinal do equipamento
- Análise de produtividade e eficiência por setor
- Controle de qualidade através de testes específicos

---

**Data de Atualização**: Outubro 2025
**Versão**: 2.0
**Responsável**: Sistema RegistroOS
**Alterações**: Implementação de múltiplos colaboradores simultâneos, status por setor, testes dinâmicos e integração com Sankhya