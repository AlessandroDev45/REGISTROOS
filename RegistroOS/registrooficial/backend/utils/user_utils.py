import logging

# Setup centralized logging to ensure visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.database_models import Usuario
from sqlalchemy.orm import Session
from typing import List, Optional


def get_pendent_users(db: Session) -> List:
    try:
        pendent_users = db.query(Usuario).filter(Usuario.is_approved == False).all()
        return pendent_users
    except Exception as e:
        logger.error(f"Database query failed: {e}", exc_info=True)
        return []

def normalize_sector_name(sector_name: str) -> str:
    """Normaliza o nome do setor (remover acentos, converter para minúsculas, remover espaços)"""
    if not sector_name:
        return ""
    import unicodedata
    # Remove acentos
    normalized = unicodedata.normalize('NFD', sector_name)
    ascii_str = normalized.encode('ascii', 'ignore').decode('ascii')
    # Converte para minúsculas, remove espaços e hífens
    # Mantém caracteres especiais como '|' se presentes no nome original
    return ascii_str.lower().replace(' ', '').replace('-', '')

def check_development_access(user: Usuario, required_sector: str) -> bool:
    """
    Verifica permissões personalizadas para acessos de setor no desenvolvimento
    """
    try:
        logger.info(f"Checking development access for user {user.nome_completo} to sector {required_sector}")
        logger.info(f"User privilege: {user.privilege_level}, setor: {user.setor}, trabalha_producao: {user.trabalha_producao}")

        # Usuários administrativos têm acesso total
        if user.privilege_level in ["ADMIN", "SUPERVISOR", "GESTAO"]:
            logger.info(f"User {user.nome_completo} has admin access, granting access to {required_sector}")
            return True

        # Verificar se o usuário trabalha na produção (campo obrigatório para desenvolvimento)
        trabalha_producao = getattr(user, 'trabalha_producao', False)
        if not trabalha_producao:
            logger.info(f"User {user.nome_completo} does not work in production, denying access")
            return False

        # Lista de setores que podem acessar o desenvolvimento (produção e laboratórios)
        setores_producao = [
            'laboratorio de ensaios eletricos motores',
            'laboratorio de ensaios eletricos transformadores',
            'mecanica dia motores',
            'mecanica dia transformadores',
            'mecanica noite motores',
            'mecanica noite transformadores'
        ]

        # Verificar se o usuário trabalha na produção
        trabalha_producao = getattr(user, 'trabalha_producao', False) == True
        logger.info(f"User trabalha_producao: {trabalha_producao}")

        # Normalizar o setor do usuário para comparação
        user_sector_normalized = normalize_sector_name(user.setor)  # type: ignore
        setor_producao = user_sector_normalized in setores_producao
        logger.info(f"User sector normalized: '{user_sector_normalized}', is production sector: {setor_producao}")

        # USER e SUPERVISOR podem acessar desenvolvimento APENAS se:
        # 1. Trabalham na produção E
        # 2. Têm privilégio ADMIN, SUPERVISOR ou USER
        if user.privilege_level in ["USER", "SUPERVISOR"]:
            # Deve trabalhar na produção para acessar desenvolvimento
            acesso_permitido = trabalha_producao
            logger.info(f"Access decision for {user.privilege_level}: trabalha_producao={trabalha_producao}, acesso_permitido={acesso_permitido}")
            return acesso_permitido

        # Outros privilégios (PCP) não têm acesso
        logger.info(f"Access denied for privilege level: {user.privilege_level}")
        return False

    except Exception as e:
        logger.error(f"Erro na verificação de acesso: {e}")
        return False
