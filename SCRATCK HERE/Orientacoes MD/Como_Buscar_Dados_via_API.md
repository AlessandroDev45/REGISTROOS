# Como Buscar Dados da Base de Dados via API

## Visão Geral

O sistema RegistroOS utiliza uma API RESTful construída com FastAPI para comunicação entre o frontend (React/TypeScript) e o backend (Python/FastAPI). A base de dados é SQLite, e os dados são acessados através de endpoints específicos.

## Estrutura da API

### Base URL
- Backend: `http://localhost:8000`
- Frontend proxy: `http://localhost:3001/api` (através do setupProxy.js)

### Autenticação
A API utiliza cookies HttpOnly para autenticação. Os endpoints requerem um usuário autenticado.

### Endpoints Principais

#### 1. Catálogos
Localizados em `/catalogos/` (frontend usa `/api/catalogos/`)

- **Tipos de Atividade**: `GET /catalogos/tipo-atividade`
  - Retorna lista de tipos de atividade
  - Parâmetro opcional: `setor` (string)

- **Descrições de Atividade**: `GET /catalogos/descricao-atividade`
  - Retorna lista de descrições de atividade
  - Parâmetro opcional: `setor` (string)
  - Filtro: `ativo = true`

- **Tipos de Falha**: `GET /catalogos/tipo-falha-laboratorio`
  - Retorna lista de tipos de falha
  - Parâmetro opcional: `setor` (string)

- **Subtipos de Máquina**: `GET /catalogos/maquina-subtipo`
  - Retorna lista de subtipos de máquina
  - Parâmetro opcional: `setor` (string)

#### 2. Administração
Localizados em `/admin/` (frontend usa `/api/admin/`)

- **Tipos de Máquina**: `GET /admin/tipos-maquina`
  - **Tipos de Teste**: `GET /admin/tipos-teste`
    - Retorna lista de tipos de teste
    - Parâmetro opcional: `machine_type` (string) - filtra por tipo de máquina
    - Filtro: `ativo = true`
    - ✅ **Status**: Funcionando corretamente (corrigido após debug extensivo - ver seção Troubleshooting)
- **Setores**: `GET /admin/setores`
- **Tipos de Teste**: `GET /admin/tipos-teste`
- **Tipos de Atividade**: `GET /admin/tipos-atividade`
- **Tipos de Falha**: `GET /admin/tipos-falha`
- **Causas de Retrabalho**: `GET /admin/causas-retrabalho`
- **Departamentos**: `GET /admin/departamentos`

### CRUD Operations
Cada endpoint administrativo suporta:
- `GET /admin/{recurso}/` - Listar todos
- `GET /admin/{recurso}/{id}` - Obter por ID
- `POST /admin/{recurso}/` - Criar novo
- `PUT /admin/{recurso}/{id}` - Atualizar
- `DELETE /admin/{recurso}/{id}` - Deletar

## Como Usar no Frontend

### 1. Importar Serviços
```typescript
import { descricaoAtividadeService, tipoTesteService } from 'services/adminApi';
```

### 2. Buscar Dados
```typescript
// Buscar descrições de atividade
const descricoes = await descricaoAtividadeService.getDescricoesAtividade();

// Buscar tipos de teste
const tiposTeste = await tipoTesteService.getTiposTeste();
```

### 3. Usar em Componentes React
```typescript
const [descricoes, setDescricoes] = useState([]);

useEffect(() => {
  const fetchData = async () => {
    try {
      const data = await descricaoAtividadeService.getDescricoesAtividade();
      setDescricoes(data);
    } catch (error) {
      console.error('Erro ao buscar dados:', error);
    }
  };
  fetchData();
}, []);
```

## Estrutura dos Dados

### Exemplo: Descrição de Atividade
```json
{
  "id": 1,
  "codigo": "TESTE001",
  "descricao": "INSPECAO VISUAL GERAL",
  "setor": "LABORATORIO DE ENSAIOS ELETRICOS",
  "ativo": true
}
```

### Exemplo: Tipo de Teste
```json
{
  "id": 1,
  "nome": "Teste de Isolamento",
  "departamento": "TRANSFORMADORES",
  "descricao": "Teste de resistência de isolamento",
  "ativo": true
}
```

## Tratamento de Erros

### CORS
- O backend permite origens: `http://localhost:3000`, `http://localhost:3001`, `http://localhost:8000`
- Cookies são enviados automaticamente

### Erros Comuns
- **500 Internal Server Error**: Problema no backend (verificar logs)
- **404 Not Found**: Endpoint incorreto
- **403 Forbidden**: Usuário não autenticado
- **CORS Error**: Origem não permitida

## Debugging

### Verificar Logs do Backend
Os logs mostram:
- Requests recebidos
- Queries executadas
- Erros detalhados

### Verificar Network no Browser
### Testar Filtros de Tipos de Teste
```bash
# Testar filtro por tipo de máquina
curl -X GET "http://localhost:8000/admin/tipos-teste?machine_type=MAQUINA+ESTATICA+CA"

# Verificar se retorna resultados (deve retornar ~36 registros para máquina estática CA)
```

## Troubleshooting Específico

### Problema: Endpoint retorna 0 resultados apesar de haver dados no banco

**Sintomas:**
- Endpoint `/admin/tipos-teste?machine_type=X` retorna lista vazia
- Banco de dados tem registros correspondentes
- Debug mostra que a query não está sendo filtrada corretamente

**Causa Raiz:**
- Coluna existe na tabela do banco mas não está definida no modelo SQLAlchemy
- Exemplo: coluna `tipo_maquina` na tabela `tipos_teste` não estava no modelo `TipoTeste`

**Solução:**
1. Verificar se todas as colunas usadas nos filtros estão definidas no modelo SQLAlchemy
2. Comparar estrutura da tabela com o modelo Python
3. Adicionar colunas faltantes ao modelo:
   ```python
   # Exemplo para adicionar coluna faltante
   tipo_maquina = Column(String(255), nullable=True)
   ```
4. Reiniciar o servidor backend após mudanças nos modelos
---

## 📋 Changelog / Atualizações

### 15/09/2025 - Correção do Endpoint de Tipos de Teste
- ✅ **CORRIGIDO**: Endpoint `/admin/tipos-teste` com filtro `machine_type` agora funciona corretamente
- **Problema**: Retornava 0 resultados apesar de haver 30+ registros no banco
- **Causa**: Coluna `tipo_maquina` existia na tabela mas não estava definida no modelo SQLAlchemy `TipoTeste`
- **Solução**: Adicionada coluna `tipo_maquina = Column(String(255), nullable=True)` ao modelo
- **Impacto**: Frontend agora consegue filtrar tipos de teste por tipo de máquina (Estática CA, Rotativa CA, etc.)
- **Teste**: `GET /admin/tipos-teste?machine_type=MAQUINA+ESTATICA+CA` retorna 36 registros
- **Duração do Debug**: Várias horas de troubleshooting sistemático
- **Lições Aprendidas**: Sempre verificar sincronização entre schema do banco e modelos SQLAlchemy

### Melhorias na Documentação
- Adicionada seção específica de Troubleshooting para problemas comuns
- Incluído exemplo de teste para filtros de tipos de teste
- Reforçado aviso sobre reinicialização do backend após mudanças nos modelos
5. Testar o endpoint novamente

**Como Evitar:**
- Sempre manter modelos SQLAlchemy sincronizados com o schema do banco
- Executar migrations quando alterar estrutura de tabelas
- Testar endpoints após mudanças nos modelos

### Problema: Campo 'ativo' não aparece nas respostas

**Sintomas:**
- Respostas da API não incluem o campo `ativo`
- Frontend não consegue filtrar registros ativos/inativos

**Solução:**
- Verificar se o campo `ativo` está sendo incluído na resposta do endpoint
- Adicionar o campo na lista de campos retornados:
  ```python
  return [{"id": item.id, "nome": item.nome, "ativo": item.ativo, ...} for item in items]
  ```

## Considerações Finais
- Abra DevTools > Network
- Verifique requests para `/api/*`
- Status codes e responses

- **CRÍTICO**: Sempre reinicie o backend após mudanças nos modelos SQLAlchemy
- Verifique se todas as colunas do banco estão definidas nos modelos Python
- Execute migrations quando alterar estrutura de tabelas
- Teste todos os endpoints após mudanças nos modelos
- Mantenha documentação atualizada com status dos endpoints
- Use os serviços TypeScript para manter consistência no frontend
- Os dados são filtrados por `ativo = true` onde aplicável
### Testar Endpoints Diretamente
```bash
curl -X GET "http://localhost:8000/catalogos/descricao-atividade" \
  -H "Cookie: session=your_session_cookie"
```

## Considerações Finais

- Sempre reinicie o backend após mudanças nos modelos
- Verifique a conectividade entre frontend e backend
- Use os serviços TypeScript para manter consistência
- Os dados são filtrados por `ativo = true` onde aplicável