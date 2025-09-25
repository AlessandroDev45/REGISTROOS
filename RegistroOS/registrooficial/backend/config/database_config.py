"""
CONFIGURAÇÃO DO BANCO DE DADOS - RegistroOS
===========================================

Este arquivo contém todas as configurações necessárias para conectar
o FastAPI com o banco de dados.

DATABASE FILES DOCUMENTATION:
============================
- registroos.db: ACTIVE PRODUCTION DATABASE
  - Currently used by the application (DATABASE_URL points here)
  - Contains live production data with complete schema migration
  - All new deployments should use this database
  - Updated structure with all tipo/tipos tables populated

- registroos_new.db: LEGACY/BACKUP DATABASE
  - Previous database file, used as source for migration
  - Contains historical data for reference
  - Should NOT be used for new deployments
  - Consider archiving or removing if no longer needed

- registroos_test.db: TEST DATABASE (when created)
  - Used for automated testing
  - Should be separate from production data
  - Automatically created during test runs

PRODUCTION vs DEVELOPMENT:
=========================
- PRODUCTION: Uses registroos.db (current active database)
- DEVELOPMENT: Can use registroos.db or create separate dev database
- TESTING: Uses registroos_test.db or PostgreSQL test database

To switch databases, modify the DATABASE_URL environment variable or
update the db_path variable below.
"""

import os
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# =============================================================================
# CONFIGURAÇÕES DE CONEXÃO
# =============================================================================

# Caminho absoluto para o banco de dados no local desejado pelo usuário
db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

# URL de conexão com o banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{db_path}"  # Usando caminho absoluto para o banco de dados
)

# Configurações adicionais (SQLite)
DATABASE_CONFIG = {
    "echo": False,         # Log de SQL (False em produção)
    "future": True         # Usar SQLAlchemy 2.0
}

# =============================================================================
# ENGINE E SESSÃO
# =============================================================================

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL, **DATABASE_CONFIG)

# Criar sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
# A resolução para conflitos de tabelas é feita em database_models.py
Base = declarative_base()

# MetaData para operações avançadas
metadata = MetaData()

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

def get_db():
    """
    Dependência para injeção de sessão de banco de dados.
    Usar em endpoints FastAPI com 'Depends(get_db)'.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Criar todas as tabelas definidas nos modelos.
    Executar apenas uma vez durante setup inicial.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

def drop_tables():
    """
    Remover todas as tabelas (USE COM CAUTELA!).
    Apenas para desenvolvimento ou reset completo.
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Todas as tabelas foram removidas!")

def reset_database():
    """
    Resetar banco de dados completamente.
    Remove todas as tabelas e recria do zero.
    """
    drop_tables()
    create_tables()

# =============================================================================
# CONFIGURAÇÕES DE TESTE
# =============================================================================

# Banco de dados para testes (separe do banco de produção)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/registroos_test"
)

# Engine para testes
test_engine = create_engine(TEST_DATABASE_URL, **DATABASE_CONFIG)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def get_test_db():
    """
    Dependência para testes automatizados.
    """
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# =============================================================================
# INFORMAÇÕES DE CONEXÃO
# =============================================================================

def get_connection_info():
    """
    Retornar informações sobre a conexão atual.
    Útil para debug e monitoramento.
    """
    try:
        pool = engine.pool
        return {
            "database_url": DATABASE_URL.replace(":password@", ":***@"),
            "database_type": "SQLite" if "sqlite" in DATABASE_URL else "PostgreSQL",
            "pool_size": getattr(pool, 'size', 'N/A'),
            "pool_checked_in": getattr(pool, 'checkedin', 'N/A'),
            "pool_checked_out": getattr(pool, 'checkedout', 'N/A'),
            "pool_invalid": getattr(pool, 'invalid', 'N/A'),
            "pool_recycle": DATABASE_CONFIG.get("pool_recycle", "N/A")
        }
    except Exception as e:
        return {
            "database_url": DATABASE_URL.replace(":password@", ":***@"),
            "database_type": "SQLite" if "sqlite" in DATABASE_URL else "PostgreSQL",
            "pool_info": f"Erro ao obter info do pool: {str(e)}",
            "pool_recycle": DATABASE_CONFIG.get("pool_recycle", "N/A")
        }

# =============================================================================
# VERIFICAÇÃO DE CONEXÃO
# =============================================================================

def test_connection():
    """
    Testar conexão com o banco de dados.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Conexão com banco de dados estabelecida!")
                return True
    except Exception as e:
        print(f"❌ Erro na conexão com banco de dados: {e}")
        return False

# =============================================================================
# EXEMPLO DE USO EM FASTAPI
# =============================================================================

"""
Exemplo de como usar no FastAPI:

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import database_config

app = FastAPI()

# Verificar conexão na inicialização
@app.on_event("startup")
async def startup_event():
    database_config.test_connection()

# Endpoint de exemplo
@app.get("/usuarios/")
def read_usuarios(db: Session = Depends(database_config.get_db)):
    # Implementar lógica aqui
    return {"message": "Endpoint funcionando!"}

# Para testes
@app.get("/db-info/")
def database_info():
    return database_config.get_connection_info()
"""

# =============================================================================
# FIM DO ARQUIVO
# =============================================================================

if __name__ == "__main__":
    # Executar verificação de conexão quando rodar o arquivo diretamente
    print("🔍 Verificando conexão com banco de dados...")
    test_connection()
    print("\nℹ️ Informações da conexão:")
    info = get_connection_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
