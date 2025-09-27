"""
Catalogs Routes - Versão Simplificada
=====================================

Versão simplificada das rotas de catálogos que não depende de modelos removidos.
Todas as funcionalidades foram temporariamente desabilitadas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
import json

from config.database_config import get_db
from app.dependencies import get_current_user
from app.database_models import Usuario, TipoMaquina

router = APIRouter()

# =============================================================================
# ENDPOINT PARA CATEGORIAS DE MÁQUINA
# =============================================================================

@router.get("/categorias-maquina")
def get_categorias_maquina(db: Session = Depends(get_db)):
    """Busca todas as categorias únicas de máquinas da tabela tipos_maquina"""
    try:
        # Buscar categorias únicas da tabela tipos_maquina
        categorias_query = db.query(distinct(TipoMaquina.categoria)).filter(
            TipoMaquina.categoria.isnot(None),
            TipoMaquina.categoria != ''
        ).all()

        # Extrair apenas os valores das categorias
        categorias = [categoria[0] for categoria in categorias_query if categoria[0]]
        categorias.sort()  # Ordenar alfabeticamente

        return {
            "categorias": categorias,
            "total": len(categorias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias de máquina: {str(e)}")

# =============================================================================
# ENDPOINTS DESABILITADOS - MODELOS REMOVIDOS
# =============================================================================

@router.get("/tipo-atividade")
async def get_tipos_atividade(
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity types, optionally filtered by sector and department"""
    try:
        from app.database_models import TipoAtividade
        query = db.query(TipoAtividade).filter(TipoAtividade.ativo.is_(True))
        
        if setor:
            query = query.filter(TipoAtividade.setor == setor)
        
        if departamento:
            query = query.filter(TipoAtividade.departamento == departamento)
        
        tipos = query.all()
        
        return [
            {
                "id": tipo.id,
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "setor": tipo.setor,
                "departamento": tipo.departamento,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao,
                "data_ultima_atualizacao": tipo.data_ultima_atualizacao,
                "id_tipo_maquina": tipo.id_tipo_maquina
            }
            for tipo in tipos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de atividade: {str(e)}")

@router.post("/tipo-atividade")
async def create_tipo_atividade(
    tipo_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new activity type"""
    try:
        from app.database_models import TipoAtividade
        
        # Validação básica dos dados
        required_fields = ["nome_tipo", "setor", "departamento"]
        for field in required_fields:
            if field not in tipo_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo obrigatório faltando: {field}"
                )
        
        novo_tipo = TipoAtividade(
            nome_tipo=tipo_data["nome_tipo"],
            descricao=tipo_data.get("descricao", ""),
            setor=tipo_data["setor"],
            departamento=tipo_data["departamento"],
            categoria=tipo_data.get("categoria", ""),
            id_tipo_maquina=tipo_data.get("id_tipo_maquina"),
            ativo=tipo_data.get("ativo", True)
        )
        
        db.add(novo_tipo)
        db.commit()
        db.refresh(novo_tipo)
        
        return {
            "message": "Tipo de atividade criado com sucesso",
            "success": True,
            "data": {
                "id": novo_tipo.id,
                "nome_tipo": novo_tipo.nome_tipo,
                "descricao": novo_tipo.descricao,
                "setor": novo_tipo.setor,
                "departamento": novo_tipo.departamento,
                "ativo": novo_tipo.ativo
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de atividade: {str(e)}"
        )

@router.get("/descricao-atividade")
async def get_descricoes_atividade(
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity descriptions, optionally filtered by sector"""
    from app.database_models import TipoDescricaoAtividade
    query = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.ativo.is_(None) | (TipoDescricaoAtividade.ativo.is_(True)))

    if setor:
        query = query.filter(TipoDescricaoAtividade.setor == setor)

    descricoes = query.all()

    return [
        {
            "id": descricao.id,
            "codigo": descricao.codigo,
            "descricao": descricao.descricao,
            "setor": descricao.setor,
            "ativo": descricao.ativo
        }
        for descricao in descricoes
    ]

@router.post("/descricao-atividade")
async def create_descricao_atividade(
    descricao_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new activity description"""
    try:
        from app.database_models import TipoDescricaoAtividade

        # Validação básica dos dados
        required_fields = ["codigo", "descricao", "setor"]
        for field in required_fields:
            if field not in descricao_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo obrigatório faltando: {field}"
                )

        nova_descricao = TipoDescricaoAtividade(
            codigo=descricao_data["codigo"],
            descricao=descricao_data["descricao"],
            setor=descricao_data["setor"],
            ativo=descricao_data.get("ativo", True)
        )
        
        db.add(nova_descricao)
        db.commit()
        db.refresh(nova_descricao)
        
        return {
            "message": "Descrição de atividade criada com sucesso",
            "success": True,
            "data": {
                "id": nova_descricao.id,
                "codigo": nova_descricao.codigo,
                "descricao": nova_descricao.descricao,
                "setor": nova_descricao.setor,
                "ativo": nova_descricao.ativo
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar descrição de atividade: {str(e)}"
        )

@router.get("/tipo-falha")
async def get_tipos_falha(
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get failure types from TipoFalha model"""
    try:
        from app.database_models import TipoFalha
        query = db.query(TipoFalha).filter(TipoFalha.ativo.is_(True))
        
        if setor:
            query = query.filter(TipoFalha.setor == setor)
        
        if departamento:
            query = query.filter(TipoFalha.departamento == departamento)
        
        tipos_falha = query.all()
        
        return [
            {
                "id": falha.id,
                "codigo": falha.codigo,
                "descricao": falha.descricao,
                "setor": falha.setor,
                "departamento": falha.departamento,
                "ativo": falha.ativo,
                "data_criacao": falha.data_criacao,
                "data_ultima_atualizacao": falha.data_ultima_atualizacao
            }
            for falha in tipos_falha
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar tipos de falha: {str(e)}"
        )

@router.post("/tipo-falha")
async def create_tipo_falha(
    falha_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new failure type"""
    try:
        from app.database_models import TipoFalha
        
        # Validação básica dos dados
        required_fields = ["codigo", "descricao", "setor", "departamento"]
        for field in required_fields:
            if field not in falha_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Campo obrigatório faltando: {field}"
                )
        
        nova_falha = TipoFalha(
            codigo=falha_data["codigo"],
            descricao=falha_data["descricao"],
            setor=falha_data["setor"],
            departamento=falha_data["departamento"],
            categoria=falha_data.get("categoria", ""),
            ativo=falha_data.get("ativo", True)
        )
        
        db.add(nova_falha)
        db.commit()
        db.refresh(nova_falha)
        
        return {
            "message": "Tipo de falha criado com sucesso",
            "success": True,
            "data": {
                "id": nova_falha.id,
                "codigo": nova_falha.codigo,
                "descricao": nova_falha.descricao,
                "setor": nova_falha.setor,
                "departamento": nova_falha.departamento,
                "ativo": nova_falha.ativo
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tipo de falha: {str(e)}"
        )

@router.get("/subtipo-maquina")
async def get_subtipos_maquina(
    tipo_id: Optional[int] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get machine subtypes
    NOTA: Funcionalidade temporariamente desabilitada - CatalogoMaquinaSubTipo removido
    """
    return {
        "message": "Funcionalidade desabilitada - CatalogoMaquinaSubTipo removido do modelo",
        "data": [],
        "status": "DISABLED"
    }

@router.post("/subtipo-maquina")
async def create_subtipo_maquina(
    subtipo_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add subcategoria to existing TipoMaquina"""
    try:
        from app.database_models import TipoMaquina
        import json

        tipo_maquina_id = subtipo_data.get("tipo_maquina_id")
        nova_subcategoria = subtipo_data.get("nome")

        if not tipo_maquina_id or not nova_subcategoria:
            raise HTTPException(status_code=400, detail="tipo_maquina_id e nome são obrigatórios")

        tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_maquina_id).first()
        if not tipo_maquina:
            raise HTTPException(status_code=404, detail="Tipo de máquina não encontrado")

        # Atualizar subcategorias
        subcategorias_atuais = []
        if tipo_maquina.subcategoria:
            try:
                subcategorias_atuais = json.loads(tipo_maquina.subcategoria)
            except:
                subcategorias_atuais = [tipo_maquina.subcategoria]

        if nova_subcategoria not in subcategorias_atuais:
            subcategorias_atuais.append(nova_subcategoria)
            tipo_maquina.subcategoria = json.dumps(subcategorias_atuais)  # type: ignore
            db.commit()

        return {
            "message": "Subcategoria adicionada com sucesso",
            "success": True,
            "subcategoria": nova_subcategoria
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar subcategoria: {str(e)}")

# =============================================================================
# ENDPOINTS DE STATUS E INFORMAÇÃO
# =============================================================================

@router.get("/status")
async def get_catalogs_status(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of all catalog endpoints"""
    return {
        "catalogs_status": {
            "tipo_atividade": "DISABLED - CatalogoAtividadeTipo removido",
            "descricao_atividade": "DISABLED - CatalogoAtividadeDescricao removido",
            "tipo_falha": "DISABLED - CatalogoFalhaLaboratorioTipo removido",
            "subtipo_maquina": "DISABLED - CatalogoMaquinaSubTipo removido"
        },
        "message": "Todos os catálogos foram temporariamente desabilitados devido à limpeza do banco de dados",
        "available_models": [
            "Usuario", "OrdemServico", "Programacao", "Pendencia", 
            "ApontamentoDetalhado", "Departamento", "Setor", 
            "TipoMaquina", "TipoTeste", "TipoCausaRetrabalho"
        ],
        "removed_models": [
            "CatalogoAtividadeTipo", "CatalogoAtividadeDescricao",
            "CatalogoFalhaLaboratorioTipo", "CatalogoMaquinaSubTipo",
            "StatusSetor", "TesteContexto", "ResultadoTesteDetalhado",
            "TesteSetor"
        ]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for catalogs service"""
    return {
        "status": "OK",
        "service": "catalogs_simple",
        "message": "Serviço de catálogos simplificado funcionando",
        "note": "Funcionalidades principais desabilitadas - modelos removidos"
    }

# =============================================================================
# ENDPOINTS ALTERNATIVOS USANDO MODELOS DISPONÍVEIS
# =============================================================================

@router.get("/departamentos")
async def get_departamentos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available departments from Departamento model"""
    try:
        from app.database_models import Departamento
        departamentos = db.query(Departamento).filter(Departamento.ativo.is_(True)).all()
        
        return [
            {
                "id": dept.id,
                "nome_tipo": dept.nome_tipo,
                "descricao": dept.descricao,
                "ativo": dept.ativo,
                "data_criacao": dept.data_criacao
            }
            for dept in departamentos
        ]
    except Exception as e:
        return {
            "message": f"Erro ao buscar departamentos: {str(e)}",
            "data": [],
            "status": "ERROR"
        }

@router.get("/setores")
async def get_setores(
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available sectors from Setor model"""
    try:
        from app.database_models import Setor, Departamento
        query = db.query(Setor).filter(Setor.ativo.is_(True))

        if departamento:
            # Join with Departamento to filter by department name
            query = query.join(Departamento, Setor.id_departamento == Departamento.id)\
                        .filter(Departamento.nome_tipo == departamento)

        setores = query.all()

        result = []
        for setor in setores:
            # Buscar nome do departamento
            departamento_nome = None
            if setor.id_departamento is not None:
                dept_obj = db.query(Departamento).filter(Departamento.id == setor.id_departamento).first()
                if dept_obj:
                    departamento_nome = dept_obj.nome_tipo

            result.append({
                "id": setor.id,
                "nome": setor.nome,
                "descricao": setor.descricao,
                "id_departamento": setor.id_departamento,
                "departamento": departamento_nome,
                "ativo": setor.ativo,
                "data_criacao": setor.data_criacao
            })

        return result
    except Exception as e:
        print(f"Erro ao buscar setores: {e}")
        return {
            "message": f"Erro ao buscar setores: {str(e)}",
            "data": [],
            "status": "ERROR"
        }

@router.get("/tipos-maquina")
async def get_tipos_maquina(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available machine types from TipoMaquina model"""
    try:
        from app.database_models import TipoMaquina
        tipos = db.query(TipoMaquina).filter(TipoMaquina.ativo.is_(True)).all()
        
        return [
            {
                "id": tipo.id,
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "departamento": tipo.departamento,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao
            }
            for tipo in tipos
        ]
    except Exception as e:
        return {
            "message": f"Erro ao buscar tipos de máquina: {str(e)}",
            "data": [],
            "status": "ERROR"
        }

@router.get("/tipos-teste")
async def get_tipos_teste(
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available test types from TipoTeste model"""
    try:
        from app.database_models import TipoTeste
        query = db.query(TipoTeste).filter(TipoTeste.ativo.is_(True))
        
        if setor:
            query = query.filter(TipoTeste.setor == setor)
        
        if departamento:
            query = query.filter(TipoTeste.departamento == departamento)
        
        tipos = query.all()
        
        return [
            {
                "id": tipo.id,
                "nome": tipo.nome,
                "descricao": tipo.descricao,
                "tipo_teste": tipo.tipo_teste,
                "departamento": tipo.departamento,
                "setor": tipo.setor,
                "categoria": tipo.categoria,
                "subcategoria": tipo.subcategoria,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao
            }
            for tipo in tipos
        ]
    except Exception as e:
        return {
            "message": f"Erro ao buscar tipos de teste: {str(e)}",
            "data": [],
            "status": "ERROR"
        }
