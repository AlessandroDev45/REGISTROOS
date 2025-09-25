# 🔍 DEBUG - TABELA TIPOS DE TESTE

## 🚨 PROBLEMAS IDENTIFICADOS

### 1. **Tabela não aparece**
- ❌ Tabela não está sendo exibida ao selecionar tipo de máquina
- 🔍 Adicionados logs detalhados para debug

### 2. **Warning controlled/uncontrolled input**
- ⚠️ Inputs mudando de undefined para controlled
- 🔧 Precisa corrigir valores iniciais

## 🔍 LOGS ADICIONADOS

### **useEffect tipos de teste:**
```javascript
console.log('🔍 useEffect tipos de teste executado:', { 
    user: user?.primeiro_nome, 
    departamento: user?.departamento, 
    setor: user?.setor, 
    selMaq: formData.selMaq 
});

if (user && formData.selMaq) {
    console.log('✅ Condições atendidas, carregando tipos de teste...');
    loadTiposTeste(departamento, setor, formData.selMaq);
} else {
    console.log('❌ Condições não atendidas:', { 
        hasUser: !!user, 
        hasSelMaq: !!formData.selMaq 
    });
}
```

### **Renderização da tabela:**
```javascript
console.log('🧪 Renderizando tabela:', { 
    tiposTesteLength: tiposTeste.length, 
    tiposTeste 
});
```

### **Função loadTiposTeste:**
```javascript
console.log('🧪 Carregando tipos de teste com filtros:', { departamento, setor, tipoMaquina });
const response = await api.get(`/tipos-teste?${params.toString()}`);
console.log('🧪 Tipos de teste carregados:', response.data);
```

## 🧪 COMO TESTAR E VERIFICAR LOGS

### **Passos para Debug:**
1. **Abra o DevTools** (F12)
2. **Vá para Console**
3. **Acesse:** `/desenvolvimento` → **Apontamento**
4. **Selecione:** Um tipo de máquina
5. **Observe os logs:**

### **Logs Esperados:**
```
🔍 useEffect tipos de teste executado: {user: "NOME", departamento: "MOTORES", setor: "MECANICA DIA", selMaq: "MAQUINA_TIPO"}
✅ Condições atendidas, carregando tipos de teste...
🧪 Carregando tipos de teste com filtros: {departamento: "MOTORES", setor: "MECANICA DIA", tipoMaquina: "MAQUINA_TIPO"}
🧪 Tipos de teste carregados: [array com tipos]
🧪 Renderizando tabela: {tiposTesteLength: X, tiposTeste: [array]}
```

### **Se não aparecer:**
```
❌ Condições não atendidas: {hasUser: false, hasSelMaq: false}
🧪 Renderizando tabela: {tiposTesteLength: 0, tiposTeste: []}
```

## 🔧 POSSÍVEIS CAUSAS

### **1. User não carregado:**
- ❌ `user` está undefined ou null
- ❌ `user.departamento` ou `user.setor` estão undefined

### **2. FormData não atualizado:**
- ❌ `formData.selMaq` não está sendo definido
- ❌ Seleção do dropdown não está funcionando

### **3. API não responde:**
- ❌ Endpoint `/tipos-teste` com erro
- ❌ Filtros não funcionando no backend

### **4. Estado não atualizado:**
- ❌ `setTiposTeste` não está funcionando
- ❌ Re-render não está acontecendo

## 🛠️ PRÓXIMOS PASSOS

### **1. Verificar logs no console**
- Identificar qual condição está falhando
- Ver se API está sendo chamada
- Verificar se dados estão chegando

### **2. Corrigir problema identificado:**

#### **Se user não carregado:**
```javascript
// Verificar AuthContext
// Verificar se login foi feito corretamente
```

#### **Se formData não atualizado:**
```javascript
// Verificar se onChange do select está funcionando
// Verificar se setFormData está sendo chamado
```

#### **Se API com erro:**
```javascript
// Verificar endpoint no backend
// Verificar se filtros estão corretos
// Verificar se dados existem na DB
```

### **3. Corrigir warning controlled/uncontrolled:**
```javascript
// Garantir que todos os campos tenham valores iniciais
// Usar '' em vez de undefined
```

## 📋 CHECKLIST DE VERIFICAÇÃO

### **Frontend:**
- [ ] User está carregado com departamento/setor
- [ ] formData.selMaq está sendo definido ao selecionar
- [ ] useEffect está sendo executado
- [ ] loadTiposTeste está sendo chamada
- [ ] setTiposTeste está atualizando o estado
- [ ] Tabela está sendo renderizada (tiposTeste.length > 0)

### **Backend:**
- [ ] Endpoint `/tipos-teste` está funcionando
- [ ] Filtros por departamento/setor/tipo_maquina funcionam
- [ ] Dados existem na base de dados
- [ ] Resposta está no formato correto

### **Rede:**
- [ ] Requisição está sendo feita
- [ ] Resposta está chegando
- [ ] Não há erros de CORS ou autenticação

## 🎯 RESULTADO ESPERADO

Após debug e correções:
- ✅ Logs mostram fluxo completo
- ✅ Tabela aparece ao selecionar máquina
- ✅ 5 colunas funcionando
- ✅ Sem warnings no console
- ✅ Funcionalidades de seleção/resultado/observação funcionando

**EXECUTE OS TESTES E REPORTE OS LOGS ENCONTRADOS!** 🔍
