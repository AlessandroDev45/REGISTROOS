# Gestão de Privilégios de Usuário

Este documento descreve os diferentes níveis de privilégio de usuário, departamentos, setores e a lógica de controle de acesso do sistema.

## Níveis de Privilégio de Usuário (`privilege_level`)

- **ADMIN**: Administrador do Sistema. Possui o mais alto nível de acesso a todas as funcionalidades e dados do sistema.
- **GESTAO**: Gestão. Destinado a usuários do setor de "gestão", com acesso amplo dentro de seu departamento. 
- **SUPERVISOR**: Supervisor. Gerencia um setor ou equipe específica.
- **PCP**: Programação da Produção. Lida com tarefas de agendamento e planejamento da produção.
- **USER**: Usuário Padrão/Regular. O nível base para a maioria dos operadores, com acesso limitado ao seu próprio trabalho.

## Departamento (`departamento`)

Os usuários pertencem a um departamento principal, que atualmente pode ser:
- `MOTORES`
- `TRANSFORMADORES`

## Setor (`setor`)

Os usuários são atribuídos a um setor operacional específico, que é uma unidade mais granular dentro de um departamento. Exemplos incluem:
- `mecanica`
- `laboratorio-ensaios-eletricos`
- `pcp`
- `gestao` (frequentemente associado a um departamento, como `MOTORES` ou `TRANSFORMADORES`)


**EM PROCESSO**
- `pintura`
- `preparacao`
- etc.

## Lógica de Controle de Acesso (`check_access`)

O acesso de um usuário aos recursos (endpoints de API, visualizações de dados) é determinado pela combinação de seu `privilege_level`, `departamento` e `setor`.

### **ADMIN**
- **Acesso**: Acesso total a todos os dados e funcionalidades em todos os departamentos (`MOTORES`, `TRANSFORMADORES`) e todos os setores.
- **Onde podem acessar**: Todas as páginas, todos os endpoints de API e todas as funções de gerenciamento.

### **GESTAO**
- **Acesso**: Podem visualizar e gerenciar baixar dados de todo os departamento. Eles têm visibilidade sobre todos os setores dentro de seu departamento (ex: um usuário `GESTAO` do departamento `MOTORES` pode ver dados de `mecanica`, `laboratorio-ensaios-eletricos`, `pcp`, etc., dentro de `MOTORES`).
- **Onde podem acessar**:
    - Dashboards e páginas de gerenciamento específicas do departamento (ex: `/gestao/mecanica` se pertencerem a `MOTORES`).
    - Ferramentas gerais de consulta de OS (`/consulta-os`), com dados filtrados pelo seu departamento.
    - Gerenciamento de usuários (aprovar/criar usuários, geralmente dentro de seu departamento gestão apenas).
    - Visualizações de PCP, mas limitadas ao escopo de seu departamento.
- **Não podem acessar**: Dados do outro departamento (ex: um usuário `GESTAO` de `MOTORES` não pode ver dados de `TRANSFORMADORES`).

### **SUPERVISOR** e **PCP**
- **Acesso**: Podem visualizar e gerenciar dados dentro de seu próprio departamento e de seu setor específico. Se o `setor` for `pcp`, eles acessam os dados de PCP do seu departamento. Se o `setor` for `mecanica`, eles acessam dados específicos da mecânica e OS relacionadas, o mesmo para laboratório de ensaios elétricos.
- **Onde podem acessar**:
    - A página de apontamento específica de seu setor (ex: `/motores/mecanica/desenvolvimento` para um usuário do setor `mecanica`).
    - Visualizações "Minhas OS", filtradas pelo seu setor.
    - Abas de gerenciamento dentro da página de seu setor.
    - Funcionalidades de PCP, se o `setor` for `pcp`.
    - Criação de usuários (se o `privilege_level` permitir, ex: `SUPERVISOR` pode criar `USER`/`SUPERVISOR` dentro de seu departamento).
- **Não podem acessar**: Dados de outros setores fora do seu, ou de outros departamentos.

### **USER** (Usuário Padrão/Regular)
- **Acesso**: Acesso limitado aos dados relacionados ao seu próprio setor e departamento. Geralmente, podem criar e gerenciar seus próprios apontamentos e ver as OS que lhes foram atribuídas.
- **Onde podem acessar**:
    - A página de apontamento específica de seu setor para entrada de dados (ex: `/motores/mecanica/desenvolvimento`).
    - Visualização "Minhas OS" para ver seu próprio trabalho.
    - Dashboards, mas geralmente filtrados para mostrar dados relevantes para sua função/setor.
- **Não podem acessar**: Páginas de gerenciamento, administração de usuários ou dados de outros setores/departamentos.
- paginas que podem ser acessadas Dashboard,Consulta OS (acesso consulta total), Desenvolvimento (
 
📝 Apontamento
📋 Minhas OS
 
📊 Dashboard
📋 Pendências
 
🔍 Pesquisa Por OS)

## Exemplos de Acesso a Páginas do Frontend

- **/motores/mecanica/desenvolvimento**: Acessada primariamente por usuários com `setor: 'mecanica'`. `SUPERVISOR` e `GESTAO` (dentro do departamento `MOTORES`) podem ter visualizações aprimoradas ou capacidades de gerenciamento nesta página.
- **/gestao/mecanica**: Destinada principalmente a usuários `GESTAO` e `ADMIN` dentro do departamento `MOTORES`.
- **/pcp**: Acessível a usuários `PCP`, `SUPERVISOR` (se `PCP` for seu setor), `GESTAO` e `ADMIN`.
- **/administrador**: Página exclusiva para usuários `ADMIN`.
- **/consulta-os**: Acessível a todos, mas os dados exibidos são filtrados com base no nível de privilégio e no departamento/setor do usuário.