# Documentação Completa de Variáveis - RegistroOS

Esta documentação consolida todas as variáveis presentes no código (backend Python e frontend TypeScript/React) e no banco de dados, estabelecendo os relacionamentos entre elas.

## 1. Variáveis do Banco de Dados

### Tabela: usuarios
- `id` (Integer, Primary Key)
- `nome_completo` (String, 255)
- `email` (String, 255, Unique)
- `matricula` (String, 100)
- `senha_hash` (String, 255)
- `cargo` (String, 100)
- `setor` (String, 100)
- `departamento` (String, 100)
- `privilege_level` (String, 50)
- `is_approved` (Boolean)
- `trabalha_producao` (Boolean)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)

### Tabela: ordens_servico
- `id` (Integer, Primary Key)
- `os_numero` (String, 50, Unique)
- `status_os` (String, 50)
- `prioridade` (String, 20)
- `id_responsavel_registro` (Integer, Foreign Key -> usuarios.id)
- `descricao_maquina` (Text)
- `setor` (String, 100)
- `departamento` (String, 100)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)
- `criado_por` (Integer, Foreign Key -> usuarios.id)
- `teste_daimer` (Boolean)
- `teste_carga` (Boolean)
- `horas_orcadas` (DECIMAL)
- `horas_previstas` (DECIMAL)
- `horas_reais` (DECIMAL)
- `testes_iniciais_finalizados` (Boolean)
- `testes_parciais_finalizados` (Boolean)
- `testes_finais_finalizados` (Boolean)

### Tabela: apontamentos_detalhados
- `id` (Integer, Primary Key)
- `id_os` (Integer, Foreign Key -> ordens_servico.id)
- `id_usuario` (Integer, Foreign Key -> usuarios.id)
- `id_setor` (Integer)
- `id_atividade` (Integer)
- `data_hora_inicio` (DateTime)
- `data_hora_fim` (DateTime)
- `status_apontamento` (String, 50)
- `foi_retrabalho` (Boolean)
- `causa_retrabalho` (String, 255)
- `observacao_os` (Text)
- `observacoes_gerais` (Text)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)
- `nome_tecnico` (String, 255)
- `cargo_tecnico` (String, 100)
- `setor_tecnico` (String, 100)
- `departamento_tecnico` (String, 100)
- `matricula_tecnico` (String, 100)
- `aprovado_supervisor` (Boolean)
- `data_aprovacao_supervisor` (DateTime)
- `supervisor_aprovacao` (String, 255)

### Tabela: pendencias
- `id` (Integer, Primary Key)
- `numero_os` (String, 50)
- `cliente` (String, 255)
- `data_inicio` (DateTime)
- `id_responsavel_inicio` (Integer, Foreign Key -> usuarios.id)
- `tipo_maquina` (String, 100)
- `descricao_maquina` (Text)
- `descricao_pendencia` (Text)
- `status` (String, 20)
- `prioridade` (String, 20)
- `data_fechamento` (DateTime)
- `id_responsavel_fechamento` (Integer, Foreign Key -> usuarios.id)
- `solucao_aplicada` (Text)
- `observacoes_fechamento` (Text)
- `id_apontamento_origem` (Integer, Foreign Key -> apontamentos_detalhados.id)
- `id_apontamento_fechamento` (Integer, Foreign Key -> apontamentos_detalhados.id)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)

### Tabela: programacoes
- `id` (Integer, Primary Key)
- `id_ordem_servico` (Integer, Foreign Key -> ordens_servico.id)
- `criado_por_id` (Integer, Foreign Key -> usuarios.id)
- `responsavel_id` (Integer, Foreign Key -> usuarios.id)
- `setor` (String, 100)
- `descricao_atividade` (Text)
- `data_inicio` (Date)
- `data_fim` (Date)
- `status` (String, 20)
- `prioridade` (String, 20)
- `observacoes` (Text)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)

### Tabela: resultados_teste
- `id` (Integer, Primary Key)
- `id_apontamento` (Integer, Foreign Key -> apontamentos_detalhados.id)
- `id_teste` (Integer, Foreign Key -> tipos_teste.id)
- `resultado` (String, 20)
- `observacao` (Text)
- `data_registro` (DateTime)

### Tabela: tipos_teste
- `id` (Integer, Primary Key)
- `nome` (String, 255)
- `departamento` (String, 100)
- `setor` (String, 100)
- `tipo_teste` (String, 20)
- `descricao` (Text)
- `ativo` (Boolean)
- `data_criacao` (DateTime)

### Tabela: setores
- `id` (Integer, Primary Key)
- `nome` (String, 100)
- `departamento` (String, 100)
- `descricao` (Text)
- `ativo` (Boolean)
- `permite_apontamento` (Boolean)
- `data_criacao` (DateTime)

### Tabela: departamentos
- `id` (Integer, Primary Key)
- `nome_tipo` (String, 100)
- `descricao` (Text)
- `ativo` (Boolean)
- `data_criacao` (DateTime)

### Tabela: tipos_maquina
- `id` (Integer, Primary Key)
- `nome_tipo` (String, 100)
- `categoria` (String, 50)
- `descricao` (Text)
- `ativo` (Boolean)
- `data_criacao` (DateTime)

### Tabela: causas_retrabalho
- `id` (Integer, Primary Key)
- `codigo` (String, 50)
- `descricao` (String, 255)
- `departamento` (String, 100)
- `ativo` (Boolean)
- `data_criacao` (DateTime)

### Tabela: tipo_atividade
- `id` (Integer, Primary Key)
- `nome_tipo` (String, 255)
- `descricao` (Text)
- `ativo` (Boolean)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)
- `setor` (String, 100)
- `departamento` (String, 100)
- `id_tipo_maquina` (Integer, Foreign Key -> tipos_maquina.id)

### Tabela: descricao_atividade
- `id` (Integer, Primary Key)
- `codigo` (String, 50)
- `descricao` (Text)
- `setor` (String, 100)
- `ativo` (Boolean)
- `data_criacao` (DateTime)
- `data_ultima_atualizacao` (DateTime)

## 2. Variáveis do Backend (Python)

### Constantes e Configurações
- `__version__` = "1.0.0" (em __init__.py)
- `SANKHYA_LOGIN_URL` = "https://api.sankhya.com.br/login"
- `SANKHYA_SERVICE_URL` = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr"
- `SECRET_KEY` (em auth.py)
- `ALGORITHM` = "HS256"
- `ACCESS_TOKEN_EXPIRE_MINUTES` = 60
- `pwd_context` = CryptContext(schemes=["bcrypt"], deprecated="auto")
- `PRIVILEGE_LEVELS` = ["ADMIN", "GESTAO", "PCP", "SUPERVISOR", "USER"]

### Instâncias de Router
- `router` (em pcp_routes.py) = APIRouter(prefix="/pcp", tags=["pcp"])
- `router` (em gestao_routes.py) = APIRouter(prefix="/gestao", tags=["gestao"])
- `router` (em config_routes_simple.py) = APIRouter(prefix="/config", tags=["configuracao"])
- `router` (em config_routes.py) = APIRouter(prefix="/config", tags=["configuracao"])
- `router` (em admin_routes_simple.py) = APIRouter(tags=["admin"])
- `router` (em admin_routes.py) = APIRouter()
- `logger` (em admin_routes.py) = logging.getLogger(__name__)

### Alias
- `ResultadoTesteDetalhado` = ResultadoTeste (em database_models_backup.py)

## 3. Variáveis do Frontend (TypeScript/React)

### Estado (useState)
- `tiposTeste`, `setTiposTeste` (array de TipoTesteData)
- `actividadesLista`, `setActividadesLista` (array de Atividade)
- `tiposMaquinaLista`, `setTiposMaquinaLista` (array de TipoMaquinaData)
- `testesSelecionados`, `setTestesSelecionados` (Record<number, TesteStatus>)
- `selectedTests`, `setSelectedTests` (Record<number, boolean>)
- `searchTeste`, `setSearchTeste` (string)
- `loadingAtividades`, `setLoadingAtividades` (boolean)
- `loadingDescricoes`, `setLoadingDescricoes` (boolean)
- `loadingCausas`, `setLoadingCausas` (boolean)
- `loadingMaquinas`, `setLoadingMaquinas` (boolean)
- `loadingTiposTeste`, `setLoadingTiposTeste` (boolean)
- `descricoesLoaded`, `setDescricoesLoaded` (boolean)
- `causasLoaded`, `setCausasLoaded` (boolean)
- `tiposMaquinaLoaded`, `setTiposMaquinaLoaded` (boolean)

### Constantes CSS
- `inputClassName` = "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
- `labelClassName` = "block text-sm font-medium text-gray-700 mb-2"

### Dados Computados (useMemo)
- `filteredTiposTeste` (array filtrado baseado em searchTeste)
- `TIPOS_MAQUINA_OPTIONS` (array de opções para select)

### Query Client
- `queryClient` = new QueryClient() (em App.tsx)

### Imports
- `availableSectors` (de './features/desenvolvimento/setorMap')

## 4. Relacionamentos entre Variáveis do Código e Banco de Dados

### Frontend -> Database

#### AtividadeFormData (Interface)
- `formData.selMaq` -> `tipos_maquina.nome_tipo`
- `formData.selAtiv` -> `tipo_atividade.id`
- `formData.selDescAtiv` -> `descricao_atividade.descricao`
- `formData.inpRetrabalho` -> `apontamentos_detalhados.foi_retrabalho`
- `formData.selCausaRetrabalho` -> `apontamentos_detalhados.causa_retrabalho` ou `causas_retrabalho.codigo`
- `formData.observacao` -> `apontamentos_detalhados.observacao_os` ou `observacoes_gerais`
- `formData.departamento` -> `usuarios.departamento`
- `formData.setor` -> `usuarios.setor`

#### Estado do Usuário
- `user.departamento` -> `usuarios.departamento`
- `user.setor` -> `usuarios.setor`
- `user.id` -> `usuarios.id`

#### Testes
- `tiposTeste` -> `tipos_teste` (tabela inteira)
- `testesSelecionados` -> `resultados_teste` (quando salvo)

#### Atividades e Máquinas
- `actividadesLista` -> `tipo_atividade`
- `tiposMaquinaLista` -> `tipos_maquina`

#### Causas de Retrabalho
- `formData.causasRetrabalho` -> `causas_retrabalho`

### Backend -> Database

#### Modelos SQLAlchemy
- Classe `Usuario` -> tabela `usuarios`
- Classe `OrdemServico` -> tabela `ordens_servico`
- Classe `ApontamentoDetalhado` -> tabela `apontamentos_detalhados`
- Classe `Pendencia` -> tabela `pendencias`
- Classe `Programacao` -> tabela `programacoes`
- Classe `ResultadoTeste` -> tabela `resultados_teste`
- Classe `TipoTeste` -> tabela `tipos_teste`
- Classe `Setor` -> tabela `setores`
- Classe `Departamento` -> tabela `departamentos`
- Classe `TipoMaquina` -> tabela `tipos_maquina`
- Classe `CausaRetrabalho` -> tabela `causas_retrabalho`
- Classe `TipoAtividade` -> tabela `tipo_atividade`
- Classe `DescricaoAtividade` -> tabela `descricao_atividade`

#### Constantes de Autenticação
- `SECRET_KEY` -> usado para JWT tokens (não armazenado no DB)
- `ALGORITHM` = "HS256" -> algoritmo JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES` = 60 -> expiração do token
- `PRIVILEGE_LEVELS` -> valida `usuarios.privilege_level`

#### URLs de Integração
- `SANKHYA_LOGIN_URL` -> integração externa (não relacionado ao DB interno)
- `SANKHYA_SERVICE_URL` -> integração externa

### Relacionamentos Estruturais

#### Ordens de Serviço
- `ordens_servico.id_responsavel_registro` -> `usuarios.id`
- `ordens_servico.criado_por` -> `usuarios.id`

#### Apontamentos
- `apontamentos_detalhados.id_os` -> `ordens_servico.id`
- `apontamentos_detalhados.id_usuario` -> `usuarios.id`
- `apontamentos_detalhados.id_setor` -> `setores.id`
- `apontamentos_detalhados.id_atividade` -> `tipo_atividade.id`

#### Pendências
- `pendencias.id_responsavel_inicio` -> `usuarios.id`
- `pendencias.id_responsavel_fechamento` -> `usuarios.id`
- `pendencias.id_apontamento_origem` -> `apontamentos_detalhados.id`
- `pendencias.id_apontamento_fechamento` -> `apontamentos_detalhados.id`

#### Programações
- `programacoes.id_ordem_servico` -> `ordens_servico.id`
- `programacoes.criado_por_id` -> `usuarios.id`
- `programacoes.responsavel_id` -> `usuarios.id`

#### Resultados de Teste
- `resultados_teste.id_apontamento` -> `apontamentos_detalhados.id`
- `resultados_teste.id_teste` -> `tipos_teste.id`

#### Tipos de Atividade
- `tipo_atividade.id_tipo_maquina` -> `tipos_maquina.id`

### Campos de Auditoria
- `data_criacao` -> preenchido automaticamente em todas as tabelas
- `data_ultima_atualizacao` -> atualizado automaticamente via triggers

### Campos de Controle
- `ativo` -> controle de registros ativos (setores, departamentos, tipos, etc.)
- `is_approved` -> controle de aprovação de usuários
- `permite_apontamento` -> controle se setor permite apontamentos

---

Esta documentação serve como referência completa para desenvolvimento e manutenção do sistema RegistroOS, facilitando o entendimento dos relacionamentos entre código e banco de dados.