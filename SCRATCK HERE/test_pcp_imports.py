from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case, literal
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel

from app.database_models import (
    Usuario, OrdemServico, ApontamentoDetalhado, Programacao,
    Pendencia, Setor, Departamento, TipoMaquina, Cliente,
    TipoAtividade, TipoDescricaoAtividade, TipoCausaRetrabalho, Equipamento
)
from config.database_config import get_db
from app.dependencies import get_current_user
from utils.validators import validate_and_format_os, check_os_exists, generate_next_os

router = APIRouter(tags=["pcp"])

class ProgramacaoPCPCreate(BaseModel):
    id_ordem_servico: int
    inicio_previsto: datetime
    fim_previsto: datetime
    id_departamento: Optional[int] = None
    id_setor: Optional[int] = None
    responsavel_id: Optional[int] = None
    observacoes: Optional[str] = None
    status: Optional[str] = "PROGRAMADA"

class FiltragemPCP(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    setor: Optional[str] = None
    departamento: Optional[str] = None
    status_os: Optional[str] = None
    prioridade: Optional[str] = None

@router.get("/test")
async def test_endpoint(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint de teste"""
    return {"message": "OK"}

print("Imports OK")
