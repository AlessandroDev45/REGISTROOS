# 🧪 INSTRUÇÕES PARA TESTE DO LAYOUT HIERARQUIA

## 📋 TESTES DISPONÍVEIS

### 1. 🌐 TESTE HTML SIMPLES (Recomendado primeiro)
**Arquivo:** `teste_layout_hierarquia.html`

**Como usar:**
1. Abra o arquivo `teste_layout_hierarquia.html` no navegador
2. Você verá o layout da hierarquia com dados simulados
3. Clique nos departamentos e setores para expandir/contrair
4. Verifique se os cliques funcionam corretamente
5. Observe o log na parte inferior da página

**O que deve acontecer:**
- ✅ Clique no departamento MOTORES → deve expandir e mostrar setores
- ✅ Clique no setor LABORATORIO DE ENSAIOS ELETRICOS → deve expandir e mostrar detalhes
- ✅ Ícones devem mudar de 📁 para 📂
- ✅ Log deve mostrar as ações realizadas
- ❌ **NÃO deve navegar para outras páginas**

### 2. ⚛️ TESTE REACT COMPONENT
**Arquivo:** `TesteLayoutHierarquia.tsx`

**Como usar:**
1. Copie o conteúdo do arquivo para dentro do seu projeto React
2. Importe e use o componente em uma página de teste
3. Teste com dados mock primeiro, depois com dados reais

### 3. 🔗 TESTE NO SISTEMA REAL

**Como testar:**
1. Inicie o backend: `cd RegistroOS\registrooficial\backend && python main.py`
2. Inicie o frontend: `cd RegistroOS\registrooficial\frontend && npm start`
3. Faça login no sistema
4. Vá para `/desenvolvimento`
5. Clique na aba "🌳 Estrutura Hierárquica"

## 🎯 O QUE VERIFICAR

### ✅ COMPORTAMENTOS CORRETOS
- [ ] Departamentos expandem/contraem ao clicar
- [ ] Setores expandem/contraem ao clicar
- [ ] Ícones mudam de 📁 para 📂
- [ ] Hover effects funcionam (mudança de cor)
- [ ] Layout responsivo funciona
- [ ] Dados são carregados corretamente
- [ ] Console não mostra erros

### ❌ PROBLEMAS A IDENTIFICAR
- [ ] Clique navega para página de edição
- [ ] Layout quebrado ou mal formatado
- [ ] Dados não carregam
- [ ] Erros no console do navegador
- [ ] Cliques não funcionam
- [ ] Ícones não mudam

## 🔧 TROUBLESHOOTING

### Problema: "Clique vai para edição de departamento"
**Possíveis causas:**
1. Há um Link ou navigate interceptando o clique
2. Evento de clique não está sendo tratado corretamente
3. Componente pai está interferindo

**Como verificar:**
1. Abra o console do navegador (F12)
2. Vá para a aba Network
3. Clique no setor
4. Verifique se há requisições sendo feitas
5. Se houver navegação, o problema está no roteamento

### Problema: "Departamento MOTORES não aparece"
**Possíveis causas:**
1. Endpoint não está retornando dados
2. Erro na requisição da API
3. Dados não estão sendo processados corretamente

**Como verificar:**
1. Abra o console do navegador
2. Vá para a aba Network
3. Procure por requisição para `/api/estrutura-hierarquica`
4. Verifique se retorna dados
5. Verifique se há erros no console

### Problema: "Layout quebrado"
**Possíveis causas:**
1. CSS não está carregando
2. Classes Tailwind não estão disponíveis
3. Estrutura HTML incorreta

**Como verificar:**
1. Teste primeiro o arquivo HTML simples
2. Se funcionar, o problema está no React
3. Verifique se Tailwind CSS está configurado

## 📊 RESULTADOS ESPERADOS

### 🌐 TESTE HTML
- ✅ Layout deve funcionar perfeitamente
- ✅ Cliques devem expandir/contrair
- ✅ Log deve mostrar ações
- ✅ Teste automático deve rodar

### ⚛️ TESTE REACT
- ✅ Dados mock devem funcionar
- ✅ Dados reais devem carregar (se backend estiver rodando)
- ✅ Interações devem funcionar igual ao HTML

### 🔗 TESTE SISTEMA REAL
- ✅ Aba "🌳 Estrutura Hierárquica" deve aparecer
- ✅ Dados reais devem carregar
- ✅ MOTORES deve aparecer com 18 setores
- ✅ LABORATORIO DE ENSAIOS ELETRICOS deve ter dados completos
- ❌ **NÃO deve navegar para edição ao clicar**

## 🚨 SE AINDA HOUVER PROBLEMAS

### 1. Teste o HTML primeiro
Se o HTML funcionar, o problema está no React/roteamento.

### 2. Verifique o console
Erros no console indicam problemas específicos.

### 3. Teste a API diretamente
Acesse `http://localhost:8000/api/estrutura-hierarquica` no navegador.

### 4. Verifique o roteamento
Pode haver conflito com rotas do React Router.

## 📝 RELATÓRIO DE TESTE

Após testar, anote:
- [ ] Teste HTML funcionou? (Sim/Não)
- [ ] Teste React funcionou? (Sim/Não)
- [ ] Sistema real funcionou? (Sim/Não)
- [ ] Qual problema específico encontrou?
- [ ] Mensagens de erro no console?

Com essas informações, posso ajudar a resolver problemas específicos.
