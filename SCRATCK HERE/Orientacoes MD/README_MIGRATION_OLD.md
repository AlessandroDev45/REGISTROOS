# 🔄 MIGRAÇÃO: Reestruturação da Ordem de Serviço

## 📋 Visão Geral
Esta migração implementa uma **reestruturação completa** da base de dados do sistema RegistroOS, migrando de uma estrutura simples para uma arquitetura **específica por setor** que melhor atende aos requisitos de negócio.

## 🎯 Objetivos da Migração

### ✅ Problemas Resolvidos
- **Unicidade OS**: Campo `os_numero` agora é único
- **Relação 1:1**: OS ↔ Equipamento agora é uma relação de 1 para 1
- **Setores Específicos**: Testes, apontamentos e programações específicos por setor
- **Integridade de Dados**: Constraints e validações aprimoradas
- **Performance**: Índices otimizados para consultas frequentes

### 🚀 Benefícios da Nova Estrutura

#### 1. **Normalização Adequada**
```
ANTES: Uma OS pode ter múltiplos equipamentos
DEPOIS: Uma OS = Um equipamento (relação 1:1)
```

#### 2. **Especificidade por Setor**
```
ANTES: Apontamentos genéricos
DEPOIS: Apontamentos específicos por setor (Mecânica, Elétrica, PCP, etc.)
```

#### 3. **Controle de Qualidade Aprimorado**
```
ANTES: Testes genéricos sem contexto de setor
DEPOIS: Testes categorizados por setor e tipo de equipamento
```

## 📁 Arquivos da Migração

```
migrations/
├── migrate_os_structure.sql          # Script SQL principal
├── run_migration_os_structure.py     # Executor Python seguro
├── README_MIGRATION.md              # Este arquivo
└── backups/                         # Diretório de backups automáticos
```

## ⚡ Como Executar a Migração

### Pré-requisitos
- ✅ Python 3.7+
- ✅ Acesso de escrita ao banco de dados
- ✅ Espaço em disco para backup (~2x tamanho do banco atual)
- ✅ Sistema em modo manutenção (sem usuários ativos)

### Passos de Execução

#### 1. **Preparação**
```bash
# Navegar para o diretório de migrações
cd RegistroOS/registrooficial/backend/migrations

# Verificar se os arquivos existem
ls -la *.sql *.py
```

#### 2. **Execução Automática (Recomendado)**
```bash
# Executar o script Python (automático e seguro)
python run_migration_os_structure.py
```

#### 3. **Execução Manual (Avançado)**
```bash
# Conectar ao SQLite
sqlite3 /caminho/para/registroos_new.db

# Executar o script SQL
.read migrate_os_structure.sql

# Verificar resultados
.schema ordens_servico
.schema os_setores
.schema apontamentos_setor
```

## 🔍 O Que a Migração Faz

### 1. **Backup Automático**
- Cria cópia completa do banco antes da migração
- Backup timestampado em `backups/`
- Recuperação automática em caso de falha

### 2. **Estrutura Nova Criada**
```sql
-- Nova tabela de setores por OS
CREATE TABLE os_setores (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,
    setor VARCHAR(100) NOT NULL,
    status_setor VARCHAR(50) DEFAULT 'PENDENTE',
    -- ... outros campos
    UNIQUE(id_os, setor)  -- Um setor por OS
);

-- Apontamentos específicos por setor
CREATE TABLE apontamentos_setor (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,
    id_os_setor INTEGER NOT NULL,  -- Vincula ao setor
    id_tecnico INTEGER NOT NULL,
    -- ... campos específicos
);

-- Testes específicos por setor
CREATE TABLE testes_setor (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,
    id_os_setor INTEGER NOT NULL,
    categoria_teste VARCHAR(100),  -- ELETRICO, MECANICO, etc.
    -- ... campos específicos
);
```

### 3. **Migração de Dados**
- **OS existentes**: Migradas mantendo IDs originais
- **Apontamentos**: Vinculados aos setores correspondentes
- **Testes**: Categorizados por setor e tipo
- **Programações**: Associadas aos setores específicos

### 4. **Constraints de Integridade**
```sql
-- Unicidade garantida
CREATE UNIQUE INDEX idx_os_numero_unico ON ordens_servico(os_numero);
CREATE UNIQUE INDEX idx_equipamento_unico ON ordens_servico(id_equipamento);

-- Relacionamentos consistentes
FOREIGN KEY (id_os) REFERENCES ordens_servico(id)
FOREIGN KEY (id_os_setor) REFERENCES os_setores(id)
```

## 📊 Validações Pós-Migração

### Verificações Automáticas
O script executa automaticamente:
- ✅ Contagem de registros antes/depois
- ✅ Validação de constraints
- ✅ Verificação de integridade referencial
- ✅ Teste de índices criados

### Verificações Manuais
```sql
-- Verificar unicidade
SELECT os_numero, COUNT(*) as duplicatas
FROM ordens_servico
GROUP BY os_numero
HAVING COUNT(*) > 1;

-- Verificar relacionamentos
SELECT os.id, os.os_numero, eq.descricao
FROM ordens_servico os
LEFT JOIN equipamentos eq ON os.id_equipamento = eq.id
WHERE os.id_equipamento IS NULL;

-- Verificar setores criados
SELECT setor, COUNT(*) as quantidade
FROM os_setores
GROUP BY setor
ORDER BY setor;
```

## 🔄 Processo de Rollback

### Rollback Automático
- Executado automaticamente se migração falhar
- Restaura backup criado no início
- Sem perda de dados

### Rollback Manual
```bash
# Restaurar backup
cp backups/backup_pre_migration_YYYYMMDD_HHMMSS.db registroos_new.db

# Verificar integridade
sqlite3 registroos_new.db "PRAGMA integrity_check;"
```

## 🎯 Benefícios da Nova Arquitetura

### Para Desenvolvedores
- ✅ Código mais organizado e específico
- ✅ Consultas mais performáticas
- ✅ Manutenção simplificada
- ✅ Escalabilidade aprimorada

### Para Usuários
- ✅ Dados mais consistentes
- ✅ Relatórios por setor mais precisos
- ✅ Controle de qualidade aprimorado
- ✅ Rastreabilidade completa

### Para o Sistema
- ✅ Integridade referencial garantida
- ✅ Performance de consultas otimizada
- ✅ Estrutura preparada para crescimento
- ✅ Backup e recuperação robustos

## 🚨 Considerações Importantes

### Durante a Migração
- ⚠️ **Sistema deve estar em manutenção**
- ⚠️ **Nenhum usuário deve estar ativo**
- ⚠️ **Backup verificado antes de prosseguir**

### Após a Migração
- 🔄 **Testar todas as funcionalidades**
- 🔄 **Verificar relatórios e consultas**
- 🔄 **Treinar equipe sobre nova estrutura**
- 🔄 **Monitorar performance por 24-48h**

## 📞 Suporte

Em caso de problemas:
1. Verificar logs da migração
2. Consultar relatório gerado automaticamente
3. Executar rollback se necessário
4. Entrar em contato com equipe de desenvolvimento

---

**Data da Migração**: Outubro 2025
**Versão do Sistema**: 2.0
**Tipo**: Estrutural (Breaking Changes)
**Tempo Estimado**: 15-30 minutos
**Downtime**: 30-60 minutos