"""
Database Lookup Functions - RegistroOS
=====================================

Funções helper para converter nomes em IDs e vice-versa.
Facilitam a compatibilidade entre frontend (nomes) e backend (IDs).

PROPÓSITO:
Este módulo resolve o problema de incompatibilidade entre frontend e backend:
- Frontend trabalha com nomes (mais amigável ao usuário)
- Backend/DB trabalha com IDs (mais eficiente e consistente)
- Estas funções fazem a ponte entre os dois mundos

PADRÕES DE NOMENCLATURA:
- get_[entidade]_id_by_nome(): Converte nome → ID
- get_[entidade]_nome_by_id(): Converte ID → nome
- get_all_[entidade]_map(): Retorna mapeamento completo nome → ID
- validate_[entidade]_exists(): Verifica se entidade existe
- convert_names_to_ids(): Conversão em lote para payloads
- enrich_with_names(): Enriquecimento de dados com nomes

PERFORMANCE:
- Queries otimizadas com filtros de ativo=True
- Mapeamentos em lote para reduzir consultas
- Cache implícito via session do SQLAlchemy
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from app.database_models import (
    Departamento, Setor, TipoMaquina, TipoAtividade, 
    TipoDescricaoAtividade, TipoCausaRetrabalho, TipoTeste,
    Usuario, Cliente, Equipamento
)

# =============================================================================
# DEPARTAMENTO LOOKUPS
# =============================================================================

def get_departamento_id_by_nome(db: Session, nome_tipo: str) -> Optional[int]:
    """Busca ID do departamento pelo nome_tipo"""
    departamento = db.query(Departamento).filter(
        Departamento.nome_tipo == nome_tipo,
        Departamento.ativo == True
    ).first()
    return departamento.id if departamento else None

def get_departamento_nome_by_id(db: Session, departamento_id: int) -> Optional[str]:
    """Busca nome_tipo do departamento pelo ID"""
    departamento = db.query(Departamento).filter(
        Departamento.id == departamento_id,
        Departamento.ativo == True
    ).first()
    return departamento.nome_tipo if departamento else None

def get_all_departamentos_map(db: Session) -> Dict[str, int]:
    """Retorna mapeamento nome_tipo → ID para todos os departamentos ativos"""
    departamentos = db.query(Departamento).filter(Departamento.ativo == True).all()
    return {dept.nome_tipo: dept.id for dept in departamentos}

def validate_departamento_exists(db: Session, nome_tipo: str) -> bool:
    """Verifica se departamento existe e está ativo"""
    return get_departamento_id_by_nome(db, nome_tipo) is not None

def validate_departamento_exists_by_id(db: Session, departamento_id: int) -> bool:
    """Verifica se departamento existe e está ativo pelo ID"""
    departamento = db.query(Departamento).filter(
        Departamento.id == departamento_id,
        Departamento.ativo == True
    ).first()
    return departamento is not None

# =============================================================================
# SETOR LOOKUPS
# =============================================================================

def get_setor_id_by_nome(db: Session, nome: str) -> Optional[int]:
    """Busca ID do setor pelo nome"""
    setor = db.query(Setor).filter(
        Setor.nome == nome,
        Setor.ativo == True
    ).first()
    return setor.id if setor else None

def get_setor_nome_by_id(db: Session, setor_id: int) -> Optional[str]:
    """Busca nome do setor pelo ID"""
    setor = db.query(Setor).filter(
        Setor.id == setor_id,
        Setor.ativo == True
    ).first()
    return setor.nome if setor else None

def get_all_setores_map(db: Session) -> Dict[str, int]:
    """Retorna mapeamento nome → ID para todos os setores ativos"""
    setores = db.query(Setor).filter(Setor.ativo == True).all()
    return {setor.nome: setor.id for setor in setores}

def validate_setor_exists(db: Session, nome: str) -> bool:
    """Verifica se setor existe e está ativo"""
    return get_setor_id_by_nome(db, nome) is not None

def validate_setor_exists_by_id(db: Session, setor_id: int) -> bool:
    """Verifica se setor existe e está ativo pelo ID"""
    setor = db.query(Setor).filter(
        Setor.id == setor_id,
        Setor.ativo == True
    ).first()
    return setor is not None

def validate_setor_belongs_to_departamento(db: Session, setor_id: int, departamento_id: int) -> bool:
    """Verifica se setor pertence ao departamento especificado"""
    setor = db.query(Setor).filter(
        Setor.id == setor_id,
        Setor.id_departamento == departamento_id,
        Setor.ativo == True
    ).first()
    return setor is not None

def get_setores_by_departamento_id(db: Session, departamento_id: int) -> List[Dict]:
    """Retorna todos os setores de um departamento"""
    setores = db.query(Setor).filter(
        Setor.id_departamento == departamento_id,
        Setor.ativo == True
    ).all()
    return [{"id": s.id, "nome": s.nome, "area_tipo": s.area_tipo} for s in setores]

# =============================================================================
# TIPO MÁQUINA LOOKUPS
# =============================================================================

def get_tipo_maquina_id_by_nome(db: Session, nome_tipo: str) -> Optional[int]:
    """Busca ID do tipo de máquina pelo nome_tipo"""
    tipo = db.query(TipoMaquina).filter(
        TipoMaquina.nome_tipo == nome_tipo,
        TipoMaquina.ativo == True
    ).first()
    return tipo.id if tipo else None

def get_tipo_maquina_nome_by_id(db: Session, tipo_id: int) -> Optional[str]:
    """Busca nome_tipo do tipo de máquina pelo ID"""
    tipo = db.query(TipoMaquina).filter(
        TipoMaquina.id == tipo_id,
        TipoMaquina.ativo == True
    ).first()
    return tipo.nome_tipo if tipo else None

def get_all_tipos_maquina_map(db: Session) -> Dict[str, int]:
    """Retorna mapeamento nome_tipo → ID para todos os tipos de máquina ativos"""
    tipos = db.query(TipoMaquina).filter(TipoMaquina.ativo == True).all()
    return {tipo.nome_tipo: tipo.id for tipo in tipos}

# =============================================================================
# TIPO ATIVIDADE LOOKUPS
# =============================================================================

def get_tipo_atividade_id_by_nome(db: Session, nome_tipo: str) -> Optional[int]:
    """Busca ID do tipo de atividade pelo nome_tipo"""
    tipo = db.query(TipoAtividade).filter(
        TipoAtividade.nome_tipo == nome_tipo,
        TipoAtividade.ativo == True
    ).first()
    return tipo.id if tipo else None

def get_tipo_atividade_nome_by_id(db: Session, tipo_id: int) -> Optional[str]:
    """Busca nome_tipo do tipo de atividade pelo ID"""
    tipo = db.query(TipoAtividade).filter(
        TipoAtividade.id == tipo_id,
        TipoAtividade.ativo == True
    ).first()
    return tipo.nome_tipo if tipo else None

# =============================================================================
# USUÁRIO LOOKUPS
# =============================================================================

def get_usuario_id_by_nome(db: Session, nome: str) -> Optional[int]:
    """Busca ID do usuário pelo nome"""
    usuario = db.query(Usuario).filter(
        Usuario.nome == nome,
        Usuario.ativo == True
    ).first()
    return usuario.id if usuario else None

def get_usuario_nome_by_id(db: Session, usuario_id: int) -> Optional[str]:
    """Busca nome do usuário pelo ID"""
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.ativo == True
    ).first()
    return usuario.nome if usuario else None

# =============================================================================
# CLIENTE LOOKUPS
# =============================================================================

def get_cliente_id_by_nome(db: Session, nome: str) -> Optional[int]:
    """Busca ID do cliente pelo nome"""
    cliente = db.query(Cliente).filter(
        Cliente.nome == nome,
        Cliente.ativo == True
    ).first()
    return cliente.id if cliente else None

def get_cliente_nome_by_id(db: Session, cliente_id: int) -> Optional[str]:
    """Busca nome do cliente pelo ID"""
    cliente = db.query(Cliente).filter(
        Cliente.id == cliente_id,
        Cliente.ativo == True
    ).first()
    return cliente.nome if cliente else None

# =============================================================================
# EQUIPAMENTO LOOKUPS
# =============================================================================

def get_equipamento_id_by_nome(db: Session, nome: str) -> Optional[int]:
    """Busca ID do equipamento pelo nome"""
    equipamento = db.query(Equipamento).filter(
        Equipamento.nome == nome,
        Equipamento.ativo == True
    ).first()
    return equipamento.id if equipamento else None

def get_equipamento_nome_by_id(db: Session, equipamento_id: int) -> Optional[str]:
    """Busca nome do equipamento pelo ID"""
    equipamento = db.query(Equipamento).filter(
        Equipamento.id == equipamento_id,
        Equipamento.ativo == True
    ).first()
    return equipamento.nome if equipamento else None

# =============================================================================
# FUNÇÕES DE CONVERSÃO EM LOTE
# =============================================================================

def convert_names_to_ids(db: Session, payload: Dict) -> Dict:
    """
    Converte nomes para IDs em um payload de dados.
    Útil para processar dados vindos do frontend.
    """
    converted = payload.copy()
    
    # Conversões específicas baseadas nos campos presentes
    if 'departamento' in payload and isinstance(payload['departamento'], str):
        dept_id = get_departamento_id_by_nome(db, payload['departamento'])
        if dept_id:
            converted['id_departamento'] = dept_id
            del converted['departamento']
    
    if 'setor' in payload and isinstance(payload['setor'], str):
        setor_id = get_setor_id_by_nome(db, payload['setor'])
        if setor_id:
            converted['id_setor'] = setor_id
            del converted['setor']
    
    if 'tipo_maquina' in payload and isinstance(payload['tipo_maquina'], str):
        tipo_id = get_tipo_maquina_id_by_nome(db, payload['tipo_maquina'])
        if tipo_id:
            converted['id_tipo_maquina'] = tipo_id
            del converted['tipo_maquina']
    
    return converted

def enrich_with_names(db: Session, data: Dict) -> Dict:
    """
    Enriquece dados com nomes baseados nos IDs.
    Útil para retornar dados mais amigáveis ao frontend.
    """
    enriched = data.copy()
    
    # Enriquecimento baseado nos IDs presentes
    if 'id_departamento' in data:
        nome = get_departamento_nome_by_id(db, data['id_departamento'])
        if nome:
            enriched['departamento'] = nome
    
    if 'id_setor' in data:
        nome = get_setor_nome_by_id(db, data['id_setor'])
        if nome:
            enriched['setor'] = nome
    
    if 'id_tipo_maquina' in data:
        nome = get_tipo_maquina_nome_by_id(db, data['id_tipo_maquina'])
        if nome:
            enriched['tipo_maquina'] = nome
    
    return enriched
