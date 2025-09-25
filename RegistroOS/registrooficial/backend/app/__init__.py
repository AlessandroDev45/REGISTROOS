# RegistroOS Backend Package
__version__ = "1.0.0"

# Import main components for easier access
try:
    from .database_models import Base, Usuario, OrdemServico, Programacao
    database_models_available = True
except ImportError as e:
    print(f"⚠️ Aviso: Alguns modelos de banco não estão disponíveis: {e}")
    database_models_available = False

# Modelos Pydantic foram movidos para SCRATCK HERE durante limpeza
# Mantendo apenas os modelos SQLAlchemy essenciais
pydantic_models_available = False
print("ℹ️ Modelos Pydantic não carregados (estrutura limpa)")

__all__ = [
    # Database models (apenas SQLAlchemy)
    "Base", "Usuario", "OrdemServico", "Programacao",
]
