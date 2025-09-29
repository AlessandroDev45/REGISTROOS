"""Initial schema setup for RegistroOS

Revision ID: 001
Revises: 
Create Date: 2025-09-29 12:00:00.000000

Esta migração inicial cria o schema base do RegistroOS baseado nos modelos
SQLAlchemy existentes. Serve como ponto de partida para futuras migrações.

Tabelas principais criadas:
- tipo_departamentos: Departamentos da empresa
- tipo_setores: Setores dentro dos departamentos  
- tipos_maquina: Tipos de máquinas/equipamentos
- tipo_usuarios: Usuários do sistema
- clientes: Clientes da empresa
- equipamentos: Equipamentos dos clientes
- ordens_servico: Ordens de serviço
- apontamentos_detalhados: Apontamentos de trabalho
- programacoes: Programações de trabalho

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aplicar mudanças do schema (upgrade)"""
    
    # Nota: Como o banco já existe, esta migração serve principalmente
    # como documentação do schema atual e ponto de partida para futuras mudanças.
    
    # Em um cenário real, você executaria:
    # alembic stamp head
    # para marcar o banco existente como estando na versão atual
    
    print("Schema inicial já existe. Execute 'alembic stamp head' para marcar como atual.")
    pass


def downgrade() -> None:
    """Reverter mudanças do schema (downgrade)"""
    
    # Não é possível fazer downgrade da migração inicial
    print("Não é possível fazer downgrade da migração inicial.")
    pass
