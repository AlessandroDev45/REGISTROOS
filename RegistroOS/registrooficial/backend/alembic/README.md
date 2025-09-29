# Alembic Database Migrations

Este diretório contém as migrações do banco de dados usando Alembic.

## Comandos Úteis

### Gerar uma nova migração
```bash
alembic revision --autogenerate -m "Descrição da migração"
```

### Aplicar migrações
```bash
alembic upgrade head
```

### Verificar status das migrações
```bash
alembic current
alembic history
```

### Reverter migração
```bash
alembic downgrade -1
```

## Configuração

- **Banco de dados**: SQLite (`registroos_new.db`)
- **Modo batch**: Habilitado para SQLite
- **Autogenerate**: Configurado para detectar mudanças automaticamente

## Estrutura

- `env.py`: Configuração do ambiente Alembic
- `script.py.mako`: Template para novos arquivos de migração
- `versions/`: Diretório com os arquivos de migração
- `alembic.ini`: Arquivo de configuração principal

## Notas Importantes

- Sempre revisar as migrações geradas antes de aplicar
- Fazer backup do banco antes de aplicar migrações em produção
- Testar migrações em ambiente de desenvolvimento primeiro
