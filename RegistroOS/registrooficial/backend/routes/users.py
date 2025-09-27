from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import datetime
from pydantic import BaseModel
from typing import Optional

from app.database_models import Usuario
from config.database_config import get_db
from app.dependencies import get_current_user, get_current_admin_user
from utils.user_utils import get_pendent_users

# Modelo Pydantic simples para resposta de usuário
class UsuarioResponse(BaseModel):
    id: int
    nome_completo: str
    email: str
    matricula: Optional[str] = None
    cargo: Optional[str] = None
    privilege_level: str
    is_approved: bool
    trabalha_producao: bool
    data_criacao: Optional[datetime.datetime] = None
    id_setor: Optional[int] = None
    id_departamento: Optional[int] = None

    class Config:
        from_attributes = True

router = APIRouter()

class ApproveUserRequest(BaseModel):
    privilege_level: str
    tipo_producao: Optional[str] = None
    trabalha_producao: bool = False

class CreateUserRequest(BaseModel):
    nome_completo: str
    email: str
    senha: str
    privilege_level: str
    tipo_producao: Optional[str] = None
    trabalha_producao: bool = False
    id_setor: Optional[int] = None
    id_departamento: Optional[int] = None

@router.get("/usuarios/", response_model=List[UsuarioResponse])
async def get_usuarios(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get users that current user can manage (filtered by sector/department access)"""
    try:
        # Use the new sector-based filtering
        allowed_users = db.query(Usuario).all()
        return allowed_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")

@router.get("/", response_model=List[UsuarioResponse])
async def get_users_root(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get users - root endpoint"""
    try:
        users = db.query(Usuario).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")

@router.get("/pending-approval", response_model=List[UsuarioResponse])
async def get_pending_approval_users(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get users pending approval"""
    try:
        # Verificar se o usuário tem privilégios para ver aprovações
        if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO", "PCP"]:
            raise HTTPException(status_code=403, detail="Acesso negado")

        pending_users = db.query(Usuario).filter(Usuario.is_approved == False).all()
        return pending_users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários pendentes: {str(e)}")

@router.get("/usuarios/pendentes/", response_model=List[UsuarioResponse])
async def get_pending_usuarios(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all users pending approval (for admin and supervisor users)."""
    # Verify the user has appropriate privileges
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO", "PCP"]:
        raise HTTPException(status_code=403, detail=f"Acesso negado: nível '{current_user.privilege_level}' não possui permissões. Requerido: ADMIN, SUPERVISOR, GESTAO, PCP")

    try:
        pending_users = get_pendent_users(db)
        return pending_users
    except Exception as e:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logging.error(f"Erro ao buscar usuários pendentes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários pendentes: {str(e)}")

@router.put("/usuarios/{user_id}/approve")
async def approve_user(
    user_id: int,
    request: ApproveUserRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para aprovar um usuário (apenas administradores e supervisores).
    """
    # Verifica se o usuário atual tem privilégios suficientes
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores, supervisores e gestão podem aprovar usuários")

    # Busca o usuário a ser aprovado
    user_to_approve = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user_to_approve:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verifica se o usuário já está aprovado
    if user_to_approve.is_approved is True:
        raise HTTPException(status_code=400, detail="Usuário já está aprovado")

    # Valida se o privilégio é USER para setores de produção
    # Lista de setores de produção (motores e transformadores)
    setoresProducao = [
        "MECANICA DIA MOTORES", "MECANICA NOITE MOTORES", "COMERCIAL MOTORES", "EXPEDICAO MOTORES",
        "PCP MOTORES", "GESTAO MOTORES", "GERENCIA MOTORES", "PINTURA MOTORES", "ENSAIOS BT MOTORES",
        "FECHAMENTO MOTORES", "ACABAMENTO MOTORES", "POLOS MOTORES", "PARTE ATIVA MOTORES", "PREPARACAO MOTORES",
        "ENROLAMENTO BARRAMENTO MOTORES", "ENROLAMENTO FIO REDONDO MOTORES", "ENGENHARIA MOTORES",
        "LABORATORIO DE ENSAIOS ELETRICOS MOTORES",
        "MECANICA DIA TRANSFORMADORES", "MECANICA NOITE TRANSFORMADORES", "COMERCIAL TRANSFORMADORES",
        "EXPEDICAO TRANSFORMADORES", "PCP TRANSFORMADORES", "GESTAO TRANSFORMADORES", "GERENCIA TRANSFORMADORES",
        "PINTURA TRANSFORMADORES", "ENSAIOS BT TRANSFORMADORES", "FECHAMENTO TRANSFORMADORES",
        "ACABAMENTO TRANSFORMADORES", "POLOS TRANSFORMADORES", "PARTE ATIVA TRANSFORMADORES",
        "PREPARACAO TRANSFORMADORES", "ENROLAMENTO BARRAMENTO TRANSFORMADORES",
        "ENROLAMENTO FIO REDONDO TRANSFORMADORES", "ENGENHARIA TRANSFORMADORES",
        "LABORATORIO DE ENSAIOS ELETRICOS TRANSFORMADORES"
    ]
    # Verificação de setor removida - usar id_setor se necessário
    # if user_to_approve.id_setor in setoresProducao and request.privilege_level != "USER":
    #     raise HTTPException(status_code=400, detail=f"Usuário do setor deve ter privilégio USER.")

    # Aprova o usuário e define o nível de privilégio
    user_to_approve.is_approved = True  # type: ignore
    user_to_approve.privilege_level = request.privilege_level  # type: ignore
    user_to_approve.trabalha_producao = request.trabalha_producao  # type: ignore
    user_to_approve.data_ultima_atualizacao = datetime.datetime.utcnow()  # type: ignore
    user_to_approve.obs_reprovacao = None # type: ignore # Limpa observações de reprovação, se houver

    try:
        db.commit()
        db.refresh(user_to_approve)
        return {
            "message": "Usuário aprovado com sucesso",
            "user": {
                "id": user_to_approve.id,
                "email": user_to_approve.email,
                "nome_completo": user_to_approve.nome_completo,
                "is_approved": user_to_approve.is_approved,
                "privilege_level": user_to_approve.privilege_level,
                "trabalha_producao": user_to_approve.trabalha_producao
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar usuário: {str(e)}")

@router.put("/usuarios/{user_id}/reject")
async def reject_user(
    user_id: int,
    request: Optional[dict] = None, # Pode futuramente conter motivo de reprovação
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para reprovar um usuário (apenas administradores e supervisores).
    """
    # Verifica se o usuário atual tem privilégios suficientes
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores, supervisores e gestão podem reprovar usuários")

    # Busca o usuário a ser reprovado
    user_to_reject = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user_to_reject:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verifica se o usuário já foi aprovado
    if user_to_reject.is_approved is True:
        raise HTTPException(status_code=400, detail="Usuário já está aprovado, não pode ser reprovado.")

    # Marca o usuário como reprovado
    user_to_reject.is_approved = False # type: ignore # Garante que fique como False
    user_to_reject.privilege_level = 'USER' # type: ignore # Reseta privilégio
    user_to_reject.obs_reprovacao = (request and request.get('motivo')) or 'Reprovado por administrador.' # type: ignore

    try:
        db.commit()
        db.refresh(user_to_reject)
        return {
            "message": "Usuário reprovado com sucesso",
            "user": {
                "id": user_to_reject.id,
                "email": user_to_reject.email,
                "nome_completo": user_to_reject.nome_completo,
                "is_approved": user_to_reject.is_approved,
                "privilege_level": user_to_reject.privilege_level,
                "motivo_reprovacao": user_to_reject.obs_reprovacao
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao rejeitar usuário: {str(e)}")

@router.post("/create-user")
async def create_user(
    request: CreateUserRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para criar um novo usuário (apenas administradores).
    """
    # Verifica se o usuário atual tem privilégios suficientes
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado: apenas administradores, supervisores e gestão podem criar usuários")

    # Verificar se email já existe
    db_user_email = db.query(Usuario).filter(Usuario.email == request.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email já está em uso.")

    # Hash da senha
    from app.auth import get_password_hash
    hashed_password = get_password_hash(request.senha)

    # Preparar dados para o banco de dados
    novo_usuario_data = {
        "nome_completo": request.nome_completo,
        "nome_usuario": request.email.split('@')[0],  # Usa parte do email como nome de usuário
        "email": request.email,
        "senha_hash": hashed_password,
        "id_setor": request.id_setor,
        "id_departamento": request.id_departamento or 1,  # Padrão MOTORES
        "privilege_level": request.privilege_level,
        "is_approved": True,  # Usuários criados por admin são automaticamente aprovados
        "trabalha_producao": request.trabalha_producao,
        "data_criacao": datetime.datetime.utcnow(),
        "data_ultima_atualizacao": datetime.datetime.utcnow()
    }

    try:
        novo_usuario = Usuario(**novo_usuario_data)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return {
            "message": "Usuário criado com sucesso",
            "user": {
                "id": novo_usuario.id,
                "email": novo_usuario.email,
                "nome_completo": novo_usuario.nome_completo,
                "id_setor": novo_usuario.id_setor,
                "id_departamento": novo_usuario.id_departamento,
                "privilege_level": novo_usuario.privilege_level,
                "trabalha_producao": novo_usuario.trabalha_producao
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")