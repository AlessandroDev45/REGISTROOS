# PADRONIZAÇÃO DE ENSAIOS/TESTES SEM ALTERAR A ESTRUTURA ATUAL

## 📊 __PADRONIZAÇÃO EXISTENTE SEM MODIFICAÇÕES__

### __Termo Atualizado: "Ensaio"__

O sistema já usa consistentemente o termo __"ensaio"__ em suas estruturas principais:

#### __Modelo Principal: `TesteContexto` (Padronizado como "Ensaio")__

```python
class TesteContexto(Base):
    __tablename__ = "testes_por_contexto"  # Nome mantido por compatibilidade
    
    # Campos já implementados que seguem a estrutura de ensaios
    id = Column(Integer, primary_key=True)
    id_setor = Column(Integer, ForeignKey("setores.id"))
    id_tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))
    classificacao_temporal = Column(String(50))  # INICIAL, PARCIAL, FINAL
    nome_teste = Column(String(255))  # Interpretado como "nome_ensaio"
    tipo_resultado = Column(String(50))  # NUMERICO, TEXTO, BOOLEAN
    procedimento_teste = Column(Text)  # Interpretado como "procedimento_ensaio"
    equipamento_necessario = Column(String(255))
    valor_referencia_min = Column(DECIMAL(15, 4))
    valor_referencia_max = Column(DECIMAL(15, 4))
    unidade_medida = Column(String(50))
```

#### __Separação Conceitual: Estático vs Dinâmico__

O sistema já implementa a separação através do campo __`classificacao_temporal`__ e estrutura de grupos:

```python
# Estrutura de grupos que define o tipo de ensaio
testesCaCarcaça = [  # Ensaios Estáticos - Carcaça
    { id: 'ca_carc_inspecao_visual', label: 'Inspeção Visual', options: true },
    { id: 'ca_carc_placa_id', label: 'Placa de identificação', options: true },
    # ... ensaios de verificação estática
]

testesCaEstator = [  # Ensaios Estáticos - Estator
    { id: 'ca_estator_inspecao_enrol', label: 'Inspeção Visual Enrolamento', options: true },
    { id: 'ca_estator_res_isol', label: 'Resistência de Isolamento', options: true },
    # ... ensaios de verificação estática
]

testesCaRotor = [    # Ensaios Dinâmicos - Rotor
    { id: 'ca_rotor_queda_ca', label: 'Queda de Tensão CA', options: true },
    { id: 'ca_rotor_queda_cc', label: 'Queda de Tensão CC', options: true },
    # ... ensaios que requerem energia/funcionamento
]
```

#### __Padronização nos Modelos de Dados__

```python
# ResultadoEnsaioDetalhado (já padronizado internamente)
class ResultadoTesteDetalhado(Base):
    __tablename__ = "resultados_teste_detalhados"  # Nome mantido
    
    id_apontamento = Column(Integer, ForeignKey("apontamentos_detalhados.id"))
    id_teste_contexto = Column(Integer, ForeignKey("testes_por_contexto.id"))
    valor_medido = Column(DECIMAL(15, 4))
    status_resultado = Column(String(20))  # OK, NOK, PENDENTE
    observacoes_tecnicas = Column(Text)  # Padronizado como observações do ensaio
    equipamento_utilizado = Column(String(255))
    condicoes_ambiente_temp = Column(DECIMAL(5, 2))
    condicoes_ambiente_umidade = Column(DECIMAL(5, 2))
```

## 🎯 __PADRONIZAÇÃO DOCUMENTAL__

### __Hierarquia com Termo "Ensaio" Padronizado__

```javascript
🏢 DEPARTAMENTO
├── nome: String (ex: "MOTORES", "TRANSFORMADORES")
├── descricao: Text
├── ativo: Boolean
└── data_criacao: DateTime

    └── 🏭 SETOR
    ├── id_departamento: FK > Departamento.id
    ├── nome: String (ex: "PCP MOTORES", "Laboratório Elétrico")
    ├── area_tipo: String ("PRODUCAO", "ADMINISTRATIVA")
    ├── permite_apontamento: Boolean
    ├── supervisor_responsavel: FK > Usuario.id
    ├── ativo: Boolean
    └── data_criacao: DateTime

        └── 🔧 TIPO DE MÁQUINA
        ├── id: Integer (PK)
        ├── nome: String (ex: "MAQUINA ESTATICA CA")
        ├── categoria: String ("MOTOR", "TRANSFORMADOR")
        ├── especificacoes_tecnicas: Text
        └── ativo: Boolean

            └── 📋 ATIVIDADE
            ├── id_setor: FK > Setor.id
            ├── nome_atividade: String
            ├── classificacao_temporal: String ("INICIAL", "PARCIAL", "FINAL")
            ├── descricao_detalhada: Text
            ├── ordem_sequencial: Integer
            ├── tempo_estimado: Float
            ├── requer_aprovacao_supervisor: Boolean
            └── atividade_prerequisito_id: FK > Atividade.id (auto-relacionamento)

                └── 🧪 ENSAIOS POR CONTEXTO
                ├── id_setor: FK > Setor.id
                ├── id_tipo_maquina: FK > TipoMaquina.id
                ├── classificacao_temporal: String ("INICIAL", "PARCIAL", "FINAL")
                ├── nome_ensaio: String (padronizado de "nome_teste")
                ├── tipo_resultado: String ("NUMERICO", "TEXTO", "BOOLEAN")
                ├── procedimento_ensaio: Text (padronizado de "procedimento_teste")
                ├── equipamento_necessario: String
                ├── valor_referencia_min/max: DECIMAL(15, 4)
                └── unidade_medida: String

                    └── 🔬 ENSAIOS ESTÁTICOS
                    ├── Inspeção Visual
                    ├── Placa de identificação
                    ├── Rtd's Mancal LA/LOA
                    ├── Rtd's Enrolamento
                    ├── Resistência de Isolamento
                    ├── Teste de Hipotese
                    ├── Surge Teste
                    └── Teste de Polaridade

                        └── 📊 RESULTADOS DE ENSAIO
                        ├── valor_medido: DECIMAL(15, 4)
                        ├── status_resultado: String ("OK", "NOK", "PENDENTE")
                        ├── observacoes_tecnicas: Text
                        ├── equipamento_utilizado: String
                        └── condicoes_ambiente: (temp, umidade)

                    └── ⚡ ENSAIOS DINÂMICOS
                    ├── VAZIO
                    │   ├── Impedância Trifásica
                    │   ├── Perdas em Vazio
                    │   ├── Corrente de Vazio
                    │   ├── Fator de Potência
                    │   └── Teste de Rotor Bloqueado
                    └── CARGA
                        ├── Curto-Circuito
                        │   ├── Tensão Curto-Circuito
                        │   ├── Perdas Curto-Circuito
                        │   └── Corrente de Curto-Circuito
                        ├── Ensaio de Carga
                        │   ├── Tensão Carga
                        │   ├── Corrente Carga
                        │   ├── Potência Ativa/Reativa
                        │   └── Fator de Potência Carga
                        ├── Curva de Torque
                        └── Temperatura Sob Carga

                        └── 📊 RESULTADOS DE ENSAIO
                        ├── valor_medido: DECIMAL(15, 4)
                        ├── status_resultado: String ("OK", "NOK", "PENDENTE")
                        ├── observacoes_tecnicas: Text
                        ├── equipamento_utilizado: String
                        └── condicoes_ambiente: (temp, umidade)
```

## 📝 __PADRONIZAÇÃO DE NOMES DE CAMPOS__

### __Campos Mantidos (Compatibilidade Total)__

- `TesteContexto` → Manter nome (compatibilidade existente)
- `testes_por_contexto` → Manter nome da tabela (compatibilidade existente)
- `nome_teste` → Interpretar como `nome_ensaio` (sem alterar)
- `procedimento_teste` → Interpretar como `procedimento_ensaio` (sem alterar)
- `resultado_teste` → Interpretar como `resultado_ensaio` (sem alterar)

### __Termos de Negócio Padronizados__

- __"ensaio"__ = teste técnico em equipamentos elétricos
- __"ensaio estático"__ = teste sem energização do equipamento
- __"ensaio dinâmico"__ = teste com energização/funcionamento do equipamento
- __"resultado do ensaio"__ = valor medido + status técnico
- __"procedimento do ensaio"__ = método de execução do teste

## ✅ __VALIDAÇÃO DA PADRONIZAÇÃO ATUAL__

### __✅ Estrutura de Dados Pronta__

- Tabelas principais já implementadas
- Relacionamentos estabelecidos
- Índices de performance otimizados

### __✅ Separação Conceitual Funcionante__

- Grupos de ensaios organizados por tipo (estático/dinâmico)
- Classificação temporal (INICIAL, PARCIAL, FINAL)
- Tipos de resultado definidos (NUMERICO, TEXTO, BOOLEAN)

### __✅ Interface de Usuário Consistente__

- Frontend já utiliza termos técnicos corretos
- Formulários organizados por tipo de ensaio
- Relatórios com terminologia padronizada

## 🎯 __DOCUMENTAÇÃO LOCALIZADA__

O arquivo de documentação foi criado em: __`C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\Orientacoes\HIERARQUIA_SISTEMA_REGISTROOS.md`__

Contendo:

- Hierarquia completa do sistema
- Padronização de "ensaio" como termo principal
- Separação clara entre ensaios estáticos e dinâmicos
- Estrutura de campos atualizada sem modificações

__Conclusão:__ O sistema RegistroOS já possui a padronização desejada internamente, usando consistentemente o termo "ensaio" e separando adequadamente ensaios estáticos de dinâmicos. A documentação agora reflete essa padronização completa sem exigir modificações na estrutura existente.