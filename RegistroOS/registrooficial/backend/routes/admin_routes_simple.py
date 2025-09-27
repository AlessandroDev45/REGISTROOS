"""
Admin Routes - Versão Simplificada
==================================

Versão simplificada das rotas de administração que usa apenas os modelos disponíveis.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.database_models import TipoMaquina, Setor as DBSetor, TipoTeste, TipoCausaRetrabalho as CausaRetrabalho, TipoFalha, Departamento, Usuario, TipoAtividade, TipoDescricaoAtividade
from sqlalchemy import distinct
from app.dependencies import get_current_user
from config.database_config import get_db

router = APIRouter(tags=["admin"])

# =============================================================================
# ENDPOINTS PARA DEPARTAMENTOS
# =============================================================================

@router.get("/departamentos/", response_model=List[Dict[str, Any]], operation_id="admin_get_departamentos_slash")
@router.get("/departamentos", response_model=List[Dict[str, Any]], operation_id="admin_get_departamentos")
def read_departamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os departamentos"""
    departamentos = db.query(Departamento).offset(skip).limit(limit).all()
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

@router.post("/departamentos/", response_model=Dict[str, Any], operation_id="admin_post_departamentos")
def create_departamento(departamento_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo departamento"""
    try:
        # Verificar se já existe
        existing = db.query(Departamento).filter(Departamento.nome_tipo == departamento_data.get("nome_tipo")).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Departamento '{departamento_data.get('nome_tipo')}' já existe")

        db_departamento = Departamento(**departamento_data)
        db.add(db_departamento)
        db.commit()
        db.refresh(db_departamento)
        return {
            "id": db_departamento.id,
            "nome_tipo": db_departamento.nome_tipo,
            "descricao": db_departamento.descricao,
            "ativo": db_departamento.ativo,
            "data_criacao": db_departamento.data_criacao
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar departamento: {str(e)}")

@router.get("/departamentos/{departamento_id}", response_model=Dict[str, Any], operation_id="admin_get_departamentos_departamento_id")
def read_departamento(departamento_id: int, db: Session = Depends(get_db)):
    """Busca um departamento por ID"""
    db_departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if db_departamento is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return {
        "id": db_departamento.id,
        "nome_tipo": db_departamento.nome_tipo,
        "descricao": db_departamento.descricao,
        "ativo": db_departamento.ativo,
        "data_criacao": db_departamento.data_criacao
    }

@router.put("/departamentos/{departamento_id}", response_model=Dict[str, Any], operation_id="admin_put_departamentos_departamento_id")
def update_departamento(departamento_id: int, departamento_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza um departamento"""
    db_departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if db_departamento is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    
    for key, value in departamento_data.items():
        setattr(db_departamento, key, value)
    
    db.commit()
    db.refresh(db_departamento)
    return {
        "id": db_departamento.id,
        "nome_tipo": db_departamento.nome_tipo,
        "descricao": db_departamento.descricao,
        "ativo": db_departamento.ativo,
        "data_criacao": db_departamento.data_criacao
    }

@router.delete("/departamentos/{departamento_id}", operation_id="admin_delete_departamentos_departamento_id")
def delete_departamento(departamento_id: int, db: Session = Depends(get_db)):
    """Deleta um departamento (soft delete)"""
    db_departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if db_departamento is None:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")

    db.query(Departamento).filter(Departamento.id == departamento_id).update({"ativo": False})
    db.commit()
    return {"message": "Departamento desativado com sucesso"}

# =============================================================================
# ENDPOINTS PARA SETORES
# =============================================================================

@router.get("/setores/", response_model=List[Dict[str, Any]], operation_id="admin_get_setores")
def read_setores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os setores"""
    setores = db.query(DBSetor).offset(skip).limit(limit).all()
    return [
        {
            "id": setor.id,
            "nome": setor.nome,
            "descricao": setor.descricao,
            "id_departamento": setor.id_departamento,
            "departamento": setor.departamento_obj.nome_tipo if setor.departamento_obj else setor.departamento,  # Usar relacionamento primeiro, fallback para campo string
            "ativo": setor.ativo,
            "permite_apontamento": setor.permite_apontamento,
            "area_tipo": setor.area_tipo,
            "data_criacao": setor.data_criacao
        }
        for setor in setores
    ]

@router.post("/setores/", response_model=Dict[str, Any], operation_id="admin_post_setores")
def create_setor(setor_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo setor"""
    try:
        # Verificar se já existe
        existing = db.query(DBSetor).filter(DBSetor.nome == setor_data.get("nome")).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Setor '{setor_data.get('nome')}' já existe")

        db_setor = DBSetor(**setor_data)
        db.add(db_setor)
        db.commit()
        db.refresh(db_setor)
        return {
            "id": db_setor.id,
            "nome": db_setor.nome,
            "descricao": db_setor.descricao,
            "id_departamento": db_setor.id_departamento,
            "departamento": db_setor.departamento_obj.nome_tipo if db_setor.departamento_obj else db_setor.departamento,  # Usar relacionamento primeiro
            "ativo": db_setor.ativo,
            "permite_apontamento": db_setor.permite_apontamento,
            "area_tipo": db_setor.area_tipo,
            "data_criacao": db_setor.data_criacao
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar setor: {str(e)}")

@router.get("/setores/{setor_id}", response_model=Dict[str, Any], operation_id="admin_get_setores_setor_id")
def read_setor(setor_id: int, db: Session = Depends(get_db)):
    """Busca um setor por ID"""
    db_setor = db.query(DBSetor).filter(DBSetor.id == setor_id).first()
    if db_setor is None:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    return {
        "id": db_setor.id,
        "nome": db_setor.nome,
        "descricao": db_setor.descricao,
        "id_departamento": db_setor.id_departamento,
        "departamento": db_setor.departamento_obj.nome_tipo if db_setor.departamento_obj else None,  # Nome do departamento
        "ativo": db_setor.ativo,
        "permite_apontamento": db_setor.permite_apontamento,
        "area_tipo": db_setor.area_tipo,
        "data_criacao": db_setor.data_criacao
    }

@router.put("/setores/{setor_id}", response_model=Dict[str, Any], operation_id="admin_put_setores_setor_id")
def update_setor(setor_id: int, setor_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza um setor"""
    db_setor = db.query(DBSetor).filter(DBSetor.id == setor_id).first()
    if db_setor is None:
        raise HTTPException(status_code=404, detail="Setor não encontrado")
    
    for key, value in setor_data.items():
        setattr(db_setor, key, value)
    
    db.commit()
    db.refresh(db_setor)
    return {
        "id": db_setor.id,
        "nome": db_setor.nome,
        "descricao": db_setor.descricao,
        "id_departamento": db_setor.id_departamento,
        "departamento": db_setor.departamento.nome_tipo if db_setor.departamento else None,  # type: ignore # Nome do departamento
        "ativo": db_setor.ativo,
        "permite_apontamento": db_setor.permite_apontamento,
        "area_tipo": db_setor.area_tipo,
        "data_criacao": db_setor.data_criacao
    }

@router.delete("/setores/{setor_id}", operation_id="admin_delete_setores_setor_id")
def delete_setor(setor_id: int, db: Session = Depends(get_db)):
    """Deleta um setor (soft delete)"""
    db_setor = db.query(DBSetor).filter(DBSetor.id == setor_id).first()
    if db_setor is None:
        raise HTTPException(status_code=404, detail="Setor não encontrado")

    db.query(DBSetor).filter(DBSetor.id == setor_id).update({"ativo": False})
    db.commit()
    return {"message": "Setor desativado com sucesso"}

# =============================================================================
# ENDPOINTS PARA TIPOS DE MÁQUINA
# =============================================================================

@router.get("/tipos-maquina/", response_model=List[Dict[str, Any]], operation_id="admin_get_tipos_maquina_slash")
@router.get("/tipos-maquina", response_model=List[Dict[str, Any]], operation_id="admin_get_tipos_maquina")
def admin_read_tipos_maquina(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    categoria: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os tipos de máquina, opcionalmente filtrados por departamento, setor e categoria"""
    print(f"🔍 Admin: FUNÇÃO CHAMADA! Buscando tipos de máquina...")
    print(f"🔍 Admin: Parâmetros - dept: {departamento}, setor: {setor}, categoria: {categoria}")

    # Usar consulta SQL direta para evitar problemas com o modelo
    try:
        from sqlalchemy import text
        sql = text("SELECT id, nome_tipo, categoria, descricao, ativo, data_criacao, departamento, setor FROM tipos_maquina WHERE ativo = 1 ORDER BY nome_tipo")
        result_proxy = db.execute(sql)
        tipos_maquina_raw = result_proxy.fetchall()

        print(f"🔍 Admin: Encontrados {len(tipos_maquina_raw)} tipos de máquina via SQL")

        result = []
        for tm in tipos_maquina_raw:
            result.append({
                "id": tm[0],
                "nome_tipo": tm[1],
                "categoria": tm[2],
                "descricao": tm[3] or "",
                "ativo": tm[4],
                "data_criacao": tm[5],
                "departamento": tm[6],
                "setor": tm[7],
                "subcategoria": None,
                "id_departamento": None
            })

        print(f"🔍 Admin: Retornando {len(result)} tipos de máquina")
        return result

    except Exception as e:
        print(f"❌ Admin: Erro na consulta SQL: {e}")
        # Fallback para o método original
        pass

    query = db.query(TipoMaquina).filter(TipoMaquina.ativo == 1)
    print(f"🔍 Admin: Query criada")

    # Filtrar por departamento se especificado
    if departamento:
        query = query.filter(TipoMaquina.departamento == departamento)

    # Filtrar por setor se especificado
    if setor:
        query = query.filter(TipoMaquina.setor == setor)

    # Filtrar por categoria se especificado
    if categoria:
        query = query.filter(TipoMaquina.categoria == categoria)

    try:
        tipos_maquina = query.offset(skip).limit(limit).all()
        print(f"🔍 Admin: Encontrados {len(tipos_maquina)} tipos de máquina")
        result = []

        for tm in tipos_maquina:
            # Tratar subcategoria JSON com segurança
            subcategoria = None
            try:
                subcategoria_raw = getattr(tm, 'subcategoria', None)
                if subcategoria_raw:
                    if isinstance(subcategoria_raw, str):
                        subcategoria = json.loads(subcategoria_raw)
                    else:
                        subcategoria = subcategoria_raw
            except (json.JSONDecodeError, TypeError):
                subcategoria = None

            result.append({
                "id": tm.id,
                "nome_tipo": tm.nome_tipo,
                "descricao": tm.descricao,
                "categoria": tm.categoria,
                "subcategoria": subcategoria,
                "id_departamento": tm.id_departamento,
                "departamento": getattr(tm, 'departamento', None),
                "setor": getattr(tm, 'setor', None),
                "ativo": tm.ativo,
                "data_criacao": tm.data_criacao
            })

        return result
    except Exception as e:
        print(f"❌ Erro ao buscar tipos de máquina: {e}")
        return []

@router.post("/tipos-maquina/", response_model=Dict[str, Any], operation_id="admin_post_tipos_maquina")
def create_tipo_maquina(tipo_maquina_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo tipo de máquina"""
    try:
        # Validar dados obrigatórios
        nome_tipo = tipo_maquina_data.get("nome_tipo")
        if not nome_tipo or nome_tipo.strip() == "":
            raise HTTPException(status_code=400, detail="Nome do tipo de máquina é obrigatório")

        # Verificar se já existe
        existing = db.query(TipoMaquina).filter(TipoMaquina.nome_tipo == nome_tipo).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Tipo de máquina '{nome_tipo}' já existe")

        # Preparar dados com valores padrão
        clean_data = {
            "nome_tipo": nome_tipo.strip(),
            "descricao": tipo_maquina_data.get("descricao", "").strip() if tipo_maquina_data.get("descricao") else "",
            "categoria": tipo_maquina_data.get("categoria", "").strip() if tipo_maquina_data.get("categoria") else "",
            "ativo": tipo_maquina_data.get("ativo", True),
            "data_criacao": datetime.now(),
            "data_ultima_atualizacao": datetime.now()
        }

        # Adicionar id_departamento se fornecido e válido
        id_departamento = tipo_maquina_data.get("id_departamento")
        if id_departamento and str(id_departamento).strip() != "":
            try:
                clean_data["id_departamento"] = int(id_departamento)
            except (ValueError, TypeError):
                pass  # Ignorar valores inválidos

        # Adicionar campos opcionais se fornecidos
        for field in ["especificacoes_tecnicas", "campos_teste_resultado", "setor", "departamento", "subcategoria"]:
            value = tipo_maquina_data.get(field)
            if value and str(value).strip() != "":
                clean_data[field] = str(value).strip()

        db_tipo_maquina = TipoMaquina(**clean_data)
        db.add(db_tipo_maquina)
        db.commit()
        db.refresh(db_tipo_maquina)

        return {
            "id": db_tipo_maquina.id,
            "nome_tipo": db_tipo_maquina.nome_tipo,
            "descricao": db_tipo_maquina.descricao,
            "categoria": db_tipo_maquina.categoria,
            "subcategoria": getattr(db_tipo_maquina, 'subcategoria', None),
            "departamento": getattr(db_tipo_maquina, 'departamento', None),
            "setor": getattr(db_tipo_maquina, 'setor', None),
            "id_departamento": db_tipo_maquina.id_departamento,
            "ativo": db_tipo_maquina.ativo,
            "especificacoes_tecnicas": getattr(db_tipo_maquina, 'especificacoes_tecnicas', None),
            "campos_teste_resultado": getattr(db_tipo_maquina, 'campos_teste_resultado', None),
            "data_criacao": db_tipo_maquina.data_criacao,
            "data_ultima_atualizacao": getattr(db_tipo_maquina, 'data_ultima_atualizacao', None)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar tipo de máquina: {str(e)}")

@router.get("/tipos-maquina/{tipo_maquina_id}", response_model=Dict[str, Any], operation_id="admin_get_tipos_maquina_tipo_maquina_id")
def admin_read_tipo_maquina_by_id(tipo_maquina_id: int, db: Session = Depends(get_db)):
    """Busca um tipo de máquina por ID"""
    db_tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_maquina_id).first()
    if db_tipo_maquina is None:
        raise HTTPException(status_code=404, detail="Tipo de máquina não encontrado")
    return {"id": db_tipo_maquina.id, "nome_tipo": db_tipo_maquina.nome_tipo, "descricao": db_tipo_maquina.descricao}

@router.put("/tipos-maquina/{tipo_maquina_id}", response_model=Dict[str, Any], operation_id="admin_put_tipos_maquina_tipo_maquina_id")
def update_tipo_maquina(tipo_maquina_id: int, tipo_maquina_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza um tipo de máquina"""
    db_tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_maquina_id).first()
    if db_tipo_maquina is None:
        raise HTTPException(status_code=404, detail="Tipo de máquina não encontrado")
    
    for key, value in tipo_maquina_data.items():
        setattr(db_tipo_maquina, key, value)
    
    db.commit()
    db.refresh(db_tipo_maquina)
    return {
        "id": db_tipo_maquina.id,
        "nome_tipo": db_tipo_maquina.nome_tipo,
        "descricao": db_tipo_maquina.descricao,
        "categoria": db_tipo_maquina.categoria,
        "subcategoria": getattr(db_tipo_maquina, 'subcategoria', None),
        "departamento": getattr(db_tipo_maquina, 'departamento', None),
        "setor": getattr(db_tipo_maquina, 'setor', None),
        "id_departamento": db_tipo_maquina.id_departamento,
        "ativo": db_tipo_maquina.ativo,
        "especificacoes_tecnicas": getattr(db_tipo_maquina, 'especificacoes_tecnicas', None),
        "campos_teste_resultado": getattr(db_tipo_maquina, 'campos_teste_resultado', None),
        "data_criacao": db_tipo_maquina.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_maquina, 'data_ultima_atualizacao', None)
    }

@router.delete("/tipos-maquina/{tipo_maquina_id}", operation_id="admin_delete_tipos_maquina_tipo_maquina_id")
def delete_tipo_maquina(tipo_maquina_id: int, db: Session = Depends(get_db)):
    """Deleta um tipo de máquina (soft delete)"""
    db_tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == tipo_maquina_id).first()
    if db_tipo_maquina is None:
        raise HTTPException(status_code=404, detail="Tipo de máquina não encontrado")

    db.query(TipoMaquina).filter(TipoMaquina.id == tipo_maquina_id).update({"ativo": False})
    db.commit()
    return {"message": "Tipo de máquina desativado com sucesso"}

# =============================================================================
# ENDPOINTS PARA TIPOS DE TESTE
# =============================================================================

@router.get("/tipos-teste/", response_model=List[Dict[str, Any]], operation_id="admin_get_tipos_teste")
def read_tipos_teste(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os tipos de teste"""
    tipos_teste = db.query(TipoTeste).offset(skip).limit(limit).all()
    return [
        {
            "id": tt.id,
            "nome": tt.nome,
            "departamento": getattr(tt, 'departamento', None),
            "setor": getattr(tt, 'setor', None),
            "descricao": tt.descricao,
            "tipo_teste": tt.tipo_teste,
            "tipo_maquina": getattr(tt, 'tipo_maquina', None),
            "categoria": getattr(tt, 'categoria', None),
            "subcategoria": getattr(tt, 'subcategoria', None),
            "exclusivo_setor": getattr(tt, 'exclusivo_setor', None),
            "visivel_desenvolvimento": getattr(tt, 'visivel_desenvolvimento', None),
            "descricao_exclusiva": getattr(tt, 'descricao_exclusiva', None),
            "teste_exclusivo_setor": getattr(tt, 'teste_exclusivo_setor', None),
            "descricao_teste_exclusivo": getattr(tt, 'descricao_teste_exclusivo', None),
            "ativo": tt.ativo,
            "data_criacao": tt.data_criacao,
            "data_ultima_atualizacao": getattr(tt, 'data_ultima_atualizacao', None)
        }
        for tt in tipos_teste
    ]

@router.post("/tipos-teste/", response_model=Dict[str, Any], operation_id="admin_post_tipos_teste")
def create_tipo_teste(tipo_teste_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo tipo de teste"""
    try:
        # Verificar se já existe
        existing = db.query(TipoTeste).filter(TipoTeste.nome == tipo_teste_data.get("nome")).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Tipo de teste '{tipo_teste_data.get('nome')}' já existe")

        db_tipo_teste = TipoTeste(**tipo_teste_data)
        db.add(db_tipo_teste)
        db.commit()
        db.refresh(db_tipo_teste)
        return {
            "id": db_tipo_teste.id,
            "nome": db_tipo_teste.nome,
            "departamento": getattr(db_tipo_teste, 'departamento', None),
            "setor": getattr(db_tipo_teste, 'setor', None),
            "descricao": db_tipo_teste.descricao,
            "tipo_teste": db_tipo_teste.tipo_teste,
            "tipo_maquina": getattr(db_tipo_teste, 'tipo_maquina', None),
            "categoria": getattr(db_tipo_teste, 'categoria', None),
            "subcategoria": getattr(db_tipo_teste, 'subcategoria', None),
            "exclusivo_setor": getattr(db_tipo_teste, 'exclusivo_setor', None),
            "visivel_desenvolvimento": getattr(db_tipo_teste, 'visivel_desenvolvimento', None),
            "descricao_exclusiva": getattr(db_tipo_teste, 'descricao_exclusiva', None),
            "teste_exclusivo_setor": getattr(db_tipo_teste, 'teste_exclusivo_setor', None),
            "descricao_teste_exclusivo": getattr(db_tipo_teste, 'descricao_teste_exclusivo', None),
            "ativo": db_tipo_teste.ativo,
            "data_criacao": db_tipo_teste.data_criacao,
            "data_ultima_atualizacao": getattr(db_tipo_teste, 'data_ultima_atualizacao', None)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar tipo de teste: {str(e)}")

@router.get("/tipos-teste/{tipo_teste_id}", response_model=Dict[str, Any], operation_id="admin_get_tipos_teste_tipo_teste_id")
def read_tipo_teste(tipo_teste_id: int, db: Session = Depends(get_db)):
    """Busca um tipo de teste por ID"""
    db_tipo_teste = db.query(TipoTeste).filter(TipoTeste.id == tipo_teste_id).first()
    if db_tipo_teste is None:
        raise HTTPException(status_code=404, detail="Tipo de teste não encontrado")
    return {
        "id": db_tipo_teste.id,
        "nome": db_tipo_teste.nome,
        "descricao": db_tipo_teste.descricao,
        "tipo_teste": db_tipo_teste.tipo_teste,
        "tipo_maquina": getattr(db_tipo_teste, 'tipo_maquina', None),
        "categoria": getattr(db_tipo_teste, 'categoria', None),
        "subcategoria": getattr(db_tipo_teste, 'subcategoria', None),
        "teste_exclusivo_setor": getattr(db_tipo_teste, 'teste_exclusivo_setor', None),
        "descricao_teste_exclusivo": getattr(db_tipo_teste, 'descricao_teste_exclusivo', None),
        "ativo": db_tipo_teste.ativo,
        "data_criacao": db_tipo_teste.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_teste, 'data_ultima_atualizacao', None)
    }

@router.put("/tipos-teste/{tipo_teste_id}", response_model=Dict[str, Any], operation_id="admin_put_tipos_teste_tipo_teste_id")
def update_tipo_teste(tipo_teste_id: int, tipo_teste_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza um tipo de teste"""
    db_tipo_teste = db.query(TipoTeste).filter(TipoTeste.id == tipo_teste_id).first()
    if db_tipo_teste is None:
        raise HTTPException(status_code=404, detail="Tipo de teste não encontrado")
    
    for key, value in tipo_teste_data.items():
        setattr(db_tipo_teste, key, value)
    
    db.commit()
    db.refresh(db_tipo_teste)
    return {
        "id": db_tipo_teste.id,
        "nome": db_tipo_teste.nome,
        "descricao": db_tipo_teste.descricao,
        "tipo_teste": db_tipo_teste.tipo_teste,
        "tipo_maquina": getattr(db_tipo_teste, 'tipo_maquina', None),
        "categoria": getattr(db_tipo_teste, 'categoria', None),
        "subcategoria": getattr(db_tipo_teste, 'subcategoria', None),
        "teste_exclusivo_setor": getattr(db_tipo_teste, 'teste_exclusivo_setor', None),
        "descricao_teste_exclusivo": getattr(db_tipo_teste, 'descricao_teste_exclusivo', None),
        "ativo": db_tipo_teste.ativo,
        "data_criacao": db_tipo_teste.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_teste, 'data_ultima_atualizacao', None)
    }

@router.delete("/tipos-teste/{tipo_teste_id}", operation_id="admin_delete_tipos_teste_tipo_teste_id")
def delete_tipo_teste(tipo_teste_id: int, db: Session = Depends(get_db)):
    """Deleta um tipo de teste (soft delete)"""
    db_tipo_teste = db.query(TipoTeste).filter(TipoTeste.id == tipo_teste_id).first()
    if db_tipo_teste is None:
        raise HTTPException(status_code=404, detail="Tipo de teste não encontrado")

    db.query(TipoTeste).filter(TipoTeste.id == tipo_teste_id).update({"ativo": False})
    db.commit()
    return {"message": "Tipo de teste desativado com sucesso"}

# =============================================================================
# ENDPOINTS PARA CAUSAS DE RETRABALHO
# =============================================================================

@router.get("/causas-retrabalho/", response_model=List[Dict[str, Any]], operation_id="admin_get_causas_retrabalho_slash")
@router.get("/causas-retrabalho", response_model=List[Dict[str, Any]], operation_id="admin_get_causas_retrabalho")
def admin_read_causas_retrabalho(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    categoria: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todas as causas de retrabalho, opcionalmente filtradas por departamento, setor e categoria"""
    query = db.query(CausaRetrabalho).filter(CausaRetrabalho.ativo.is_(True))

    # Filtrar por departamento se especificado
    if departamento:
        query = query.filter(CausaRetrabalho.departamento == departamento)

    # Filtrar por setor se especificado
    if setor:
        query = query.filter(CausaRetrabalho.setor == setor)

    # Filtrar por categoria se especificado (se existir no modelo)
    if categoria and hasattr(CausaRetrabalho, 'categoria'):
        query = query.filter(CausaRetrabalho.categoria == categoria)

    causas = query.offset(skip).limit(limit).all()
    return [
        {
            "id": causa.id,
            "codigo": causa.codigo,
            "descricao": causa.descricao,
            "id_departamento": causa.id_departamento,
            "departamento": getattr(causa, 'departamento', None),
            "setor": getattr(causa, 'setor', None),
            "categoria": getattr(causa, 'categoria', None),
            "ativo": causa.ativo,
            "data_criacao": causa.data_criacao,
            "data_ultima_atualizacao": getattr(causa, 'data_ultima_atualizacao', None)
        }
        for causa in causas
    ]

@router.post("/causas-retrabalho/", response_model=Dict[str, Any], operation_id="admin_post_causas_retrabalho")
def create_causa_retrabalho(causa_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria uma nova causa de retrabalho"""
    try:
        # Verificar se já existe
        existing = db.query(CausaRetrabalho).filter(CausaRetrabalho.codigo == causa_data.get("codigo")).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Causa de retrabalho '{causa_data.get('codigo')}' já existe")

        db_causa = CausaRetrabalho(**causa_data)
        db.add(db_causa)
        db.commit()
        db.refresh(db_causa)
        return {
            "id": db_causa.id,
            "codigo": db_causa.codigo,
            "descricao": db_causa.descricao,
            "departamento": getattr(db_causa, 'departamento', None),
            "setor": getattr(db_causa, 'setor', None),
            "id_departamento": db_causa.id_departamento,
            "ativo": db_causa.ativo,
            "data_criacao": db_causa.data_criacao,
            "data_ultima_atualizacao": getattr(db_causa, 'data_ultima_atualizacao', None)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar causa de retrabalho: {str(e)}")

@router.get("/causas-retrabalho/{causa_id}", response_model=Dict[str, Any], operation_id="admin_get_causas_retrabalho_causa_id")
def admin_read_causa_retrabalho_by_id(causa_id: int, db: Session = Depends(get_db)):
    """Busca uma causa de retrabalho por ID"""
    db_causa = db.query(CausaRetrabalho).filter(CausaRetrabalho.id == causa_id).first()
    if db_causa is None:
        raise HTTPException(status_code=404, detail="Causa de retrabalho não encontrada")
    return {
        "id": db_causa.id,
        "codigo": db_causa.codigo,
        "descricao": db_causa.descricao,
        "id_departamento": db_causa.id_departamento,
        "ativo": db_causa.ativo,
        "data_criacao": db_causa.data_criacao,
        "data_ultima_atualizacao": getattr(db_causa, 'data_ultima_atualizacao', None)
    }

@router.put("/causas-retrabalho/{causa_id}", response_model=Dict[str, Any], operation_id="admin_put_causas_retrabalho_causa_id")
def update_causa_retrabalho(causa_id: int, causa_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza uma causa de retrabalho"""
    db_causa = db.query(CausaRetrabalho).filter(CausaRetrabalho.id == causa_id).first()
    if db_causa is None:
        raise HTTPException(status_code=404, detail="Causa de retrabalho não encontrada")

    for key, value in causa_data.items():
        setattr(db_causa, key, value)

    db.commit()
    db.refresh(db_causa)
    return {
        "id": db_causa.id,
        "codigo": db_causa.codigo,
        "descricao": db_causa.descricao,
        "departamento": getattr(db_causa, 'departamento', None),
        "setor": getattr(db_causa, 'setor', None),
        "id_departamento": db_causa.id_departamento,
        "ativo": db_causa.ativo,
        "data_criacao": db_causa.data_criacao,
        "data_ultima_atualizacao": getattr(db_causa, 'data_ultima_atualizacao', None)
    }

@router.delete("/causas-retrabalho/{causa_id}", operation_id="admin_delete_causas_retrabalho_causa_id")
def delete_causa_retrabalho(causa_id: int, db: Session = Depends(get_db)):
    """Deleta uma causa de retrabalho (soft delete)"""
    db_causa = db.query(CausaRetrabalho).filter(CausaRetrabalho.id == causa_id).first()
    if db_causa is None:
        raise HTTPException(status_code=404, detail="Causa de retrabalho não encontrada")

    db.query(CausaRetrabalho).filter(CausaRetrabalho.id == causa_id).update({"ativo": False})
    db.commit()
    return {"message": "Causa de retrabalho desativada com sucesso"}

# =============================================================================
# ENDPOINTS DESABILITADOS - MODELOS REMOVIDOS
# =============================================================================

@router.get("/tipos-atividade/", operation_id="admin_get_tipos_atividade_slash")
@router.get("/tipos-atividade", operation_id="admin_get_tipos_atividade")
def admin_read_tipos_atividade(
    tipo_maquina: Optional[str] = None,
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os tipos de atividade, opcionalmente filtrados por tipo de máquina, departamento e setor"""

    query = db.query(TipoAtividade).filter(TipoAtividade.ativo.is_(True))

    # Filtrar por tipo de máquina se especificado
    if tipo_maquina:
        # Buscar ID do tipo de máquina pelo nome
        tipo_maq = db.query(TipoMaquina).filter(TipoMaquina.nome_tipo == tipo_maquina).first()
        if tipo_maq:
            query = query.filter(TipoAtividade.id_tipo_maquina == tipo_maq.id)

    # Filtrar por departamento se especificado
    if departamento:
        query = query.filter(TipoAtividade.departamento == departamento)

    # Filtrar por setor se especificado
    if setor:
        query = query.filter(TipoAtividade.setor == setor)

    tipos = query.offset(skip).limit(limit).all()
    return [
        {
            "id": tipo.id,
            "nome_tipo": tipo.nome_tipo,
            "descricao": tipo.descricao,
            "ativo": tipo.ativo,
            "id_tipo_maquina": tipo.id_tipo_maquina,
            "data_criacao": tipo.data_criacao,
            "categoria": getattr(tipo, 'categoria', None),
            "departamento": getattr(tipo, 'departamento', None),
            "setor": getattr(tipo, 'setor', None),
            "id_departamento": getattr(tipo, 'id_departamento', None)
        }
        for tipo in tipos
    ]

@router.post("/tipos-atividade/", response_model=Dict[str, Any], operation_id="admin_post_tipos_atividade")
def create_tipo_atividade(tipo_atividade_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo tipo de atividade"""
    try:
        # Validar dados obrigatórios
        nome_tipo = tipo_atividade_data.get("nome_tipo")
        if not nome_tipo or nome_tipo.strip() == "":
            raise HTTPException(status_code=400, detail="Nome do tipo de atividade é obrigatório")

        # Verificar se já existe
        existing = db.query(TipoAtividade).filter(TipoAtividade.nome_tipo == nome_tipo).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Tipo de atividade '{nome_tipo}' já existe")

        # Preparar dados com valores padrão
        clean_data = {
            "nome_tipo": nome_tipo.strip(),
            "descricao": tipo_atividade_data.get("descricao", "").strip() if tipo_atividade_data.get("descricao") else "",
            "categoria": tipo_atividade_data.get("categoria", "").strip() if tipo_atividade_data.get("categoria") else "",
            "ativo": tipo_atividade_data.get("ativo", True),
            "data_criacao": datetime.now(),
            "data_ultima_atualizacao": datetime.now()
        }

        # Adicionar campos de departamento e setor
        departamento = tipo_atividade_data.get("departamento")
        if departamento and str(departamento).strip() != "":
            clean_data["departamento"] = str(departamento).strip()

        setor = tipo_atividade_data.get("setor")
        if setor and str(setor).strip() != "":
            clean_data["setor"] = str(setor).strip()

        # Buscar id_departamento se departamento foi fornecido
        if departamento:
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                clean_data["id_departamento"] = dept_obj.id

        # Adicionar id_tipo_maquina se fornecido e válido
        id_tipo_maquina = tipo_atividade_data.get("id_tipo_maquina")
        if id_tipo_maquina and str(id_tipo_maquina).strip() != "":
            try:
                clean_data["id_tipo_maquina"] = int(id_tipo_maquina)
            except (ValueError, TypeError):
                pass  # Ignorar valores inválidos

        db_tipo_atividade = TipoAtividade(**clean_data)
        db.add(db_tipo_atividade)
        db.commit()
        db.refresh(db_tipo_atividade)

        return {
            "id": db_tipo_atividade.id,
            "nome_tipo": db_tipo_atividade.nome_tipo,
            "descricao": db_tipo_atividade.descricao,
            "categoria": db_tipo_atividade.categoria,
            "departamento": getattr(db_tipo_atividade, 'departamento', None),
            "setor": getattr(db_tipo_atividade, 'setor', None),
            "id_departamento": getattr(db_tipo_atividade, 'id_departamento', None),
            "ativo": db_tipo_atividade.ativo,
            "id_tipo_maquina": db_tipo_atividade.id_tipo_maquina,
            "data_criacao": db_tipo_atividade.data_criacao,
            "data_ultima_atualizacao": getattr(db_tipo_atividade, 'data_ultima_atualizacao', None)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar tipo de atividade: {str(e)}")

@router.get("/tipos-atividade/{tipo_atividade_id}", response_model=Dict[str, Any], operation_id="admin_get_tipos_atividade_tipo_atividade_id")
def admin_read_tipo_atividade_by_id(tipo_atividade_id: int, db: Session = Depends(get_db)):
    """Busca um tipo de atividade por ID"""
    db_tipo_atividade = db.query(TipoAtividade).filter(TipoAtividade.id == tipo_atividade_id).first()
    if db_tipo_atividade is None:
        raise HTTPException(status_code=404, detail="Tipo de atividade não encontrado")
    return {
        "id": db_tipo_atividade.id,
        "nome_tipo": db_tipo_atividade.nome_tipo,
        "descricao": db_tipo_atividade.descricao,
        "categoria": db_tipo_atividade.categoria,
        "ativo": db_tipo_atividade.ativo,
        "id_tipo_maquina": db_tipo_atividade.id_tipo_maquina,
        "data_criacao": db_tipo_atividade.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_atividade, 'data_ultima_atualizacao', None)
    }

@router.put("/tipos-atividade/{tipo_atividade_id}", response_model=Dict[str, Any], operation_id="admin_put_tipos_atividade_tipo_atividade_id")
def update_tipo_atividade(tipo_atividade_id: int, tipo_atividade_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza um tipo de atividade"""
    db_tipo_atividade = db.query(TipoAtividade).filter(TipoAtividade.id == tipo_atividade_id).first()
    if db_tipo_atividade is None:
        raise HTTPException(status_code=404, detail="Tipo de atividade não encontrado")

    for key, value in tipo_atividade_data.items():
        setattr(db_tipo_atividade, key, value)

    db.commit()
    db.refresh(db_tipo_atividade)
    return {
        "id": db_tipo_atividade.id,
        "nome_tipo": db_tipo_atividade.nome_tipo,
        "descricao": db_tipo_atividade.descricao,
        "categoria": db_tipo_atividade.categoria,
        "ativo": db_tipo_atividade.ativo,
        "id_tipo_maquina": db_tipo_atividade.id_tipo_maquina,
        "data_criacao": db_tipo_atividade.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_atividade, 'data_ultima_atualizacao', None)
    }

@router.delete("/tipos-atividade/{tipo_atividade_id}", operation_id="admin_delete_tipos_atividade_tipo_atividade_id")
def delete_tipo_atividade(tipo_atividade_id: int, db: Session = Depends(get_db)):
    """Deleta um tipo de atividade (soft delete)"""
    db_tipo_atividade = db.query(TipoAtividade).filter(TipoAtividade.id == tipo_atividade_id).first()
    if db_tipo_atividade is None:
        raise HTTPException(status_code=404, detail="Tipo de atividade não encontrado")

    db.query(TipoAtividade).filter(TipoAtividade.id == tipo_atividade_id).update({"ativo": False})
    db.commit()
    return {"message": "Tipo de atividade desativado com sucesso"}

@router.get("/tipos-falha/", operation_id="admin_get_tipos_falha_slash")
@router.get("/tipos-falha", operation_id="admin_get_tipos_falha")
def admin_read_tipos_falha(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    categoria: Optional[str] = None,
    severidade: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os tipos de falha, opcionalmente filtrados por departamento, setor, categoria e severidade"""
    query = db.query(TipoFalha).filter(TipoFalha.ativo.is_(True))

    # Filtrar por departamento se especificado
    if departamento:
        query = query.filter(TipoFalha.departamento == departamento)

    # Filtrar por setor se especificado
    if setor:
        query = query.filter(TipoFalha.setor == setor)

    # Filtrar por categoria se especificado
    if categoria:
        query = query.filter(TipoFalha.categoria == categoria)

    # Filtrar por severidade se especificado
    if severidade:
        query = query.filter(TipoFalha.severidade == severidade)

    tipos_falha = query.offset(skip).limit(limit).all()
    return [
        {
            "id": tf.id,
            "codigo": tf.codigo,
            "descricao": tf.descricao,
            "categoria": getattr(tf, 'categoria', None),
            "severidade": getattr(tf, 'severidade', None),
            "departamento": getattr(tf, 'departamento', None),
            "setor": getattr(tf, 'setor', None),
            "id_departamento": getattr(tf, 'id_departamento', None),
            "ativo": tf.ativo,
            "data_criacao": tf.data_criacao,
            "data_ultima_atualizacao": getattr(tf, 'data_ultima_atualizacao', None)
        }
        for tf in tipos_falha
    ]

@router.post("/tipos-falha/", response_model=Dict[str, Any], operation_id="admin_post_tipos_falha")
def create_tipo_falha(tipo_falha_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo tipo de falha"""
    try:
        # Validar dados obrigatórios
        codigo = tipo_falha_data.get("codigo")
        if not codigo or codigo.strip() == "":
            raise HTTPException(status_code=400, detail="Código do tipo de falha é obrigatório")

        # Verificar se já existe
        existing = db.query(TipoFalha).filter(TipoFalha.codigo == codigo).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Tipo de falha com código '{codigo}' já existe")

        # Preparar dados com valores padrão
        clean_data = {
            "codigo": codigo.strip(),
            "descricao": tipo_falha_data.get("descricao", "").strip() if tipo_falha_data.get("descricao") else "",
            "ativo": tipo_falha_data.get("ativo", True),
            "data_criacao": datetime.now(),
            "data_ultima_atualizacao": datetime.now()
        }

        # Adicionar campos opcionais se fornecidos
        for field in ["categoria", "severidade", "id_departamento", "departamento", "setor", "observacoes"]:
            value = tipo_falha_data.get(field)
            if value and str(value).strip() != "":
                if field == "id_departamento":
                    try:
                        clean_data[field] = int(value)
                    except (ValueError, TypeError):
                        pass  # Ignorar valores inválidos
                else:
                    clean_data[field] = str(value).strip()

        # Buscar id_departamento se departamento foi fornecido
        departamento = tipo_falha_data.get("departamento")
        if departamento and "id_departamento" not in clean_data:
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                clean_data["id_departamento"] = dept_obj.id

        db_tipo_falha = TipoFalha(**clean_data)
        db.add(db_tipo_falha)
        db.commit()
        db.refresh(db_tipo_falha)

        return {
            "id": db_tipo_falha.id,
            "codigo": db_tipo_falha.codigo,
            "descricao": db_tipo_falha.descricao,
            "categoria": getattr(db_tipo_falha, 'categoria', None),
            "departamento": getattr(db_tipo_falha, 'departamento', None),
            "setor": getattr(db_tipo_falha, 'setor', None),
            "id_departamento": getattr(db_tipo_falha, 'id_departamento', None),
            "severidade": getattr(db_tipo_falha, 'severidade', None),
            "ativo": db_tipo_falha.ativo,
            "data_criacao": db_tipo_falha.data_criacao,
            "data_ultima_atualizacao": getattr(db_tipo_falha, 'data_ultima_atualizacao', None)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar tipo de falha: {str(e)}")

@router.get("/tipos-falha/{tipo_falha_id}", response_model=Dict[str, Any], operation_id="admin_get_tipos_falha_tipo_falha_id")
def admin_read_tipo_falha_by_id(tipo_falha_id: int, db: Session = Depends(get_db)):
    """Busca um tipo de falha por ID"""
    db_tipo_falha = db.query(TipoFalha).filter(TipoFalha.id == tipo_falha_id).first()
    if db_tipo_falha is None:
        raise HTTPException(status_code=404, detail="Tipo de falha não encontrado")
    return {
        "id": db_tipo_falha.id,
        "codigo": db_tipo_falha.codigo,
        "descricao": db_tipo_falha.descricao,
        "categoria": getattr(db_tipo_falha, 'categoria', None),
        "ativo": db_tipo_falha.ativo,
        "data_criacao": db_tipo_falha.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_falha, 'data_ultima_atualizacao', None)
    }

@router.put("/tipos-falha/{tipo_falha_id}", response_model=Dict[str, Any], operation_id="admin_put_tipos_falha_tipo_falha_id")
def update_tipo_falha(tipo_falha_id: int, tipo_falha_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza um tipo de falha"""
    db_tipo_falha = db.query(TipoFalha).filter(TipoFalha.id == tipo_falha_id).first()
    if db_tipo_falha is None:
        raise HTTPException(status_code=404, detail="Tipo de falha não encontrado")

    for key, value in tipo_falha_data.items():
        setattr(db_tipo_falha, key, value)

    db.commit()
    db.refresh(db_tipo_falha)
    return {
        "id": db_tipo_falha.id,
        "codigo": db_tipo_falha.codigo,
        "descricao": db_tipo_falha.descricao,
        "categoria": getattr(db_tipo_falha, 'categoria', None),
        "ativo": db_tipo_falha.ativo,
        "data_criacao": db_tipo_falha.data_criacao,
        "data_ultima_atualizacao": getattr(db_tipo_falha, 'data_ultima_atualizacao', None)
    }

@router.delete("/tipos-falha/{tipo_falha_id}", operation_id="admin_delete_tipos_falha_tipo_falha_id")
def delete_tipo_falha(tipo_falha_id: int, db: Session = Depends(get_db)):
    """Deleta um tipo de falha (soft delete)"""
    db_tipo_falha = db.query(TipoFalha).filter(TipoFalha.id == tipo_falha_id).first()
    if db_tipo_falha is None:
        raise HTTPException(status_code=404, detail="Tipo de falha não encontrado")

    db.query(TipoFalha).filter(TipoFalha.id == tipo_falha_id).update({"ativo": False})
    db.commit()
    return {"message": "Tipo de falha desativado com sucesso"}

# =============================================================================
# ENDPOINTS PARA USUÁRIOS
# =============================================================================

def buscar_id_setor(nome_setor: str, db: Session) -> Optional[int]:
    """Busca o ID do setor pelo nome"""
    try:
        setor = db.query(DBSetor).filter(DBSetor.nome == nome_setor, DBSetor.ativo.is_(True)).first()
        return setor.id if setor else None  # type: ignore
    except Exception as e:
        print(f"Erro ao buscar ID do setor '{nome_setor}': {e}")
        return None

def buscar_id_departamento(nome_departamento: str, db: Session) -> Optional[int]:
    """Busca o ID do departamento pelo nome"""
    try:
        departamento = db.query(Departamento).filter(Departamento.nome_tipo == nome_departamento, Departamento.ativo.is_(True)).first()
        return departamento.id if departamento else None  # type: ignore
    except Exception as e:
        print(f"Erro ao buscar ID do departamento '{nome_departamento}': {e}")
        return None

def verificar_setor_producao(nome_setor: str, db: Session) -> bool:
    """Verifica se o setor é de produção"""
    try:
        setor = db.query(DBSetor).filter(DBSetor.nome == nome_setor, DBSetor.ativo.is_(True)).first()
        if setor:
            # Setores de produção geralmente têm area_tipo = 'PRODUCAO'
            return str(setor.area_tipo) == 'PRODUCAO'
        return False
    except Exception as e:
        print(f"Erro ao verificar se setor '{nome_setor}' é de produção: {e}")
        return False

@router.post("/usuarios", response_model=Dict[str, Any], operation_id="admin_post_usuarios")
def create_usuario_admin(usuario_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria um novo usuário via admin"""
    try:
        from app.auth import get_password_hash
        import secrets
        import string

        # Gerar senha temporária
        senha_temporaria = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

        # Extrair dados do usuário
        nome_setor = usuario_data.get("setor", "")
        nome_departamento = usuario_data.get("departamento", "MOTORES")
        matricula = usuario_data.get("matricula", "")
        trabalha_producao = usuario_data.get("trabalha_producao", False)

        # Buscar IDs de setor e departamento
        id_setor = buscar_id_setor(nome_setor, db) if nome_setor else None
        id_departamento = buscar_id_departamento(nome_departamento, db) if nome_departamento else None

        # Se não foi especificado trabalha_producao, verificar automaticamente pelo setor
        if not trabalha_producao and nome_setor:
            trabalha_producao = verificar_setor_producao(nome_setor, db)

        # Preparar dados do usuário
        novo_usuario_data = {
            "nome_completo": usuario_data.get("nome_completo"),
            "nome_usuario": usuario_data.get("email", "").split('@')[0],
            "email": usuario_data.get("email"),
            "matricula": matricula,
            "senha_hash": get_password_hash(senha_temporaria),
            "setor": nome_setor,
            "departamento": nome_departamento,
            "cargo": usuario_data.get("cargo", ""),
            "privilege_level": usuario_data.get("privilege_level", "USER"),
            "is_approved": True,
            "trabalha_producao": trabalha_producao,
            "primeiro_login": True,  # Marca que é primeiro login e precisa trocar senha
            "id_setor": id_setor,
            "id_departamento": id_departamento,
            "data_criacao": datetime.now(),
            "data_ultima_atualizacao": datetime.now()
        }

        # Verificar se email já existe
        existing = db.query(Usuario).filter(Usuario.email == usuario_data.get("email")).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email já está em uso")

        # Criar usuário
        novo_usuario = Usuario(**novo_usuario_data)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)

        return {
            "id": novo_usuario.id,
            "nome_completo": novo_usuario.nome_completo,
            "email": novo_usuario.email,
            "matricula": novo_usuario.matricula,
            "id_setor": novo_usuario.id_setor,
            "id_departamento": novo_usuario.id_departamento,
            "cargo": novo_usuario.cargo,
            "privilege_level": novo_usuario.privilege_level,
            "trabalha_producao": novo_usuario.trabalha_producao,
            "id_setor": novo_usuario.id_setor,
            "id_departamento": novo_usuario.id_departamento,
            "primeiro_login": novo_usuario.primeiro_login,
            "senha_temporaria": senha_temporaria,
            "instrucoes": "O usuário deve alterar a senha no primeiro login"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")

# =============================================================================
# ENDPOINTS PARA DESCRIÇÕES DE ATIVIDADE
# =============================================================================

@router.get("/descricoes-atividade/")
@router.get("/descricoes-atividade", operation_id="admin_get_descricoes_atividade")
def admin_read_descricoes_atividade(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    categoria: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todas as descrições de atividade, opcionalmente filtradas por departamento, setor e categoria"""
    query = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.ativo.is_(True))

    # Filtrar por departamento se especificado
    if departamento:
        query = query.filter(TipoDescricaoAtividade.departamento == departamento)

    # Filtrar por setor se especificado
    if setor:
        query = query.filter(TipoDescricaoAtividade.setor == setor)

    # Filtrar por categoria se especificado
    if categoria:
        query = query.filter(TipoDescricaoAtividade.categoria == categoria)

    descricoes = query.offset(skip).limit(limit).all()
    return [
        {
            "id": desc.id,
            "codigo": desc.codigo,
            "descricao": desc.descricao,
            "categoria": getattr(desc, 'categoria', None),
            "departamento": getattr(desc, 'departamento', None),
            "setor": getattr(desc, 'setor', None),
            "id_departamento": getattr(desc, 'id_departamento', None),
            "ativo": desc.ativo,
            "data_criacao": desc.data_criacao
        }
        for desc in descricoes
    ]

@router.post("/descricoes-atividade/", response_model=Dict[str, Any], operation_id="admin_post_descricoes_atividade")
def create_descricao_atividade(descricao_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Cria uma nova descrição de atividade"""
    try:
        # Validar dados obrigatórios
        codigo = descricao_data.get("codigo")
        if not codigo or codigo.strip() == "":
            raise HTTPException(status_code=400, detail="Código da descrição de atividade é obrigatório")

        # Verificar se já existe
        existing = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.codigo == codigo).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Descrição de atividade com código '{codigo}' já existe")

        # Preparar dados com valores padrão
        clean_data = {
            "codigo": codigo.strip(),
            "descricao": descricao_data.get("descricao", "").strip() if descricao_data.get("descricao") else "",
            "ativo": descricao_data.get("ativo", True),
            "data_criacao": datetime.now(),
            "data_ultima_atualizacao": datetime.now()
        }

        # Adicionar categoria se fornecida
        categoria = descricao_data.get("categoria")
        if categoria and str(categoria).strip() != "":
            clean_data["categoria"] = str(categoria).strip()

        # Adicionar campos de departamento e setor
        departamento = descricao_data.get("departamento")
        if departamento and str(departamento).strip() != "":
            clean_data["departamento"] = str(departamento).strip()

        setor = descricao_data.get("setor")
        if setor and str(setor).strip() != "":
            clean_data["setor"] = str(setor).strip()

        # Buscar id_departamento se departamento foi fornecido
        if departamento:
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                clean_data["id_departamento"] = dept_obj.id

        db_descricao = TipoDescricaoAtividade(**clean_data)
        db.add(db_descricao)
        db.commit()
        db.refresh(db_descricao)

        return {
            "id": db_descricao.id,
            "codigo": db_descricao.codigo,
            "descricao": db_descricao.descricao,
            "categoria": getattr(db_descricao, 'categoria', None),
            "departamento": getattr(db_descricao, 'departamento', None),
            "setor": getattr(db_descricao, 'setor', None),
            "id_departamento": getattr(db_descricao, 'id_departamento', None),
            "ativo": db_descricao.ativo,
            "data_criacao": getattr(db_descricao, 'data_criacao', None),
            "data_ultima_atualizacao": getattr(db_descricao, 'data_ultima_atualizacao', None)
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar descrição de atividade: {str(e)}")

@router.get("/descricoes-atividade/{descricao_id}", response_model=Dict[str, Any], operation_id="admin_get_descricoes_atividade_descricao_id")
def read_descricao_atividade(descricao_id: int, db: Session = Depends(get_db)):
    """Busca uma descrição de atividade por ID"""
    db_descricao = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).first()
    if db_descricao is None:
        raise HTTPException(status_code=404, detail="Descrição de atividade não encontrada")
    return {
        "id": db_descricao.id,
        "codigo": db_descricao.codigo,
        "descricao": db_descricao.descricao,
        "categoria": getattr(db_descricao, 'categoria', None),
        "ativo": db_descricao.ativo,
        "data_criacao": getattr(db_descricao, 'data_criacao', None),
        "data_ultima_atualizacao": getattr(db_descricao, 'data_ultima_atualizacao', None)
    }

@router.put("/descricoes-atividade/{descricao_id}", response_model=Dict[str, Any], operation_id="admin_put_descricoes_atividade_descricao_id")
def update_descricao_atividade(descricao_id: int, descricao_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Atualiza uma descrição de atividade"""
    db_descricao = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).first()
    if db_descricao is None:
        raise HTTPException(status_code=404, detail="Descrição de atividade não encontrada")

    for key, value in descricao_data.items():
        setattr(db_descricao, key, value)

    db.commit()
    db.refresh(db_descricao)
    return {
        "id": db_descricao.id,
        "codigo": db_descricao.codigo,
        "descricao": db_descricao.descricao,
        "categoria": getattr(db_descricao, 'categoria', None),
        "ativo": db_descricao.ativo,
        "data_criacao": getattr(db_descricao, 'data_criacao', None),
        "data_ultima_atualizacao": getattr(db_descricao, 'data_ultima_atualizacao', None)
    }

@router.delete("/descricoes-atividade/{descricao_id}", operation_id="admin_delete_descricoes_atividade_descricao_id")
def delete_descricao_atividade(descricao_id: int, db: Session = Depends(get_db)):
    """Deleta uma descrição de atividade (soft delete)"""
    db_descricao = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).first()
    if db_descricao is None:
        raise HTTPException(status_code=404, detail="Descrição de atividade não encontrada")

    db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.id == descricao_id).update({"ativo": False})
    db.commit()
    return {"message": "Descrição de atividade desativada com sucesso"}

# =============================================================================
# ENDPOINTS PARA USUÁRIOS
# =============================================================================

@router.get("/usuarios-pendentes", response_model=List[Dict[str, Any]], operation_id="admin_get_usuarios_pendentes")
def read_usuarios_pendentes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista usuários pendentes de aprovação"""
    # Verificar privilégios
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        usuarios = db.query(Usuario).filter(Usuario.is_approved.is_(False)).all()
        return [
            {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "matricula": user.matricula,
                "id_setor": user.id_setor,
                "id_departamento": user.id_departamento,
                "cargo": user.cargo,
                "data_criacao": user.data_criacao.isoformat() if user.data_criacao else None,  # type: ignore
                "privilege_level": user.privilege_level,
                "status": "PENDENTE"
            }
            for user in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários pendentes: {str(e)}")

@router.get("/usuarios", response_model=List[Dict[str, Any]], operation_id="admin_get_usuarios")
def read_usuarios(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todos os usuários"""
    # Verificar privilégios
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        usuarios = db.query(Usuario).all()
        return [
            {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "matricula": user.matricula,
                "id_setor": user.id_setor,
                "id_departamento": user.id_departamento,
                "cargo": user.cargo,
                "data_criacao": user.data_criacao.isoformat() if user.data_criacao else None,  # type: ignore
                "privilege_level": user.privilege_level,
                "is_approved": bool(user.is_approved),  # type: ignore
                "status": "APROVADO" if bool(user.is_approved) else "PENDENTE"  # type: ignore
            }
            for user in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")

@router.put("/usuarios/{user_id}/approve", operation_id="admin_approve_usuario")
def approve_usuario(
    user_id: int,
    approve_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aprovar usuário"""
    # Verificar privilégios
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        db.query(Usuario).filter(Usuario.id == user_id).update({"is_approved": True})
        if "privilege_level" in approve_data:
            user.privilege_level = approve_data["privilege_level"]

        db.commit()
        db.refresh(user)

        return {
            "message": "Usuário aprovado com sucesso",
            "user_id": user_id,
            "status": "APROVADO"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao aprovar usuário: {str(e)}")

@router.put("/usuarios/{user_id}/reject", operation_id="admin_reject_usuario")
def reject_usuario(
    user_id: int,
    reject_data: Optional[Dict[str, Any]] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rejeitar usuário"""
    # Verificar privilégios
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Marcar como rejeitado (pode implementar campo específico se necessário)
        db.query(Usuario).filter(Usuario.id == user_id).update({"is_approved": False})

        db.commit()

        return {
            "message": "Usuário rejeitado",
            "user_id": user_id,
            "status": "REJEITADO"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao rejeitar usuário: {str(e)}")

@router.put("/usuarios/{user_id}", operation_id="admin_update_usuario")
def update_usuario(
    user_id: int,
    update_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar dados de um usuário"""
    # Verificar privilégios
    if current_user.privilege_level not in ["ADMIN", "SUPERVISOR", "GESTAO"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Extrair dados de atualização
        nome_setor = update_data.get("setor", user.id_setor)
        nome_departamento = update_data.get("departamento", user.id_departamento)
        trabalha_producao = update_data.get("trabalha_producao", user.trabalha_producao)

        # Buscar IDs se necessário
        if nome_setor != user.setor:  # type: ignore
            id_setor = buscar_id_setor(nome_setor, db) if nome_setor else None
            db.query(Usuario).filter(Usuario.id == user_id).update({"id_setor": id_setor, "setor": nome_setor})

        if nome_departamento != user.departamento:  # type: ignore
            id_departamento = buscar_id_departamento(nome_departamento, db) if nome_departamento else None
            db.query(Usuario).filter(Usuario.id == user_id).update({"id_departamento": id_departamento, "departamento": nome_departamento})

        # Atualizar outros campos usando update
        update_dict = {}
        if "nome_completo" in update_data:
            update_dict["nome_completo"] = update_data["nome_completo"]
        if "email" in update_data:
            update_dict["email"] = update_data["email"]
        if "matricula" in update_data:
            update_dict["matricula"] = update_data["matricula"]
        if "cargo" in update_data:
            update_dict["cargo"] = update_data["cargo"]
        if "privilege_level" in update_data:
            update_dict["privilege_level"] = update_data["privilege_level"]
        if "trabalha_producao" in update_data:
            update_dict["trabalha_producao"] = update_data["trabalha_producao"]

        update_dict["data_ultima_atualizacao"] = datetime.now()

        if update_dict:
            db.query(Usuario).filter(Usuario.id == user_id).update(update_dict)

        db.commit()
        db.refresh(user)

        return {
            "message": "Usuário atualizado com sucesso",
            "user": {
                "id": user.id,
                "nome_completo": user.nome_completo,
                "email": user.email,
                "matricula": user.matricula,
                "id_setor": user.id_setor,
                "id_departamento": user.id_departamento,
                "cargo": user.cargo,
                "privilege_level": user.privilege_level,
                "trabalha_producao": user.trabalha_producao,
                "is_approved": user.is_approved
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

# =============================================================================
# ENDPOINTS DE STATUS
# =============================================================================

# =============================================================================
# ENDPOINTS DE STATUS
# =============================================================================

# =============================================================================
# ENDPOINT PARA CATEGORIAS DE TIPOS DE MÁQUINA
# =============================================================================

@router.get("/categorias-maquina/", response_model=List[str], operation_id="admin_get_categorias_maquina")
@router.get("/categorias-maquina", response_model=List[str], operation_id="admin_get_categorias_maquina_no_slash")
def get_categorias_maquina(db: Session = Depends(get_db)):
    """Lista todas as categorias únicas de tipos de máquina para uso em formulários"""
    try:
        # Buscar categorias únicas e não nulas da tabela tipos_maquina
        categorias = db.query(distinct(TipoMaquina.categoria)).filter(
            TipoMaquina.categoria.isnot(None),
            TipoMaquina.categoria != "",
            TipoMaquina.ativo.is_(True)
        ).all()

        # Extrair valores e filtrar vazios
        categorias_list = [cat[0] for cat in categorias if cat[0] and cat[0].strip()]

        # Ordenar alfabeticamente
        categorias_list.sort()

        return categorias_list

    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        # Retornar categorias padrão em caso de erro
        return ["MOTORES", "TRANSFORMADORES", "GERADORES", "OUTROS"]

@router.get("/status", operation_id="admin_get_status")
def get_admin_status():
    """Status dos endpoints de administração"""
    return {
        "available_endpoints": {
            "departamentos": "ACTIVE",
            "setores": "ACTIVE",
            "tipos_maquina": "ACTIVE",
            "tipos_teste": "ACTIVE",
            "tipos_atividade": "ACTIVE",
            "tipos_falha": "ACTIVE",
            "descricoes_atividade": "ACTIVE",
            "causas_retrabalho": "ACTIVE",
            "usuarios": "ACTIVE",
            "usuarios_pendentes": "ACTIVE",
            "categorias_maquina": "ACTIVE"
        },
        "message": "Admin routes completas - todos os endpoints implementados"
    }
