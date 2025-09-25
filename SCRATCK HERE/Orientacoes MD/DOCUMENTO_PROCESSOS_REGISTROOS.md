# Documento de Processos - Sistema RegistroOS

Este documento descreve os processos completos do sistema RegistroOS, desde o cadastro de usuários até o acompanhamento de ordens de serviço, incluindo todos os relacionamentos entre os módulos.

## 1. Cadastro de Usuário

### Processo:
1. **Registro Inicial**: Usuário acessa o sistema e preenche formulário de cadastro
2. **Dados Obrigatórios**:
   - Nome completo
   - Email (único)
   - Matrícula
   - Cargo
   - Setor
   - Departamento
   - Senha
3. **Status Inicial**: `is_approved = False`
4. **Nível de Privilégio**: Definido como 'USER' por padrão

### Responsáveis:
- **Usuário**: Preenche seus dados
- **Sistema**: Valida dados e cria registro na tabela `usuarios`

### Relacionamentos:
- Usuário criado pode ser associado a setores e departamentos existentes
- Dados do usuário serão usados em apontamentos e aprovações

## 2. Aprovação de Usuário

### Processo:
1. **Notificação**: Sistema notifica administradores/supervisores sobre novo usuário pendente
2. **Revisão**: Admin/Supervisor analisa dados do usuário
3. **Aprovação**: Se aprovado, `is_approved = True`
4. **Rejeição**: Se rejeitado, usuário permanece inativo

### Responsáveis:
- **Administrador/Supervisor**: Aprova ou rejeita cadastros
- **Sistema**: Atualiza status e envia notificações

### Níveis de Privilégio:
- **ADMIN**: Acesso total ao sistema
- **GESTAO**: Gerenciamento de OS e relatórios
- **PCP**: Controle de produção e programações
- **SUPERVISOR**: Aprovação de apontamentos
- **USER**: Acesso básico (apontamentos)

### Relacionamentos:
- Usuários aprovados podem criar OS, fazer apontamentos
- Status de aprovação controla permissões de acesso

## 3. Criação de Ordem de Serviço (OS)

### Processo:
1. **Registro**: Usuário autorizado cria nova OS
2. **Dados da OS**:
   - Número único da OS
   - Descrição da máquina
   - Cliente
   - Status   
   - Setor e departamento responsáveis   
   - Responsável pelo registro
   - Data de criação
   - Testes iniciais finalizados
   - Testes parciais finalizados
   - Testes finais finalizados
3. **Status Inicial**: 'ABERTA'
4. **Campos Específicos**:
   - Testes necessários (Daimer, Carga)
   - Horas orçadas/previstas/reais
   - Status de testes (iniciais/parciais/finais)

### Responsáveis:
- **Usuário Autorizado**: Cria a OS
- **Sistema**: Gera número único e associa responsável

### Relacionamentos:
- OS criada serve como base para apontamentos
- Pode ter múltiplas pendências associadas
- Pode ter programações vinculadas
- Vinculada a usuário responsável

## 4. Apontamento de Atividades

### Processo:
1. **Seleção de OS**: Usuário seleciona OS ativa
2. **Registro de Atividade**:
   - Tipo de máquina
   - Tipo de atividade
   - Descrição da atividade
   - Data/hora início e fim
   - Status do apontamento
3. **Dados do Usuário**: Capturados automaticamente
4. **Retrabalho**: Se aplicável, causa deve ser informada
5. **Observações**: Gerais sobre a atividade
6. **Aprovação**: Supervisor pode aprovar/reprovar

### Responsáveis:
- **Técnico**: Registra apontamento
- **Supervisor**: Aprova ou solicita correções
- **Sistema**: Valida dados e armazena

### Relacionamentos:
- Apontamento vinculado a OS (`id_os`)
- Vinculado a usuário (`id_usuario`)
- Pode gerar ou resolver pendências
- Pode estar associado a testes (`resultados_teste`)
- Vinculado a setores e tipos de atividade

## 5. Gestão de Pendências

### Processo:
1. **Identificação**: Durante apontamento ou inspeção
2. **Registro**:
   - os_numero
   - Tipo de máquina
   - Descrição da pendência
   - Prioridade
   - Responsável inicial
   - Data de início

3. **Acompanhamento**:
   - Status atualizado (ABERTA/FECHADA)
   - Responsável pelo fechamento
   - Solução aplicada
   - Observações do fechamento
   - Data de fechamento
4. **Vinculação**: Pode estar ligada a apontamentos específicos

### Responsáveis:
- **Técnico/PCP**: Identifica e registra pendência
- **Setor Responsável**: Resolve a pendência
- **PCP**: Acompanha resolução e fechamento

### Acompanhamento pelo PCP:
- Dashboard com todas as pendências ativas
- Filtros por setor, prioridade, status
- Relatórios de resolução
- Alertas para pendências críticas

### Acompanhamento pelos Setores:
- Lista de pendências do seu setor
- Notificações sobre novas pendências
- Possibilidade de atualizar status
- Histórico completo de ações

### Relacionamentos:
- Pendência vinculada a OS (`numero_os`)
- Associada a usuários responsáveis
- Pode estar ligada a apontamentos específicos
- Vinculada a setores e tipos de máquina

## 6. Programação de Atividades

### Processo:
1. **Planejamento**: PCP ou responsável cria programação
2. **Definição**:
   - OS relacionada
   - Setor responsável
   - Descrição da atividade
   - Data início e fim
   - Prioridade
   - Responsável pela execução
3. **Status**: PLANEJADA → EM_ANDAMENTO → CONCLUÍDA
4. **Observações**: Detalhes adicionais

### Como os Setores Saberão da Programação:

#### Notificações Automáticas:
- Email/notificação no sistema para setores envolvidos
- Dashboard com programações do setor
- Calendário visual de atividades

#### Acesso aos Dados:
- Lista filtrada por setor
- Detalhes completos da programação
- Histórico de atualizações

### Acompanhamento pelo PCP:
- Visão geral de todas as programações
- Status de execução por setor
- Relatórios de cumprimento
- Alertas para atrasos
- Métricas de produtividade

### Acompanhamento pelos Setores Responsáveis:
- Programações específicas do setor
- Status atualizável
- Possibilidade de adicionar observações
- Notificações de mudanças
- Histórico de execuções

### Relacionamentos:
- Programação vinculada a OS (`id_ordem_servico`)
- Associada a usuários (criado_por, responsável)
- Vinculada a setores
- Pode gerar apontamentos quando executada

## 7. Relacionamentos e Fluxo Geral

### Fluxo Principal:
```
Cadastro Usuário → Aprovação → Criação OS → Programação → Apontamentos → Pendências → Fechamento OS
```

### Relacionamentos Chave:

#### Usuário ↔ Sistema:
- Usuário cria/aprova OS
- Usuário faz apontamentos
- Usuário resolve pendências
- Usuário é notificado sobre programações

#### OS ↔ Apontamentos:
- Uma OS pode ter múltiplos apontamentos
- Apontamentos registram trabalho na OS
- Status da OS atualizado baseado em apontamentos

#### OS ↔ Pendências:
- Pendências identificadas durante apontamentos
- Pendências vinculadas por número da OS
- Resolução de pendências atualiza status da OS

#### OS ↔ Programações:
- Programações criadas para executar atividades da OS
- Múltiplas programações por OS
- Execução de programações gera apontamentos

#### PCP ↔ Setores:
- PCP cria programações e acompanha execução
- Setores recebem notificações e atualizam status
- PCP monitora pendências de todos os setores
- Setores resolvem pendências do seu escopo

#### Setores ↔ Apontamentos:
- Apontamentos feitos por usuários de setores específicos
- Dados do setor capturados automaticamente
- Setores responsáveis por atividades programadas

### Controle de Acesso:
- Níveis de privilégio controlam permissões
- Setores têm acesso limitado aos seus dados
- PCP tem visão global do sistema
- Administradores têm acesso total

### Auditoria:
- Todos os registros têm `data_criacao` e `data_ultima_atualizacao`
- Histórico completo de mudanças
- Rastreabilidade de ações por usuário

### Notificações:
- Sistema notifica setores sobre programações
- Alertas para pendências críticas
- Notificações de aprovações pendentes
- Atualizações de status importantes

---

Este documento serve como guia completo para implementação e uso do sistema RegistroOS, garantindo que todos os processos estejam integrados e os relacionamentos sejam mantidos de forma consistente.