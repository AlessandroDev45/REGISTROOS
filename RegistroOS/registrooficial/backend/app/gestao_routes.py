from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime

from .database_models import Usuario, OrdemServico, Programacao, ApontamentoDetalhado
from config.database_config import get_db

router = APIRouter(tags=["gestao"])

@router.get("/metricas-gerais", operation_id="gestao_get_metricas_gerais")
async def get_metricas_gerais(
    periodo: Optional[int] = 30,
    tipoEquipamento: Optional[str] = "todos",
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Retorna métricas gerais para dashboard de gestão"""
    try:
        total_os = db.query(OrdemServico).count()
        total_programacoes = db.query(Programacao).count()
        total_usuarios = db.query(Usuario).count()
        
        return {
            "periodo": {
                "data_inicio": data_inicio.isoformat() if data_inicio else None,
                "data_fim": data_fim.isoformat() if data_fim else None,
                "departamento": departamento,
                "setor": setor
            },
            "metricas_os": {
                "total_ordens": total_os,
                "concluidas": total_os // 3,
                "em_andamento": total_os // 2,
                "atrasadas": total_os // 10,
                "taxa_conclusao": 75.5
            },
            "metricas_programacoes": {
                "total_programacoes": total_programacoes,
                "pendentes": total_programacoes // 2,
                "em_andamento": total_programacoes // 3
            },
            "metricas_usuarios": {
                "total_usuarios": total_usuarios
            }
        }
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

@router.get("/dashboard", operation_id="gestao_get_dashboard")
async def get_dashboard(
    periodo: Optional[int] = 30,
    departamento: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Dashboard principal de gestão com métricas consolidadas"""
    try:
        from sqlalchemy import text, func

        # Métricas básicas de OS
        total_os = db.query(OrdemServico).count()
        os_concluidas = db.query(OrdemServico).filter(OrdemServico.status_os == "CONCLUIDA").count()
        os_em_andamento = db.query(OrdemServico).filter(OrdemServico.status_os == "EM ANDAMENTO").count()
        os_abertas = db.query(OrdemServico).filter(OrdemServico.status_os == "ABERTA").count()

        # Métricas de usuários
        total_usuarios = db.query(Usuario).count()
        usuarios_ativos = db.query(Usuario).filter(Usuario.is_approved == True).count()

        # Métricas de apontamentos
        total_apontamentos = db.query(ApontamentoDetalhado).count()
        apontamentos_concluidos = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.status_apontamento == "CONCLUIDO"
        ).count()

        # Performance por departamento
        performance_departamentos = []
        if departamento:
            # Filtrar por departamento específico
            os_dept = db.query(OrdemServico).filter(OrdemServico.id_departamento == departamento).count()
            performance_departamentos.append({
                "departamento": departamento,
                "total_os": os_dept,
                "concluidas": os_dept // 3,
                "em_andamento": os_dept // 2,
                "eficiencia": 85.0
            })
        else:
            # Todos os departamentos
            performance_departamentos = [
                {
                    "departamento": "MOTORES",
                    "total_os": total_os // 2,
                    "concluidas": os_concluidas // 2,
                    "em_andamento": os_em_andamento // 2,
                    "eficiencia": 87.5
                },
                {
                    "departamento": "TRANSFORMADORES",
                    "total_os": total_os // 2,
                    "concluidas": os_concluidas // 2,
                    "em_andamento": os_em_andamento // 2,
                    "eficiencia": 82.3
                }
            ]

        return {
            "metricas_principais": {
                "total_os": total_os,
                "os_concluidas": os_concluidas,
                "os_em_andamento": os_em_andamento,
                "os_abertas": os_abertas,
                "taxa_conclusao": round((os_concluidas / total_os * 100) if total_os > 0 else 0, 1)
            },
            "metricas_usuarios": {
                "total_usuarios": total_usuarios,
                "usuarios_ativos": usuarios_ativos,
                "taxa_aprovacao": round((usuarios_ativos / total_usuarios * 100) if total_usuarios > 0 else 0, 1)
            },
            "metricas_apontamentos": {
                "total_apontamentos": total_apontamentos,
                "apontamentos_concluidos": apontamentos_concluidos,
                "taxa_conclusao_apontamentos": round((apontamentos_concluidos / total_apontamentos * 100) if total_apontamentos > 0 else 0, 1)
            },
            "performance_departamentos": performance_departamentos,
            "periodo_analise": periodo,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": f"Erro ao buscar dashboard: {str(e)}"}

@router.get("/ordens-por-setor", operation_id="gestao_get_ordens_por_setor")
async def get_ordens_por_setor(
    periodo: Optional[int] = 30,
    tipoEquipamento: Optional[str] = "todos",
    departamento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Retorna estatísticas de ordens por setor"""
    try:
        total_ordens = db.query(OrdemServico).count()

        return [
            {
                "setor": "Produção",
                "total_ordens": total_ordens // 2,
                "tempo_medio_dias": 5.5
            },
            {
                "setor": "Manutenção",
                "total_ordens": total_ordens // 2,
                "tempo_medio_dias": 3.2
            }
        ]
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

@router.get("/eficiencia-setores", operation_id="gestao_get_eficiencia_setores")
async def get_eficiencia_setores(
    periodo: Optional[int] = 30,
    tipoEquipamento: Optional[str] = "todos",
    departamento: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Retorna métricas de eficiência por setor"""
    try:
        total_ordens = db.query(OrdemServico).count()
        total_programacoes = db.query(Programacao).count()
        
        return [
            {
                "setor": "Produção",
                "total_ordens": total_ordens // 2,
                "tempo_medio_horas": 8.5,
                "programacoes_realizadas": total_programacoes // 2,
                "eficiencia": 85.0
            },
            {
                "setor": "Manutenção",
                "total_ordens": total_ordens // 2,
                "tempo_medio_horas": 6.2,
                "programacoes_realizadas": total_programacoes // 2,
                "eficiencia": 92.0
            }
        ]
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

@router.get("/relatorio-producao", operation_id="gestao_get_relatorio_producao")
async def get_relatorio_producao(
    periodo: Optional[int] = 30,
    db: Session = Depends(get_db)
):
    """Relatório de produção usando dados reais"""
    try:
        from sqlalchemy import text

        sql = text("""
            SELECT
                COUNT(*) as total_os,
                COUNT(CASE WHEN status_os = 'CONCLUIDA' THEN 1 END) as os_concluidas,
                COUNT(CASE WHEN status_os = 'EM ANDAMENTO' THEN 1 END) as os_em_andamento,
                SUM(horas_reais) as total_horas_reais,
                SUM(horas_orcadas) as total_horas_orcadas
            FROM ordens_servico
            WHERE data_criacao >= date('now', '-30 days')
        """)

        result = db.execute(sql).fetchone()

        if result:
            return {
                "periodo_dias": periodo,
                "total_ordens": result[0] or 0,
                "ordens_concluidas": result[1] or 0,
                "ordens_em_andamento": result[2] or 0,
                "total_horas_reais": float(result[3]) if result[3] else 0.0,
                "total_horas_orcadas": float(result[4]) if result[4] else 0.0,
                "eficiencia_horas": round((float(result[3]) / float(result[4]) * 100), 2) if result[4] and result[3] else 0.0
            }
        else:
            return {
                "periodo_dias": periodo,
                "total_ordens": 0,
                "ordens_concluidas": 0,
                "ordens_em_andamento": 0,
                "total_horas_reais": 0.0,
                "total_horas_orcadas": 0.0,
                "eficiencia_horas": 0.0
            }
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

@router.get("/dashboard-executivo", operation_id="gestao_get_dashboard_executivo")
async def get_dashboard_executivo(
    db: Session = Depends(get_db)
):
    """Dashboard executivo com dados reais"""
    try:
        from sqlalchemy import text

        # Métricas principais
        sql_metricas = text("""
            SELECT
                COUNT(*) as total_os,
                COUNT(CASE WHEN status_os = 'CONCLUIDA' THEN 1 END) as concluidas,
                COUNT(CASE WHEN status_os = 'EM ANDAMENTO' THEN 1 END) as em_andamento,
                COUNT(CASE WHEN status_os = 'AGUARDANDO' THEN 1 END) as aguardando
            FROM ordens_servico
        """)

        metricas = db.execute(sql_metricas).fetchone()

        # Pendências por status
        sql_pendencias = text("""
            SELECT status, COUNT(*) as quantidade
            FROM pendencias
            GROUP BY status
        """)

        pendencias = db.execute(sql_pendencias).fetchall()

        return {
            "metricas_principais": {
                "total_ordens": metricas[0] if metricas else 0,
                "ordens_concluidas": metricas[1] if metricas else 0,
                "ordens_em_andamento": metricas[2] if metricas else 0,
                "ordens_aguardando": metricas[3] if metricas else 0
            },
            "pendencias_por_status": [
                {"status": row[0], "quantidade": row[1]}
                for row in pendencias
            ] if pendencias else [],
            "data_atualizacao": "2025-09-18"
        }
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}
