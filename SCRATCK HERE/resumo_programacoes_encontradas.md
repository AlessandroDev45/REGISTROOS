# 📊 RESUMO DAS PROGRAMAÇÕES ENCONTRADAS

## 🗄️ TABELA: `programacoes` (Sistema PCP Oficial)
**Relacionada com Ordens de Serviço**

| ID | OS | Responsável | Status | Período | Setor |
|----|----|-----------|---------|---------| ------|
| 1 | TEST003 | SUPERVISOR LABORATORIO DE ENSAIOS ELETRICOS | PROGRAMADA | 2025-01-20 08:00 até 17:00 | TESTES |

**Relacionamento**: `id_ordem_servico` → `ordens_servico.id`

---

## 🧪 TABELA: `programacao_testes` (Testes Específicos)
**Sistema de testes independente**

| ID | Código | Título | Status | Prioridade | Período |
|----|--------|--------|--------|------------|---------|
| 1 | PROG_TESTE_001 | Teste Completo - Equipamento A | EM_ANDAMENTO | ALTA | 2025-09-24 |
| 2 | PROG_TESTE_002 | Teste de Durabilidade - Equipamento B | PROGRAMADO | NORMAL | 2025-09-25 até 2025-09-27 |
| 3 | PROG_TESTE_003 | Validação Rápida - Equipamento C | PROGRAMADO | URGENTE | 2025-09-26 |
| 4 | PROG_TESTE_004 | Bateria Completa - Todos Equipamentos | PROGRAMADO | ALTA | 2025-09-30 até 2025-10-03 |
| 5 | PROG_TESTE_005 | Bateria Completa de Validação | CONCLUIDO | URGENTE | 2025-10-07 até 2025-10-12 |

**Relacionamento**: Não relacionada com OS, sistema independente

---

## 🔗 DIFERENÇAS PRINCIPAIS:

### `programacoes` (PCP Oficial):
- ✅ **Relacionada** com `ordens_servico`
- ✅ **Usada** pelo formulário PCP
- ✅ **11 colunas** simples
- ✅ **Foco**: Programação de produção

### `programacao_testes` (Testes):
- ❌ **Não relacionada** com OS
- ❌ **Não usada** pelo PCP
- ✅ **26 colunas** complexas
- ✅ **Foco**: Programação de testes específicos

---

## 🎯 CONCLUSÃO:

**AMBAS AS TABELAS TINHAM DADOS!**

O problema era o **erro SQL** no endpoint PCP que impedia a visualização dos dados da tabela `programacoes` oficial.

Após a correção do erro (`c.nome` → `c.razao_social`), o sistema PCP agora funciona perfeitamente e mostra a programação criada.
