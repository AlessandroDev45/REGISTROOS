
# Registro de Pendencias

## Como sao geradas as pendencias no Sistema Registros OS?

As pendencias podem nascer **somente a partir de um registro de apontamento**.  
Se existir qualquer pendencia em aberto, o campo de pendencia deve mostrar um **icone de alerta** indicando que ha pendencia.

---

## Regras principais

- Caso exista uma pendencia vinculada a um numero de OS:
  - Ao inserir o mesmo numero de OS no campo de consulta, o usuario sera avisado que ha uma pendencia em aberto.
  - O motivo da pendencia tambem sera exibido ao usuario.
  - Mesmo assim, o usuario podera realizar um novo apontamento para essa OS, podendo ser outra descricao de atividade, nao necessariamente a pendencia existente clicando em **Nao Finalizar Pendencia**.

- Se ao final de um apontamento o usuario escolher **Salvar com Pendencia**:
  - Os dados do apontamento sao salvos normalmente.
  - **Adicionalmente, e criada uma pendencia automaticamente** na aba **Pendencias**.

---

## Dados registrados em uma pendencia

Uma pendencia contem obrigatoriamente os seguintes dados:
- Numero da OS  
- Cliente  
- Data de inicio  
- Responsavel pelo inicio  
- Tipo de maquina  
- Descricao da maquina  
- Descricao da pendencia  
- Tempo em que a pendencia esta em aberto  

Ao ser criada, a pendencia gera automaticamente um **icone de alerta** visivel na aba **Pendencias**.  
Essa pendencia fica exposta para qualquer colaborador, que podera encerra-la quando necessario.

---

## Finalizacao de pendencias

Ha **duas formas de finalizar uma pendencia**:

### 1. Finalizar diretamente pela aba Pendencias
1. O colaborador clica em **Finalizar Pendencia**.  
2. O sistema redireciona automaticamente para a tela de **Apontamento**.  
3. Nesta tela, os campos serao **preenchidos automaticamente** com os dados da pendencia:
   - Numero da OS  
   - Cliente  
   - Descricao da maquina  
   - Tipo de maquina  
   - Data e hora de inicio  

   As demais abas devem ser preenchidas manualmente pelo operador.

4. Ao clicar em **Salvar Apontamento**:
   - A pendencia e encerrada automaticamente.  
   - E gerado um novo registro de apontamento.  
   - A pendencia recebe a atribuicao do responsavel pelo fechamento, data e hora do fechamento.  
   - O campo **Observacao** da aba Apontamento sera registrado como **solucao da pendencia**.  
   - O sistema calcula e mostra o **tempo gasto para fechar a pendencia**.

---

### 2. Finalizar pelo fluxo normal de Apontamento (pagina Desenvolvimento -> Aba Apontamento)

- Caso exista uma pendencia vinculada a um numero de OS:
  - Ao inserir esse numero no campo de consulta, o sistema avisa que existe pendencia e mostra o motivo.  
  - O usuario pode:
    - Realizar um novo apontamento para a mesma OS com outra descricao de atividade (**Nao Finalizar Pendencia**).  
    - Ou clicar no botao **Finalizar essa Pendencia**.  

- Se optar por finalizar a pendencia:
  - O processo de apontamento continua normalmente.  
  - Ao salvar o apontamento:
    - A pendencia e automaticamente encerrada.  
    - E gerado um novo registro de apontamento.  
    - A pendencia recebe atribuicao do responsavel, data e hora de fechamento.  
    - O campo **Observacao** da aba Apontamento sera registrado como **solucao da pendencia**.  
    - O sistema calcula e mostra o **tempo gasto para fechar a pendencia**.

---

## Fluxo resumido

1. Criacao da pendencia: Desenvolvimento --> Apontamento --> via "Salvar com Pendencia".  
2. Exibicao: icone de alerta na aba Pendencias.  
3. Consulta: ao pesquisar uma OS com pendencia, o usuario recebe aviso e motivo.  
4. Finalizacao:  
   - Opcao 1: pela aba Pendencias, com dados carregados automaticamente no Apontamento.  
   - Opcao 2: pela aba Apontamento, ao escolher finalizar a pendencia vinculada a uma OS.  
5. Encerramento: gera apontamento, registra responsavel, solucao e tempo total gasto.  
