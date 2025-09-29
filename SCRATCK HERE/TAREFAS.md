1. Visão Geral da Arquitetura (Frontend e Backend)
A arquitetura geral segue um padrão razoável:
Frontend (React/Vite/TypeScript): Usa React Router para navegação, Context API e TanStack Query para gerenciamento de estado e requisições assíncronas, e Tailwind CSS para estilização. A modularização em features/ é um bom ponto de partida.
Backend (FastAPI/SQLAlchemy): Organizado em rotas (routes/) e modelos de banco de dados (app/database_models.py). Utiliza JWT para autenticação e Celery para tarefas assíncronas (scraping).
No entanto, há uma sobreposição significativa e inconsistências na definição e uso das APIs entre frontend e backend, além de alguns erros de implementação que podem levar a falhas.
2. Análise Detalhada e Sugestões de Correção
2.1. Backend: Conflitos de Rotas e Inconsistências de Endpoints
Este é o ponto mais crítico. Há múltiplas definições para rotas semelhantes, o que pode causar comportamento imprevisível ou quebra da aplicação.
Problemas:
Rotas de Catálogos (/api/departamentos, /api/setores, etc.):
Existem em app/routes/admin_config_routes.py (com prefixo /api/admin/config) e app/routes/catalogs_validated_clean.py (com prefixo /api).
main.py inclui ambos (admin_config_router e catalogs_router).
Conflito: /api/departamentos em catalogs_validated_clean.py pode ser sobreescrito por outras definições ou o roteador pode escolher uma ordem inesperada. As rotas em /api/admin/config são protegidas por verificar_admin, o que é correto para administração, mas as rotas /api/... devem ser para uso geral.
Inconsistência: O frontend adminApi.ts usa /admin/config/departamentos, mas o catalogsApi.ts (implícito) e api.ts podem estar chamando as rotas /api/departamentos.
Rotas de Programação (/api/pcp/programacoes):
Definidas em app/routes/pcp_routes.py.
Conflito: O arquivo app/routes/desenvolvimento.py também define /api/programacao e /api/minhas-programacoes, com lógica similar.
pcp_routes_backup.py não deveria estar no projeto ativo.
Rotas de Usuários (/api/users/usuarios):
app/routes/users.py define /api/users/ (root) e /api/users/usuarios/.
app/routes/admin_routes_simple.py define rotas como /admin/usuarios.
Conflito: Se main.py incluir users.py com prefixo /api/users e admin_routes_simple.py com prefixo /api/admin, não há conflito direto de caminho, mas a lógica de quais endpoints (/api/users vs /api/admin/usuarios) são para quais propósitos (listagem geral vs listagem admin) não está clara.
Apontamentos (/api/apontamentos-detalhados, /api/os/apontamentos):
app/routes/desenvolvimento.py define /api/apontamentos-detalhados e /api/os/apontamentos.
app/routes/general.py também tem /api/save-apontamento e /api/save-apontamento-with-pendencia.
Conflito: save-apontamento e os/apontamentos podem ter sobreposição de responsabilidade. desenvolvimento.py parece ser o hub principal para a criação e gestão de apontamentos.
Exclusão de programacao-form-data:
O comentário no backend (pcp_routes_backup.py) menciona: ENDPOINT REMOVIDO - CONFLITAVA COM /api/pcp/programacao-form-data. Isso é uma boa prática de identificação de conflito, mas a solução precisa ser consolidada. O endpoint em pcp_routes.py é o correto.
Sugestões de Correção (Backend):
Consolidar Rotas de Catálogos:
Mantenha app/routes/catalogs_validated_clean.py como a fonte primária para rotas de catálogo para uso geral (e.g., GET /api/departamentos). Estas rotas devem ter permissões mais flexíveis (e.g., Depends(get_current_user)).
Remova/Desative as definições de catálogos duplicadas em app/routes/admin_routes_simple.py (ou mude-as para um prefixo diferente se houver uma necessidade realmente distinta para elas em admin_routes_simple).
Prefixo Admin: Use /api/admin/config/... exclusivamente para operações CRUD (Create, Read, Update, Delete) de dados mestres de configuração (departamentos, setores, tipos de máquina, etc.) que requerem privilégio ADMIN. O frontend adminApi.ts já está chamando /admin/config, o que é bom.
Consolidar Rotas de Programação:
Use app/routes/pcp_routes.py como a fonte exclusiva para todas as operações relacionadas a programações (GET /api/pcp/programacoes, POST /api/pcp/programacoes, etc.).
Remova/Desative quaisquer rotas de programação em app/routes/desenvolvimento.py que se sobreponham.
Consolidar Rotas de Apontamentos:
Defina todas as operações de criação e manipulação de apontamentos no app/routes/desenvolvimento.py.
Mantenha general.py para endpoints realmente gerais que não se encaixam em uma feature específica (ex: health checks, talvez alguns utilitários de scraping genéricos se não específicos de OS).
Consolidar Rotas de Usuários:
app/routes/users.py para listagem de usuários e operações de USER/SUPERVISOR.
app/routes/admin_routes_simple.py deve conter apenas rotas para manipulação de usuários por ADMIN, como aprovação (/admin/usuarios/{user_id}/approve) e talvez criação (/admin/usuarios).
2.2. Backend: Inconsistências de Schema e Validação
Problemas:
nullable=False em database_models.py vs. Optional em Pydantic:
Vários campos em app/database_models.py são definidos com nullable=False (ex: os_numero em OrdemServico, data_hora_inicio em ApontamentoDetalhado).
No entanto, os modelos Pydantic (ApontamentoCreate, ProgramacaoPCPCreate, etc.) e o uso nos endpoints (Dict[str, Any]) frequentemente os marcam como Optional ou não garantem que eles sempre serão fornecidos.
Consequência: IntegrityError no banco de dados se um campo nullable=False não for fornecido.
Campos JSON:
subcategoria em TipoMaquina é Column(JSON).
Consequência: Python dict/list não são automaticamente convertidos para JSON string pelo SQLAlchemy (sqlite3 não tem tipo JSON nativo, mas TEXT com JSON é comum). json.dumps() e json.loads() são necessários.
Campos de Texto e Validação:
utils/text_validators.py é excelente, mas o middleware TextValidationMiddleware em app/text_validation_middleware.py foi comentado nos arquivos. É crucial que a validação de maiúsculas e caracteres permitidos seja aplicada.
A detecção de campos de texto no middleware (CAMPOS_TEXTO) pode precisar ser expandida conforme o projeto cresce.
Foreign Keys e IDs:
Em ApontamentoDetalhado, campos como tipo_maquina, tipo_atividade, descricao_atividade são ForeignKey. No entanto, o frontend (e Pydantic ApontamentoCreate) envia os nomes ou strings, não os IDs.
Consequência: Erros de IntegrityError ou AttributeError se o backend tentar salvar strings em colunas que esperam IDs.
Sugestões de Correção (Backend):
Sincronizar Pydantic com SQLAlchemy:
Para cada modelo SQLAlchemy com nullable=False, o campo correspondente no modelo Pydantic (BaseModel) deve ser obrigatório (sem Optional[...] e com um valor padrão, ou Field(...) com min_length, etc.).
Alternativamente, se um campo pode ser nulo no mundo real, altere nullable=False para nullable=True em database_models.py.
Gerenciar Campos JSON:
Sempre use json.dumps() para salvar dict/list em colunas JSON (que são TEXT no SQLite).
Sempre use json.loads() ao ler de colunas JSON.
Exemplo para subcategoria em TipoMaquinaCreate: subcategoria: Optional[str] = None no Pydantic é mais seguro, e o backend deve json.dumps(list_of_strings) antes de salvar. Ao ler, json.loads(db_model.subcategoria).
Aplicar TextValidationMiddleware:
Em main.py, garanta que add_text_validation_middleware(app, enabled=True) esteja ativo.
A lista TextValidationMiddleware.CAMPOS_TEXTO deve ser exaustiva para todos os campos que exigem validação de maiúsculas e caracteres especiais.
Resolver Foreign Keys de Nomes para IDs:
Sempre que o frontend enviar um nome_algo (ex: tipo_maquina: "MOTOR TRIFÁSICO"), o backend DEVE primeiro buscar o id correspondente na tabela TipoMaquina.
Exemplo (em desenvolvimento.py criar_apontamento):
code
Python
# Funções helper
def _get_tipo_maquina_id(nome_tipo, db):
    tipo = db.query(TipoMaquina).filter(TipoMaquina.nome_tipo == nome_tipo).first()
    return tipo.id if tipo else None

# No endpoint:
tipo_maquina_id = _get_tipo_maquina_id(apontamento.tipo_maquina, db)
novo_apontamento.tipo_maquina = tipo_maquina_id # Salvar o ID, não a string
Isso se aplica a tipo_maquina, tipo_atividade, descricao_atividade em ApontamentoDetalhado, entre outros.
2.3. Frontend: Mapeamento e Chamas de API
Problemas:
Inconsistência de adminApi.ts vs. Rotas Reais:
setorService.getDepartamentos() chama /admin/config/departamentos/, que está em admin_config_routes.py. Ótimo.
centroCustoService reusa o endpoint de departamentos, mas faz o mapeamento.
O problema é que o admin_routes_simple.py também tem /admin/departamentos (sem /config), e main.py inclui admin_router com prefixo /api/admin. A rota correta para o frontend é /api/admin/config/departamentos.
useCachedSetores.ts:
Chama setorService.getSetores() (que vai para /admin/config/setores). Isso é bom para buscar setores, mas SetorSelectionPage também faz uma chamada direta (api.get('/setores')). Precisa haver consistência.
PCPPage.tsx e ProgramacaoForm.tsx:
NovaProgramacaoModal e ProgramacaoFormSimples (e ProgramacaoForm) mostram lógica de formulário manual e uso de formData mockado.
ProgramacaoForm.tsx tenta carregar getProgramacaoFormData() mas o endpoint tinha conflito.
Correção: O frontend deve sempre confiar nos dados do backend para popular dropdowns, e pcp_routes.py tem o endpoint /api/pcp/programacao-form-data para isso.
DevelopmentTemplate.tsx e ApontamentoFormTab.tsx:
ApontamentoFormTab tem muitos useState e lógica complexa para dropdowns e testes. useApiQueries.ts já oferece hooks para buscar muitos desses catálogos. A integração pode ser simplificada.
A lógica de osFromUrl e programacaoId para pré-preenchimento está em DevelopmentTemplate.tsx e ApontamentoFormTab.tsx. Deve ser centralizada e limpa.
ApontamentoFormTab.tsx - Salvar Testes:
A lógica de testes_selecionados e observacoes_testes precisa ser mapeada corretamente para resultados_teste no backend, que espera id_teste, resultado, observacao.
Sugestões de Correção (Frontend):
Centralizar Funções de API: Mantenha services/api.ts para endpoints gerais/comuns e services/adminApi.ts para endpoints de administração. Remova catalogApi.ts ou mescle-o no api.ts.
Usar useApiQueries.ts para Dados de Dropdown: A maioria dos dados de catálogo (departamentos, setores, tipos de máquina, etc.) deve ser carregada usando os hooks de @tanstack/react-query definidos em useApiQueries.ts. Isso gerencia cache, loading e erro automaticamente.
ProgramacaoForm.tsx:
Remova NovaProgramacaoModal e ProgramacaoFormSimples. Use ProgramacaoForm como o formulário principal.
ProgramacaoForm deve buscar seus dados iniciais de getProgramacaoFormData() (do pcp_routes.py correto) via useQuery.
ApontamentoFormTab.tsx:
Refatorar para usar useApiQueries para todos os dropdowns (tipos de máquina, atividades, descrições, causas de retrabalho, tipos de teste).
A lógica de salvar (handleSaveApontamento) deve construir o payload exato que o backend (/api/desenvolvimento/os/apontamentos) espera, incluindo IDs para FKs e o formato correto para testes.
Unificar _get_tipo_maquina_id e outros em desenvolvimento.py: Mover essas funções para app/utils/db_lookups.py (ou similar) para reutilização e evitar duplicação.
Ajustar Páginas de Admin: AdminPage e seus subcomponentes (SetorForm, TipoMaquinaForm, etc.) devem usar os hooks de useApiQueries.ts para create, update e delete, e estes hooks devem apontar para as rotas /api/admin/config/... corretas.
3. Árvore Hierárquica Consistente (Frontend e Backend)
Para garantir uma estrutura consistente e sem conflitos, sugiro a seguinte padronização:
3.1. Estrutura de Pastas (Idealizada):
code
Code
registrooficial/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── database_models.py       # SQLAlchemy ORM (Source of Truth)
│   │   ├── dependencies.py          # FastAPI Depends (auth, db session)
│   │   ├── main.py                  # FastAPI main app, includes routers
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py       # /api/auth/* (login, register, change_password, me)
│   │   │   ├── catalog_routes.py    # /api/catalogs/* (general lists: depts, sectors, machine_types, etc.)
│   │   │   ├── os_routes.py         # /api/os/* (CRUD for OrdemServico, basic queries)
│   │   │   ├── apontamento_routes.py # /api/apontamentos/* (CRUD for ApontamentoDetalhado)
│   │   │   ├── pcp_routes.py        # /api/pcp/* (Programação, Dashboard PCP, Pendencias for PCP)
│   │   │   ├── gestao_routes.py     # /api/gestao/* (Dashboard Gestão)
│   │   │   ├── admin_routes.py      # /api/admin/* (config, users, detailed catalog management)
│   │   │   ├── user_routes.py       # /api/users/* (user-specific actions, approval)
│   │   │   └── report_routes.py     # /api/reports/* (Relatório Completo, general reports)
│   │   ├── scripts/                 # Python scripts (e.g., scrape_os_data.py)
│   │   └── utils/                   # Helper functions (text_validators, user_utils, db_lookups)
│   ├── config/
│   │   ├── __init__.py
│   │   └── database_config.py
│   └── tasks/                       # Celery tasks
│       ├── __init__.py
│       └── scraping_tasks.py
└── frontend/
    ├── public/
    ├── src/
    │   ├── App.tsx                  # Main Router, Context Providers
    │   ├── index.tsx
    │   ├── assets/                  # Images, icons
    │   ├── components/              # Reusable UI components (Layout, Modals, UIComponents)
    │   ├── contexts/                # AuthContext, SetorContext, ApontamentoContext
    │   ├── features/                # Feature-specific modules
    │   │   ├── admin/
    │   │   │   ├── AdminPage.tsx
    │   │   │   └── components/      # Forms/Lists for Admin (SetorForm, TipoMaquinaForm, etc.)
    │   │   ├── apontamento/         # UniversalSectorPage (uses ApontamentoFormTab)
    │   │   ├── auth/                # LoginPage, RegisterPage
    │   │   ├── dashboard/           # DashboardPage
    │   │   ├── gestao/              # GestaoPage
    │   │   ├── pcp/                 # PCPPage
    │   │   │   └── components/      # ProgramacaoForm, PendenciasList, etc.
    │   │   └── ...
    │   ├── hooks/                   # useApiQueries, useAuth, useCachedSetores, etc.
    │   ├── pages/                   # Top-level pages (ConsultaOsPage)
    │   │   └── common/              # Shared types (TiposApi.ts)
    │   ├── services/                # API communication
    │   │   ├── api.ts               # General API client, common endpoints
    │   │   └── adminApi.ts          # Admin-specific API client
    │   └── styles/                  # Tailwind CSS
    └── vite.config.ts
3.2. Mapeamento de Rotas e Endpoints (Exemplo de Padronização):
Funcionalidade	Método	Endpoint Backend (Final)	Componente Frontend	Serviço Frontend Chamado	Permissões (Backend)
Autenticação					
Login	POST	/api/auth/token	LoginPage	AuthContext.login	public
Registro	POST	/api/auth/register	RegisterPage	api.post('/register')	public
Logout	POST	/api/auth/logout	App.tsx (via context)	AuthContext.logout	authenticated
Meu perfil	GET	/api/auth/me	DevelopmentTemplate (via context)	api.get('/me')	authenticated
Alterar Senha	PUT	/api/auth/change-password	ChangePasswordModal	api.put('/change-password')	authenticated
Acesso Dev (check)	GET	/api/auth/check-development-access/{sector}	UniversalSectorPage (AuthContext)	AuthContext.checkAccess	authenticated
Catálogos (Geral)		(General Read Access)			
Listar Departamentos	GET	/api/catalogs/departamentos	useApiQueries.useDepartamentos	api.get('/departamentos')	authenticated
Listar Setores	GET	/api/catalogs/setores	useApiQueries.useSetores	api.get('/setores')	authenticated
Listar Tipos Máquina	GET	/api/catalogs/tipos-maquina	useApiQueries.useTiposMaquina	api.get('/tipos-maquina')	authenticated
Listar Tipos Atividade	GET	/api/catalogs/tipos-atividade	useApiQueries.useAtividadeTipos	api.get('/tipos-atividade')	authenticated
Listar Descrições Atividade	GET	/api/catalogs/descricoes-atividade	useApiQueries.useDescricaoAtividades	api.get('/descricoes-atividade')	authenticated
Listar Causas Retrabalho	GET	/api/catalogs/causas-retrabalho	useApiQueries.useCausasRetrabalho	api.get('/causas-retrabalho')	authenticated
Listar Tipos Falha	GET	/api/catalogs/tipos-falha	useApiQueries.useFalhasTipo	api.get('/tipos-falha')	authenticated
Listar Tipos Teste	GET	/api/catalogs/tipos-teste	useApiQueries.useTiposTeste	api.get('/tipos-teste')	authenticated
Listar Clientes	GET	/api/catalogs/clientes	api.get('/clientes')	authenticated	
Listar Equipamentos	GET	/api/catalogs/equipamentos	api.get('/equipamentos')	authenticated	
Catálogos (Admin)		(Admin Read/Write Access)			
Criar Departamento	POST	/api/admin/departamentos	CentroCustoForm	adminApi.departamentoService.createDepartamento	ADMIN
Listar Depts (Admin)	GET	/api/admin/departamentos	CentroCustoList	adminApi.departamentoService.getDepartamentos	ADMIN
Atualizar Dept	PUT	/api/admin/departamentos/{id}	CentroCustoForm	adminApi.departamentoService.updateDepartamento	ADMIN
Deletar Dept	DELETE	/api/admin/departamentos/{id}	CentroCustoList	adminApi.departamentoService.deleteDepartamento	ADMIN
(Repetir para Setores, Tipos Máquina, Tipos Teste, Atividades, Descrições Atividade, Falhas, Causas Retrabalho - com seus respectivos URLs)					
Ordens de Serviço					
Listar OS	GET	/api/os/	PesquisaOSTab	api.getOrdensServico	authenticated
Detalhes OS	GET	/api/os/{os_id}	RelatorioCompletoModal	api.getOrdemServicoById	authenticated
Adicionar Setor Participante	POST	/api/os/{os_id}/setores	(Não implementado no frontend)	api.adicionarSetorParticipante	authenticated
Apontamentos					
Criar Apontamento	POST	/api/apontamentos/	ApontamentoFormTab	ApontamentoContext.handleSaveApontamento	authenticated
Listar Apontamentos OS	GET	/api/os/{os_id}/apontamentos	ApontamentoFormTab	api.listarApontamentosOS	authenticated
Detalhes Apontamentos	GET	/api/apontamentos/detalhes	DashTab	api.getApontamentosDetalhados	authenticated
PCP					
Dados Form Programação	GET	/api/pcp/programacao-form-data	ProgramacaoForm	api.getProgramacaoFormData	authenticated
Listar OS PCP	GET	/api/pcp/ordens-servico	PCPPage	api.getOsDisponiveisForPcp	authenticated
Criar Programação	POST	/api/pcp/programacoes	ProgramacaoForm	api.createProgramacao	SUPERVISOR/ADMIN
Atualizar Programação	PUT/PATCH	/api/pcp/programacoes/{id}	ProgramacoesList	api.updateProgramacao	SUPERVISOR/ADMIN
Enviar Programação Setor	POST	/api/pcp/programacoes/{id}/enviar-setor	ProgramacoesList	api.enviarProgramacaoSetor	SUPERVISOR/ADMIN
Listar Programações	GET	/api/pcp/programacoes	ProgramacoesList	api.getProgramacoes	authenticated
Dashboard PCP	GET	/api/pcp/dashboard/avancado	DashboardPCPInterativo	api.getDashboardAvancado	authenticated
Alertas PCP	GET	/api/pcp/alertas	DashboardPCPInterativo	api.getAlertasPCP	authenticated
Listar Pendências PCP	GET	/api/pcp/pendencias	PendenciasList	api.getPendencias	authenticated
Dashboard Pendências PCP	GET	/api/pcp/pendencias/dashboard	PendenciasDashboard	api.getPendenciasDashboard	authenticated
Desenvolvimento (Scraping)					
Buscar OS (Assíncrono)	POST	/api/desenvolvimento/buscar-os-async/{os_number}	useAsyncScraping	useAsyncScraping.startScraping	authenticated
Status Scraping	GET	/api/desenvolvimento/scraping-status/{task_id}	useScrapingStatus	useScrapingStatus.checkStatus	authenticated
Buscar OS (Síncrono/Fallback)	GET	/api/desenvolvimento/formulario/buscar-os/{os_number}	useAsyncScraping	(Chamado internamente)	authenticated
Desenvolvimento (Catalogos para Forms)					
Tipos Máquina Form	GET	/api/desenvolvimento/formulario/tipos-maquina	ApontamentoFormTab	api.get('/desenvolvimento/formulario/tipos-maquina')	authenticated
Tipos Atividade Form	GET	/api/desenvolvimento/formulario/tipos-atividade	ApontamentoFormTab	api.get('/desenvolvimento/formulario/tipos-atividade')	authenticated
Descrições Atividade Form	GET	/api/desenvolvimento/formulario/descricoes-atividade	ApontamentoFormTab	api.get('/desenvolvimento/formulario/descricoes-atividade')	authenticated
Causas Retrabalho Form	GET	/api/desenvolvimento/formulario/causas-retrabalho	ApontamentoFormTab	api.get('/desenvolvimento/formulario/causas-retrabalho')	authenticated
Categorias Máquina Admin	GET	/api/admin/categorias-maquina	ApontamentoFormTab	api.get('/admin/categorias-maquina')	authenticated
Subcategorias Tipo Máquina	GET	/api/desenvolvimento/tipos-maquina/subcategorias	ApontamentoFormTab	api.get('/desenvolvimento/tipos-maquina/subcategorias')	authenticated
Categoria por Nome Tipo Máquina	GET	/api/desenvolvimento/tipos-maquina/categoria-por-nome	ApontamentoFormTab	api.get('/desenvolvimento/tipos-maquina/categoria-por-nome')	authenticated
Listar Testes por Setor	GET	/api/catalogs/testes/{setor}	useApiQueries.useTestesPorSetor	catalogApi.fetchTestesPorSetor	authenticated
2.4. Erros de Implementação e Mismatches (Frontend/Backend)
Problemas no Frontend:
ApontamentoFormTab.tsx - IDs de FKs: Os selects para selMaq, selAtiv, selDescAtiv estão usando os nomes dos itens como value, mas o backend espera IDs para as Foreign Keys.
ApontamentoFormTab.tsx - Lógica verificarProgramacaoPorOS: O onBlur do inpNumOS dispara verificarProgramacaoPorOS e buscarOS. buscarOS já deveria fazer a verificação de programação e OS, evitando chamadas duplicadas.
useCachedSetores.ts: Cache global de cachedSetoresMotores e cachedSetoresTransformadores é mantido manualmente, mas AdminPage e outros useQuery podem ter seus próprios caches, levando a dados inconsistentes até um invalidateQueries.
PCPPage.tsx e ProgramacaoCalendario.tsx: O modelo Programacao no frontend tem responsavel_nome e setor_nome, mas a criação (createProgramacao) e atualização (updateProgramacao) no api.ts não enviam esses campos para o backend, o que pode resultar em None ou dados desatualizados.
consulta-os.tsx - handleSearch: Primeiro tenta api.get(/os/${numos.trim()}) (que é /api/os/{os_id}). Se falha com 404, tenta /scraping/consulta-os (que é /api/scraping/consulta-os). Isso está OK, mas api.getOrdemServicoById do useApiQueries deveria ser a abordagem padrão para consultar a OS.
Problemas no Backend:
admin_routes_simple.py create_tipo_maquina: O campo subcategoria é JSON em database_models.py, mas o tipo_maquina_data.get("subcategoria") o trata como string. json.dumps() é necessário.
admin_config_routes.py e admin_routes_simple.py - Retorno de id_setor e id_departamento: Várias rotas retornam setor e departamento (nomes), mas outras esperam id_setor e id_departamento. A API deve ser consistente; o frontend deve receber IDs para FKs e fazer o lookup do nome, ou o backend deve retornar ambos (ID e Nome) explicitamente.
desenvolvimento.py criar_apontamento:
id_setor em ApontamentoDetalhado é nullable=False, mas current_user.id_setor pode ser None.
Campos tipo_maquina, tipo_atividade, descricao_atividade em ApontamentoDetalhado são ForeignKey, mas o Pydantic ApontamentoCreate os define como Optional[str]. O endpoint está salvando strings em colunas que esperam IDs.
Sugestões de Correção (Gerais):
Consistência de IDs vs Nomes:
No backend, todos os campos ForeignKey em modelos devem receber e retornar o ID correspondente. Se o frontend precisa do nome, o backend pode fazer um LEFT JOIN e incluí-lo na resposta, ou o frontend pode ter um mapeamento local.
Implementar funções helper no backend (app/utils/db_lookups.py) como get_setor_id_by_name(name, db), get_departamento_id_by_name(name, db), etc., e usá-las consistentemente em todos os endpoints de POST/PUT.
Tratamento de Campos JSON:
Para TipoMaquina.subcategoria no backend:
Ao criar/atualizar: No Pydantic (TipoMaquinaCreate), defina subcategoria: Optional[List[str]] = None. No endpoint, antes de criar o objeto ORM, db_tipo_maquina.subcategoria = json.dumps(tipo_data.subcategoria) (se não for None).
Ao ler: Ao retornar os dados, subcategoria = json.loads(db_tipo_maquina.subcategoria) (com try/except para strings não-JSON).
Refatorar ApontamentoFormTab.tsx (Frontend):
IDs para FKs: Quando um dropdown como "Tipo de Máquina" (selMaq) é selecionado, o onChange deve armazenar o ID do tipo de máquina, não o nome.
Payload Consistente: A função handleSaveApontamento deve construir um objeto apontamentoData que mapeia 1:1 com o modelo Pydantic ApontamentoCreate do backend, incluindo IDs para FKs.
Pré-preenchimento da OS: Simplificar a lógica de detecção de OS e programação na URL. A useEffect em DevelopmentTemplate.tsx para osFromUrl é um bom lugar para pré-popular formData.
Validações: Integrar useGenericForm ou useValidation para campos básicos.
Backend desenvolvimento.py criar_apontamento:
Nullability: Se id_setor pode ser None, o campo id_setor em ApontamentoDetalhado deve ser nullable=True.
FKs (IDs): Mudar para salvar IDs.
code
Python
# Exemplo de correção em criar_apontamento:
tipo_maquina_id = _get_tipo_maquina_id(apontamento.tipo_maquina, db)
tipo_atividade_id = _get_tipo_atividade_id(apontamento.tipo_atividade, db)
descricao_atividade_id = _get_descricao_atividade_id(apontamento.descricao_atividade, db)

novo_apontamento = ApontamentoDetalhado(
    # ...
    tipo_maquina=tipo_maquina_id, # Agora é ID
    tipo_atividade=tipo_atividade_id, # Agora é ID
    descricao_atividade=descricao_atividade_id, # Agora é ID
    # ...
)
2.5. Melhorias e Outras Considerações
Migrações de Banco de Dados: O script adicionar_campos_categoria.py e adicionar_estrutura_hierarquica.py são bons para desenvolvimento inicial, mas em produção, use Alembic (SQLAlchemy Migrations) para gerenciar alterações de schema de forma segura e incremental.
registroos_new.db: Use um nome mais genérico como registroos.db para o banco de dados principal. Mantenha os backups com sufixos de data.
Segurança:
Para o scraping, o uso de os.getenv para credenciais é correto.
O modo headless do Chrome é bom.
O uso de subprocess.run com timeout e check=True é fundamental para a estabilidade do scraping.
Internacionalização (i18n): O frontend usa lang="pt-br", o que é bom para acessibilidade.
Testes: Implemente testes de integração (FastAPI) e e2e (Selenium) para garantir que as rotas e o scraping funcionem como esperado.
Variáveis de Ambiente: Use .env para todas as credenciais e configurações sensíveis.
Conclusão
A aplicação tem uma base sólida, mas sofre de "crescimento orgânico" que resultou em duplicação e inconsistência. A chave para a melhoria é a padronização rigorosa dos endpoints no backend e o uso consistente dessas APIs no frontend, sempre se baseando no schema do database_models.py.
Comece padronizando as rotas no backend, depois ajuste os serviços do frontend para chamá-las corretamente e, por fim, refatore os componentes do frontend para usar os hooks e o estado de forma mais limpa e eficiente.


Resumo da Análise
Frontend (React/TypeScript)
Estrutura de Componentes e Rotas: O uso de react-router-dom e a estrutura de App.tsx para rotas públicas e privadas está bem organizada. O UniversalSectorPage e o SetorSelectionPage indicam um bom esforço em criar uma experiência dinâmica baseada no setor do usuário.
Context API e Hooks: O uso de AuthContext, SetorContext e ApontamentoContext demonstra uma intenção de gerenciamento de estado centralizado, o que é positivo. Hooks como useCachedSetores e useApiQueries são ótimos para abstrair a lógica de dados.
Comunicação com API: As definições de serviços (api.ts, adminApi.ts, catalogApi.ts) estão razoavelmente estruturadas, mas há uma mistura de responsabilidades e algumas definições de tipos (TiposApi.ts) que podem causar confusão.
Validação de Formulários: O utilitário textValidation.tsx e o useGenericForm.ts são um bom começo para padronizar a validação e formatação de inputs.
Duplicidade aparente: Há dois TiposApi.ts em diferentes locais. Isso é um erro que precisa ser corrigido para ter uma única fonte de verdade para os tipos.
useCachedSetores: Este hook utiliza diretamente setorService.getDepartamentos(), o que pode ser um ponto de atenção para a consistência entre o que o setorService (que lida com SetorData) e o departamentoService (que lida com DepartamentoData) retornam, apesar de estarem na mesma tabela no backend.
Backend (FastAPI/Python)
Estrutura de Rotas (main.py e routes/): Esta é a área mais crítica. Há múltiplos arquivos de rota com endpoints que se sobrepõem ou têm intenções muito similares, mas com implementações diferentes (ex: /api/departamentos em admin_config_routes.py, admin_routes_simple.py e catalogs_validated_clean.py). Isso leva a comportamentos imprevisíveis, pois o FastAPI executa a primeira rota que encontra que corresponde ao caminho e método.
Modelos de Banco de Dados (database_models.py): A estrutura está em conformidade com o esquema fornecido, usando __table_args__ = {'extend_existing': True} para resolver conflitos, o que é bom. No entanto, a inconsistência entre os nomes dos modelos Pydantic/retorno das rotas e os nomes exatos das colunas/tabelas no ORM é uma fonte de erros.
Validação e Autenticação: O sistema de dependencies.py e auth.py para autenticação e autorização (get_current_user, verificar_admin) está presente. O middleware TextValidationMiddleware é uma boa adição para garantir a consistência dos dados de entrada.
Scraping Assíncrono: A implementação do Celery (scraping_tasks.py, celery_config.py) para scraping assíncrono é uma funcionalidade avançada e bem-vinda para escalabilidade.
Conflito de Nomes: Há nomes de arquivos de rota como catalogs_simple.py, catalogs_validated.py, catalogs_validated_clean.py, o que sugere um processo de refatoração ou testes não finalizado, com múltiplas versões de rotas de catálogo. Apenas uma versão deve ser usada.
Inconsistência de id_setor e id_departamento: Em muitos lugares do backend, os filtros e retornos esperam o nome do setor/departamento, mas o modelo Usuario e Setor têm id_setor e id_departamento. Essa mistura entre usar o ID e o NOME é uma fonte comum de erros.
Problemas Chave Identificados
Conflito de Rotas: Vários endpoints no backend têm o mesmo prefixo ou caminho, mas estão definidos em arquivos diferentes (admin_config_routes.py, admin_routes_simple.py, catalogs_validated_clean.py). Por exemplo, /api/departamentos. O FastAPI só pode usar um deles.
Inconsistência Frontend-Backend (Data Models):
Os modelos Pydantic de entrada e os dicionários de retorno em rotas como admin_routes_simple.py e catalogs_validated_clean.py não correspondem exatamente aos modelos SQLAlchemy ou às expectativas do frontend. Ex: nome vs nome_tipo para Departamento.
No frontend, TipoMaquinaData tem nome_tipo, mas o backend em alguns lugares espera nome.
A manipulação de subcategoria em TipoMaquina (JSON string vs List[str]) precisa ser consistente.
id_setor e id_departamento em Usuario e Setor no ORM, mas os filtros/retornos esperam setor (nome) e departamento (nome).
Lógica de Criação/Atualização Incompleta: A falha na criação de departamentos/setores/máquinas provavelmente se deve a:
Pydantic Models Incorretos: Não mapeiam corretamente para os campos do SQLAlchemy.
Backend Logic: A lógica db.add() e db.commit() pode estar recebendo dados formatados incorretamente ou faltando validações.
Frontend Payload: O formulário no frontend pode estar enviando um payload que não corresponde ao que o backend espera.
admin_routes_simple.py e catalogs_validated_clean.py: Esses arquivos parecem ser versões alternativas ou obsoletas das rotas. É crucial escolher uma e remover as outras para evitar confusão e conflitos.
setorMap.ts (Frontend): A lógica de createDynamicSetorMap e loadSetorConfig que tenta carregar configurações específicas e mesclar é boa, mas depende muito da consistência do backend para fornecer os dados.
Lista de Tarefas para o Sucesso
As tarefas estão listadas em ordem de prioridade, focando primeiro em resolver os problemas de consistência fundamental e conflitos.
Fase 1: Saneamento do Backend (Prioridade Alta)
Consolidar Arquivos de Rota de Catálogo e Admin:
Escolha UMA versão para os catálogos (ex: catalogs_validated_clean.py) e UMA para as rotas administrativas (admin_routes_simple.py).
Remova/Archive as versões antigas (catalogs_simple.py, catalogs_validated.py, pcp_routes_backup.py).
Atualize main.py para incluir apenas as rotas consolidadas.
Priorize admin_config_routes.py para operações POST/PUT/DELETE em configurações, e catalogs_validated_clean.py para GET (listagem).
Padronizar Nomes de Campos (SQLAlchemy vs. Retorno/Pydantic):
Defina uma convenção. Se no banco é nome_tipo, use nome_tipo consistentemente em Pydantic e nos retornos JSON. Se o frontend prefere nome, faça a transformação no backend no momento do retorno.
Ex: Para Departamento, o campo da DB é nome_tipo.
Pydantic Models (schemas.py - a ser criado): Use nome_tipo.
Funções de Rota: Ao construir o dicionário de retorno, use {"id": dept.id, "nome": dept.nome_tipo, ...} se o frontend espera nome.
Revisar Pydantic Models de Entrada:
Crie um arquivo schemas.py (se ainda não existir) e defina todos os modelos Pydantic para POST/PUT (DepartamentoCreate, SetorCreate, TipoMaquinaCreate, etc.).
Garanta que estes modelos reflitam exatamente os campos que o SQLAlchemy espera no database_models.py, incluindo tipos (Optional, List[str], etc.).
Atenção para TipoMaquina.subcategoria: Na DB é JSON, então no Pydantic deve ser Optional[List[str]] ou Optional[Union[List[str], str]] e a lógica de salvamento deve usar json.dumps() para a DB.
Atenção para id_setor e id_departamento: Se o frontend envia o NOME, o backend precisa buscar o ID correspondente antes de salvar no modelo SQLAlchemy. Se o frontend envia o ID, o Pydantic deve ser id_setor: Optional[int].
Corrigir Lógica de Criação/Atualização de Entidades:
Nos endpoints POST/PUT (ex: /admin/config/departamentos, /admin/config/setores, /admin/config/tipos-maquina):
Use os Pydantic models corrigidos.
Garanta que a criação de objetos (Departamento(**departamento_data.dict())) mapeie corretamente os campos.
Adicione validações de existência (db.query(...).filter(...).first()) para evitar duplicidades (ex: nome do departamento, nome do setor).
Implemente "soft delete" (setar ativo=False) para todas as entidades que tiverem o campo ativo, em vez de db.delete().
Refatorar database_models.py para extend_existing=True:
Já está feito com __table_args__ = {'extend_existing': True}, o que é ótimo para evitar conflitos de declaração de tabelas. Certifique-se de que não haja declarações duplicadas do Base ou de tabelas no mesmo arquivo.
Fase 2: Consistência Frontend-Backend (Prioridade Média)
Unificar Arquivos TiposApi.ts:
Escolha um único TiposApi.ts (recomendo o do pages/common por ser mais abrangente) e remova o outro.
Atualize todos os imports no frontend para apontar para este arquivo único.
Garanta que todas as interfaces neste arquivo correspondam aos modelos Pydantic de retorno finais do backend (após as transformações no backend).
Ajustar Payloads do Frontend:
Modifique os formulários e chamadas axios no frontend (adminApi.ts, catalogApi.ts, componentes de formulário) para enviar dados que correspondam aos modelos Pydantic de entrada corrigidos no backend.
Ex: Se o backend agora espera nome_tipo para departamento, o formulário deve enviar nome_tipo.
Ajuste a lógica de useCachedSetores para buscar Departamento por nome_tipo se esse for o campo padrão.
Revisar Mapeamento de id_setor/id_departamento:
No frontend, ao selecionar um setor/departamento por nome (dropdown), obtenha o ID correspondente e envie o ID para o backend, se o backend espera o ID para criar o relacionamento.
Nos retornos, se o backend retorna id_setor, mas o frontend precisa do nome, o frontend precisará fazer uma busca adicional ou o backend deverá incluir o nome_setor no retorno.
Fase 3: Otimização e Melhorias (Prioridade Baixa)
Otimizar Queries no Backend:
Para listagens de entidades, utilize JOIN com as tabelas de TipoSetor e TipoDepartamento para incluir os nomes no retorno e evitar que o frontend precise fazer buscas adicionais. Ex:
code
Python
# Exemplo em admin_routes_simple.py para Setores
setores = db.query(DBSetor, Departamento.nome_tipo.label("departamento_nome")) \
            .join(Departamento, DBSetor.id_departamento == Departamento.id) \
            .all()
return [
    {
        "id": setor.DBSetor.id,
        "nome": setor.DBSetor.nome,
        "departamento": setor.departamento_nome, # Usar o nome do JOIN
        # ...
    } for setor in setores
]
A função buscar_id_setor e buscar_id_departamento em admin_routes_simple.py pode ser otimizada ou tornada mais genérica.
Centralizar Constantes de Texto/Enums:
No frontend, crie um arquivo src/utils/constants.ts para constantes como PRIVILEGE_LEVELS, status_os_opcoes, etc., para evitar duplicação em vários componentes.
Documentação e Comentários:
Adicione comentários explicativos em pontos complexos do código, especialmente nas rotas e lógicas de validação.
Exemplo de Ajuste (Backend: Departamento)
Vamos pegar o exemplo do Departamento (nome_tipo na DB, nome esperado no frontend).
database_models.py (já está ok):
code
Python
class Departamento(Base):
    __tablename__ = "tipo_departamentos"
    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String) # <-- Campo real no banco
    descricao = Column(Text)
    ativo = Column(Boolean)
    # ...
schemas.py (a ser criado):
code
Python
# app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List

class DepartamentoBase(BaseModel):
    nome_tipo: str = Field(..., alias="nome") # Alias para compatibilidade com frontend que espera 'nome'
    descricao: Optional[str] = None
    ativo: bool = True

    class Config:
        allow_population_by_field_name = True # Permite usar 'nome' na entrada e mapear para 'nome_tipo'
        from_attributes = True

class DepartamentoCreate(DepartamentoBase):
    pass

class DepartamentoResponse(DepartamentoBase):
    id: int
    data_criacao: Optional[datetime] = None # Assuming datetime from DB

# ... outros schemas ...
admin_config_routes.py (endpoints para Departamento):
code
Python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
# Importar schemas daqui
from app.schemas import DepartamentoCreate, DepartamentoResponse 
from app.database_models import Usuario, Departamento
from config.database_config import get_db
from app.dependencies import get_current_user

router = APIRouter(tags=["admin-config"])

def verificar_admin(current_user: Any = Depends(get_current_user)):
    if current_user.privilege_level != 'ADMIN':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas administradores podem acessar esta funcionalidade")
    return current_user

@router.get("/departamentos", response_model=List[DepartamentoResponse]) # Usar o Response Model
async def listar_departamentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    departamentos = db.query(Departamento).all()
    return departamentos # Retorna diretamente, Pydantic fará o mapeamento com alias 'nome'

@router.post("/departamentos", response_model=DepartamentoResponse) # Usar o Response Model
async def criar_departamento(
    departamento_data: DepartamentoCreate, # Usar o modelo Pydantic para entrada
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    try:
        existente = db.query(Departamento).filter_by(nome_tipo=departamento_data.nome_tipo).first()
        if existente:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Departamento '{departamento_data.nome_tipo}' já existe")
        
        novo_departamento = Departamento(
            nome_tipo=departamento_data.nome_tipo,
            descricao=departamento_data.descricao,
            ativo=departamento_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        db.add(novo_departamento)
        db.commit()
        db.refresh(novo_departamento)
        
        return novo_departamento # Retorna o objeto, Pydantic fará o mapeamento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar departamento: {str(e)}")

# ... endpoints PUT e DELETE seriam ajustados de forma similar
adminApi.ts (Frontend):
code
TypeScript
// frontend/src/services/adminApi.ts
// ... (outros imports)

// Usar o nome 'nome' no frontend para o campo do departamento
export interface DepartamentoData {
    id?: number;
    nome: string; // <-- Agora corresponde ao alias do Pydantic
    descricao: string;
    ativo: boolean;
}

// CentroCustoData agora pode ser um alias direto para DepartamentoData
export type CentroCustoData = DepartamentoData;

export const departamentoService = {
    getDepartamentos: () => api.get<DepartamentoData[]>('/admin/config/departamentos').then(res => res.data),
    getDepartamentoById: (id: number) => api.get<DepartamentoData>(`/admin/config/departamentos/${id}`).then(res => res.data),
    createDepartamento: (data: DepartamentoData) => api.post<DepartamentoData>('/admin/config/departamentos', data).then(res => res.data),
    updateDepartamento: (id: number, data: DepartamentoData) => api.put<DepartamentoData>(`/admin/config/departamentos/${id}`, data).then(res => res.data),
    deleteDepartamento: (id: number) => api.delete(`/admin/config/departamentos/${id}`).then(res => res.data),
};

// CentroCustoService pode ser simplificado para usar departamentoService diretamente
export const centroCustoService = {
    getCentrosCusto: departamentoService.getDepartamentos,
    getCentroCustoById: departamentoService.getDepartamentoById,
    createCentroCusto: departamentoService.createDepartamento,
    updateCentroCusto: departamentoService.updateDepartamento,
    deleteCentroCusto: departamentoService.deleteDepartamento,
};

// ... outros services ajustados para usar os nomes padronizados ...
DepartamentoForm.tsx (Frontend):
code
TypeScript
// frontend/src/features/admin/components/config/DepartamentoForm.tsx
import React, { useState, useEffect } from 'react';
import { StyledInput } from '../../../../components/UIComponents';
import { DepartamentoData } from '../../../../services/adminApi'; // <-- Importa o tipo do adminApi

// O tipo de dados agora corresponde ao que o frontend espera e o backend processa
interface DepartamentoFormProps {
    initialData?: Partial<DepartamentoData>;
    onCancel: () => void;
    onSubmit: (data: DepartamentoData, isEdit: boolean) => void;
    isEdit?: boolean;
}

const DepartamentoForm: React.FC<DepartamentoFormProps> = ({
    initialData,
    onCancel,
    onSubmit,
    isEdit = false,
}) => {
    // Usar 'nome' aqui
    const [formData, setFormData] = useState<DepartamentoData>({
        nome: initialData?.nome || '', // <-- Usar 'nome'
        descricao: initialData?.descricao || '',
        ativo: initialData?.ativo ?? true,
    });
    // ... restante do componente ...
    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div>
                <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                    Nome do Departamento <span className="text-red-500">*</span>
                </label>
                <StyledInput
                    id="nome"
                    name="nome" // <-- name é 'nome'
                    value={formData.nome}
                    onChange={handleInputChange}
                    placeholder="Ex: MOTORES"
                    error={errors.nome}
                    required
                />
                {errors.nome && <p className="mt-1 text-sm text-red-600">{errors.nome}</p>}
            </div>
            {/* ... */}
        </form>
    );
};

export default DepartamentoForm;
Esta abordagem garante que a "árvore hierárquica" dos dados e das rotas seja consistente em todo o stack, resolvendo as duplicações e problemas de comunicação.