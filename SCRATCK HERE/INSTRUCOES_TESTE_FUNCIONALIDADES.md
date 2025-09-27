# 🧪 INSTRUÇÕES PARA TESTE DAS FUNCIONALIDADES IMPLEMENTADAS

## 📊 DADOS DE TESTE CRIADOS

✅ **5 Ordens de Serviço** (TEST20250001 a TEST20250005)
✅ **3 Pendências** (IDs 1, 2, 3) - OSs TEST20250001, TEST20250002, TEST20250003
✅ **2 Programações** (IDs 1, 2) - OSs TEST20250004, TEST20250005
✅ **3 Apontamentos de origem** para as pendências

---

## 🔧 COMO TESTAR CADA FUNCIONALIDADE

### 1. 📋 **TESTE DE PENDÊNCIAS**

#### **1.1 Visualizar Pendências**
1. Acesse a aplicação web
2. Vá para a aba **"Pendências"**
3. Verifique se aparecem 3 pendências:
   - **Pendência ID 1**: OS TEST20250001 - Vazamento no sistema hidráulico
   - **Pendência ID 2**: OS TEST20250002 - Ruído anormal durante operação
   - **Pendência ID 3**: OS TEST20250003 - Temperatura elevada nos mancais

#### **1.2 Teste do Controle de Acesso**
1. Faça login com usuários de diferentes setores
2. Verifique se cada usuário vê apenas pendências do seu setor
3. Teste com usuário PCP/GESTÃO - deve ver todas as pendências

#### **1.3 Teste de Resolução via Apontamento**
1. Na aba **"Pendências"**, clique em **"📝 Resolver via Apontamento"** em uma pendência
2. **Resultado esperado**: 
   - Sistema redireciona para aba **"Apontamento"**
   - Formulário é preenchido automaticamente com dados da pendência
   - Campo OS mostra o número da OS da pendência
   - Campo observação contém referência à pendência

3. Complete o apontamento normalmente:
   - Preencha data/hora início e fim
   - Adicione observações adicionais
   - Clique em **"💾 Salvar Apontamento"**

4. **Resultado esperado**:
   - Apontamento é criado com sucesso
   - Pendência é automaticamente finalizada
   - Sistema retorna para estado limpo

### 2. 📅 **TESTE DE PROGRAMAÇÕES**

#### **2.1 Visualizar Programações**
1. Acesse a aba **"Minhas Programações"**
2. Verifique se aparecem 2 programações:
   - **Programação ID 1**: OS TEST20250004
   - **Programação ID 2**: OS TEST20250005
3. **Verificar**: Não deve haver botão **"✅ Finalizar"** nas programações

#### **2.2 Teste de Detecção Automática de Programação**
1. Vá para a aba **"Apontamento"**
2. Digite **"TEST20250004"** no campo **"Número da OS"**
3. **Resultado esperado**:
   - Sistema detecta automaticamente a programação ativa
   - Aparece uma caixa mostrando dados da programação
   - Botão muda para **"💾 Salvar Apontamento/Programação"** (cor azul)

#### **2.3 Teste de Finalização de Programação via Apontamento**
1. Com a OS TEST20250004 no formulário (programação detectada)
2. Preencha o apontamento:
   - Data/hora início e fim
   - Tipo de atividade
   - Observações
3. Clique em **"💾 Salvar Apontamento/Programação"**
4. **Resultado esperado**:
   - Apontamento é criado
   - Programação é automaticamente finalizada
   - Mensagem confirma ambas as ações

### 3. 🔄 **TESTE DE FLUXO COMPLETO**

#### **3.1 Fluxo: Pendência → Apontamento → Resolução**
1. Acesse **"Pendências"**
2. Clique **"📝 Resolver via Apontamento"** na Pendência ID 1
3. Complete o apontamento
4. Salve o apontamento
5. Volte para **"Pendências"**
6. **Verificar**: Pendência não aparece mais (foi resolvida)

#### **3.2 Fluxo: Programação → Apontamento → Finalização**
1. Acesse **"Minhas Programações"**
2. Note a Programação ID 1 (status PROGRAMADA)
3. Vá para **"Apontamento"**
4. Digite OS TEST20250004
5. Complete e salve o apontamento/programação
6. Volte para **"Minhas Programações"**
7. **Verificar**: Programação mudou para status FINALIZADA

### 4. 📝 **TESTE DE APONTAMENTO COM PENDÊNCIA**

#### **4.1 Criar Apontamento com Pendência**
1. Na aba **"Apontamento"**
2. Preencha uma OS qualquer (ex: TEST20250005)
3. Complete o formulário normalmente
4. Clique em **"📋 Salvar com Pendência"**
5. **Resultado esperado**:
   - Apontamento é criado
   - Nova pendência é criada automaticamente
   - Se houver programação ativa, ela também é finalizada

---

## 🎯 CENÁRIOS DE TESTE ESPECÍFICOS

### **Cenário A: Usuário Normal**
- Login com usuário comum
- Deve ver apenas pendências do seu setor
- Pode resolver pendências do seu setor via apontamento
- Pode finalizar programações apenas via apontamento

### **Cenário B: Usuário PCP/GESTÃO**
- Login com usuário PCP ou GESTÃO
- Deve ver todas as pendências do sistema
- Pode resolver qualquer pendência
- Pode criar e gerenciar programações

### **Cenário C: Programação Ativa**
- Digite OS com programação ativa (TEST20250004 ou TEST20250005)
- Botão deve mudar para "Salvar Apontamento/Programação"
- Ao salvar, programação deve ser finalizada automaticamente

### **Cenário D: Resolução de Pendência**
- Use botão "Resolver via Apontamento" em qualquer pendência
- Formulário deve ser preenchido automaticamente
- Ao salvar, pendência deve ser finalizada

---

## ✅ CHECKLIST DE VALIDAÇÃO

### **Interface:**
- [ ] Botões mudam conforme contexto (programação ativa)
- [ ] Preenchimento automático funciona (resolução de pendência)
- [ ] Mensagens de sucesso aparecem corretamente
- [ ] Navegação entre abas funciona

### **Funcionalidades:**
- [ ] Detecção automática de programação ativa
- [ ] Finalização automática de programação via apontamento
- [ ] Resolução de pendência via apontamento
- [ ] Controle de acesso por setor funciona
- [ ] Criação de pendência via apontamento

### **Banco de Dados:**
- [ ] Programações são marcadas como FINALIZADA
- [ ] Pendências são marcadas como FECHADA
- [ ] Apontamentos são criados corretamente
- [ ] Histórico é atualizado nas programações

---

## 🚨 PROBLEMAS CONHECIDOS E SOLUÇÕES

### **Problema**: Programação não é detectada
**Solução**: Verifique se a OS digitada corresponde exatamente às OSs de teste (TEST20250004 ou TEST20250005)

### **Problema**: Pendência não aparece
**Solução**: Verifique se o usuário logado tem acesso ao setor da pendência

### **Problema**: Botão não muda de cor
**Solução**: Aguarde alguns segundos após digitar a OS para a detecção automática

### **Problema**: Erro ao salvar
**Solução**: Verifique se todos os campos obrigatórios estão preenchidos

---

## 📞 SUPORTE

Se encontrar problemas durante os testes:

1. **Verifique os logs do backend** para erros de API
2. **Abra o console do navegador** para erros de frontend
3. **Confirme se o servidor backend está rodando**
4. **Verifique se os dados de teste foram criados corretamente**

**Dados de teste disponíveis:**
- OSs: TEST20250001 a TEST20250005
- Pendências: IDs 1, 2, 3
- Programações: IDs 1, 2

🎉 **Boa sorte com os testes!**
