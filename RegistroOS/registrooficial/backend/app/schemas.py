"""
Pydantic Schemas - RegistroOS
============================

Modelos Pydantic para validação de entrada e saída da API.
Seguem a convenção: DB como fonte da verdade + aliases para frontend.

ESTRUTURA DOS SCHEMAS:
- Base: Campos comuns compartilhados entre Create/Update
- Create: Dados necessários para criação (sem ID, campos obrigatórios)
- Update: Dados opcionais para atualização (todos campos opcionais)
- Response: Dados retornados pela API (inclui ID e metadados)

ALIASES IMPORTANTES:
- nome_tipo (DB) ↔ nome (Frontend) - Para departamentos e tipos de máquina
- subcategoria (JSON string no DB) ↔ subcategoria (List[str] no Frontend)
- Foreign Keys: Sistema híbrido ID + nome para flexibilidade

VALIDADORES CUSTOMIZADOS:
- JSON fields: Conversão automática entre string e lista
- Text fields: Limpeza e formatação automática via middleware
- Foreign Keys: Validação de existência e integridade referencial
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, time
import json

# =============================================================================
# SCHEMAS BASE
# =============================================================================

class BaseSchema(BaseModel):
    """Schema base com configurações padrão"""
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            time: lambda v: v.isoformat() if v else None,
        }
    }

# =============================================================================
# DEPARTAMENTO SCHEMAS
# =============================================================================

class DepartamentoBase(BaseSchema):
    nome_tipo: Optional[str] = Field(None, description="Nome do departamento")
    nome: Optional[str] = Field(None, description="Nome do departamento (alias)")
    descricao: Optional[str] = None
    ativo: bool = True

class DepartamentoCreate(DepartamentoBase):
    pass

class DepartamentoUpdate(BaseSchema):
    nome_tipo: Optional[str] = Field(None, description="Nome do departamento")
    nome: Optional[str] = Field(None, description="Nome do departamento (alias)")
    descricao: Optional[str] = None
    ativo: Optional[bool] = None

class DepartamentoResponse(DepartamentoBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# SETOR SCHEMAS
# =============================================================================

class SetorBase(BaseSchema):
    nome: str = Field(..., description="Nome do setor")
    descricao: Optional[str] = None
    ativo: bool = True
    area_tipo: Optional[str] = Field(None, description="Tipo da área")
    tipo_area: Optional[str] = Field(None, description="Tipo da área (alias)")
    permite_apontamento: bool = True
    id_departamento: int = Field(..., description="ID do departamento")

class SetorCreate(SetorBase):
    pass

class SetorUpdate(BaseSchema):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativo: Optional[bool] = None
    area_tipo: Optional[str] = None
    tipo_area: Optional[str] = None
    permite_apontamento: Optional[bool] = None
    id_departamento: Optional[int] = None

class SetorResponse(SetorBase):
    id: int
    departamento: Optional[str] = None  # Nome do departamento para compatibilidade
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# TIPO MÁQUINA SCHEMAS
# =============================================================================

class TipoMaquinaBase(BaseSchema):
    nome_tipo: Optional[str] = Field(None, description="Nome do tipo de máquina")
    nome: Optional[str] = Field(None, description="Nome do tipo de máquina (alias)")
    departamento: Optional[str] = Field(None, description="Nome do departamento")
    setor: Optional[str] = Field(None, description="Nome do setor")
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[List[str]] = Field(default_factory=list, description="Lista de subcategorias")
    id_departamento: Optional[int] = Field(None, description="ID do departamento")
    ativo: bool = True

    @field_validator('subcategoria', mode='before')
    @classmethod
    def parse_subcategoria(cls, v):
        """Converter string JSON para lista se necessário"""
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v or []

class TipoMaquinaCreate(TipoMaquinaBase):
    pass

class TipoMaquinaUpdate(BaseSchema):
    nome_tipo: Optional[str] = Field(None, alias="nome")
    departamento: Optional[str] = None
    setor: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[List[str]] = None
    id_departamento: Optional[int] = None
    ativo: Optional[bool] = None

    @field_validator('subcategoria', mode='before')
    @classmethod
    def parse_subcategoria(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else []
            except json.JSONDecodeError:
                return []
        return v

class TipoMaquinaResponse(TipoMaquinaBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# TIPO ATIVIDADE SCHEMAS
# =============================================================================

class TipoAtividadeBase(BaseSchema):
    nome_tipo: Optional[str] = Field(None, description="Nome do tipo de atividade")
    nome: Optional[str] = Field(None, description="Nome do tipo de atividade (alias)")
    departamento: str = Field(..., description="Nome do departamento")
    setor: str = Field(..., description="Nome do setor")
    categoria: Optional[str] = Field(None, description="Categoria da atividade")
    descricao: Optional[str] = None
    id_departamento: Optional[Union[int, str]] = Field(None, description="ID do departamento")
    id_setor: Optional[Union[int, str]] = Field(None, description="ID do setor")
    ativo: bool = True

class TipoAtividadeCreate(TipoAtividadeBase):
    pass

class TipoAtividadeUpdate(BaseSchema):
    nome_tipo: Optional[str] = Field(None, alias="nome")
    departamento: Optional[str] = None
    setor: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    id_departamento: Optional[Union[int, str]] = None
    id_setor: Optional[Union[int, str]] = None
    ativo: Optional[bool] = None

class TipoAtividadeResponse(TipoAtividadeBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# DESCRIÇÃO ATIVIDADE SCHEMAS
# =============================================================================

class DescricaoAtividadeBase(BaseSchema):
    codigo: str = Field(..., description="Código da descrição de atividade")
    descricao: str = Field(..., description="Descrição da atividade")
    setor: str = Field(..., description="Nome do setor")
    categoria: Optional[str] = Field(None, description="Categoria da descrição")
    departamento: Optional[str] = Field(None, description="Nome do departamento")
    id_setor: Optional[Union[int, str]] = Field(None, description="ID do setor")
    id_departamento: Optional[Union[int, str]] = Field(None, description="ID do departamento")
    ativo: bool = True

class DescricaoAtividadeCreate(DescricaoAtividadeBase):
    pass

class DescricaoAtividadeUpdate(BaseSchema):
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    setor: Optional[str] = None
    categoria: Optional[str] = None
    departamento: Optional[str] = None
    id_setor: Optional[Union[int, str]] = None
    id_departamento: Optional[Union[int, str]] = None
    ativo: Optional[bool] = None

class DescricaoAtividadeResponse(DescricaoAtividadeBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# TIPO FALHA SCHEMAS
# =============================================================================

class TipoFalhaBase(BaseSchema):
    codigo: str = Field(..., description="Código do tipo de falha")
    descricao: str = Field(..., description="Descrição do tipo de falha")
    departamento: str = Field(..., description="Nome do departamento")
    setor: str = Field(..., description="Nome do setor")
    categoria: Optional[str] = Field(None, description="Categoria da falha")
    id_departamento: Optional[Union[int, str]] = Field(None, description="ID do departamento")
    id_setor: Optional[Union[int, str]] = Field(None, description="ID do setor")
    ativo: bool = True

class TipoFalhaCreate(TipoFalhaBase):
    pass

class TipoFalhaUpdate(BaseSchema):
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    departamento: Optional[str] = None
    setor: Optional[str] = None
    categoria: Optional[str] = None
    id_departamento: Optional[Union[int, str]] = None
    id_setor: Optional[Union[int, str]] = None
    ativo: Optional[bool] = None

class TipoFalhaResponse(TipoFalhaBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# TIPO TESTE SCHEMAS
# =============================================================================

class TipoTesteBase(BaseSchema):
    nome_tipo: str = Field(..., alias="nome", description="Nome do tipo de teste")
    departamento: str = Field(..., description="Nome do departamento")
    setor: str = Field(..., description="Nome do setor")
    tipo_teste: Optional[str] = Field(None, description="Tipo do teste (ESTÁTICO, DINÂMICO)")
    descricao: Optional[str] = None
    tipo_maquina: Optional[str] = Field(None, description="Tipo de máquina relacionado")
    categoria: Optional[str] = Field(None, description="Categoria do teste (Visual, Elétrico, Mecânico)")
    subcategoria: Optional[int] = Field(None, description="Subcategoria (0=Padrão, 1=Especiais)")
    id_departamento: Optional[int] = Field(None, description="ID do departamento")
    id_setor: Optional[int] = Field(None, description="ID do setor")
    ativo: bool = True

class TipoTesteCreate(TipoTesteBase):
    pass

class TipoTesteUpdate(BaseSchema):
    nome_tipo: Optional[str] = Field(None, alias="nome")
    departamento: Optional[str] = None
    setor: Optional[str] = None
    tipo_teste: Optional[str] = None
    descricao: Optional[str] = None
    tipo_maquina: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[int] = None
    id_departamento: Optional[int] = None
    id_setor: Optional[int] = None
    ativo: Optional[bool] = None

class TipoTesteResponse(TipoTesteBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None

# =============================================================================
# CAUSA RETRABALHO SCHEMAS
# =============================================================================

class CausaRetrabalhoBase(BaseSchema):
    codigo: str = Field(..., description="Código da causa de retrabalho")
    descricao: str = Field(..., description="Descrição da causa de retrabalho")
    departamento: str = Field(..., description="Nome do departamento")
    setor: Optional[str] = Field(None, description="Nome do setor")
    categoria: Optional[str] = Field(None, description="Categoria da causa")
    id_departamento: Optional[int] = Field(None, description="ID do departamento")
    id_setor: Optional[int] = Field(None, description="ID do setor")
    ativo: bool = True

class CausaRetrabalhoCreate(CausaRetrabalhoBase):
    pass

class CausaRetrabalhoUpdate(BaseSchema):
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    departamento: Optional[str] = None
    setor: Optional[str] = None
    categoria: Optional[str] = None
    id_departamento: Optional[int] = None
    id_setor: Optional[int] = None
    ativo: Optional[bool] = None

class CausaRetrabalhoResponse(CausaRetrabalhoBase):
    id: int
    data_criacao: Optional[datetime] = None
    data_ultima_atualizacao: Optional[datetime] = None


