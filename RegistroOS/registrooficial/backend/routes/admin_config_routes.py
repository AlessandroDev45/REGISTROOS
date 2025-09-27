"""
ADMIN CONFIG ROUTES - RegistroOS
================================

Rotas específicas para configuração administrativa e criação de entidades.
Apenas usuários com privilege_level ADMIN podem acessar estes endpoints.

ENDPOINTS DISPONÍVEIS:
- POST /api/admin/config/departamentos - Criar departamento
- POST /api/admin/config/setores - Criar setor
- POST /api/admin/config/tipos-maquina - Criar tipo de máquina
- POST /api/admin/config/tipos-teste - Criar tipo de teste
- POST /api/admin/config/tipos-atividade - Criar tipo de atividade
- POST /api/admin/config/descricoes-atividade - Criar descrição de atividade
- POST /api/admin/config/causas-retrabalho - Criar causa de retrabalho
- POST /api/admin/config/tipos-falha - Criar tipo de falha
- POST /api/admin/config/clientes - Criar cliente
- POST /api/admin/config/equipamentos - Criar equipamento
- GET /api/admin/config/sistema - Configurações do sistema
- POST /api/admin/config/backup - Criar backup
- POST /api/admin/config/restore - Restaurar backup
- GET /api/admin/config/logs - Logs do sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

from config.database_config import get_db
from app.dependencies import get_current_user
from app.database_models import (
    Usuario, Departamento, Setor, TipoMaquina, TipoTeste,
    Cliente, Equipamento, TipoAtividade, TipoDescricaoAtividade,
    TipoCausaRetrabalho, TipoFalha, OrdemServico
)

router = APIRouter(tags=["admin-config"])

# ============================================================================
# MODELOS PYDANTIC PARA CRIAÇÃO DE ENTIDADES
# ============================================================================

class DepartamentoCreate(BaseModel):
    nome_tipo: str
    descricao: Optional[str] = None
    ativo: bool = True

class SetorCreate(BaseModel):
    nome: str
    departamento: str
    descricao: Optional[str] = None
    id_departamento: int
    area_tipo: str
    supervisor_responsavel: Optional[int] = None
    permite_apontamento: bool = True
    ativo: bool = True

class TipoMaquinaCreate(BaseModel):
    nome_tipo: str
    categoria: str
    subcategoria: Optional[List[str]] = None
    descricao: Optional[str] = None
    id_departamento: int
    especificacoes_tecnicas: Optional[str] = None
    campos_teste_resultado: Optional[str] = None
    setor: Optional[str] = None
    departamento: Optional[str] = None
    ativo: bool = True

class TipoTesteCreate(BaseModel):
    nome: str
    departamento: str
    setor: Optional[str] = None
    tipo_teste: Optional[str] = None
    descricao: Optional[str] = None
    tipo_maquina: Optional[int] = None
    teste_exclusivo_setor: bool = False
    descricao_teste_exclusivo: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[int] = None
    ativo: bool = True

class ClienteCreate(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj_cpf: str
    contato_principal: Optional[str] = None
    telefone_contato: Optional[str] = None
    email_contato: Optional[str] = None
    endereco: Optional[str] = None

class EquipamentoCreate(BaseModel):
    descricao: str
    tipo: Optional[str] = None
    fabricante: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None

# ============================================================================
# MIDDLEWARE DE VERIFICAÇÃO DE ADMIN
# ============================================================================

def verificar_admin(current_user: Any = Depends(get_current_user)):
    """Verificar se o usuário é admin"""
    if current_user.__dict__.get('privilege_level') != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar esta funcionalidade"
        )
    return current_user

# ============================================================================
# ENDPOINTS DE CRIAÇÃO DE ENTIDADES
# ============================================================================

@router.get("/departamentos", response_model=List[Dict[str, Any]])
async def listar_departamentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os departamentos"""
    try:
        departamentos = db.query(Departamento).all()

        return [
            {
                "id": dept.id,
                "nome_tipo": dept.nome_tipo,
                "descricao": dept.descricao,
                "ativo": dept.ativo,
                "data_criacao": dept.data_criacao,
                "data_ultima_atualizacao": dept.data_ultima_atualizacao
            }
            for dept in departamentos
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar departamentos: {str(e)}"
        )

@router.post("/departamentos", response_model=Dict[str, Any])
async def criar_departamento(
    departamento_data: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo departamento"""
    try:
        # Verificar se já existe
        existente = db.query(Departamento).filter_by(nome_tipo=departamento_data.nome_tipo).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Departamento '{departamento_data.nome_tipo}' já existe"
            )
        
        # Criar novo departamento
        novo_departamento = Departamento()  # type: ignore
        novo_departamento.nome_tipo = departamento_data.nome_tipo  # type: ignore
        novo_departamento.descricao = departamento_data.descricao  # type: ignore
        novo_departamento.ativo = departamento_data.ativo  # type: ignore
        novo_departamento.data_criacao = datetime.now()  # type: ignore
        novo_departamento.data_ultima_atualizacao = datetime.now()  # type: ignore
        
        db.add(novo_departamento)
        db.commit()
        db.refresh(novo_departamento)
        
        return {
            "id": novo_departamento.id,
            "nome_tipo": novo_departamento.nome_tipo,
            "descricao": novo_departamento.descricao,
            "ativo": novo_departamento.ativo,
            "data_criacao": novo_departamento.data_criacao,
            "message": "Departamento criado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar departamento: {str(e)}"
        )

@router.get("/departamentos/{departamento_id}", response_model=Dict[str, Any])
async def buscar_departamento(
    departamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar departamento por ID"""
    try:
        departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()

        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento com ID {departamento_id} não encontrado"
            )

        return {
            "id": departamento.id,
            "nome_tipo": departamento.nome_tipo,
            "descricao": departamento.descricao,
            "ativo": departamento.ativo,
            "data_criacao": departamento.data_criacao,
            "data_ultima_atualizacao": departamento.data_ultima_atualizacao
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar departamento: {str(e)}"
        )

@router.put("/departamentos/{departamento_id}", response_model=Dict[str, Any])
async def atualizar_departamento(
    departamento_id: int,
    departamento_data: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar departamento"""
    try:
        departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()

        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento com ID {departamento_id} não encontrado"
            )

        # Verificar se o novo nome já existe (exceto para o próprio departamento)
        existente = db.query(Departamento).filter(
            Departamento.nome_tipo == departamento_data.nome_tipo,
            Departamento.id != departamento_id
        ).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Departamento '{departamento_data.nome_tipo}' já existe"
            )

        # Atualizar dados
        departamento.nome_tipo = departamento_data.nome_tipo  # type: ignore
        departamento.descricao = departamento_data.descricao  # type: ignore
        departamento.ativo = departamento_data.ativo  # type: ignore
        departamento.data_ultima_atualizacao = datetime.now()  # type: ignore

        db.commit()
        db.refresh(departamento)

        return {
            "id": departamento.id,
            "nome_tipo": departamento.nome_tipo,
            "descricao": departamento.descricao,
            "ativo": departamento.ativo,
            "data_criacao": departamento.data_criacao,
            "data_ultima_atualizacao": departamento.data_ultima_atualizacao,
            "message": "Departamento atualizado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar departamento: {str(e)}"
        )

@router.delete("/departamentos/{departamento_id}", response_model=Dict[str, Any])
async def deletar_departamento(
    departamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar departamento"""
    try:
        departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()

        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento com ID {departamento_id} não encontrado"
            )

        # Verificar se há setores vinculados
        setores_vinculados = db.query(Setor).filter(Setor.id_departamento == departamento_id).count()

        if setores_vinculados > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível deletar o departamento. Há {setores_vinculados} setor(es) vinculado(s)"
            )

        db.delete(departamento)
        db.commit()

        return {
            "message": f"Departamento '{departamento.nome_tipo}' deletado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar departamento: {str(e)}"
        )

@router.post("/setores", response_model=Dict[str, Any])
async def criar_setor(
    setor_data: SetorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo setor"""
    try:
        # Verificar se já existe
        existente = db.query(Setor).filter(
            Setor.nome == setor_data.nome
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Setor '{setor_data.nome}' já existe"
            )
        
        # Verificar se departamento existe
        departamento = db.query(Departamento).filter(
            Departamento.id == setor_data.id_departamento
        ).first()
        
        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Departamento com ID {setor_data.id_departamento} não encontrado"
            )
        
        # Criar novo setor
        novo_setor = Setor(
            nome=setor_data.nome,
            departamento=setor_data.departamento,
            descricao=setor_data.descricao,
            ativo=setor_data.ativo,
            id_departamento=setor_data.id_departamento,
            area_tipo=setor_data.area_tipo,
            supervisor_responsavel=setor_data.supervisor_responsavel,
            permite_apontamento=setor_data.permite_apontamento,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        
        db.add(novo_setor)
        db.commit()
        db.refresh(novo_setor)
        
        return {
            "id": novo_setor.id,
            "nome": novo_setor.nome,
            "departamento": novo_setor.departamento,
            "descricao": novo_setor.descricao,
            "area_tipo": novo_setor.area_tipo,
            "ativo": novo_setor.ativo,
            "data_criacao": novo_setor.data_criacao,
            "message": "Setor criado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar setor: {str(e)}"
        )

@router.post("/tipos-maquina", response_model=Dict[str, Any])
async def criar_tipo_maquina(
    tipo_data: TipoMaquinaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de máquina"""
    try:
        # Verificar se já existe
        existente = db.query(TipoMaquina).filter(
            TipoMaquina.nome_tipo == tipo_data.nome_tipo
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de máquina '{tipo_data.nome_tipo}' já existe"
            )
        
        # Criar novo tipo de máquina
        novo_tipo = TipoMaquina(
            nome_tipo=tipo_data.nome_tipo,
            categoria=tipo_data.categoria,
            subcategoria=tipo_data.subcategoria,
            descricao=tipo_data.descricao,
            ativo=tipo_data.ativo,
            id_departamento=tipo_data.id_departamento,
            especificacoes_tecnicas=tipo_data.especificacoes_tecnicas,
            campos_teste_resultado=tipo_data.campos_teste_resultado,
            setor=tipo_data.setor,
            departamento=tipo_data.departamento,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        
        db.add(novo_tipo)
        db.commit()
        db.refresh(novo_tipo)
        
        return {
            "id": novo_tipo.id,
            "nome_tipo": novo_tipo.nome_tipo,
            "categoria": novo_tipo.categoria,
            "subcategoria": novo_tipo.subcategoria,
            "descricao": novo_tipo.descricao,
            "ativo": novo_tipo.ativo,
            "data_criacao": novo_tipo.data_criacao,
            "message": "Tipo de máquina criado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de máquina: {str(e)}"
        )

@router.post("/clientes", response_model=Dict[str, Any])
async def criar_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo cliente"""
    try:
        # Verificar se já existe
        existente = db.query(Cliente).filter(
            Cliente.cnpj_cpf == cliente_data.cnpj_cpf
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cliente com CNPJ/CPF '{cliente_data.cnpj_cpf}' já existe"
            )
        
        # Criar novo cliente
        novo_cliente = Cliente(
            razao_social=cliente_data.razao_social,
            nome_fantasia=cliente_data.nome_fantasia,
            cnpj_cpf=cliente_data.cnpj_cpf,
            contato_principal=cliente_data.contato_principal,
            telefone_contato=cliente_data.telefone_contato,
            email_contato=cliente_data.email_contato,
            endereco=cliente_data.endereco,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        
        return {
            "id": novo_cliente.id,
            "razao_social": novo_cliente.razao_social,
            "nome_fantasia": novo_cliente.nome_fantasia,
            "cnpj_cpf": novo_cliente.cnpj_cpf,
            "contato_principal": novo_cliente.contato_principal,
            "data_criacao": novo_cliente.data_criacao,
            "message": "Cliente criado com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@router.get("/sistema", response_model=Dict[str, Any])
async def get_configuracoes_sistema(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter configurações do sistema"""
    try:
        # Contar entidades
        total_usuarios = db.query(Usuario).count()
        total_departamentos = db.query(Departamento).count()
        total_setores = db.query(Setor).count()
        total_tipos_maquina = db.query(TipoMaquina).count()
        total_clientes = db.query(Cliente).count()

        # Buscar dados reais do banco
        privilege_levels_query = db.query(Usuario.privilege_level).distinct().all()
        privilege_levels = [p[0] for p in privilege_levels_query if p[0]]

        status_os_query = db.query(OrdemServico.status_os).distinct().all()
        status_os = [s[0] for s in status_os_query if s[0]]

        tipos_area_query = db.query(Setor.area_tipo).distinct().all()
        tipos_area = [a[0] for a in tipos_area_query if a[0]]

        return {
            "sistema": {
                "nome": "RegistroOS",
                "versao": "1.9.0",
                "banco_dados": "registroos_new.db",
                "data_consulta": datetime.now()
            },
            "estatisticas": {
                "total_usuarios": total_usuarios,
                "total_departamentos": total_departamentos,
                "total_setores": total_setores,
                "total_tipos_maquina": total_tipos_maquina,
                "total_clientes": total_clientes
            },
            "configuracoes": {
                "privilege_levels": privilege_levels,
                "status_os": status_os,
                "tipos_area": tipos_area
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter configurações: {str(e)}"
        )

@router.get("/setores", response_model=List[Dict[str, Any]])
async def listar_setores(
    db: Session = Depends(get_db),
    current_user: Any = Depends(verificar_admin)
):
    """Listar todos os setores"""
    try:
        setores = db.query(Setor).all()
        return [
            {
                "id": setor.id,
                "nome": setor.nome,
                "departamento": setor.departamento,
                "descricao": setor.descricao,
                "ativo": setor.ativo,
                "data_criacao": setor.data_criacao,
                "data_ultima_atualizacao": setor.data_ultima_atualizacao
            }
            for setor in setores
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar setores: {str(e)}"
        )

@router.get("/status")
async def get_admin_config_status(
    current_user: Usuario = Depends(verificar_admin)
):
    """Status das configurações administrativas"""
    return {
        "status": "ACTIVE",
        "admin_config_endpoints": [
            "POST /departamentos - Criar departamento",
            "POST /setores - Criar setor", 
            "POST /tipos-maquina - Criar tipo de máquina",
            "POST /tipos-teste - Criar tipo de teste",
            "POST /clientes - Criar cliente",
            "POST /equipamentos - Criar equipamento",
            "GET /sistema - Configurações do sistema",
            "GET /setores - Listar setores"
        ],
        "privilege_required": "ADMIN",
        "current_user": {
            "email": current_user.email,
            "privilege_level": current_user.privilege_level
        }
    }
