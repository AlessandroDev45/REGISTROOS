# 🔍 DIAGNÓSTICO - LOOP INFINITO NA PROGRAMAÇÃO PCP

## 🎯 POSSÍVEIS CAUSAS IDENTIFICADAS

### 1. **Problema no useEffect com dependência `filtros`**
**Arquivo:** `ProgramacoesList.tsx` linha 49-51

```typescript
useEffect(() => {
  carregarProgramacoes();
}, [filtros]);
```

**🚨 PROBLEMA POTENCIAL:**
- Se o objeto `filtros` está sendo recriado a cada render do componente pai
- Isso causa execução infinita do useEffect
- Cada execução chama `carregarProgramacoes()` → API → re-render → novo `filtros` → loop

### 2. **Problema no PCPPage.tsx**
**Arquivo:** `PCPPage.tsx` linha 100-124

```typescript
useEffect(() => {
  const loadData = async () => {
    // Carregar programações
    const progData = await getProgramacoes();
    setProgramacoes(progData);
    
    // Carregar dados do formulário
    const formDataResponse = await getProgramacaoFormData();
    setFormData(formDataResponse);
  };
  loadData();
}, []);
```

**🚨 PROBLEMA POTENCIAL:**
- Se `getProgramacoes()` ou `getProgramacaoFormData()` estão falhando
- Podem estar causando re-renders infinitos

### 3. **Problema no ProgramacaoForm.tsx**
**Arquivo:** `ProgramacaoForm.tsx` linha 92-94

```typescript
useEffect(() => {
  carregarDadosFormulario();
}, []);
```

**🚨 PROBLEMA POTENCIAL:**
- Se `carregarDadosFormulario()` está falhando ou causando state updates
- Pode estar causando re-renders infinitos

## 🔧 SOLUÇÕES PROPOSTAS

### ✅ **SOLUÇÃO 1: Estabilizar objeto filtros**

**No componente pai que passa `filtros`:**
```typescript
// ❌ ERRADO - cria novo objeto a cada render
const filtros = {
  status: filtroStatus,
  setor: filtroSetor
};

// ✅ CORRETO - usar useMemo
const filtros = useMemo(() => ({
  status: filtroStatus,
  setor: filtroSetor
}), [filtroStatus, filtroSetor]);
```

### ✅ **SOLUÇÃO 2: Usar useCallback para funções**

**No ProgramacoesList.tsx:**
```typescript
const carregarProgramacoes = useCallback(async () => {
  setLoading(true);
  try {
    const response = await getProgramacoes(filtros);
    setProgramacoes(Array.isArray(response) ? response : []);
  } catch (error) {
    console.error('Erro ao carregar programações:', error);
    setProgramacoes([]);
  } finally {
    setLoading(false);
  }
}, [filtros]);
```

### ✅ **SOLUÇÃO 3: Verificar se filtros mudaram realmente**

```typescript
useEffect(() => {
  if (filtros && Object.keys(filtros).length > 0) {
    carregarProgramacoes();
  }
}, [filtros]);
```

### ✅ **SOLUÇÃO 4: Adicionar logs para debug**

```typescript
useEffect(() => {
  console.log('🔄 useEffect executado com filtros:', filtros);
  carregarProgramacoes();
}, [filtros]);
```

## 🧪 SCRIPT DE TESTE PARA IDENTIFICAR O PROBLEMA

### **Verificar no Console do Browser:**

1. **Abrir DevTools** (F12)
2. **Ir para aba Console**
3. **Procurar por:**
   - Logs repetitivos de "Carregando dados..."
   - Múltiplas chamadas para `/api/pcp/programacoes`
   - Múltiplas chamadas para `/api/pcp/programacao-form-data`

### **Verificar no Network Tab:**

1. **Abrir DevTools** → **Network**
2. **Recarregar página**
3. **Procurar por:**
   - Múltiplas requisições para mesmos endpoints
   - Requisições sendo feitas continuamente
   - Status 200 mas sendo chamadas infinitamente

## 🎯 IMPLEMENTAÇÃO DA CORREÇÃO

### **PASSO 1: Corrigir ProgramacoesList.tsx**
```typescript
import React, { useState, useEffect, useCallback, useMemo } from 'react';

const carregarProgramacoes = useCallback(async () => {
  setLoading(true);
  try {
    const response = await getProgramacoes(filtros);
    setProgramacoes(Array.isArray(response) ? response : []);
  } catch (error) {
    console.error('Erro ao carregar programações:', error);
    setProgramacoes([]);
  } finally {
    setLoading(false);
  }
}, [filtros]);

useEffect(() => {
  console.log('🔄 Carregando programações com filtros:', filtros);
  carregarProgramacoes();
}, [carregarProgramacoes]);
```

### **PASSO 2: Corrigir componente pai**
```typescript
// No componente que usa ProgramacoesList
const filtros = useMemo(() => ({
  status: filtroStatus,
  setor: filtroSetor,
  departamento: filtroDepartamento
}), [filtroStatus, filtroSetor, filtroDepartamento]);

return (
  <ProgramacoesList 
    filtros={filtros}
    onProgramacaoSelect={handleSelect}
    onProgramacaoUpdate={handleUpdate}
  />
);
```

## 🚨 VERIFICAÇÃO FINAL

Após implementar as correções:

1. **Verificar Console** - Não deve haver logs repetitivos
2. **Verificar Network** - Apenas 1 chamada inicial para cada endpoint
3. **Verificar Performance** - Página deve carregar normalmente
4. **Testar Filtros** - Mudanças nos filtros devem funcionar sem loops

## 📋 CHECKLIST DE CORREÇÃO

- [ ] Adicionar useMemo para objeto filtros
- [ ] Adicionar useCallback para funções assíncronas
- [ ] Verificar dependências dos useEffect
- [ ] Adicionar logs de debug temporários
- [ ] Testar em ambiente de desenvolvimento
- [ ] Remover logs de debug após correção
- [ ] Verificar se não há outros componentes com mesmo problema
