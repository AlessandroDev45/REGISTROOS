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

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

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
    id_setor: Optional[int] = None
    id_departamento: Optional[int] = None

# =============================================================================
# ENDPOINTS PRINCIPAIS DO PCP
# =============================================================================

# @router.get("/programacoes", operation_id="pcp_get_programacoes")
# async def get_programacoes_pcp(
#     current_user: Usuario = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Obter todas as programações para PCP"""
#     try:
#         from sqlalchemy import text
#
#         sql = text("""
#             SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
#                    p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
#                    p.created_at, p.updated_at, p.id_setor,
#                    os.os_numero, u.nome_completo as responsavel_nome,
#                    s.nome as setor_nome
#             FROM programacoes p
#             LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
#             LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
#             LEFT JOIN tipo_setores s ON p.id_setor = s.id
#             ORDER BY p.inicio_previsto DESC
#             LIMIT 100
#         """)
#
#         result = db.execute(sql)
#         programacoes = result.fetchall()
#
#         return [
#             {
#                 "id": row[0],
#                 "id_ordem_servico": row[1],
#                 "responsavel_id": row[2],
#                 "inicio_previsto": str(row[3]) if row[3] else None,
#                 "fim_previsto": str(row[4]) if row[4] else None,
#                 "status": row[5] or "PROGRAMADA",
#                 "criado_por_id": row[6],
#                 "observacoes": row[7] or "",
#                 "created_at": str(row[8]) if row[8] else None,
#                 "updated_at": str(row[9]) if row[9] else None,
#                 "id_setor": row[10],
#                 "os_numero": row[11] or "",
#                 "responsavel_nome": row[12] or "Não informado",
#                 "setor_nome": row[13] or "Não informado"
#             }
#             for row in programacoes
#         ]
#
#     except Exception as e:
#         print(f"Erro ao buscar programações PCP: {e}")
#         return []

@router.get("/dashboard", operation_id="pcp_get_dashboard")
async def get_pcp_dashboard(
    periodo: Optional[int] = 30,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard do PCP com métricas de programação e controle de produção"""
    try:
        from sqlalchemy import func, text

        # Métricas de programações
        total_programacoes = db.query(Programacao).count()
        programacoes_pendentes = db.query(Programacao).filter(
            Programacao.status == "PENDENTE"
        ).count()
        programacoes_em_andamento = db.query(Programacao).filter(
            Programacao.status == "EM_ANDAMENTO"
        ).count()
        programacoes_concluidas = db.query(Programacao).filter(
            Programacao.status == "CONCLUIDA"
        ).count()

        # Métricas de ordens de serviço
        total_os = db.query(OrdemServico).count()
        os_disponiveis = db.query(OrdemServico).filter(
            OrdemServico.status_os == "ABERTA"
        ).count()
        os_programadas = db.query(OrdemServico).filter(
            OrdemServico.status_os == "EM ANDAMENTO"
        ).count()

        # Eficiência por setor (dados simulados baseados em dados reais)
        eficiencia_setores = [
            {
                "setor": "ENROLAMENTO",
                "programacoes_realizadas": total_programacoes // 4,
                "tempo_medio_horas": 8.5,
                "eficiencia": 88.0
            },
            {
                "setor": "MECANICA",
                "programacoes_realizadas": total_programacoes // 4,
                "tempo_medio_horas": 6.2,
                "eficiencia": 92.0
            },
            {
                "setor": "PINTURA",
                "programacoes_realizadas": total_programacoes // 5,
                "tempo_medio_horas": 4.8,
                "eficiencia": 85.0
            },
            {
                "setor": "ENSAIOS",
                "programacoes_realizadas": total_programacoes // 6,
                "tempo_medio_horas": 3.5,
                "eficiencia": 95.0
            }
        ]

        # Próximas programações (últimas 5)
        try:
            proximas_programacoes = db.query(Programacao).filter(
                Programacao.status.in_(["PENDENTE", "EM_ANDAMENTO"])
            ).limit(5).all()
        except:
            # Se houver erro, buscar todas as programações
            proximas_programacoes = db.query(Programacao).limit(5).all()

        programacoes_lista = []
        for prog in proximas_programacoes:
            # Buscar OS relacionada para obter numero_os
            os_relacionada = db.query(OrdemServico).filter(
                OrdemServico.id == prog.id_ordem_servico
            ).first()

            programacoes_lista.append({
                "id": prog.id,
                "os_numero": os_relacionada.os_numero if os_relacionada else f"OS-{prog.id_ordem_servico}",
                "setor": "Não informado",  # Setor seria obtido via relacionamento
                "status": prog.status or "PENDENTE",
                "data_criacao": prog.created_at.isoformat() if prog.created_at is not None else datetime.now().isoformat(),
                "prioridade": "MEDIA"  # Valor padrão
            })

        return {
            "metricas_programacao": {
                "total_programacoes": total_programacoes,
                "programacoes_pendentes": programacoes_pendentes,
                "programacoes_em_andamento": programacoes_em_andamento,
                "programacoes_concluidas": programacoes_concluidas,
                "taxa_conclusao": round((programacoes_concluidas / total_programacoes * 100) if total_programacoes > 0 else 0, 1)
            },
            "metricas_ordens": {
                "total_os": total_os,
                "os_disponiveis": os_disponiveis,
                "os_programadas": os_programadas,
                "taxa_programacao": round((os_programadas / total_os * 100) if total_os > 0 else 0, 1)
            },
            "eficiencia_setores": eficiencia_setores,
            "proximas_programacoes": programacoes_lista,
            "periodo_analise": periodo,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": f"Erro ao buscar dashboard PCP: {str(e)}"}

@router.get("/programacoes-gerar", operation_id="pcp_get_programacoes_gerar")
async def gerar_programacoes_pcp(
    filtros: Optional[FiltragemPCP] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerar programações automáticas com base em ordens de serviço disponíveis
    na base de dados para envio aos setores de produção
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem gerar programações")

        # Construir query de filtros
        query = db.query(OrdemServico).filter(OrdemServico.status_os.isnot(None))
        
        # Filtrar por datas
        if filtros:
            if filtros.data_inicio is not None:
                query = query.filter(OrdemServico.data_criacao >= filtros.data_inicio)
            if filtros.data_fim is not None:
                query = query.filter(OrdemServico.data_criacao <= filtros.data_fim)
            if filtros.id_setor is not None:
                query = query.filter(OrdemServico.id_setor == filtros.id_setor)
            if filtros.id_departamento is not None:
                query = query.filter(OrdemServico.id_departamento == filtros.id_departamento)
            if filtros.status_os is not None:
                query = query.filter(OrdemServico.status_os == filtros.status_os)
            if filtros.prioridade is not None:
                query = query.filter(OrdemServico.prioridade == filtros.prioridade)
        
        # Filtrar por prioridade - apenas OS com prioridade NORMAL ou ALTA
        query = query.filter(OrdemServico.prioridade.in_(['NORMAL', 'ALTA']))
        
        # Ordernar por prioridade e data de criação
        ordens_servico = query.order_by(
            desc(case([(OrdemServico.prioridade == 'ALTA', literal(1))], else_=literal(0))),  # type: ignore
            OrdemServico.data_criacao
        ).limit(50).all()

        programacoes_geradas = []
        
        for os in ordens_servico:
            # Buscar setor da OS
            setor = db.query(Setor).filter(Setor.id == os.id_setor).first()  # type: ignore
            if not setor:
                continue
            
            # Buscar tipo de atividade padrão para o setor
            tipo_atividade = db.query(TipoAtividade).filter(
                TipoAtividade.id_setor == os.id_setor,  # type: ignore
                TipoAtividade.ativo.is_(True)
            ).first()
            
            # Buscar colaboradores disponíveis do setor
            colaboradores_disponiveis = db.query(Usuario).filter(
                Usuario.id_setor == os.id_setor,  # type: ignore
                Usuario.is_approved.is_(True),
                Usuario.privilege_level.in_(['USER', 'SUPERVISOR'])
            ).all()
            
            # Calcular duração estimada baseada em horas_orcadas
            duracao_horas = float(os.horas_orcadas) if os.horas_orcadas else 8.0  # type: ignore
            
            # Definir horário de trabalho (8h as 17h)
            hora_inicio = "08:00"
            hora_fim = (datetime.strptime(hora_inicio, "%H:%M") + timedelta(hours=duracao_horas)).strftime("%H:%M")
            
            # Criar programação
            if colaboradores_disponiveis:
                # Distribuir entre colaboradores disponíveis
                responsavel_id = colaboradores_disponiveis[0].id
                
                # Buscar cliente da OS
                cliente = "Cliente não informado"
                if os.id_cliente is not None:  # type: ignore
                    cliente_info = db.query(Cliente).filter(Cliente.id == os.id_cliente).first()  # type: ignore
                    if cliente_info:
                        cliente = cliente_info.razao_social or cliente_info.nome_fantasia or "Cliente não informado"

                # Buscar equipamento da OS
                equipamento = os.descricao_maquina or "Equipamento não informado"  # type: ignore
                if os.id_equipamento is not None:  # type: ignore
                    equipamento_info = db.query(Equipamento).filter(Equipamento.id == os.id_equipamento).first()  # type: ignore
                    if equipamento_info:
                        equipamento = equipamento_info.descricao or "Equipamento não informado"
                
                nova_programacao = Programacao(
                    id_ordem_servico=os.id,  # type: ignore
                    numero_os=os.os_numero,  # type: ignore
                    cliente=cliente,
                    equipamento=equipamento,
                    tipo_atividade=tipo_atividade.nome_tipo if tipo_atividade else "Atividade Padrão",
                    data_programada=os.data_criacao.date() if os.data_criacao else date.today(),  # type: ignore
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    responsavel_id=responsavel_id,
                    setor=os.id_setor,  # type: ignore
                    departamento=os.id_departamento,  # type: ignore
                    status='AGENDADO',
                    observacoes=f"Programação automática gerada via PCP para OS {os.os_numero}",  # type: ignore
                    criado_por_id=current_user.id,  # type: ignore
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    id_setor=setor.id
                )

                db.add(nova_programacao)
                programacoes_geradas.append({
                    "id_ordem_servico": os.id,  # type: ignore
                    "os_numero": os.os_numero,  # type: ignore
                    "id_setor": os.id_setor,  # type: ignore
                    "responsavel_id": responsavel_id,
                    "responsavel_nome": colaboradores_disponiveis[0].nome_completo,
                    "data_programada": os.data_criacao.date().isoformat() if os.data_criacao else date.today().isoformat(),  # type: ignore
                    "hora_inicio": hora_inicio,
                    "hora_fim": hora_fim,
                    "status": "AGENDADO"
                })
        
        db.commit()
        
        return {
            "message": f"Programações geradas com sucesso para {len(programacoes_geradas)} ordens de serviço",
            "total_programacoes": len(programacoes_geradas),
            "programacoes": programacoes_geradas,
            "detalhes": {
                "data_geracao": datetime.now().isoformat(),
                "usuario_gerou": current_user.nome_completo,
                "id_setor": current_user.id_setor
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao gerar programações via PCP: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar programações: {str(e)}")

@router.get("/ordens-disponiveis", operation_id="pcp_get_ordens_disponiveis")
async def get_ordens_disponiveis_pcp(
    filtros: Optional[FiltragemPCP] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter ordens de serviço disponíveis para programação via PCP
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem acessar")

        # Construir query
        query = db.query(OrdemServico).filter(
            OrdemServico.status_os.in_(['ABERTA', 'EM_ANDAMENTO']),
            OrdemServico.horas_orcadas.isnot(None)
        )
        
        # Aplicar filtros
        if filtros:
            if filtros.data_inicio is not None:
                query = query.filter(OrdemServico.data_criacao >= filtros.data_inicio)
            if filtros.data_fim is not None:
                query = query.filter(OrdemServico.data_criacao <= filtros.data_fim)
            if filtros.id_setor is not None:
                query = query.filter(OrdemServico.id_setor == filtros.id_setor)
            if filtros.id_departamento is not None:
                query = query.filter(OrdemServico.id_departamento == filtros.id_departamento)
            if filtros.prioridade is not None:
                query = query.filter(OrdemServico.prioridade == filtros.prioridade)
        
        ordens = query.order_by(
            desc(OrdemServico.prioridade),
            OrdemServico.data_criacao
        ).limit(100).all()

        return [
            {
                "id": os.id,
                "os_numero": os.os_numero,
                "status_os": os.status_os,
                "prioridade": os.prioridade,
                "descricao_maquina": os.descricao_maquina,
                "horas_orcadas": float(os.horas_orcadas) if os.horas_orcadas else 0,  # type: ignore
                "horas_reais": float(os.horas_reais) if os.horas_reais else 0,  # type: ignore
                "id_setor": os.id_setor,
                "id_departamento": os.id_departamento,
                "data_criacao": os.data_criacao.isoformat() if os.data_criacao is not None else None,  # type: ignore
                "id_responsavel_registro": os.id_responsavel_registro,
                "tem_programacao": db.query(Programacao).filter(
                    Programacao.id_ordem_servico == os.id
                ).first() is not None
            }
            for os in ordens
        ]
        
    except Exception as e:
        print(f"Erro ao buscar ordens disponíveis: {e}")
        return []

@router.post("/programacoes-manuais", operation_id="pcp_post_programacoes_manuais")
async def criar_programacao_manual(
    programacao: ProgramacaoPCPCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar programação manual via PCP
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem criar programações")

        # Buscar OS
        ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == programacao.id_ordem_servico).first()
        if not ordem_servico:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

        # Buscar setor
        setor = db.query(Setor).filter(Setor.id == ordem_servico.id_setor).first()
        if not setor:
            raise HTTPException(status_code=404, detail="Setor não encontrado")

        # Verificar se já existe programação para esta OS
        programacao_existente = db.query(Programacao).filter(
            Programacao.id_ordem_servico == programacao.id_ordem_servico
        ).first()
        
        if programacao_existente:
            raise HTTPException(status_code=400, detail="Já existe programação para esta ordem de serviço")

        # Criar nova programação
        nova_programacao = Programacao(
            id_ordem_servico=programacao.id_ordem_servico,
            inicio_previsto=programacao.inicio_previsto,
            fim_previsto=programacao.fim_previsto,
            responsavel_id=programacao.responsavel_id,
            status=programacao.status or 'PROGRAMADA',
            observacoes=programacao.observacoes or f"Programação manual criada via PCP para OS {ordem_servico.os_numero}",
            criado_por_id=current_user.id,  # type: ignore
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id_setor=ordem_servico.id_setor
        )

        db.add(nova_programacao)
        db.commit()
        db.refresh(nova_programacao)

        return {
            "message": "Programação criada com sucesso",
            "id": nova_programacao.id,
            "os_numero": ordem_servico.os_numero,
            "inicio_previsto": programacao.inicio_previsto.isoformat() if programacao.inicio_previsto else datetime.now().isoformat(),
            "fim_previsto": programacao.fim_previsto.isoformat() if programacao.fim_previsto else datetime.now().isoformat()
        }

    except Exception as e:
        db.rollback()
        print(f"Erro ao criar programação manual: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar programação: {str(e)}")

@router.get("/setores-producao", operation_id="pcp_get_setores_producao")
async def get_setores_producao(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter lista de setores de produção para distribuição de programações
    """
    try:
        # Buscar todos os setores ativos
        setores = db.query(Setor).filter(Setor.ativo.is_(True)).all()  # type: ignore
        
        setores_com_detalhes = []
        for setor in setores:
            # Buscar colaboradores disponíveis do setor
            colaboradores = db.query(Usuario).filter(
                Usuario.id_setor == setor.id,  # type: ignore
                Usuario.is_approved.is_(True),
                Usuario.privilege_level.in_(['USER', 'SUPERVISOR'])
            ).all()

            # Buscar programações ativas do setor
            programacoes_ativas = db.query(Programacao).filter(
                Programacao.id_setor == setor.id,
                Programacao.status.in_(['AGENDADO', 'EM_ANDAMENTO'])
            ).count()
            
            setores_com_detalhes.append({
                "id": setor.id,
                "nome": setor.nome,
                "id_departamento": setor.id_departamento,
                "descricao": setor.descricao,
                "ativo": setor.ativo,
                "total_colaboradores": len(colaboradores),
                "colaboradores_disponiveis": len([c for c in colaboradores if c.is_approved]),  # type: ignore
                "programacoes_ativas": programacoes_ativas,
                "capacidade_disponivel": max(0, 10 - programacoes_ativas)  # Capacidade estimada
            })
        
        return setores_com_detalhes
        
    except Exception as e:
        print(f"Erro ao buscar setores de produção: {e}")
        return []

@router.get("/programacoes-enviadas", operation_id="pcp_get_programacoes_enviadas")
async def get_programacoes_enviadas(
    data: Optional[str] = Query(None),
    setor: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter programações enviadas para setores de produção
    """
    try:
        query = db.query(Programacao)
        
        # Filtrar por permissão
        if current_user.privilege_level != 'ADMIN':  # type: ignore
            # Supervisores veem apenas do seu setor
            query = query.filter(Programacao.id_setor == current_user.id_setor)
        
        # Aplicar filtros
        if data:
            try:
                data_filtro = datetime.strptime(data, '%Y-%m-%d').date()
                query = query.filter(func.date(Programacao.inicio_previsto) == data_filtro)
            except ValueError:
                pass
        
        if setor:
            query = query.filter(Programacao.id_setor == setor)
        
        if status:
            query = query.filter(Programacao.status == status)
        
        programacoes = query.order_by(
            desc(Programacao.inicio_previsto),
            Programacao.created_at
        ).limit(100).all()
        
        return [
            {
                "id": prog.id,
                "id_ordem_servico": prog.id_ordem_servico,
                "numero_os": f"OS-{prog.id_ordem_servico}",
                "cliente": "Cliente não informado",
                "equipamento": "Equipamento não informado",
                "tipo_atividade": "Atividade padrão",
                "data_programada": prog.inicio_previsto.isoformat() if prog.inicio_previsto is not None else None,
                "hora_inicio": prog.inicio_previsto.strftime("%H:%M") if prog.inicio_previsto is not None else None,
                "hora_fim": prog.fim_previsto.strftime("%H:%M") if prog.fim_previsto is not None else None,
                "status": prog.status,
                "setor": "Não informado",
                "departamento": "Não informado",
                "responsavel_id": prog.responsavel_id,
                "observacoes": prog.observacoes or "",
                "created_at": str(prog.created_at) if prog.created_at is not None else None,
                "updated_at": str(prog.updated_at) if prog.updated_at is not None else None
            }
            for prog in programacoes
        ]
        
    except Exception as e:
        print(f"Erro ao buscar programações enviadas: {e}")
        return []

@router.patch("/programacoes/{programacao_id}/status", operation_id="pcp_patch_programacoes_programacao_id_status")
async def atualizar_status_programacao(
    programacao_id: int,
    status: str,
    observacoes: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar status de uma programação enviada para os setores
    """
    try:
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada")
        
        # Verificar permissão
        if current_user.privilege_level != 'ADMIN':  # type: ignore
            if current_user.privilege_level == 'SUPERVISOR' and programacao.id_setor != current_user.id_setor:  # type: ignore
                raise HTTPException(status_code=403, detail="Sem permissão para esta programação")
        
        # Atualizar status
        programacao.status = status  # type: ignore
        programacao.updated_at = datetime.now()  # type: ignore
        
        if observacoes:
            if programacao.observacoes is None:  # type: ignore
                programacao.observacoes = observacoes  # type: ignore
            else:
                programacao.observacoes += f" | {observacoes}"  # type: ignore
        
        db.commit()
        
        return {
            "message": "Status atualizado com sucesso",
            "programacao_id": programacao_id,
            "novo_status": status,
            "data_atualizacao": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao atualizar status da programação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")

@router.get("/relatorio-programacoes", operation_id="pcp_get_relatorio_programacoes")
async def get_relatorio_programacoes(
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gerar relatório de programações enviadas para setores de produção
    """
    try:
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=30)
        if not data_fim:
            data_fim = date.today()
        
        query = db.query(Programacao).filter(
            func.date(Programacao.inicio_previsto) >= data_inicio,
            func.date(Programacao.inicio_previsto) <= data_fim
        )
        
        # Filtrar por permissão (simplificado)
        # if current_user.privilege_level != 'ADMIN':
        #     query = query.filter(Programacao.id_setor == current_user.id_setor)
        
        programacoes = query.all()
        
        # Gerar estatísticas
        total_programacoes = len(programacoes)
        programacoes_por_setor = {}
        programacoes_por_status = {}
        
        for prog in programacoes:
            # Por setor
            setor = "Não informado"
            if setor not in programacoes_por_setor:
                programacoes_por_setor[setor] = 0
            programacoes_por_setor[setor] += 1
            
            # Por status
            status = prog.status or "Não informado"
            if status not in programacoes_por_status:
                programacoes_por_status[status] = 0
            programacoes_por_status[status] += 1
        
        return {
            "periodo": {
                "data_inicio": data_inicio.isoformat(),
                "data_fim": data_fim.isoformat()
            },
            "total_programacoes": total_programacoes,
            "programacoes_por_setor": programacoes_por_setor,
            "programacoes_por_status": programacoes_por_status,
            "detalhes": [
                {
                    "id": prog.id,
                    "numero_os": f"OS-{prog.id_ordem_servico}",
                    "setor": "Não informado",
                    "data_programada": prog.inicio_previsto.isoformat() if prog.inicio_previsto is not None else None,
                    "hora_inicio": prog.inicio_previsto.strftime("%H:%M") if prog.inicio_previsto is not None else None,
                    "status": prog.status,
                    "criado_por": f"Usuário {prog.criado_por_id}"
                }
                for prog in programacoes
            ]
        }
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/pendencias", operation_id="pcp_get_pendencias")
async def get_pendencias_pcp(
    status: Optional[str] = Query(None, description="Filtrar por status: ABERTA, FECHADA"),
    setor: Optional[str] = Query(None, description="Filtrar por setor"),
    prioridade: Optional[str] = Query(None, description="Filtrar por prioridade"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Visualizar pendências para o PCP - apenas visualização, sem resolução
    O PCP precisa saber das pendências geradas mas não pode resolver
    """
    try:
        query = db.query(Pendencia)

        # Aplicar filtros
        if status:
            query = query.filter(Pendencia.status == status)
        if prioridade:
            query = query.filter(Pendencia.prioridade == prioridade)
        if setor:
            # Filtrar por setor através do apontamento origem
            setor_obj = db.query(Setor).filter(Setor.nome == setor).first()
            if setor_obj:
                apontamento_ids = db.query(ApontamentoDetalhado.id).filter(
                    ApontamentoDetalhado.id_setor == setor_obj.id
                ).all()
                ids_list = [apt.id for apt in apontamento_ids]
                if ids_list:
                    query = query.filter(Pendencia.id_apontamento_origem.in_(ids_list))

        # Ordenar por data de criação (mais recentes primeiro)
        pendencias = query.order_by(desc(Pendencia.data_inicio)).limit(100).all()

        return {
            "total": len(pendencias),
            "pendencias": [
                {
                    "id": pend.id,
                    "numero_os": pend.numero_os,
                    "cliente": pend.cliente,
                    "tipo_maquina": pend.tipo_maquina,
                    "descricao_maquina": pend.descricao_maquina,
                    "descricao_pendencia": pend.descricao_pendencia,
                    "status": pend.status,
                    "prioridade": pend.prioridade,
                    "data_inicio": pend.data_inicio.isoformat() if pend.data_inicio is not None else None,
                    "data_fechamento": pend.data_fechamento.isoformat() if pend.data_fechamento is not None else None,
                    "responsavel_inicio_id": pend.id_responsavel_inicio,
                    "responsavel_fechamento_id": pend.id_responsavel_fechamento,
                    "id_apontamento_origem": pend.id_apontamento_origem,
                    "observacoes_fechamento": pend.observacoes_fechamento or "",
                    "tempo_aberto_horas": pend.tempo_aberto_horas or 0,
                    # Campos específicos para PCP
                    "pode_resolver": False,  # PCP não pode resolver pendências
                    "visualizacao_apenas": True
                }
                for pend in pendencias
            ]
        }

    except Exception as e:
        print(f"Erro ao buscar pendências para PCP: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pendências: {str(e)}")

@router.get("/pendencias/dashboard", operation_id="pcp_get_pendencias_dashboard")
async def get_pendencias_dashboard(
    periodo_dias: Optional[int] = Query(30, description="Período em dias para análise"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard de pendências para PCP com métricas e análises
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, case

        # Data limite para análise
        data_limite = datetime.now() - timedelta(days=periodo_dias or 30)

        # Métricas básicas
        total_pendencias = db.query(Pendencia).count()
        pendencias_abertas = db.query(Pendencia).filter(Pendencia.status == 'ABERTA').count()
        pendencias_fechadas = db.query(Pendencia).filter(Pendencia.status == 'FECHADA').count()
        pendencias_periodo = db.query(Pendencia).filter(Pendencia.data_inicio >= data_limite).count()

        # Pendências por prioridade
        pendencias_por_prioridade = db.query(
            Pendencia.prioridade,
            func.count(Pendencia.id).label('total')
        ).filter(Pendencia.status == 'ABERTA').group_by(Pendencia.prioridade).all()

        # Pendências por setor (através dos apontamentos)
        pendencias_por_setor = db.query(
            Setor.nome.label('setor'),
            func.count(Pendencia.id).label('total')
        ).join(
            ApontamentoDetalhado, Pendencia.id_apontamento_origem == ApontamentoDetalhado.id
        ).join(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).filter(Pendencia.status == 'ABERTA').group_by(Setor.nome).all()

        # Tempo médio de resolução
        tempo_medio_resolucao = db.query(
            func.avg(Pendencia.tempo_aberto_horas).label('media')
        ).filter(Pendencia.status == 'FECHADA').scalar() or 0

        # Pendências críticas (alta prioridade + tempo aberto > 24h)
        pendencias_criticas = db.query(Pendencia).filter(
            and_(
                Pendencia.status == 'ABERTA',
                or_(
                    Pendencia.prioridade == 'ALTA',
                    Pendencia.prioridade == 'URGENTE',
                    func.julianday('now') - func.julianday(Pendencia.data_inicio) > 1
                )
            )
        ).count()

        # Evolução das pendências nos últimos 7 dias
        evolucao_pendencias = []
        for i in range(7):
            data = datetime.now() - timedelta(days=i)
            data_inicio = data.replace(hour=0, minute=0, second=0, microsecond=0)
            data_fim = data_inicio + timedelta(days=1)

            abertas = db.query(Pendencia).filter(
                and_(
                    Pendencia.data_inicio >= data_inicio,
                    Pendencia.data_inicio < data_fim
                )
            ).count()

            fechadas = db.query(Pendencia).filter(
                and_(
                    Pendencia.data_fechamento >= data_inicio,
                    Pendencia.data_fechamento < data_fim
                )
            ).count()

            evolucao_pendencias.append({
                "data": data.strftime("%Y-%m-%d"),
                "abertas": abertas,
                "fechadas": fechadas
            })

        return {
            "metricas_gerais": {
                "total_pendencias": total_pendencias,
                "pendencias_abertas": pendencias_abertas,
                "pendencias_fechadas": pendencias_fechadas,
                "pendencias_periodo": pendencias_periodo,
                "pendencias_criticas": pendencias_criticas,
                "tempo_medio_resolucao_horas": round(tempo_medio_resolucao, 2)
            },
            "distribuicao_prioridade": [
                {"prioridade": item.prioridade or "NORMAL", "total": item.total}
                for item in pendencias_por_prioridade
            ],
            "distribuicao_setor": [
                {"setor": item.setor, "total": item.total}
                for item in pendencias_por_setor
            ],
            "evolucao_7_dias": list(reversed(evolucao_pendencias))
        }

    except Exception as e:
        print(f"Erro ao buscar dashboard de pendências: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dashboard: {str(e)}")

@router.get("/pendencias/{pendencia_id}", operation_id="pcp_get_pendencia_detalhes")
async def get_pendencia_detalhes(
    pendencia_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter detalhes completos de uma pendência específica
    """
    try:
        pendencia = db.query(Pendencia).filter(Pendencia.id == pendencia_id).first()

        if not pendencia:
            raise HTTPException(status_code=404, detail="Pendência não encontrada")

        # Buscar dados do responsável de início
        responsavel_inicio = db.query(Usuario).filter(Usuario.id == pendencia.id_responsavel_inicio).first()

        # Buscar dados do responsável de fechamento (se houver)
        responsavel_fechamento = None
        if pendencia.id_responsavel_fechamento is not None:
            responsavel_fechamento = db.query(Usuario).filter(Usuario.id == pendencia.id_responsavel_fechamento).first()

        # Buscar apontamento de origem
        apontamento_origem = None
        if pendencia.id_apontamento_origem is not None:
            apontamento_origem = db.query(ApontamentoDetalhado).filter(
                ApontamentoDetalhado.id == pendencia.id_apontamento_origem
            ).first()

        # Buscar setor relacionado
        setor_relacionado = None
        if apontamento_origem:
            setor_relacionado = db.query(Setor).filter(Setor.id == apontamento_origem.id_setor).first()

        # Calcular tempo aberto atual
        tempo_aberto_atual = 0
        if str(pendencia.status) == 'ABERTA' and pendencia.data_inicio is not None:
            tempo_aberto_atual = (datetime.now() - pendencia.data_inicio).total_seconds() / 3600

        return {
            "id": pendencia.id,
            "numero_os": pendencia.numero_os,
            "cliente": pendencia.cliente,
            "tipo_maquina": pendencia.tipo_maquina,
            "descricao_maquina": pendencia.descricao_maquina,
            "descricao_pendencia": pendencia.descricao_pendencia,
            "status": pendencia.status,
            "prioridade": pendencia.prioridade,
            "data_inicio": pendencia.data_inicio.isoformat() if pendencia.data_inicio is not None else None,
            "data_fechamento": pendencia.data_fechamento.isoformat() if pendencia.data_fechamento is not None else None,
            "solucao_aplicada": pendencia.solucao_aplicada,
            "observacoes_fechamento": pendencia.observacoes_fechamento,
            "tempo_aberto_horas": pendencia.tempo_aberto_horas or tempo_aberto_atual,
            "tempo_aberto_atual": round(tempo_aberto_atual, 2),
            "responsavel_inicio": {
                "id": responsavel_inicio.id if responsavel_inicio else None,
                "nome": responsavel_inicio.nome_completo if responsavel_inicio else "Usuário não encontrado",
                "id_setor": responsavel_inicio.id_setor if responsavel_inicio else None,
                "id_departamento": responsavel_inicio.id_departamento if responsavel_inicio else None
            } if responsavel_inicio else None,
            "responsavel_fechamento": {
                "id": responsavel_fechamento.id if responsavel_fechamento else None,
                "nome": responsavel_fechamento.nome_completo if responsavel_fechamento else None,
                "id_setor": responsavel_fechamento.id_setor if responsavel_fechamento else None,
                "id_departamento": responsavel_fechamento.id_departamento if responsavel_fechamento else None
            } if responsavel_fechamento else None,
            "setor_relacionado": {
                "id": setor_relacionado.id if setor_relacionado else None,
                "nome": setor_relacionado.nome if setor_relacionado else None,
                "id_departamento": setor_relacionado.id_departamento if setor_relacionado else None
            } if setor_relacionado else None,
            "apontamento_origem_id": pendencia.id_apontamento_origem,
            "data_criacao": pendencia.data_criacao.isoformat() if pendencia.data_criacao is not None else None,
            "data_ultima_atualizacao": pendencia.data_ultima_atualizacao.isoformat() if pendencia.data_ultima_atualizacao is not None else None
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao buscar detalhes da pendência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar detalhes: {str(e)}")

@router.get("/ordens-servico", operation_id="pcp_get_ordens_servico")
async def get_ordens_servico_pcp(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter ordens de serviço disponíveis para PCP"""
    try:
        from sqlalchemy import text

        sql = text("""
            SELECT os.id, os.os_numero, os.descricao_maquina, os.status_os,
                   os.data_criacao, os.fim_os, os.id_cliente,
                   os.id_tipo_maquina
            FROM ordens_servico os
            WHERE os.status_os IN ('ABERTA', 'EM ANDAMENTO', 'AGUARDANDO')
            ORDER BY os.data_criacao DESC
            LIMIT 100
        """)

        result = db.execute(sql)
        ordens = result.fetchall()

        return [
            {
                "id": row[0],
                "os_numero": row[1] or "",
                "descricao_maquina": row[2] or "",
                "status": row[3] or "ABERTA",
                "data_abertura": str(row[4]) if row[4] else None,
                "data_fechamento": str(row[5]) if row[5] else None,
                "id_cliente": row[6],
                "id_tipo_maquina": row[7],
                "cliente_nome": "Cliente não informado",
                "tipo_maquina_nome": "Não informado"
            }
            for row in ordens
        ]

    except Exception as e:
        print(f"Erro ao buscar ordens de serviço PCP: {e}")
        return []

@router.get("/programacao-form-data", operation_id="pcp_get_programacao_form_data")
async def get_programacao_form_data(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter dados para formulário de programação"""
    try:
        from sqlalchemy import text

        # Buscar setores com informações de departamento
        setores_sql = text("""
            SELECT s.id, s.nome, s.id_departamento, d.nome_tipo as departamento_nome
            FROM tipo_setores s
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            ORDER BY s.nome
        """)
        setores_result = db.execute(setores_sql)
        setores = [
            {
                "id": row[0],
                "nome": row[1],
                "id_departamento": row[2],
                "departamento_nome": row[3] or "Não informado"
            }
            for row in setores_result.fetchall()
        ]

        # Buscar lista de departamentos disponíveis
        departamentos_sql = text("SELECT id, nome_tipo FROM tipo_departamentos ORDER BY nome_tipo")
        departamentos_result = db.execute(departamentos_sql)
        departamentos = [
            {"id": row[0], "nome_tipo": row[1]}
            for row in departamentos_result.fetchall()
        ]

        # Buscar apenas supervisores da produção
        usuarios_sql = text("""
            SELECT u.id, u.nome_completo, u.privilege_level, u.id_setor, u.id_departamento,
                   s.nome as setor_nome, d.nome_tipo as departamento_nome
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON u.id_departamento = d.id
            WHERE u.is_approved = 1
            AND u.privilege_level = 'SUPERVISOR'
            AND u.trabalha_producao = 1
            AND s.area_tipo = 'PRODUCAO'
            ORDER BY u.nome_completo
        """)
        usuarios_result = db.execute(usuarios_sql)
        usuarios = [
            {
                "id": row[0],
                "nome_completo": row[1],
                "privilege_level": row[2] or "",
                "id_setor": row[3],
                "id_departamento": row[4],
                "setor_nome": row[5] or "",
                "departamento_nome": row[6] or ""
            }
            for row in usuarios_result.fetchall()
        ]

        # Buscar ordens de serviço disponíveis (sem JOINs problemáticos)
        ordens_sql = text("""
            SELECT os.id, os.os_numero, os.descricao_maquina, os.status_os
            FROM ordens_servico os
            WHERE os.status_os IN ('ABERTA', 'EM ANDAMENTO', 'AGUARDANDO')
            ORDER BY os.data_criacao DESC
            LIMIT 100
        """)
        ordens_result = db.execute(ordens_sql)
        ordens_servico = [
            {
                "id": row[0],
                "os_numero": row[1] or "",
                "descricao_maquina": row[2] or "",
                "status": row[3] or "ABERTA",
                "cliente_nome": "Cliente não informado",
                "tipo_maquina_nome": "Não informado",
                "setor": "Produção"  # valor padrão
            }
            for row in ordens_result.fetchall()
        ]

        return {
            "setores": setores,
            "departamentos": departamentos,
            "usuarios": usuarios,
            "ordens_servico": ordens_servico,
            "status_opcoes": ["PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA"]
        }

    except Exception as e:
        print(f"Erro ao buscar dados do formulário: {e}")
        return {
            "setores": [],
            "departamentos": [],
            "usuarios": [],
            "ordens_servico": [],
            "status_opcoes": ["PROGRAMADA", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA"]
        }

# =============================================================================
# ENDPOINTS EXPANDIDOS DE PROGRAMAÇÕES
# =============================================================================

@router.post("/programacoes", operation_id="pcp_create_programacao")
async def create_programacao_pcp(
    programacao_data: ProgramacaoPCPCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Criar nova programação via PCP
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem criar programações")

        # Verificar se a OS existe
        ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == programacao_data.id_ordem_servico).first()
        if not ordem_servico:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

        # Verificar se já existe programação para esta OS
        programacao_existente = db.query(Programacao).filter(
            Programacao.id_ordem_servico == programacao_data.id_ordem_servico,
            Programacao.status.in_(['PROGRAMADA', 'EM_ANDAMENTO'])
        ).first()

        if programacao_existente:
            raise HTTPException(status_code=400, detail="Já existe uma programação ativa para esta OS")

        # Buscar setor para obter departamento
        setor = db.query(Setor).filter(Setor.id == programacao_data.id_setor).first()
        if not setor:
            raise HTTPException(status_code=404, detail="Setor não encontrado")

        # Criar nova programação
        nova_programacao = Programacao(
            id_ordem_servico=programacao_data.id_ordem_servico,
            criado_por_id=current_user.id,  # type: ignore
            responsavel_id=programacao_data.responsavel_id,
            inicio_previsto=programacao_data.inicio_previsto,
            fim_previsto=programacao_data.fim_previsto,
            observacoes=programacao_data.observacoes,
            status=programacao_data.status or "PROGRAMADA",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id_setor=programacao_data.id_setor
        )

        # Atualizar campos da OS com setor e departamento corretos
        ordem_servico.id_setor = programacao_data.id_setor  # type: ignore
        ordem_servico.id_departamento = setor.id_departamento  # type: ignore
        ordem_servico.data_ultima_atualizacao = datetime.now()  # type: ignore

        db.add(nova_programacao)
        db.commit()
        db.refresh(nova_programacao)

        return {
            "id": nova_programacao.id,
            "id_ordem_servico": nova_programacao.id_ordem_servico,
            "os_numero": ordem_servico.os_numero,
            "status": nova_programacao.status,
            "inicio_previsto": nova_programacao.inicio_previsto.isoformat(),
            "fim_previsto": nova_programacao.fim_previsto.isoformat(),
            "criado_por": current_user.nome_completo,  # type: ignore
            "message": "Programação criada com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar programação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar programação: {str(e)}")

@router.put("/programacoes/{programacao_id}", operation_id="pcp_update_programacao")
async def update_programacao_pcp(
    programacao_id: int,
    programacao_data: ProgramacaoPCPCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualizar programação existente
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem atualizar programações")

        # Buscar programação
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada")

        # Atualizar campos
        programacao.id_ordem_servico = programacao_data.id_ordem_servico  # type: ignore
        programacao.responsavel_id = programacao_data.responsavel_id  # type: ignore
        programacao.inicio_previsto = programacao_data.inicio_previsto  # type: ignore
        programacao.fim_previsto = programacao_data.fim_previsto  # type: ignore
        programacao.observacoes = programacao_data.observacoes  # type: ignore
        programacao.status = programacao_data.status or programacao.status  # type: ignore
        if programacao_data.id_setor is not None:
            programacao.id_setor = programacao_data.id_setor  # type: ignore
        programacao.updated_at = datetime.now()  # type: ignore

        db.commit()
        db.refresh(programacao)

        return {
            "id": programacao.id,
            "status": programacao.status,
            "message": "Programação atualizada com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao atualizar programação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar programação: {str(e)}")

@router.delete("/programacoes/{programacao_id}", operation_id="pcp_delete_programacao")
async def delete_programacao_pcp(
    programacao_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancelar/deletar programação
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem cancelar programações")

        # Buscar programação
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada")

        # Verificar se pode ser cancelada
        if str(programacao.status) == 'CONCLUIDA':
            raise HTTPException(status_code=400, detail="Não é possível cancelar uma programação já concluída")

        # Marcar como cancelada ao invés de deletar
        programacao.status = 'CANCELADA'  # type: ignore
        programacao.updated_at = datetime.now()  # type: ignore

        db.commit()

        return {
            "id": programacao.id,
            "status": "CANCELADA",
            "message": "Programação cancelada com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao cancelar programação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao cancelar programação: {str(e)}")

@router.post("/programacoes/{programacao_id}/enviar-setor", operation_id="pcp_enviar_programacao_setor")
async def enviar_programacao_setor(
    programacao_id: int,
    setor_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar programação para um setor específico
    """
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:  # type: ignore
            raise HTTPException(status_code=403, detail="Apenas administradores e supervisores podem enviar programações")

        # Buscar programação
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada")

        # Buscar setor
        setor = db.query(Setor).filter(Setor.id == setor_id).first()
        if not setor:
            raise HTTPException(status_code=404, detail="Setor não encontrado")

        # Atualizar programação com setor
        programacao.id_setor = setor_id  # type: ignore
        programacao.status = 'ENVIADA'  # type: ignore
        programacao.updated_at = datetime.now()  # type: ignore

        db.commit()

        return {
            "id": programacao.id,
            "setor_nome": setor.nome,
            "status": "ENVIADA",
            "message": f"Programação enviada para o setor {setor.nome} com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao enviar programação para setor: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao enviar programação: {str(e)}")

@router.get("/programacoes/dashboard", operation_id="pcp_get_programacoes_dashboard")
async def get_programacoes_dashboard(
    periodo_dias: Optional[int] = Query(30, description="Período em dias para análise"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard de programações para PCP com métricas e análises
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Data limite para análise
        data_limite = datetime.now() - timedelta(days=periodo_dias or 30)

        # Métricas básicas
        total_programacoes = db.query(Programacao).count()
        programacoes_ativas = db.query(Programacao).filter(
            Programacao.status.in_(['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA'])
        ).count()
        programacoes_concluidas = db.query(Programacao).filter(Programacao.status == 'CONCLUIDA').count()
        programacoes_canceladas = db.query(Programacao).filter(Programacao.status == 'CANCELADA').count()

        # Programações por status
        programacoes_por_status = db.query(
            Programacao.status,
            func.count(Programacao.id).label('total')
        ).group_by(Programacao.status).all()

        # Programações por setor
        programacoes_por_setor = db.query(
            Setor.nome.label('setor'),
            func.count(Programacao.id).label('total')
        ).join(
            Setor, Programacao.id_setor == Setor.id
        ).filter(
            Programacao.status.in_(['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA'])
        ).group_by(Setor.nome).all()

        # Programações atrasadas (fim previsto já passou)
        programacoes_atrasadas = db.query(Programacao).filter(
            and_(
                Programacao.fim_previsto < datetime.now(),
                Programacao.status.in_(['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA'])
            )
        ).count()

        # Programações próximas do prazo (próximas 24h)
        prazo_limite = datetime.now() + timedelta(hours=24)
        programacoes_prazo_critico = db.query(Programacao).filter(
            and_(
                Programacao.fim_previsto <= prazo_limite,
                Programacao.fim_previsto > datetime.now(),
                Programacao.status.in_(['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA'])
            )
        ).count()

        # Evolução das programações nos últimos 7 dias
        evolucao_programacoes = []
        for i in range(7):
            data = datetime.now() - timedelta(days=i)
            data_inicio = data.replace(hour=0, minute=0, second=0, microsecond=0)
            data_fim = data_inicio + timedelta(days=1)

            criadas = db.query(Programacao).filter(
                and_(
                    Programacao.created_at >= data_inicio,
                    Programacao.created_at < data_fim
                )
            ).count()

            concluidas = db.query(Programacao).filter(
                and_(
                    Programacao.updated_at >= data_inicio,
                    Programacao.updated_at < data_fim,
                    Programacao.status == 'CONCLUIDA'
                )
            ).count()

            evolucao_programacoes.append({
                "data": data.strftime("%Y-%m-%d"),
                "criadas": criadas,
                "concluidas": concluidas
            })

        # Taxa de conclusão no prazo
        programacoes_no_prazo = db.query(Programacao).filter(
            and_(
                Programacao.status == 'CONCLUIDA',
                Programacao.updated_at <= Programacao.fim_previsto
            )
        ).count()

        taxa_conclusao_prazo = 0
        if programacoes_concluidas > 0:
            taxa_conclusao_prazo = round((programacoes_no_prazo / programacoes_concluidas) * 100, 2)

        return {
            "metricas_gerais": {
                "total_programacoes": total_programacoes,
                "programacoes_ativas": programacoes_ativas,
                "programacoes_concluidas": programacoes_concluidas,
                "programacoes_canceladas": programacoes_canceladas,
                "programacoes_atrasadas": programacoes_atrasadas,
                "programacoes_prazo_critico": programacoes_prazo_critico,
                "taxa_conclusao_prazo": taxa_conclusao_prazo
            },
            "distribuicao_status": [
                {"status": item.status or "SEM_STATUS", "total": item.total}
                for item in programacoes_por_status
            ],
            "distribuicao_setor": [
                {"setor": item.setor, "total": item.total}
                for item in programacoes_por_setor
            ],
            "evolucao_7_dias": list(reversed(evolucao_programacoes))
        }

    except Exception as e:
        print(f"Erro ao buscar dashboard de programações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dashboard: {str(e)}")

@router.get("/dashboard/avancado", operation_id="pcp_get_dashboard_avancado")
async def get_dashboard_avancado(
    periodo_dias: Optional[int] = Query(30, description="Período em dias para análise"),
    setor_id: Optional[int] = Query(None, description="Filtrar por setor específico"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dashboard avançado do PCP com métricas detalhadas de produção e eficiência
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, case, extract

        # Data limite para análise
        data_limite = datetime.now() - timedelta(days=periodo_dias or 30)

        # =============================================================================
        # MÉTRICAS GERAIS DE PRODUÇÃO
        # =============================================================================

        # Ordens de serviço por status
        os_por_status = db.query(
            OrdemServico.status_os,
            func.count(OrdemServico.id).label('total')
        ).group_by(OrdemServico.status_os).all()

        # Apontamentos por setor no período
        # Calcular tempo gasto como soma das etapas
        apontamentos_por_setor = db.query(
            Setor.id.label('id_setor'),
            Setor.nome.label('setor'),
            func.count(ApontamentoDetalhado.id).label('total_apontamentos'),
            func.avg(
                func.coalesce(ApontamentoDetalhado.horas_etapa_inicial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_parcial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_final, 0)
            ).label('tempo_medio')
        ).join(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).filter(
            ApontamentoDetalhado.data_hora_inicio >= data_limite
        ).group_by(Setor.id, Setor.nome).all()

        # Pendências por setor
        pendencias_por_setor = db.query(
            Setor.id.label('id_setor'),
            Setor.nome.label('setor'),
            func.count(Pendencia.id).label('total_pendencias'),
            func.sum(case((Pendencia.status == 'ABERTA', 1), else_=0)).label('pendencias_abertas')
        ).join(
            ApontamentoDetalhado, Pendencia.id_apontamento_origem == ApontamentoDetalhado.id
        ).join(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).group_by(Setor.id, Setor.nome).all()

        # =============================================================================
        # ANÁLISE DE EFICIÊNCIA
        # =============================================================================

        # Tempo médio de execução por tipo de máquina
        tempo_por_tipo_maquina = db.query(
            TipoMaquina.nome_tipo.label('tipo_maquina'),
            func.avg(
                func.coalesce(ApontamentoDetalhado.horas_etapa_inicial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_parcial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_final, 0)
            ).label('tempo_medio'),
            func.count(ApontamentoDetalhado.id).label('total_apontamentos')
        ).join(
            OrdemServico, ApontamentoDetalhado.id_os == OrdemServico.id
        ).join(
            TipoMaquina, OrdemServico.id_tipo_maquina == TipoMaquina.id
        ).filter(
            ApontamentoDetalhado.data_hora_inicio >= data_limite
        ).group_by(TipoMaquina.nome_tipo).all()

        # Taxa de retrabalho por setor
        retrabalho_por_setor = db.query(
            Setor.id.label('id_setor'),
            Setor.nome.label('setor'),
            func.count(ApontamentoDetalhado.id).label('total_apontamentos'),
            func.sum(case((ApontamentoDetalhado.foi_retrabalho.is_(True), 1), else_=0)).label('retrabalhos')
        ).join(
            Setor, ApontamentoDetalhado.id_setor == Setor.id
        ).filter(
            ApontamentoDetalhado.data_hora_inicio >= data_limite
        ).group_by(Setor.id, Setor.nome).all()

        # =============================================================================
        # ANÁLISE TEMPORAL
        # =============================================================================

        # Produtividade por dia da semana
        produtividade_semanal = db.query(
            extract('dow', ApontamentoDetalhado.data_hora_inicio).label('dia_semana'),
            func.count(ApontamentoDetalhado.id).label('total_apontamentos'),
            func.avg(
                func.coalesce(ApontamentoDetalhado.horas_etapa_inicial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_parcial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_final, 0)
            ).label('tempo_medio')
        ).filter(
            ApontamentoDetalhado.data_hora_inicio >= data_limite
        ).group_by(extract('dow', ApontamentoDetalhado.data_hora_inicio)).all()

        # Evolução mensal de OS abertas vs fechadas
        evolucao_mensal = []
        for i in range(6):  # Últimos 6 meses
            data_ref = datetime.now() - timedelta(days=30*i)
            inicio_mes = data_ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                fim_mes = datetime.now()
            else:
                fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            os_abertas = db.query(OrdemServico).filter(
                and_(
                    OrdemServico.data_criacao >= inicio_mes,
                    OrdemServico.data_criacao <= fim_mes
                )
            ).count()

            os_fechadas = db.query(OrdemServico).filter(
                and_(
                    OrdemServico.fim_os >= inicio_mes,
                    OrdemServico.fim_os <= fim_mes,
                    OrdemServico.status_os == 'FINALIZADA'
                )
            ).count()

            evolucao_mensal.append({
                "mes": inicio_mes.strftime("%Y-%m"),
                "os_abertas": os_abertas,
                "os_fechadas": os_fechadas
            })

        # =============================================================================
        # INDICADORES DE PERFORMANCE (KPIs)
        # =============================================================================

        # Tempo médio de ciclo (abertura até fechamento)
        tempo_ciclo_medio = db.query(
            func.avg(
                func.julianday(OrdemServico.fim_os) - func.julianday(OrdemServico.data_criacao)
            ).label('dias_medio')
        ).filter(
            and_(
                OrdemServico.status_os == 'FINALIZADA',
                OrdemServico.fim_os.isnot(None),
                OrdemServico.data_criacao >= data_limite
            )
        ).scalar() or 0

        # Taxa de cumprimento de prazo
        os_no_prazo = db.query(OrdemServico).filter(
            and_(
                OrdemServico.status_os == 'FINALIZADA',
                OrdemServico.fim_os <= OrdemServico.data_fim_prevista,
                OrdemServico.data_criacao >= data_limite
            )
        ).count()

        total_os_finalizadas = db.query(OrdemServico).filter(
            and_(
                OrdemServico.status_os == 'FINALIZADA',
                OrdemServico.data_criacao >= data_limite
            )
        ).count()

        taxa_cumprimento_prazo = 0
        if total_os_finalizadas > 0:
            taxa_cumprimento_prazo = round((os_no_prazo / total_os_finalizadas) * 100, 2)

        # Utilização de recursos (baseado em apontamentos)
        utilizacao_recursos = db.query(
            func.sum(
                func.coalesce(ApontamentoDetalhado.horas_etapa_inicial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_parcial, 0) +
                func.coalesce(ApontamentoDetalhado.horas_etapa_final, 0)
            ).label('horas_trabalhadas')
        ).filter(
            ApontamentoDetalhado.data_hora_inicio >= data_limite
        ).scalar() or 0

        # Calcular eficiência por setor
        eficiencia_setores = []
        for setor_info in apontamentos_por_setor:
            # Buscar pendências para este setor
            pendencias_setor = next(
                (p for p in pendencias_por_setor if p.id_setor == setor_info.id_setor),
                None
            )

            # Buscar retrabalho para este setor
            retrabalho_setor = next(
                (r for r in retrabalho_por_setor if r.id_setor == setor_info.id_setor),
                None
            )

            # Calcular eficiência (fórmula simplificada)
            taxa_retrabalho = 0
            if retrabalho_setor and retrabalho_setor.total_apontamentos > 0:
                taxa_retrabalho = (retrabalho_setor.retrabalhos / retrabalho_setor.total_apontamentos) * 100

            pendencias_abertas = 0
            if pendencias_setor:
                pendencias_abertas = pendencias_setor.pendencias_abertas or 0

            # Eficiência = 100% - taxa_retrabalho - (pendencias_abertas * 5)
            eficiencia = max(0, 100 - taxa_retrabalho - (pendencias_abertas * 5))

            eficiencia_setores.append({
                "id_setor": setor_info.id_setor,
                "total_apontamentos": setor_info.total_apontamentos,
                "tempo_medio_horas": round(setor_info.tempo_medio or 0, 2),
                "taxa_retrabalho": round(taxa_retrabalho, 2),
                "pendencias_abertas": pendencias_abertas,
                "eficiencia": round(eficiencia, 2)
            })

        return {
            "periodo_analise": periodo_dias,
            "data_atualizacao": datetime.now().isoformat(),
            "metricas_gerais": {
                "os_por_status": [
                    {"status": item.status_os or "SEM_STATUS", "total": item.total}
                    for item in os_por_status
                ],
                "tempo_ciclo_medio_dias": round(tempo_ciclo_medio, 2),
                "taxa_cumprimento_prazo": taxa_cumprimento_prazo,
                "horas_trabalhadas_periodo": round(utilizacao_recursos, 2)
            },
            "eficiencia_setores": eficiencia_setores,
            "tempo_por_tipo_maquina": [
                {
                    "tipo_maquina": item.tipo_maquina,
                    "tempo_medio_horas": round(item.tempo_medio or 0, 2),
                    "total_apontamentos": item.total_apontamentos
                }
                for item in tempo_por_tipo_maquina
            ],
            "produtividade_semanal": [
                {
                    "dia_semana": int(item.dia_semana),
                    "nome_dia": ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"][int(item.dia_semana)],
                    "total_apontamentos": item.total_apontamentos,
                    "tempo_medio_horas": round(item.tempo_medio or 0, 2)
                }
                for item in produtividade_semanal
            ],
            "evolucao_mensal": list(reversed(evolucao_mensal))
        }

    except Exception as e:
        print(f"Erro ao buscar dashboard avançado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dashboard avançado: {str(e)}")

@router.get("/relatorios/eficiencia-setores", operation_id="pcp_get_relatorio_eficiencia")
async def get_relatorio_eficiencia_setores(
    periodo_dias: Optional[int] = Query(30, description="Período em dias para análise"),
    setor_id: Optional[int] = Query(None, description="Filtrar por setor específico"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Relatório detalhado de eficiência por setores
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, case

        data_limite = datetime.now() - timedelta(days=periodo_dias or 30)

        # Query base para setores
        query_setores = db.query(Setor).filter(Setor.ativo.is_(True))
        if setor_id:
            query_setores = query_setores.filter(Setor.id == setor_id)

        setores = query_setores.all()
        relatorio_setores = []

        for setor in setores:
            # Apontamentos do setor no período
            apontamentos = db.query(ApontamentoDetalhado).filter(
                and_(
                    ApontamentoDetalhado.id_setor == setor.id,
                    ApontamentoDetalhado.data_hora_inicio >= data_limite
                )
            ).all()

            # Métricas básicas
            total_apontamentos = len(apontamentos)
            horas_trabalhadas = sum(
                (a.horas_etapa_inicial or 0) +
                (a.horas_etapa_parcial or 0) +
                (a.horas_etapa_final or 0)
                for a in apontamentos
            )
            retrabalhos = sum(1 for a in apontamentos if a.foi_retrabalho is True)

            # Pendências do setor
            pendencias_setor = db.query(Pendencia).join(
                ApontamentoDetalhado, Pendencia.id_apontamento_origem == ApontamentoDetalhado.id
            ).filter(
                ApontamentoDetalhado.id_setor == setor.id
            ).all()

            pendencias_abertas = sum(1 for p in pendencias_setor if str(p.status) == 'ABERTA')
            pendencias_fechadas = sum(1 for p in pendencias_setor if str(p.status) == 'FECHADA')

            # Cálculos de eficiência
            taxa_retrabalho = (retrabalhos / total_apontamentos * 100) if total_apontamentos > 0 else 0
            tempo_medio_apontamento = (horas_trabalhadas / total_apontamentos) if total_apontamentos > 0 else 0

            # Eficiência geral (fórmula customizada)
            eficiencia_geral = max(0, 100 - taxa_retrabalho - (pendencias_abertas * 3))

            # Produtividade (apontamentos por dia)
            produtividade_diaria = total_apontamentos / (periodo_dias or 1) if (periodo_dias or 1) > 0 else 0

            relatorio_setores.append({
                "setor": {
                    "id": setor.id,
                    "nome": setor.nome,
                    "id_departamento": setor.id_departamento,
                    "permite_apontamento": setor.permite_apontamento
                },
                "metricas": {
                    "total_apontamentos": total_apontamentos,
                    "horas_trabalhadas": 0.0 if horas_trabalhadas is None else float(str(horas_trabalhadas)),
                    "tempo_medio_apontamento": 0.0 if tempo_medio_apontamento is None else float(str(tempo_medio_apontamento)),
                    "produtividade_diaria": round(produtividade_diaria, 2)
                },
                "qualidade": {
                    "total_retrabalhos": retrabalhos,
                    "taxa_retrabalho": round(taxa_retrabalho, 2),
                    "pendencias_abertas": pendencias_abertas,
                    "pendencias_fechadas": pendencias_fechadas,
                    "total_pendencias": len(pendencias_setor)
                },
                "eficiencia": {
                    "eficiencia_geral": round(eficiencia_geral, 2),
                    "classificacao": "EXCELENTE" if eficiencia_geral >= 90 else
                                   "BOA" if eficiencia_geral >= 75 else
                                   "REGULAR" if eficiencia_geral >= 60 else "BAIXA"
                }
            })

        # Ordenar por eficiência
        relatorio_setores.sort(key=lambda x: x["eficiencia"]["eficiencia_geral"], reverse=True)

        return {
            "periodo_analise": periodo_dias,
            "data_geracao": datetime.now().isoformat(),
            "total_setores": len(relatorio_setores),
            "setores": relatorio_setores,
            "resumo_geral": {
                "eficiencia_media": round(
                    sum(s["eficiencia"]["eficiencia_geral"] for s in relatorio_setores) / len(relatorio_setores)
                    if relatorio_setores else 0, 2
                ),
                "total_apontamentos": sum(s["metricas"]["total_apontamentos"] for s in relatorio_setores),
                "total_horas": round(sum(s["metricas"]["horas_trabalhadas"] for s in relatorio_setores), 2),
                "total_retrabalhos": sum(s["qualidade"]["total_retrabalhos"] for s in relatorio_setores),
                "total_pendencias_abertas": sum(s["qualidade"]["pendencias_abertas"] for s in relatorio_setores)
            }
        }

    except Exception as e:
        print(f"Erro ao gerar relatório de eficiência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/alertas", operation_id="pcp_get_alertas")
async def get_alertas_pcp(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obter alertas e notificações importantes para o PCP
    """
    try:
        from datetime import datetime, timedelta

        alertas = []

        # Programações atrasadas
        programacoes_atrasadas = db.query(Programacao).filter(
            and_(
                Programacao.fim_previsto < datetime.now(),
                Programacao.status.in_(['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA'])
            )
        ).all()

        for prog in programacoes_atrasadas:
            os_relacionada = db.query(OrdemServico).filter(OrdemServico.id == prog.id_ordem_servico).first()
            atraso_horas = (datetime.now() - prog.fim_previsto).total_seconds() / 3600

            alertas.append({
                "tipo": "PROGRAMACAO_ATRASADA",
                "prioridade": "ALTA" if atraso_horas > 24 else "MEDIA",
                "titulo": f"Programação atrasada - OS {os_relacionada.os_numero if os_relacionada else prog.id_ordem_servico}",
                "descricao": f"Programação com atraso de {round(atraso_horas, 1)} horas",
                "data_alerta": datetime.now().isoformat(),
                "dados": {
                    "programacao_id": prog.id,
                    "os_numero": os_relacionada.os_numero if os_relacionada else None,
                    "atraso_horas": round(atraso_horas, 1)
                }
            })

        # Pendências críticas (alta prioridade ou muito antigas)
        pendencias_criticas = db.query(Pendencia).filter(
            and_(
                Pendencia.status == 'ABERTA',
                or_(
                    Pendencia.prioridade.in_(['ALTA', 'URGENTE']),
                    func.julianday('now') - func.julianday(Pendencia.data_inicio) > 2
                )
            )
        ).all()

        for pend in pendencias_criticas:
            tempo_aberto = (datetime.now() - pend.data_inicio).total_seconds() / 3600 if pend.data_inicio is not None else 0

            alertas.append({
                "tipo": "PENDENCIA_CRITICA",
                "prioridade": "URGENTE" if str(pend.prioridade) == 'URGENTE' else "ALTA",
                "titulo": f"Pendência crítica - OS {pend.numero_os}",
                "descricao": f"Pendência {pend.prioridade} aberta há {round(tempo_aberto, 1)} horas",
                "data_alerta": datetime.now().isoformat(),
                "dados": {
                    "pendencia_id": pend.id,
                    "os_numero": pend.numero_os,
                    "prioridade": pend.prioridade,
                    "tempo_aberto_horas": round(tempo_aberto, 1)
                }
            })

        # Setores com baixa eficiência (simulado)
        setores_baixa_eficiencia = db.query(Setor).filter(Setor.ativo.is_(True)).limit(2).all()

        for setor in setores_baixa_eficiencia:
            # Verificar se há muitos retrabalhos recentes
            retrabalhos_recentes = db.query(ApontamentoDetalhado).filter(
                and_(
                    ApontamentoDetalhado.id_setor == setor.id,
                    ApontamentoDetalhado.foi_retrabalho.is_(True),
                    ApontamentoDetalhado.data_hora_inicio >= datetime.now() - timedelta(days=7)
                )
            ).count()

            if retrabalhos_recentes > 3:
                alertas.append({
                    "tipo": "EFICIENCIA_BAIXA",
                    "prioridade": "MEDIA",
                    "titulo": f"Eficiência baixa - Setor {setor.nome}",
                    "descricao": f"Setor com {retrabalhos_recentes} retrabalhos nos últimos 7 dias",
                    "data_alerta": datetime.now().isoformat(),
                    "dados": {
                        "setor_id": setor.id,
                        "setor_nome": setor.nome,
                        "retrabalhos_semana": retrabalhos_recentes
                    }
                })

        # Ordenar alertas por prioridade
        ordem_prioridade = {"URGENTE": 0, "ALTA": 1, "MEDIA": 2, "BAIXA": 3}
        alertas.sort(key=lambda x: ordem_prioridade.get(x["prioridade"], 4))

        return {
            "total_alertas": len(alertas),
            "alertas_por_prioridade": {
                "urgente": len([a for a in alertas if a["prioridade"] == "URGENTE"]),
                "alta": len([a for a in alertas if a["prioridade"] == "ALTA"]),
                "media": len([a for a in alertas if a["prioridade"] == "MEDIA"]),
                "baixa": len([a for a in alertas if a["prioridade"] == "BAIXA"])
            },
            "alertas": alertas,
            "data_atualizacao": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Erro ao buscar alertas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar alertas: {str(e)}")
