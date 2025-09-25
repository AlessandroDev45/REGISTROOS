# Procedimento Completo para Fazer Apontamento - Sistema Registros OS

## Estrutura da Aplicação

### Página Inicial
A aplicação **Registros OS** inicia com:
- Uma nave
- Barra de navegação contendo as seguintes abas:
  - Registros de OS
  - Dashboard
  - PCP
  - Administrador
  - Gestão
  - Consultas de OS

### Área de Desenvolvimento
**Importante**: No desenvolvimento atual, está sendo tratada apenas a parte do **Laboratório de Ensaios Elétricos**.

Ao clicar na aba "Desenvolvimento", abrem-se 7 sub-abas:
1. **Apontamento** (tela inicial)
2. Minhas OS
3. Gerenciar
4. Dash
5. Pendências
6. Programação
7. Aprovação de novos usuários

---

## Procedimento para Fazer um Apontamento Normal

### 1. Acessar a Tela de Apontamento
- Clicar na aba "Desenvolvimento"
- Clicar na sub-aba "**Apontamento**" (que é a tela inicial após entrar em desenvolvimento)

### 2. Consulta de OS
- Na tela de apontamento, localizar a **parte de consulta de OS**
- Inserir o número da OS no **input** disponível
- Clicar no botão "**Consulta OS**"

**Importante**: Esta consulta é feita via **API externa do Sankya** (apenas esta consulta utiliza API externa)

**Retorno da consulta**:
- Nome do cliente
- Tipo de máquina
- Descrição da máquina

### 3. Lançamento de Dados Iniciais
Após a consulta bem-sucedida, preencher:
- **Hora inicial** do apontamento
- **Data inicial**

### 4. Configuração do Tipo de Máquina
No campo "Configuração do tipo de máquina", selecionar uma das opções:
- **CA** (Corrente Alternada)
- **CC** (Corrente Contínua)
- **Estática**
- **Parada**

### 5. Seleção do Tipo de Atividade
Escolher o tipo de atividade entre as opções:
- Teste inicial
- Teste parcial
- Teste final
- Manutenção

### 6. Descrição da Atividade
Selecionar a descrição da atividade de uma **lista de testes** disponível.

### 7. Configuração Específica por Tipo de Máquina

#### Exemplo: Máquina Rotativa
Quando selecionado o tipo "**Máquina Rotativa CA**" por ex., abre-se a aba "Máquina Rotativa CA" contendo **7 sub-abas**.

**Exemplo de preenchimento - Sub-aba "Estator Principal"**:
- Cada sub-aba contém vários itens cada um com um  **check**
- Para cada item (exemplo: "Inspeção Visual"):
  1. Clicar no check "Inspeção Visual"
  2. Aparecerão **3 opções**:
     - Aprovado
     - Reprovado
     - Inconclusivo
  3. Selecionar a opção adequada (ex: "Aprovado")
  4. Fazer uma **observação pequena** (ex: "Aprovado - qualquer observação")

**Este processo deve ser repetido para**:
- Todas as **7 sub-abas**
- Todos os **sub-itens** dentro de cada sub-aba

### 8. Detalhes Complementares

#### Retrabalho (se aplicável)
Se o apontamento for um retrabalho:
1. Clicar na aba "**Retrabalho**"
2. Será aberto um **drop-down** com todos os setores que causaram o retrabalho
3. Selecionar o setor responsável

#### Motivo da Falha
1. Acessar o drop-down "**Motivo da falha**"
2. Será aberto um **drop-down** com todos os setores que causaram o retrabalho
3. Selecionar o motivo adequado

#### Observações
- Inserir **observações** gerais sobre o campo especifico do apontamento ou registro

### 9. Finalização do Apontamento
Preencher os dados finais:
- **Data fim**: Data em que o operador terminou o lançamento
- **Hora final**: Hora de conclusão do apontamento

### 10. Opções de Salvamento

Após completar todos os campos, o usuário tem **3 opções**:

#### A) Finalizar Agora
- Clique no botão "**Finalizar Agora**"

#### B) Salvar Apontamento
- Clique no botão "**Salvar Apontamento**"
- **Importante**: Todos os dados são salvos na **database local** (diferente do Sankya)

#### C) Salvar com Pendência
- Utilizar quando algum item do apontamento foi marcado como "**Inconclusivo**"
- Clique no botão "**Salvar com Pendência**"
- **Processo automático**:
  1. Uma pendência é criada automaticamente
  2. A pendência vai para um campo específico(Ver procedimento pendencia)
  3. **Todos os usuários do laboratório** podem visualizar esta pendência

---

## Resumo do Fluxo Completo

1. **Navegação**: Desenvolvimento → Apontamento
2. **Consulta**: Inserir OS → Consultar via API Sankya
3. **Dados Iniciais**: Data/hora inicial + tipo de máquina
4. **Atividade**: Tipo + descrição da atividade
5. **Configuração Específica**: Preenchimento das sub-abas conforme tipo de máquina
6. **Detalhes**: Retrabalho, motivo da falha, observações
7. **Finalização**: Data/hora final
8. **Salvamento**: Escolher entre finalizar, salvar ou salvar com pendência

**Observação**: Todos os dados são armazenados na database local do sistema, exceto a consulta inicial que utiliza a API externa do Sankya.