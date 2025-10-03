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

from config.database_config import get_db
from app.dependencies import get_current_user
from app.database_models import (
    Usuario, Departamento, Setor, TipoMaquina, TipoTeste,
    Cliente, TipoAtividade, TipoDescricaoAtividade,
    TipoCausaRetrabalho, TipoFalha, OrdemServico
)
from app.schemas import (
    DepartamentoCreate, DepartamentoUpdate, DepartamentoResponse,
    SetorCreate, SetorUpdate, SetorResponse,
    TipoMaquinaCreate, TipoMaquinaUpdate, TipoMaquinaResponse,
    TipoTesteCreate, TipoTesteUpdate, TipoTesteResponse,
    TipoAtividadeCreate, TipoAtividadeUpdate, TipoAtividadeResponse,
    DescricaoAtividadeCreate, DescricaoAtividadeUpdate, DescricaoAtividadeResponse,
    TipoFalhaCreate, TipoFalhaUpdate, TipoFalhaResponse,
    CausaRetrabalhoCreate, CausaRetrabalhoUpdate, CausaRetrabalhoResponse
)
from app.utils.db_lookups import (
    validate_departamento_exists_by_id,
    get_departamento_nome_by_id
)

# Importar funções de scraping com fallback
try:
    from tasks.scraping_tasks import get_scraping_statistics, get_queue_status
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    get_scraping_statistics = None
    get_queue_status = None

router = APIRouter(tags=["admin-config"])

# ============================================================================
# MODELOS PYDANTIC IMPORTADOS DE app.schemas
# ============================================================================
# Os modelos Pydantic agora estão centralizados em app/schemas.py
# Importados: DepartamentoCreate, SetorCreate, TipoMaquinaCreate, etc.

# Removido TipoTesteCreate local - usando o centralizado de app.schemas

# Schemas corretos para entidades que usam 'codigo' no banco
class FalhaTipoCreateCorrect(BaseModel):
    codigo: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    severidade: Optional[str] = None
    departamento: Optional[str] = None
    setor: Optional[str] = None
    ativo: bool = True

class CausaRetrabalhoCreateCorrect(BaseModel):
    codigo: str
    descricao: Optional[str] = None
    departamento: Optional[str] = None
    setor: Optional[str] = None
    ativo: bool = True

class DescricaoAtividadeCreateCorrect(BaseModel):
    codigo: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    departamento: Optional[str] = None
    setor: Optional[str] = None
    ativo: bool = True

class AtividadeTipoCreateCorrect(BaseModel):
    nome_tipo: str
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    departamento: Optional[str] = None
    setor: Optional[str] = None
    id_tipo_maquina: Optional[int] = None
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

# ============================================================================
# ENDPOINTS DE CONFIGURAÇÃO - COMPATIBILIDADE COM FRONTEND
# ============================================================================

# Endpoint adicional para compatibilidade com frontend
@router.get("/config/departamentos", response_model=List[dict])
async def listar_departamentos_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os departamentos (endpoint de configuração)"""
    try:
        departamentos = db.query(Departamento).all()
        return [
            {
                "id": dept.id,
                "nome": dept.nome_tipo,  # Alias para compatibilidade frontend
                "nome_tipo": dept.nome_tipo,  # Campo original
                "descricao": dept.descricao,
                "ativo": dept.ativo,
                "data_criacao": dept.data_criacao,
                "data_ultima_atualizacao": dept.data_ultima_atualizacao
            }
            for dept in departamentos
        ]

    except Exception as e:
        print(f"❌ Erro ao listar departamentos (config): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar departamentos: {str(e)}"
        )

@router.post("/config/departamentos", response_model=DepartamentoResponse)
async def criar_departamento_config(
    departamento_data: DepartamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo departamento (endpoint de configuração)"""
    return criar_departamento(departamento_data, db, current_user)

@router.get("/config/departamentos/{departamento_id}", response_model=DepartamentoResponse)
async def obter_departamento_config(
    departamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter departamento por ID (endpoint de configuração)"""
    return buscar_departamento(departamento_id, db, current_user)

@router.put("/config/departamentos/{departamento_id}", response_model=DepartamentoResponse)
async def atualizar_departamento_config(
    departamento_id: int,
    departamento_data: DepartamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar departamento (endpoint de configuração)"""
    return atualizar_departamento(departamento_id, departamento_data, db, current_user)

# =============================================================================
# ENDPOINTS DE CONFIGURAÇÃO PARA SETORES
# =============================================================================

@router.get("/config/setores", response_model=List[SetorResponse])
async def listar_setores_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os setores (endpoint de configuração)"""
    return listar_setores(db, current_user)

@router.post("/config/setores", response_model=SetorResponse)
async def criar_setor_config(
    setor_data: SetorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo setor (endpoint de configuração)"""
    return criar_setor(setor_data, db, current_user)

@router.get("/config/setores/{setor_id}", response_model=SetorResponse)
async def obter_setor_config(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter setor por ID (endpoint de configuração)"""
    return buscar_setor(setor_id, db, current_user)

@router.put("/config/setores/{setor_id}", response_model=SetorResponse)
async def atualizar_setor_config(
    setor_id: int,
    setor_data: SetorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar setor (endpoint de configuração)"""
    return atualizar_setor(setor_id, setor_data, db, current_user)

@router.delete("/config/setores/{setor_id}")
async def deletar_setor_config(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar setor (endpoint de configuração)"""
    return deletar_setor(setor_id, db, current_user)

# =============================================================================
# ENDPOINTS DE CONFIGURAÇÃO PARA TIPOS DE MÁQUINA
# =============================================================================

@router.get("/config/tipos-maquina", response_model=List[dict])
async def listar_tipos_maquina_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de máquina (endpoint de configuração)"""
    return listar_tipos_maquina(db, current_user)

@router.post("/config/tipos-maquina", response_model=TipoMaquinaResponse)
async def criar_tipo_maquina_config(
    tipo_data: TipoMaquinaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de máquina (endpoint de configuração)"""
    return criar_tipo_maquina(tipo_data, db, current_user)

@router.get("/config/tipos-maquina/{tipo_id}", response_model=TipoMaquinaResponse)
async def obter_tipo_maquina_config(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter tipo de máquina por ID (endpoint de configuração)"""
    return buscar_tipo_maquina(tipo_id, db, current_user)

@router.put("/config/tipos-maquina/{tipo_id}", response_model=TipoMaquinaResponse)
async def atualizar_tipo_maquina_config(
    tipo_id: int,
    tipo_data: TipoMaquinaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de máquina (endpoint de configuração)"""
    return atualizar_tipo_maquina(tipo_id, tipo_data, db, current_user)

@router.delete("/config/tipos-maquina/{tipo_id}")
async def deletar_tipo_maquina_config(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de máquina (endpoint de configuração)"""
    return deletar_tipo_maquina(tipo_id, db, current_user)



@router.get("/departamentos", response_model=List[dict])
async def listar_departamentos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os departamentos ativos"""
    try:
        departamentos = db.query(Departamento).all()
        return [
            {
                "id": dept.id,
                "nome": dept.nome_tipo,  # Alias para compatibilidade frontend
                "nome_tipo": dept.nome_tipo,  # Campo original
                "descricao": dept.descricao,
                "ativo": dept.ativo,
                "data_criacao": dept.data_criacao,
                "data_ultima_atualizacao": dept.data_ultima_atualizacao
            }
            for dept in departamentos
        ]

    except Exception as e:
        print(f"❌ Erro ao listar departamentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar departamentos: {str(e)}"
        )





# Endpoint adicional para compatibilidade com frontend - DELETE
@router.delete("/config/departamentos/{departamento_id}")
async def deletar_departamento_config(
    departamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar departamento (endpoint de configuração)"""
    try:
        departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()

        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento com ID {departamento_id} não encontrado"
            )

        # Verificar se há setores vinculados
        setores_vinculados = db.query(Setor).filter(Setor.departamento == departamento.nome_tipo).count()
        if setores_vinculados > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível deletar o departamento. Existem {setores_vinculados} setores vinculados."
            )

        # Soft delete - marcar como inativo ao invés de deletar
        setattr(departamento, 'ativo', False)
        setattr(departamento, 'data_ultima_atualizacao', datetime.now())

        db.commit()

        return {"message": f"Departamento '{departamento.nome_tipo}' foi desativado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar departamento: {str(e)}"
        )

@router.post("/departamentos", response_model=DepartamentoResponse)
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

        # Criar novo departamento usando dados do schema
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

        return DepartamentoResponse.model_validate(novo_departamento)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar departamento: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA TIPOS DE MÁQUINA
# ============================================================================

@router.get("/tipos-maquina", response_model=List[dict])
async def listar_tipos_maquina(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de máquina ativos"""
    try:
        print("🔧 [DEBUG] Iniciando busca de tipos de máquina...")
        tipos_maquina = db.query(TipoMaquina).all()
        print(f"🔧 [DEBUG] Encontrados {len(tipos_maquina)} tipos de máquina")

        result = []
        for tm in tipos_maquina:
            print(f"🔧 [DEBUG] Processando máquina ID: {tm.id}, Nome: {tm.nome_tipo}")
            print(f"🔧 [DEBUG] campos_teste_resultado: {repr(tm.campos_teste_resultado)}")

            item = {
                "id": tm.id,
                "nome": tm.nome_tipo,  # Campo correto
                "nome_tipo": tm.nome_tipo,
                "departamento": tm.departamento,
                "setor": tm.setor,
                "categoria": tm.categoria,
                "subcategoria": tm.subcategoria,
                "descricao": tm.descricao,
                "campos_teste_resultado": tm.campos_teste_resultado or "{}",  # Garantir que não seja None
                "ativo": tm.ativo
            }
            result.append(item)
            print(f"🔧 [DEBUG] Item processado com sucesso: {item['id']}")

        print(f"🔧 [DEBUG] Retornando {len(result)} itens")
        return result

    except Exception as e:
        print(f"❌ Erro ao listar tipos de máquina: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar tipos de máquina: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA TIPOS DE TESTE
# ============================================================================

@router.get("/tipos-teste", response_model=List[TipoTesteResponse])
async def listar_tipos_teste(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de teste"""
    try:
        tipos_teste = db.query(TipoTeste).all()
        return [TipoTesteResponse.model_validate(tt) for tt in tipos_teste]

    except Exception as e:
        print(f"❌ Erro ao listar tipos de teste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar tipos de teste: {str(e)}"
        )

# Endpoints de configuração para tipos de teste
@router.get("/config/tipos-teste", response_model=List[TipoTesteResponse])
async def listar_tipos_teste_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Endpoint de compatibilidade para tipos de teste"""
    return await listar_tipos_teste(db, current_user)

@router.post("/config/tipos-teste", response_model=TipoTesteResponse)
async def criar_tipo_teste_config(
    tipo_data: TipoTesteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de teste (endpoint de configuração)"""
    return await criar_tipo_teste(tipo_data, db, current_user)

@router.get("/config/tipos-teste/{tipo_id}", response_model=TipoTesteResponse)
async def obter_tipo_teste_config(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter tipo de teste por ID (endpoint de configuração)"""
    return await buscar_tipo_teste(tipo_id, db, current_user)

@router.put("/config/tipos-teste/{tipo_id}", response_model=TipoTesteResponse)
async def atualizar_tipo_teste_config(
    tipo_id: int,
    tipo_data: TipoTesteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de teste (endpoint de configuração)"""
    return await atualizar_tipo_teste(tipo_id, tipo_data, db, current_user)

@router.delete("/config/tipos-teste/{tipo_id}")
async def deletar_tipo_teste_config(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de teste (endpoint de configuração)"""
    return await deletar_tipo_teste(tipo_id, db, current_user)

# =============================================================================
# ENDPOINTS DE CONFIGURAÇÃO PARA TIPOS DE ATIVIDADE
# =============================================================================

@router.get("/config/tipos-atividade", response_model=List[TipoAtividadeResponse])
async def listar_tipos_atividade_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de atividade (endpoint de configuração)"""
    return await listar_tipos_atividade(db, current_user)

@router.post("/config/tipos-atividade", response_model=TipoAtividadeResponse)
async def criar_tipo_atividade_config(
    atividade_data: TipoAtividadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de atividade (endpoint de configuração)"""
    return await criar_tipo_atividade(atividade_data, db, current_user)

@router.get("/config/tipos-atividade/{atividade_id}", response_model=TipoAtividadeResponse)
async def obter_tipo_atividade_config(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter tipo de atividade por ID (endpoint de configuração)"""
    return await buscar_tipo_atividade(atividade_id, db, current_user)

@router.put("/config/tipos-atividade/{atividade_id}", response_model=TipoAtividadeResponse)
async def atualizar_tipo_atividade_config(
    atividade_id: int,
    atividade_data: TipoAtividadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de atividade (endpoint de configuração)"""
    return await atualizar_tipo_atividade(atividade_id, atividade_data, db, current_user)

@router.delete("/config/tipos-atividade/{atividade_id}")
async def deletar_tipo_atividade_config(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de atividade (endpoint de configuração)"""
    return await deletar_tipo_atividade(atividade_id, db, current_user)

# =============================================================================
# ENDPOINTS DE CONFIGURAÇÃO PARA DESCRIÇÕES DE ATIVIDADE
# =============================================================================

@router.get("/config/descricoes-atividade", response_model=List[DescricaoAtividadeResponse])
async def listar_descricoes_atividade_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todas as descrições de atividade (endpoint de configuração)"""
    return await listar_descricoes_atividade(db, current_user)

@router.post("/config/descricoes-atividade", response_model=DescricaoAtividadeResponse)
async def criar_descricao_atividade_config(
    descricao_data: DescricaoAtividadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar nova descrição de atividade (endpoint de configuração)"""
    return await criar_descricao_atividade(descricao_data, db, current_user)

@router.get("/config/descricoes-atividade/{descricao_id}", response_model=DescricaoAtividadeResponse)
async def obter_descricao_atividade_config(
    descricao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter descrição de atividade por ID (endpoint de configuração)"""
    return await buscar_descricao_atividade(descricao_id, db, current_user)

@router.put("/config/descricoes-atividade/{descricao_id}", response_model=DescricaoAtividadeResponse)
async def atualizar_descricao_atividade_config(
    descricao_id: int,
    descricao_data: DescricaoAtividadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar descrição de atividade (endpoint de configuração)"""
    return await atualizar_descricao_atividade(descricao_id, descricao_data, db, current_user)

@router.delete("/config/descricoes-atividade/{descricao_id}")
async def deletar_descricao_atividade_config(
    descricao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar descrição de atividade (endpoint de configuração)"""
    return await deletar_descricao_atividade(descricao_id, db, current_user)

# =============================================================================
# ENDPOINTS DE CONFIGURAÇÃO PARA TIPOS DE FALHA
# =============================================================================

@router.get("/config/tipos-falha", response_model=List[TipoFalhaResponse])
async def listar_tipos_falha_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de falha (endpoint de configuração)"""
    return await listar_tipos_falha(db, current_user)

@router.post("/config/tipos-falha", response_model=TipoFalhaResponse)
async def criar_tipo_falha_config(
    falha_data: TipoFalhaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de falha (endpoint de configuração)"""
    return await criar_tipo_falha(falha_data, db, current_user)

@router.get("/config/tipos-falha/{falha_id}", response_model=TipoFalhaResponse)
async def obter_tipo_falha_config(
    falha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter tipo de falha por ID (endpoint de configuração)"""
    return await buscar_tipo_falha(falha_id, db, current_user)

@router.put("/config/tipos-falha/{falha_id}", response_model=TipoFalhaResponse)
async def atualizar_tipo_falha_config(
    falha_id: int,
    falha_data: TipoFalhaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de falha (endpoint de configuração)"""
    return await atualizar_tipo_falha(falha_id, falha_data, db, current_user)

@router.delete("/config/tipos-falha/{falha_id}")
async def deletar_tipo_falha_config(
    falha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de falha (endpoint de configuração)"""
    return await deletar_tipo_falha(falha_id, db, current_user)

# =============================================================================
# ENDPOINTS DE CONFIGURAÇÃO PARA CAUSAS DE RETRABALHO
# =============================================================================

@router.get("/config/causas-retrabalho", response_model=List[CausaRetrabalhoResponse])
async def listar_causas_retrabalho_config(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todas as causas de retrabalho (endpoint de configuração)"""
    return await listar_causas_retrabalho(db, current_user)

@router.post("/config/causas-retrabalho", response_model=CausaRetrabalhoResponse)
async def criar_causa_retrabalho_config(
    causa_data: CausaRetrabalhoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar nova causa de retrabalho (endpoint de configuração)"""
    return await criar_causa_retrabalho(causa_data, db, current_user)

@router.get("/config/causas-retrabalho/{causa_id}", response_model=CausaRetrabalhoResponse)
async def obter_causa_retrabalho_config(
    causa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter causa de retrabalho por ID (endpoint de configuração)"""
    return await buscar_causa_retrabalho(causa_id, db, current_user)

@router.put("/config/causas-retrabalho/{causa_id}", response_model=CausaRetrabalhoResponse)
async def atualizar_causa_retrabalho_config(
    causa_id: int,
    causa_data: CausaRetrabalhoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar causa de retrabalho (endpoint de configuração)"""
    return await atualizar_causa_retrabalho(causa_id, causa_data, db, current_user)

@router.delete("/config/causas-retrabalho/{causa_id}")
async def deletar_causa_retrabalho_config(
    causa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar causa de retrabalho (endpoint de configuração)"""
    return await deletar_causa_retrabalho(causa_id, db, current_user)

@router.get("/tipos-teste/{tipo_id}", response_model=TipoTesteResponse)
async def buscar_tipo_teste(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar tipo de teste por ID"""
    try:
        tipo_teste = db.query(TipoTeste).filter(TipoTeste.id == tipo_id).first()

        if not tipo_teste:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de teste com ID {tipo_id} não encontrado"
            )

        return TipoTesteResponse.model_validate(tipo_teste)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tipo de teste: {str(e)}"
        )

@router.post("/tipos-teste", response_model=TipoTesteResponse)
async def criar_tipo_teste(
    tipo_data: TipoTesteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de teste"""
    try:
        # Verificar se já existe
        existente = db.query(TipoTeste).filter(TipoTeste.nome == tipo_data.nome_tipo).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de teste '{tipo_data.nome_tipo}' já existe"
            )

        # Criar novo tipo de teste
        novo_tipo = TipoTeste(
            nome=tipo_data.nome_tipo,  # Usar nome_tipo do schema
            departamento=tipo_data.departamento,
            setor=tipo_data.setor,
            tipo_teste=tipo_data.tipo_teste,
            descricao=tipo_data.descricao,
            tipo_maquina=tipo_data.tipo_maquina,
            categoria=tipo_data.categoria,
            subcategoria=tipo_data.subcategoria,
            ativo=tipo_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(novo_tipo)
        db.commit()
        db.refresh(novo_tipo)

        return TipoTesteResponse.model_validate(novo_tipo)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de teste: {str(e)}"
        )

@router.put("/tipos-teste/{tipo_id}", response_model=TipoTesteResponse)
async def atualizar_tipo_teste(
    tipo_id: int,
    tipo_data: TipoTesteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de teste"""
    try:
        tipo_teste = db.query(TipoTeste).filter(TipoTeste.id == tipo_id).first()

        if not tipo_teste:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de teste com ID {tipo_id} não encontrado"
            )

        # Verificar se o novo nome já existe (se foi alterado)
        if tipo_data.nome_tipo and tipo_data.nome_tipo != tipo_teste.nome:
            existente = db.query(TipoTeste).filter(TipoTeste.nome == tipo_data.nome_tipo).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de teste '{tipo_data.nome_tipo}' já existe"
                )

        # Atualizar apenas campos fornecidos (partial update)
        update_data = tipo_data.model_dump(exclude_unset=True, by_alias=False)
        for field, value in update_data.items():
            if field == 'nome_tipo':
                setattr(tipo_teste, 'nome', value)  # Mapear nome_tipo para nome na DB
            else:
                setattr(tipo_teste, field, value)

        setattr(tipo_teste, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(tipo_teste)

        return TipoTesteResponse.model_validate(tipo_teste)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar tipo de teste: {str(e)}"
        )

@router.delete("/tipos-teste/{tipo_id}")
async def deletar_tipo_teste(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de teste (soft delete)"""
    try:
        tipo_teste = db.query(TipoTeste).filter(TipoTeste.id == tipo_id).first()

        if not tipo_teste:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de teste com ID {tipo_id} não encontrado"
            )

        # DELETE FÍSICO - apagar da database
        db.delete(tipo_teste)
        db.commit()

        return {"message": f"Tipo de teste '{tipo_teste.nome}' foi deletado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tipo de teste: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA TIPOS DE ATIVIDADE
# ============================================================================

@router.get("/tipos-atividade", response_model=List[TipoAtividadeResponse])
async def listar_tipos_atividade(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de atividade ativos"""
    try:
        tipos_atividade = db.query(TipoAtividade).all()

        # Criar lista com campos nome_tipo e nome para cada atividade
        atividades_response = []
        for ta in tipos_atividade:
            atividade_dict = {
                "id": ta.id,
                "nome_tipo": ta.nome_tipo,
                "nome": ta.nome_tipo,  # Alias para compatibilidade
                "descricao": ta.descricao,
                "departamento": ta.departamento,
                "setor": ta.setor,
                "categoria": ta.categoria,
                "ativo": ta.ativo,
                "data_criacao": ta.data_criacao,
                "data_ultima_atualizacao": ta.data_ultima_atualizacao
            }
            atividades_response.append(TipoAtividadeResponse.model_validate(atividade_dict))

        return atividades_response

    except Exception as e:
        print(f"❌ Erro ao listar tipos de atividade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar tipos de atividade: {str(e)}"
        )

@router.post("/tipos-atividade", response_model=TipoAtividadeResponse)
async def criar_tipo_atividade(
    atividade_data: TipoAtividadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de atividade"""
    try:
        # Verificar se já existe
        existente = db.query(TipoAtividade).filter(TipoAtividade.nome_tipo == atividade_data.nome_tipo).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de atividade '{atividade_data.nome_tipo}' já existe"
            )

        # Criar novo tipo de atividade
        novo_tipo = TipoAtividade(
            nome_tipo=atividade_data.nome_tipo,
            departamento=atividade_data.departamento,
            setor=atividade_data.setor,
            descricao=atividade_data.descricao,
            categoria=atividade_data.categoria,
            ativo=atividade_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(novo_tipo)
        db.commit()
        db.refresh(novo_tipo)

        return TipoAtividadeResponse.model_validate(novo_tipo)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de atividade: {str(e)}"
        )

@router.get("/tipos-atividade/{atividade_id}", response_model=TipoAtividadeResponse)
async def buscar_tipo_atividade(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar tipo de atividade por ID"""
    try:
        tipo_atividade = db.query(TipoAtividade).filter(TipoAtividade.id == atividade_id).first()

        if not tipo_atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de atividade com ID {atividade_id} não encontrado"
            )

        # Criar resposta com ambos os campos nome_tipo e nome
        atividade_dict = {
            "id": tipo_atividade.id,
            "nome_tipo": tipo_atividade.nome_tipo,
            "nome": tipo_atividade.nome_tipo,  # Alias para compatibilidade
            "descricao": tipo_atividade.descricao,
            "departamento": tipo_atividade.departamento,
            "setor": tipo_atividade.setor,
            "categoria": tipo_atividade.categoria,
            "ativo": tipo_atividade.ativo,
            "data_criacao": tipo_atividade.data_criacao,
            "data_ultima_atualizacao": tipo_atividade.data_ultima_atualizacao
        }
        return TipoAtividadeResponse.model_validate(atividade_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tipo de atividade: {str(e)}"
        )

@router.put("/tipos-atividade/{atividade_id}", response_model=TipoAtividadeResponse)
async def atualizar_tipo_atividade(
    atividade_id: int,
    atividade_data: TipoAtividadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de atividade"""
    try:
        tipo_atividade = db.query(TipoAtividade).filter(TipoAtividade.id == atividade_id).first()

        if not tipo_atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de atividade com ID {atividade_id} não encontrado"
            )

        # Verificar se o novo nome já existe (se foi alterado)
        if atividade_data.nome_tipo and atividade_data.nome_tipo != tipo_atividade.nome_tipo:
            existente = db.query(TipoAtividade).filter(TipoAtividade.nome_tipo == atividade_data.nome_tipo).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de atividade '{atividade_data.nome_tipo}' já existe"
                )

        # Atualizar campos usando setattr
        update_data = atividade_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            # Se o campo for 'nome', atualizar também 'nome_tipo'
            if field == 'nome':
                setattr(tipo_atividade, 'nome_tipo', value)
            setattr(tipo_atividade, field, value)

        setattr(tipo_atividade, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(tipo_atividade)

        # Criar resposta com ambos os campos nome_tipo e nome
        atividade_dict = {
            "id": tipo_atividade.id,
            "nome_tipo": tipo_atividade.nome_tipo,
            "nome": tipo_atividade.nome_tipo,  # Alias para compatibilidade
            "descricao": tipo_atividade.descricao,
            "departamento": tipo_atividade.departamento,
            "setor": tipo_atividade.setor,
            "categoria": tipo_atividade.categoria,
            "ativo": tipo_atividade.ativo,
            "data_criacao": tipo_atividade.data_criacao,
            "data_ultima_atualizacao": tipo_atividade.data_ultima_atualizacao
        }
        return TipoAtividadeResponse.model_validate(atividade_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar tipo de atividade: {str(e)}"
        )

@router.delete("/tipos-atividade/{atividade_id}")
async def deletar_tipo_atividade(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de atividade (soft delete)"""
    try:
        tipo_atividade = db.query(TipoAtividade).filter(TipoAtividade.id == atividade_id).first()

        if not tipo_atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de atividade com ID {atividade_id} não encontrado"
            )

        # DELETE FÍSICO - apagar da database
        db.delete(tipo_atividade)
        db.commit()

        return {"message": f"Tipo de atividade '{tipo_atividade.nome_tipo}' foi deletado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tipo de atividade: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA TIPOS DE FALHA
# ============================================================================

@router.get("/tipos-falha", response_model=List[TipoFalhaResponse])
async def listar_tipos_falha(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os tipos de falha ativos"""
    try:
        tipos_falha = db.query(TipoFalha).all()
        return [TipoFalhaResponse.model_validate(tf) for tf in tipos_falha]

    except Exception as e:
        print(f"❌ Erro ao listar tipos de falha: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar tipos de falha: {str(e)}"
        )

@router.post("/tipos-falha", response_model=TipoFalhaResponse)
async def criar_tipo_falha(
    falha_data: TipoFalhaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo tipo de falha"""
    try:
        # Verificar se já existe
        existente = db.query(TipoFalha).filter(TipoFalha.codigo == falha_data.codigo).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de falha '{falha_data.codigo}' já existe"
            )

        # Criar novo tipo de falha
        novo_tipo = TipoFalha(
            codigo=falha_data.codigo,
            departamento=falha_data.departamento,
            setor=falha_data.setor,
            descricao=falha_data.descricao,
            categoria=falha_data.categoria,
            ativo=falha_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(novo_tipo)
        db.commit()
        db.refresh(novo_tipo)

        return TipoFalhaResponse.model_validate(novo_tipo)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de falha: {str(e)}"
        )

@router.get("/tipos-falha/{falha_id}", response_model=TipoFalhaResponse)
async def buscar_tipo_falha(
    falha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar tipo de falha por ID"""
    try:
        tipo_falha = db.query(TipoFalha).filter(TipoFalha.id == falha_id).first()

        if not tipo_falha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de falha com ID {falha_id} não encontrado"
            )

        return TipoFalhaResponse.model_validate(tipo_falha)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tipo de falha: {str(e)}"
        )

@router.put("/tipos-falha/{falha_id}", response_model=TipoFalhaResponse)
async def atualizar_tipo_falha(
    falha_id: int,
    falha_data: TipoFalhaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de falha"""
    try:
        tipo_falha = db.query(TipoFalha).filter(TipoFalha.id == falha_id).first()

        if not tipo_falha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de falha com ID {falha_id} não encontrado"
            )

        # Verificar se o novo código já existe (se foi alterado)
        if falha_data.codigo and falha_data.codigo != tipo_falha.codigo:
            existente = db.query(TipoFalha).filter(TipoFalha.codigo == falha_data.codigo).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de falha '{falha_data.codigo}' já existe"
                )

        # Atualizar campos usando setattr
        update_data = falha_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tipo_falha, field, value)

        setattr(tipo_falha, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(tipo_falha)

        return TipoFalhaResponse.model_validate(tipo_falha)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar tipo de falha: {str(e)}"
        )

@router.delete("/tipos-falha/{falha_id}")
async def deletar_tipo_falha(
    falha_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de falha (soft delete)"""
    try:
        tipo_falha = db.query(TipoFalha).filter(TipoFalha.id == falha_id).first()

        if not tipo_falha:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de falha com ID {falha_id} não encontrado"
            )

        # DELETE FÍSICO - apagar da database
        db.delete(tipo_falha)
        db.commit()

        return {"message": f"Tipo de falha '{tipo_falha.codigo}' foi deletado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tipo de falha: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA CAUSAS DE RETRABALHO
# ============================================================================

@router.get("/causas-retrabalho", response_model=List[CausaRetrabalhoResponse])
async def listar_causas_retrabalho(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todas as causas de retrabalho ativas"""
    try:
        causas_retrabalho = db.query(TipoCausaRetrabalho).all()
        return [CausaRetrabalhoResponse.model_validate(cr) for cr in causas_retrabalho]

    except Exception as e:
        print(f"❌ Erro ao listar causas de retrabalho: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar causas de retrabalho: {str(e)}"
        )

@router.get("/causas-retrabalho/{causa_id}", response_model=CausaRetrabalhoResponse)
async def buscar_causa_retrabalho(
    causa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar causa de retrabalho por ID"""
    try:
        causa_retrabalho = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.id == causa_id).first()

        if not causa_retrabalho:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Causa de retrabalho com ID {causa_id} não encontrada"
            )

        return CausaRetrabalhoResponse.model_validate(causa_retrabalho)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar causa de retrabalho: {str(e)}"
        )

@router.post("/causas-retrabalho", response_model=CausaRetrabalhoResponse)
async def criar_causa_retrabalho(
    causa_data: CausaRetrabalhoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar nova causa de retrabalho"""
    try:
        # Verificar se já existe
        existente = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.codigo == causa_data.codigo).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Causa de retrabalho '{causa_data.codigo}' já existe"
            )

        # Criar nova causa de retrabalho
        nova_causa = TipoCausaRetrabalho(
            codigo=causa_data.codigo,
            descricao=causa_data.descricao,
            departamento=causa_data.departamento,
            setor=causa_data.setor,
            ativo=causa_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(nova_causa)
        db.commit()
        db.refresh(nova_causa)

        return CausaRetrabalhoResponse.model_validate(nova_causa)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar causa de retrabalho: {str(e)}"
        )

@router.put("/causas-retrabalho/{causa_id}", response_model=CausaRetrabalhoResponse)
async def atualizar_causa_retrabalho(
    causa_id: int,
    causa_data: CausaRetrabalhoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar causa de retrabalho"""
    try:
        causa_retrabalho = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.id == causa_id).first()

        if not causa_retrabalho:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Causa de retrabalho com ID {causa_id} não encontrada"
            )

        # Verificar se o novo código já existe (se foi alterado)
        if causa_data.codigo and causa_data.codigo != causa_retrabalho.codigo:
            existente = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.codigo == causa_data.codigo).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Causa de retrabalho '{causa_data.codigo}' já existe"
                )

        # Atualizar apenas campos fornecidos (partial update)
        update_data = causa_data.model_dump(exclude_unset=True, by_alias=False)
        for field, value in update_data.items():
            setattr(causa_retrabalho, field, value)

        setattr(causa_retrabalho, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(causa_retrabalho)

        return CausaRetrabalhoResponse.model_validate(causa_retrabalho)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar causa de retrabalho: {str(e)}"
        )

@router.delete("/causas-retrabalho/{causa_id}")
async def deletar_causa_retrabalho(
    causa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar causa de retrabalho (soft delete)"""
    try:
        causa_retrabalho = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.id == causa_id).first()

        if not causa_retrabalho:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Causa de retrabalho com ID {causa_id} não encontrada"
            )

        # DELETE FÍSICO - apagar da database
        db.delete(causa_retrabalho)
        db.commit()

        return {"message": f"Causa de retrabalho '{causa_retrabalho.codigo}' foi deletada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar causa de retrabalho: {str(e)}"
        )

# ============================================================================
# ENDPOINTS PARA DESCRIÇÕES DE ATIVIDADE
# ============================================================================

@router.get("/descricoes-atividade", response_model=List[DescricaoAtividadeResponse])
async def listar_descricoes_atividade(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todas as descrições de atividade ativas"""
    try:
        descricoes_atividade = db.query(TipoDescricaoAtividade).all()
        return [DescricaoAtividadeResponse.model_validate(da) for da in descricoes_atividade]

    except Exception as e:
        print(f"❌ Erro ao listar descrições de atividade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar descrições de atividade: {str(e)}"
        )

@router.post("/descricoes-atividade", response_model=DescricaoAtividadeResponse)
async def criar_descricao_atividade(
    descricao_data: DescricaoAtividadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar nova descrição de atividade"""
    try:
        # Verificar se já existe
        existente = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.codigo == descricao_data.codigo).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Descrição de atividade '{descricao_data.codigo}' já existe"
            )

        # Criar nova descrição de atividade
        nova_descricao = TipoDescricaoAtividade(
            codigo=descricao_data.codigo,
            descricao=descricao_data.descricao,
            departamento=descricao_data.departamento,
            setor=descricao_data.setor,
            categoria=descricao_data.categoria,
            ativo=descricao_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(nova_descricao)
        db.commit()
        db.refresh(nova_descricao)

        return DescricaoAtividadeResponse.model_validate(nova_descricao)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar descrição de atividade: {str(e)}"
        )

@router.get("/descricoes-atividade/{descricao_id}", response_model=DescricaoAtividadeResponse)
async def buscar_descricao_atividade(
    descricao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar descrição de atividade por ID"""
    try:
        descricao_atividade = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).first()

        if not descricao_atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Descrição de atividade com ID {descricao_id} não encontrada"
            )

        return DescricaoAtividadeResponse.model_validate(descricao_atividade)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar descrição de atividade: {str(e)}"
        )

@router.put("/descricoes-atividade/{descricao_id}", response_model=DescricaoAtividadeResponse)
async def atualizar_descricao_atividade(
    descricao_id: int,
    descricao_data: DescricaoAtividadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar descrição de atividade"""
    try:
        descricao_atividade = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).first()

        if not descricao_atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Descrição de atividade com ID {descricao_id} não encontrada"
            )

        # Verificar se o novo código já existe (se foi alterado)
        if descricao_data.codigo and descricao_data.codigo != descricao_atividade.codigo:
            existente = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.codigo == descricao_data.codigo).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Descrição de atividade '{descricao_data.codigo}' já existe"
                )

        # Atualizar campos usando setattr
        update_data = descricao_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(descricao_atividade, field, value)

        setattr(descricao_atividade, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(descricao_atividade)

        return DescricaoAtividadeResponse.model_validate(descricao_atividade)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar descrição de atividade: {str(e)}"
        )

@router.delete("/descricoes-atividade/{descricao_id}")
async def deletar_descricao_atividade(
    descricao_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar descrição de atividade (soft delete)"""
    try:
        descricao_atividade = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).first()

        if not descricao_atividade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Descrição de atividade com ID {descricao_id} não encontrada"
            )

        # DELETE FÍSICO - apagar da database
        db.delete(descricao_atividade)
        db.commit()

        return {"message": f"Descrição de atividade '{descricao_atividade.codigo}' foi deletada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar descrição de atividade: {str(e)}"
        )

# ============================================================================
# ENDPOINT PARA ESTRUTURA HIERÁRQUICA
# ============================================================================

@router.get("/estrutura-hierarquica", response_model=dict)
async def obter_estrutura_hierarquica(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Obter estrutura hierárquica completa (departamentos -> setores)"""
    try:
        # Buscar todos os departamentos
        departamentos = db.query(Departamento).filter(Departamento.ativo == True).all()

        estrutura = []
        for dept in departamentos:
            # Buscar setores do departamento
            setores = db.query(Setor).filter(
                Setor.id_departamento == dept.id,
                Setor.ativo == True
            ).all()

            dept_data = {
                "id": dept.id,
                "nome": dept.nome_tipo,
                "tipo": "departamento",
                "descricao": dept.descricao,
                "ativo": dept.ativo,
                "setores": [
                    {
                        "id": setor.id,
                        "nome": setor.nome,
                        "tipo": "setor",
                        "descricao": setor.descricao,
                        "ativo": setor.ativo,
                        "departamento_id": setor.id_departamento
                    }
                    for setor in setores
                ]
            }
            estrutura.append(dept_data)

        return {
            "estrutura": estrutura,
            "total_departamentos": len(estrutura),
            "total_setores": sum(len(dept["setores"]) for dept in estrutura),
            "data_consulta": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Erro ao obter estrutura hierárquica: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estrutura hierárquica: {str(e)}"
        )

@router.get("/departamentos/{departamento_id}", response_model=DepartamentoResponse)
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

        # Criar resposta com ambos os campos nome_tipo e nome
        dept_dict = {
            "id": departamento.id,
            "nome_tipo": departamento.nome_tipo,
            "nome": departamento.nome_tipo,  # Alias para compatibilidade
            "descricao": departamento.descricao,
            "ativo": departamento.ativo,
            "data_criacao": departamento.data_criacao,
            "data_ultima_atualizacao": departamento.data_ultima_atualizacao
        }
        return DepartamentoResponse.model_validate(dept_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar departamento: {str(e)}"
        )

@router.put("/departamentos/{departamento_id}", response_model=DepartamentoResponse)
async def atualizar_departamento(
    departamento_id: int,
    departamento_data: DepartamentoUpdate,
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
        if departamento_data.nome_tipo:
            existente = db.query(Departamento).filter(
                Departamento.nome_tipo == departamento_data.nome_tipo,
                Departamento.id != departamento_id
            ).first()

            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Departamento '{departamento_data.nome_tipo}' já existe"
                )

        # Atualizar apenas campos fornecidos (partial update)
        update_data = departamento_data.model_dump(exclude_unset=True, by_alias=False)
        for field, value in update_data.items():
            # Se o campo for 'nome', atualizar também 'nome_tipo'
            if field == 'nome':
                setattr(departamento, 'nome_tipo', value)
            setattr(departamento, field, value)

        # Atualizar timestamp usando setattr para evitar problemas de tipo
        setattr(departamento, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(departamento)

        # Criar resposta com ambos os campos nome_tipo e nome
        dept_dict = {
            "id": departamento.id,
            "nome_tipo": departamento.nome_tipo,
            "nome": departamento.nome_tipo,  # Alias para compatibilidade
            "descricao": departamento.descricao,
            "ativo": departamento.ativo,
            "data_criacao": departamento.data_criacao,
            "data_ultima_atualizacao": departamento.data_ultima_atualizacao
        }
        return DepartamentoResponse.model_validate(dept_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
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
    """Deletar departamento (soft delete - marca como inativo)"""
    try:
        # Buscar departamento
        departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()

        if not departamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Departamento com ID {departamento_id} não encontrado"
            )



        # DELETE FÍSICO - apagar da database
        db.delete(departamento)
        db.commit()

        return {
            "message": f"Departamento '{departamento.nome_tipo}' deletado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar departamento: {str(e)}"
        )

@router.post("/setores", response_model=SetorResponse)
async def criar_setor(
    setor_data: SetorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo setor"""
    try:
        # Verificar se já existe setor com mesmo nome no mesmo departamento
        existente = db.query(Setor).filter(
            Setor.nome == setor_data.nome,
            Setor.id_departamento == setor_data.id_departamento
        ).first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Setor '{setor_data.nome}' já existe no departamento especificado"
            )

        # Validar se departamento existe e está ativo usando ID
        if not validate_departamento_exists_by_id(db, setor_data.id_departamento):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Departamento com ID {setor_data.id_departamento} não encontrado ou inativo"
            )

        # Obter nome do departamento para compatibilidade
        departamento_nome = get_departamento_nome_by_id(db, setor_data.id_departamento)

        # Criar novo setor
        novo_setor = Setor(
            nome=setor_data.nome,
            departamento=departamento_nome,  # Campo de compatibilidade
            descricao=setor_data.descricao,
            ativo=setor_data.ativo,
            id_departamento=setor_data.id_departamento,
            area_tipo=setor_data.area_tipo,
            supervisor_responsavel=getattr(setor_data, 'supervisor_responsavel', None),
            permite_apontamento=setor_data.permite_apontamento,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(novo_setor)
        db.commit()
        db.refresh(novo_setor)

        # Retornar com schema tipado e nome do departamento
        setor_response = SetorResponse.model_validate(novo_setor)
        setor_response.departamento = departamento_nome

        return setor_response

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar setor: {str(e)}"
        )

@router.get("/setores/{setor_id}", response_model=SetorResponse)
async def buscar_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar setor por ID"""
    try:
        setor = db.query(Setor).filter(Setor.id == setor_id).first()

        if not setor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setor com ID {setor_id} não encontrado"
            )

        # Criar resposta com todos os campos necessários
        setor_dict = {
            "id": setor.id,
            "nome": setor.nome,
            "descricao": setor.descricao,
            "ativo": setor.ativo,
            "area_tipo": setor.area_tipo,
            "tipo_area": setor.area_tipo,  # Alias para compatibilidade
            "permite_apontamento": setor.permite_apontamento,
            "id_departamento": setor.id_departamento,
            "departamento": setor.departamento,  # Nome do departamento
            "data_criacao": setor.data_criacao,
            "data_ultima_atualizacao": setor.data_ultima_atualizacao
        }

        # Enriquecer com nome do departamento se necessário
        departamento_id = getattr(setor, 'id_departamento', None)
        if departamento_id is not None:
            dept_nome = get_departamento_nome_by_id(db, departamento_id)
            setor_dict["departamento"] = dept_nome

        return SetorResponse.model_validate(setor_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar setor: {str(e)}"
        )

@router.put("/setores/{setor_id}", response_model=SetorResponse)
async def atualizar_setor(
    setor_id: int,
    setor_data: SetorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar setor"""
    try:
        setor = db.query(Setor).filter(Setor.id == setor_id).first()

        if not setor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setor com ID {setor_id} não encontrado"
            )

        # Verificar se o novo nome já existe no mesmo departamento (exceto para o próprio setor)
        if setor_data.nome and setor_data.id_departamento:
            existente = db.query(Setor).filter(
                Setor.nome == setor_data.nome,
                Setor.id_departamento == setor_data.id_departamento,
                Setor.id != setor_id
            ).first()

            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Setor '{setor_data.nome}' já existe no departamento especificado"
                )

        # Validar departamento se fornecido usando ID
        if setor_data.id_departamento and not validate_departamento_exists_by_id(db, setor_data.id_departamento):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Departamento com ID {setor_data.id_departamento} não encontrado ou inativo"
            )

        # Atualizar apenas campos fornecidos (partial update)
        update_data = setor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(setor, field, value)

        # Atualizar campo de compatibilidade se departamento mudou
        if setor_data.id_departamento:
            departamento_nome = get_departamento_nome_by_id(db, setor_data.id_departamento)
            setattr(setor, 'departamento', departamento_nome)

        setattr(setor, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(setor)

        # Retornar com nome do departamento
        setor_response = SetorResponse.model_validate(setor)
        departamento_id = getattr(setor, 'id_departamento', None)
        if departamento_id is not None:
            dept_nome = get_departamento_nome_by_id(db, departamento_id)
            setor_response.departamento = dept_nome

        return setor_response

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar setor: {str(e)}"
        )

@router.delete("/setores/{setor_id}", response_model=Dict[str, Any])
async def deletar_setor(
    setor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar setor (soft delete - marca como inativo)"""
    try:
        # Buscar setor
        setor = db.query(Setor).filter(Setor.id == setor_id).first()

        if not setor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Setor com ID {setor_id} não encontrado"
            )



        # DELETE FÍSICO - apagar da database
        db.delete(setor)
        db.commit()

        return {
            "message": f"Setor '{setor.nome}' deletado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar setor: {str(e)}"
        )

@router.get("/tipos-maquina/{tipo_id}", response_model=TipoMaquinaResponse)
async def buscar_tipo_maquina(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Buscar tipo de máquina por ID"""
    try:
        tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_id).first()

        if not tipo_maquina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de máquina com ID {tipo_id} não encontrado"
            )

        # Criar resposta com ambos os campos nome_tipo e nome
        tipo_dict = {
            "id": tipo_maquina.id,
            "nome_tipo": tipo_maquina.nome_tipo,
            "nome": tipo_maquina.nome_tipo,  # Alias para compatibilidade
            "categoria": tipo_maquina.categoria,
            "subcategoria": tipo_maquina.subcategoria,
            "setor": tipo_maquina.setor,
            "ativo": tipo_maquina.ativo,
            "data_criacao": tipo_maquina.data_criacao,
            "data_ultima_atualizacao": tipo_maquina.data_ultima_atualizacao
        }
        return TipoMaquinaResponse.model_validate(tipo_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tipo de máquina: {str(e)}"
        )

@router.post("/tipos-maquina", response_model=TipoMaquinaResponse)
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

        # Converter subcategoria para JSON se necessário
        subcategoria_json = None
        if tipo_data.subcategoria:
            import json
            subcategoria_json = json.dumps(tipo_data.subcategoria)

        # Criar novo tipo de máquina
        novo_tipo = TipoMaquina(
            nome_tipo=tipo_data.nome_tipo,
            departamento=tipo_data.departamento,
            setor=tipo_data.setor,
            categoria=tipo_data.categoria,
            subcategoria=subcategoria_json,  # Armazenar como JSON
            descricao=tipo_data.descricao,
            id_departamento=tipo_data.id_departamento,
            ativo=tipo_data.ativo,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )

        db.add(novo_tipo)
        db.commit()
        db.refresh(novo_tipo)

        # Retornar com schema tipado
        return TipoMaquinaResponse.model_validate(novo_tipo)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de máquina: {str(e)}"
        )

@router.put("/tipos-maquina/{tipo_id}", response_model=TipoMaquinaResponse)
async def atualizar_tipo_maquina(
    tipo_id: int,
    tipo_data: TipoMaquinaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar tipo de máquina"""
    try:
        tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_id).first()

        if not tipo_maquina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de máquina com ID {tipo_id} não encontrado"
            )

        # Verificar se o novo nome já existe (se foi alterado)
        if tipo_data.nome_tipo and tipo_data.nome_tipo != tipo_maquina.nome_tipo:
            existente = db.query(TipoMaquina).filter(TipoMaquina.nome_tipo == tipo_data.nome_tipo).first()
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de máquina '{tipo_data.nome_tipo}' já existe"
                )

        # Atualizar campos
        update_data = tipo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'subcategoria':
                if value and isinstance(value, list):
                    import json
                    setattr(tipo_maquina, field, json.dumps(value))
                elif isinstance(value, str):
                    setattr(tipo_maquina, field, value)
                else:
                    setattr(tipo_maquina, field, None)
            else:
                setattr(tipo_maquina, field, value)

        setattr(tipo_maquina, 'data_ultima_atualizacao', datetime.now())

        db.commit()
        db.refresh(tipo_maquina)

        # Criar resposta com ambos os campos nome_tipo e nome
        tipo_dict = {
            "id": tipo_maquina.id,
            "nome_tipo": tipo_maquina.nome_tipo,
            "nome": tipo_maquina.nome_tipo,  # Alias para compatibilidade
            "categoria": tipo_maquina.categoria,
            "subcategoria": tipo_maquina.subcategoria,
            "setor": tipo_maquina.setor,
            "ativo": tipo_maquina.ativo,
            "data_criacao": tipo_maquina.data_criacao,
            "data_ultima_atualizacao": tipo_maquina.data_ultima_atualizacao
        }
        return TipoMaquinaResponse.model_validate(tipo_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar tipo de máquina: {str(e)}"
        )

@router.delete("/tipos-maquina/{tipo_id}")
async def deletar_tipo_maquina(
    tipo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar tipo de máquina (soft delete)"""
    try:
        tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_id).first()

        if not tipo_maquina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de máquina com ID {tipo_id} não encontrado"
            )

        # DELETE FÍSICO - apagar da database
        db.delete(tipo_maquina)
        db.commit()

        return {"message": f"Tipo de máquina '{tipo_maquina.nome_tipo}' foi deletado com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar tipo de máquina: {str(e)}"
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

@router.get("/setores", response_model=List[SetorResponse])
async def listar_setores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os setores ativos com informações do departamento (otimizado com JOIN)"""
    try:
        # Query otimizada com JOIN para evitar múltiplas consultas - apenas setores ativos
        setores_query = db.query(
            Setor,
            Departamento.nome_tipo.label('departamento_nome')
        ).outerjoin(
            Departamento, Setor.id_departamento == Departamento.id
        ).all()

        # Construir resposta com dados já carregados
        setores_enriched = []
        for setor, departamento_nome in setores_query:
            setor_data = SetorResponse.model_validate(setor)
            setor_data.departamento = departamento_nome
            setores_enriched.append(setor_data)

        return setores_enriched

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
            "GET /departamentos - Listar departamentos",
            "POST /departamentos - Criar departamento",
            "GET /departamentos/{id} - Buscar departamento",
            "PUT /departamentos/{id} - Atualizar departamento",
            "DELETE /departamentos/{id} - Deletar departamento",
            "GET /setores - Listar setores",
            "POST /setores - Criar setor",
            "GET /setores/{id} - Buscar setor",
            "PUT /setores/{id} - Atualizar setor",
            "DELETE /setores/{id} - Deletar setor",
            "POST /tipos-maquina - Criar tipo de máquina",
            "POST /tipos-teste - Criar tipo de teste",
            "POST /clientes - Criar cliente",
            "POST /equipamentos - Criar equipamento",
            "GET /sistema - Configurações do sistema"
        ],
        "privilege_required": "ADMIN",
        "current_user": {
            "email": current_user.email,
            "privilege_level": current_user.privilege_level
        }
    }

# ============================================================================
# ENDPOINTS DE MONITORAMENTO DE SCRAPING - PAINEL ADMINISTRATIVO
# ============================================================================

@router.get("/scraping/dashboard", operation_id="admin_scraping_dashboard")
async def get_scraping_dashboard(
    days: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard completo de monitoramento de scraping para administradores
    Inclui estatísticas, gráficos e métricas de performance
    """
    # Verificar se é admin
    if current_user.privilege_level not in ['ADMIN', 'GESTAO']:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")

    try:
        # Verificar se módulo de scraping está disponível
        if not SCRAPING_AVAILABLE:
            return {"error": "Módulo de estatísticas não disponível"}

        # Obter estatísticas detalhadas
        stats = {}
        queue_status = {}

        if get_scraping_statistics and callable(get_scraping_statistics):
            try:
                stats = get_scraping_statistics(days)
            except Exception as e:
                print(f"Erro ao obter estatísticas: {e}")
                stats = {}

        if get_queue_status and callable(get_queue_status):
            try:
                queue_status = get_queue_status()
            except Exception as e:
                print(f"Erro ao obter status da fila: {e}")
                queue_status = {}

        # Estatísticas adicionais do banco
        from sqlalchemy import text

        # Total de OS no sistema
        total_os = db.execute(text("SELECT COUNT(*) FROM ordens_servico")).scalar() or 0

        # OS criadas via scraping (últimos X dias)
        try:
            os_scraping_sql = text("""
            SELECT COUNT(*) FROM ordens_servico
            WHERE observacoes_gerais LIKE '%scraping%'
            AND data_criacao >= datetime('now', '-{} days')
            """.format(days))
            os_via_scraping = db.execute(os_scraping_sql).scalar() or 0
        except Exception as e:
            print(f"Erro ao consultar OS via scraping: {e}")
            os_via_scraping = 0

        # Usuários mais ativos no scraping
        try:
            usuarios_ativos_sql = text("""
            SELECT u.nome_completo, u.email, u.departamento, COUNT(s.id) as total_requests
            FROM scraping_usage_stats s
            JOIN usuarios u ON s.user_id = u.id
            WHERE s.created_at >= datetime('now', '-{} days')
            GROUP BY s.user_id, u.nome_completo, u.email, u.departamento
            ORDER BY total_requests DESC
            LIMIT 10
            """.format(days))

            usuarios_ativos = db.execute(usuarios_ativos_sql).fetchall()
        except Exception as e:
            print(f"Erro ao consultar usuários ativos: {e}")
            usuarios_ativos = []

        # Horários de maior uso
        try:
            horarios_uso_sql = text("""
            SELECT strftime('%H', created_at) as hora, COUNT(*) as requests
            FROM scraping_usage_stats
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY strftime('%H', created_at)
            ORDER BY hora
            """.format(days))

            horarios_uso = db.execute(horarios_uso_sql).fetchall()
        except Exception as e:
            print(f"Erro ao consultar horários de uso: {e}")
            horarios_uso = []

        return {
            "dashboard_data": {
                "periodo_dias": days,
                "timestamp": datetime.now().isoformat(),
                "estatisticas_gerais": stats.get("general_stats", {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "success_rate": 0.0,
                    "avg_processing_time": 0.0
                }),
                "status_fila": queue_status if queue_status else {
                    "workers_online": 0,
                    "active_tasks": 0,
                    "scheduled_tasks": 0
                },
                "metricas_sistema": {
                    "total_os_sistema": total_os,
                    "os_via_scraping_periodo": os_via_scraping,
                    "percentual_scraping": round((os_via_scraping / total_os * 100) if total_os > 0 else 0, 2)
                },
                "usuarios_mais_ativos": [
                    {
                        "nome": row[0],
                        "email": row[1],
                        "departamento": row[2],
                        "total_requests": row[3]
                    }
                    for row in usuarios_ativos
                ],
                "horarios_maior_uso": [
                    {
                        "hora": f"{row[0]}:00",
                        "requests": row[1]
                    }
                    for row in horarios_uso
                ],
                "estatisticas_usuarios": stats.get("user_stats", []),
                "estatisticas_diarias": stats.get("daily_stats", []),
                "estatisticas_lotes": stats.get("batch_stats", []),
                "top_os_consultadas": stats.get("top_os", [])
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dashboard: {str(e)}")

@router.get("/scraping/users-ranking", operation_id="admin_scraping_users_ranking")
async def get_users_scraping_ranking(
    days: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ranking detalhado de usuários por uso do scraping
    """
    if current_user.privilege_level not in ['ADMIN', 'GESTAO']:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")

    try:
        from sqlalchemy import text

        # Ranking completo de usuários
        try:
            ranking_sql = text("""
            SELECT
                u.nome_completo,
                u.email,
                u.departamento,
                u.privilege_level,
                COUNT(s.id) as total_requests,
                SUM(CASE WHEN s.success = 1 THEN 1 ELSE 0 END) as successful_requests,
                SUM(CASE WHEN s.success = 0 THEN 1 ELSE 0 END) as failed_requests,
                AVG(s.processing_time) as avg_processing_time,
                MAX(s.created_at) as last_usage,
                MIN(s.created_at) as first_usage
            FROM scraping_usage_stats s
            JOIN tipo_usuarios u ON s.user_id = u.id
            WHERE s.created_at >= datetime('now', '-{} days')
            GROUP BY s.user_id, u.nome_completo, u.email, u.departamento, u.privilege_level
            ORDER BY total_requests DESC
            """.format(days))

            ranking = db.execute(ranking_sql).fetchall()
        except Exception as e:
            print(f"Erro ao consultar ranking de usuários: {e}")
            ranking = []

        return {
            "ranking_usuarios": [
                {
                    "posicao": idx + 1,
                    "nome": row[0],
                    "email": row[1],
                    "departamento": row[2],
                    "nivel_privilegio": row[3],
                    "total_requests": row[4],
                    "successful_requests": row[5],
                    "failed_requests": row[6],
                    "success_rate": round((row[5] / row[4] * 100) if row[4] > 0 else 0, 2),
                    "avg_processing_time": round(row[7], 2) if row[7] else 0,
                    "last_usage": row[8],
                    "first_usage": row[9],
                    "dias_usando": (datetime.now() - datetime.fromisoformat(row[9].replace('Z', '+00:00'))).days if row[9] else 0
                }
                for idx, row in enumerate(ranking)
            ],
            "periodo_dias": days,
            "total_usuarios": len(ranking)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter ranking: {str(e)}")

@router.get("/scraping/performance-metrics", operation_id="admin_scraping_performance")
async def get_scraping_performance_metrics(
    days: int = 30,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Métricas detalhadas de performance do scraping
    """
    if current_user.privilege_level not in ['ADMIN', 'GESTAO']:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")

    try:
        from sqlalchemy import text

        # Métricas de performance por hora do dia
        performance_hora_sql = text("""
        SELECT
            strftime('%H', created_at) as hora,
            COUNT(*) as total_requests,
            AVG(processing_time) as avg_time,
            MIN(processing_time) as min_time,
            MAX(processing_time) as max_time,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
        FROM scraping_usage_stats
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY strftime('%H', created_at)
        ORDER BY hora
        """.format(days))

        performance_hora = db.execute(performance_hora_sql).fetchall()

        # Métricas de performance por dia da semana
        performance_dia_sql = text("""
        SELECT
            CASE strftime('%w', created_at)
                WHEN '0' THEN 'Domingo'
                WHEN '1' THEN 'Segunda'
                WHEN '2' THEN 'Terça'
                WHEN '3' THEN 'Quarta'
                WHEN '4' THEN 'Quinta'
                WHEN '5' THEN 'Sexta'
                WHEN '6' THEN 'Sábado'
            END as dia_semana,
            COUNT(*) as total_requests,
            AVG(processing_time) as avg_time,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
        FROM scraping_usage_stats
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY strftime('%w', created_at)
        ORDER BY strftime('%w', created_at)
        """.format(days))

        performance_dia = db.execute(performance_dia_sql).fetchall()

        # OS com mais tentativas de scraping
        os_mais_tentativas_sql = text("""
        SELECT
            os_number,
            COUNT(*) as tentativas,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as sucessos,
            AVG(processing_time) as avg_time
        FROM scraping_usage_stats
        WHERE created_at >= datetime('now', '-{} days')
        GROUP BY os_number
        HAVING tentativas > 1
        ORDER BY tentativas DESC
        LIMIT 20
        """.format(days))

        os_mais_tentativas = db.execute(os_mais_tentativas_sql).fetchall()

        return {
            "performance_por_hora": [
                {
                    "hora": f"{row[0]}:00",
                    "total_requests": row[1],
                    "avg_time": round(row[2], 2) if row[2] else 0,
                    "min_time": round(row[3], 2) if row[3] else 0,
                    "max_time": round(row[4], 2) if row[4] else 0,
                    "success_rate": round((row[5] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in performance_hora
            ],
            "performance_por_dia_semana": [
                {
                    "dia_semana": row[0],
                    "total_requests": row[1],
                    "avg_time": round(row[2], 2) if row[2] else 0,
                    "success_rate": round((row[3] / row[1] * 100) if row[1] > 0 else 0, 2)
                }
                for row in performance_dia
            ],
            "os_mais_tentativas": [
                {
                    "os_number": row[0],
                    "tentativas": row[1],
                    "sucessos": row[2],
                    "success_rate": round((row[2] / row[1] * 100) if row[1] > 0 else 0, 2),
                    "avg_time": round(row[3], 2) if row[3] else 0
                }
                for row in os_mais_tentativas
            ],
            "periodo_dias": days
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter métricas: {str(e)}")
