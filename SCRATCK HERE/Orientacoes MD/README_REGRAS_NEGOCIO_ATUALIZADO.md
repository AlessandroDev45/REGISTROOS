# 📋 **REGRAS DE NEGÓCIO - Sistema RegistroOS** (Versão Atualizada)

## 🎯 **Visão Geral das Regras de Negócio**

O Sistema RegistroOS segue regras específicas de relacionamento entre entidades, permitindo flexibilidade operacional mantendo integridade de dados.

---

## 📊 **1. Relacionamentos Principais**

### 1.1 **Cliente ↔ Ordem de Serviço (N:1)**
- **Regra**: **Um cliente pode ter múltiplas OS**
- **Justificativa**: Mesmo cliente pode ter vários equipamentos/serviços
- **Exemplo**:
  ```
  BRASKEM SA (Cliente)
  ├── OS 15205 - Motor Indução VILLARES 650
  ├── OS 15207 - Motor Indução VILLARES 660
  └── OS 15206 - Motor Indução VILLARES 650 (mesmo equipamento, diferente OS)
  ```

### 1.2 **Equipamento ↔ Ordem de Serviço (N:1)**
- **Regra**: **Um equipamento pode ter múltiplas OS**
- **Justificativa**: Mesmo equipamento pode voltar para manutenção em épocas diferentes
- **Exemplo**:
  ```
  MOTOR DE INDUÇÃO VILLARES 650 Ns 123 (Equipamento)
  ├── OS 15205 - Janeiro 2025
  └── OS 15206 - Junho 2025 (mesmo equipamento, manutenção futura)
  ```

### 1.3 **Ordem de Serviço ↔ Apontamentos (1:N)**
- **Regra**: **Uma OS pode ter múltiplos apontamentos**
- **Justificativa**: Mesmo trabalho pode ter várias intervenções/colaboradores
- **Exemplo**:
  ```
  OS 15205
  ├── Apontamento 1: Colaboradores A,B - Setores C,D
  ├── Apontamento 2: Colaboradores A,B,E - Setores C,D
  └── Apontamento 3: Colaboradores X,Y - Setores F,G
  ```

---

## 🔧 **2. Estrutura Técnica Corrigida**

### 2.1 **Modelo OrdemServico (Corrigido)**
```python
class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    # Campos únicos
    id = Column(Integer, primary_key=True, index=True)
    os_numero = Column(String(50), nullable=False, index=True, unique=True)

    # Relacionamentos N:1 (SEM unique constraints)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=True)        # ✅ N:1
    id_equipamento = Column(Integer, ForeignKey("equipamentos.id"), nullable=True) # ✅ N:1

    # Relacionamentos 1:N
    apontamentos_setor = relationship("ApontamentoSetor", back_populates="ordem_servico", cascade="all, delete-orphan")
    testes_setor = relationship("TesteSetor", back_populates="ordem_servico", cascade="all, delete-orphan")
```

### 2.2 **Estrutura de Dados Final**
```sql
-- Ordem de Serviço (CORRIGIDA)
CREATE TABLE ordens_servico (
    id INTEGER PRIMARY KEY,
    os_numero VARCHAR(50) NOT NULL UNIQUE,           -- ✅ Único
    id_cliente INTEGER,                              -- ✅ N:1 (sem UNIQUE)
    id_equipamento INTEGER,                          -- ✅ N:1 (sem UNIQUE)
    -- ... outros campos
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_equipamento) REFERENCES equipamentos(id)
);

-- Apontamentos (1:N)
CREATE TABLE apontamentos_setor (
    id INTEGER PRIMARY KEY,
    id_os INTEGER NOT NULL,                          -- ✅ 1:N
    setor VARCHAR(100) NOT NULL,
    id_tecnico INTEGER NOT NULL,
    data_inicio DATETIME,
    data_fim DATETIME,
    horas_gastas FLOAT DEFAULT 0.0,
    atividade VARCHAR(255),
    observacoes TEXT,
    FOREIGN KEY (id_os) REFERENCES ordens_servico(id)
);
```

---

## 📈 **3. Cenários de Uso Permitidos**

### 3.1 **Cenário 1: Mesmo Cliente, Equipamentos Diferentes**
```
BRASKEM SA (Cliente)
├── OS 15205: MOTOR VILLARES 650 Ns 123
├── OS 15207: MOTOR VILLARES 660 Ns 321
└── OS 15208: GERADOR VILLARES 750 Ns 456
```

### 3.2 **Cenário 2: Mesmo Equipamento, Épocas Diferentes**
```
MOTOR VILLARES 650 Ns 123 (Equipamento)
├── OS 15205: Janeiro 2025 - Manutenção Preventiva
├── OS 15206: Junho 2025 - Manutenção Corretiva
└── OS 15209: Dezembro 2025 - Modernização
```

### 3.3 **Cenário 3: Múltiplos Apontamentos na Mesma OS**
```
OS 15205: MOTOR VILLARES 650 Ns 123
├── Apontamento 1: João + Maria - Mecânica + Elétrica
├── Apontamento 2: João + Maria + Pedro - Mecânica + Elétrica
├── Apontamento 3: Carlos + Ana - PCP + Gestão
└── Apontamento 4: João - Mecânica (revisão)
```

### 3.4 **Cenário 4: Colaboradores Repetindo em Diferentes Apontamentos**
```
Colaborador João
├── OS 15205: Apontamento 1 (Mecânica)
├── OS 15205: Apontamento 2 (Mecânica)
├── OS 15205: Apontamento 4 (Mecânica)
├── OS 15207: Apontamento 1 (Elétrica)
└── OS 15208: Apontamento 2 (PCP)
```

---

## 🚫 **4. Cenários BLOQUEADOS (Não Permitidos)**

### 4.1 **OS_Numero Duplicado** ❌
```
OS 15205 - MOTOR VILLARES 650 ✅
OS 15205 - GERADOR WEG 500 ❌ (BLOQUEADO - mesmo número)
```

### 4.2 **Apontamentos no Mesmo Horário** ❌
```
OS 15205
├── Apontamento 1: 14:00-16:00 ✅
└── Apontamento 2: 14:00-16:00 ❌ (Mesmo horário - BLOQUEADO)
```

---

## ✅ **5. Validação Final das Regras**

| Relacionamento | Tipo | Status | Justificativa |
|---------------|------|--------|---------------|
| OS_Numero | 1:1 (único) | ✅ OK | Controle de unicidade |
| Cliente ↔ OS | N:1 | ✅ OK | Cliente pode ter várias OS |
| Equipamento ↔ OS | N:1 | ✅ OK | Equipamento pode voltar |
| OS ↔ Apontamentos | 1:N | ✅ OK | Múltiplas intervenções |
| Colaboradores | N:N | ✅ OK | Mesmo colaborador, várias OS |

---

## 🎯 **6. Benefícios da Estrutura Corrigida**

### 6.1 **Flexibilidade Operacional**
- ✅ **Reincidência de Equipamentos**: Mesmo equipamento pode ter várias OS
- ✅ **Histórico Completo**: Rastreamento longitudinal de manutenções
- ✅ **Colaboração**: Múltiplos técnicos na mesma OS
- ✅ **Especialização**: Diferentes setores trabalhando na mesma OS

### 6.2 **Integridade de Dados**
- ✅ **Rastreabilidade**: Histórico completo por equipamento
- ✅ **Consistência**: Dados fixos por OS mantidos
- ✅ **Auditoria**: Facilita compliance e relatórios
- ✅ **Performance**: Índices otimizados para consultas

### 6.3 **Cenários Reais Suportados**
- **Manutenção Preventiva**: Mesmo equipamento, diferentes épocas
- **Manutenção Corretiva**: Urgências em equipamentos já trabalhados
- **Modernização**: Upgrades em equipamentos existentes
- **Retrabalho**: Revisões em intervenções anteriores

---

## 📊 **7. Exemplos Práticos dos Cenários**

### **Exemplo 1: BRASKEM SA - Múltiplas OS**
```json
{
  "cliente": "BRASKEM SA",
  "ordens_servico": [
    {
      "os_numero": "15205",
      "equipamento": "MOTOR DE INDUÇÃO VILLARES 650 Ns 123",
      "apontamentos": [
        {"colaboradores": ["A", "B"], "setores": ["C", "D"]},
        {"colaboradores": ["A", "B", "E"], "setores": ["C", "D"]}
      ]
    },
    {
      "os_numero": "15207",
      "equipamento": "MOTOR DE INDUÇÃO VILLARES 660 Ns 321",
      "apontamentos": [
        {"colaboradores": ["A", "B"], "setores": ["C", "D"]},
        {"colaboradores": ["A", "B", "E"], "setores": ["C", "D"]}
      ]
    },
    {
      "os_numero": "15206",
      "equipamento": "MOTOR DE INDUÇÃO VILLARES 650 Ns 123",
      "apontamentos": [
        {"colaboradores": ["A", "B"], "setores": ["C", "D"]},
        {"colaboradores": ["A", "B", "E"], "setores": ["C", "D"]}
      ]
    }
  ]
}
```

---

## 📞 **8. Conclusão**

**✅ SISTEMA AGORA TOTALMENTE CONFORME COM AS REGRAS DE NEGÓCIO!**

A estrutura corrigida permite:
- **Flexibilidade**: Equipamentos podem ter várias OS em diferentes épocas
- **Escalabilidade**: Clientes podem ter quantas OS precisarem
- **Colaboração**: Múltiplos colaboradores podem trabalhar na mesma OS
- **Rastreabilidade**: Histórico completo mantido por equipamento
- **Integridade**: Constraints apropriadas aplicadas apenas onde necessário

**A arquitetura do RegistroOS agora reflete perfeitamente os processos reais de manutenção industrial!** 🚀