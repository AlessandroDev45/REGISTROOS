"""
Rotas para relatório completo de OS
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
from datetime import datetime
import logging

from config.database_config import get_db
from app.dependencies import get_current_user
from app.database_models import Usuario, OrdemServico, ApontamentoDetalhado

router = APIRouter(prefix="/api", tags=["relatorio-completo"])
logger = logging.getLogger(__name__)

@router.get("/relatorio/completo")
async def get_relatorio_completo_geral(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get general complete report"""
    try:
        from sqlalchemy import text, func

        # Métricas gerais
        total_os = db.query(OrdemServico).count()
        os_concluidas = db.query(OrdemServico).filter(OrdemServico.status_os == "CONCLUIDA").count()
        os_em_andamento = db.query(OrdemServico).filter(OrdemServico.status_os == "EM_ANDAMENTO").count()

        # Apontamentos
        total_apontamentos = db.query(ApontamentoDetalhado).count()
        apontamentos_concluidos = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.status_apontamento == "CONCLUIDO"
        ).count()

        # Pendências
        total_pendencias = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.pendencia.is_(True)
        ).count()

        return {
            "metricas_gerais": {
                "total_os": total_os,
                "os_concluidas": os_concluidas,
                "os_em_andamento": os_em_andamento,
                "taxa_conclusao": round((os_concluidas / total_os * 100) if total_os > 0 else 0, 1)
            },
            "apontamentos": {
                "total": total_apontamentos,
                "concluidos": apontamentos_concluidos,
                "taxa_conclusao": round((apontamentos_concluidos / total_apontamentos * 100) if total_apontamentos > 0 else 0, 1)
            },
            "pendencias": {
                "total": total_pendencias
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório completo geral: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/os/{os_id}/relatorio-completo", response_model=Dict[str, Any])
async def get_relatorio_completo_os(
    os_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca relatório completo de uma OS com todos os dados consolidados
    """
    try:
        logger.info(f"Buscando relatório completo para OS {os_id}")
        
        # 1. DADOS GERAIS DA OS
        os_query = text("""
            SELECT
                os.*,
                c.razao_social as cliente_nome,
                c.nome_fantasia as cliente_fantasia,
                e.descricao as equipamento_descricao,
                tm.nome_tipo as tipo_maquina_nome,
                u1.nome_completo as responsavel_registro_nome,
                u2.nome_completo as responsavel_pcp_nome,
                u3.nome_completo as responsavel_final_nome,
                s.nome as setor_nome,
                d.nome_tipo as departamento_nome
            FROM ordens_servico os
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            LEFT JOIN tipos_maquina tm ON os.id_tipo_maquina = tm.id
            LEFT JOIN tipo_usuarios u1 ON os.id_responsavel_registro = u1.id
            LEFT JOIN tipo_usuarios u2 ON os.id_responsavel_pcp = u2.id
            LEFT JOIN tipo_usuarios u3 ON os.id_responsavel_final = u3.id
            LEFT JOIN tipo_setores s ON os.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE os.id = :os_id
        """)
        
        os_result = db.execute(os_query, {"os_id": os_id}).fetchone()
        if not os_result:
            raise HTTPException(status_code=404, detail="OS não encontrada")
        
        os_data = dict(os_result._mapping)
        
        # 2. APONTAMENTOS POR SETOR (incluindo campos de etapas)
        apontamentos_query = text("""
            SELECT
                a.*,
                u.nome_completo as usuario_nome,
                us.nome as usuario_setor,
                ud.nome_tipo as usuario_departamento,
                s.nome as setor_nome,
                d.nome_tipo as setor_departamento
            FROM apontamentos_detalhados a
            LEFT JOIN tipo_usuarios u ON a.id_usuario = u.id
            LEFT JOIN tipo_setores us ON u.id_setor = us.id
            LEFT JOIN tipo_departamentos ud ON u.id_departamento = ud.id
            LEFT JOIN tipo_setores s ON a.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE a.id_os = :os_id
            ORDER BY a.data_hora_inicio DESC
        """)
        
        apontamentos_result = db.execute(apontamentos_query, {"os_id": os_id}).fetchall()
        apontamentos_data = [dict(row._mapping) for row in apontamentos_result]
        
        # 3. RESULTADOS DE TESTES (Nova estrutura consolidada)
        testes_query = text("""
            SELECT
                rt.*,
                tt.nome as tipo_teste_nome,
                tt.categoria,
                tt.subcategoria,
                s.nome as apontamento_setor,
                u.nome_completo as usuario_nome
            FROM resultados_teste rt
            LEFT JOIN tipos_teste tt ON rt.id_teste = tt.id
            LEFT JOIN apontamentos_detalhados a ON rt.id_apontamento = a.id
            LEFT JOIN tipo_usuarios u ON a.id_usuario = u.id
            LEFT JOIN tipo_setores s ON a.id_setor = s.id
            WHERE a.id_os = :os_id
            ORDER BY rt.data_registro DESC
        """)

        testes_result = db.execute(testes_query, {"os_id": os_id}).fetchall()

        # Processar dados dos testes
        testes_data = []
        for row in testes_result:
            row_dict = dict(row._mapping)

            # Criar objeto de teste individual
            teste_individual = {
                'id': row_dict['id'],
                'id_apontamento': row_dict['id_apontamento'],
                'id_teste': row_dict['id_teste'],
                'teste_nome': row_dict.get('tipo_teste_nome', 'N/A'),
                'tipo_teste': row_dict.get('tipo_teste_nome', 'N/A'),
                'resultado': row_dict['resultado'],
                'observacao': row_dict['observacao'],
                'data_registro': row_dict['data_registro'],
                'apontamento_setor': row_dict.get('apontamento_setor', 'N/A'),
                'usuario_nome': row_dict.get('usuario_nome', 'N/A')
            }
            testes_data.append(teste_individual)

            # Tentar processar JSON se existir (compatibilidade com dados antigos)
            try:
                import json
                dados_json = json.loads(row_dict['observacao'])

                # Se for JSON válido, extrair testes individuais
                for teste in dados_json.get('testes', []):
                    teste_json = {
                        'id': row_dict['id'],
                        'id_apontamento': row_dict['id_apontamento'],
                        'teste_nome': teste.get('nome_teste', 'N/A'),
                        'tipo_teste': teste.get('tipo_teste', 'N/A'),
                        'resultado': teste.get('resultado', 'N/A'),
                        'observacao': teste.get('observacao', ''),
                        'data_registro': row_dict['data_registro'],
                        'apontamento_setor': row_dict['apontamento_setor'],
                        'usuario_nome': row_dict['usuario_nome']
                    }
                    testes_data.append(teste_json)

            except (Exception,):
                # Não é JSON, continuar com dados simples já adicionados
                pass
        
        # 4. PENDÊNCIAS E RETRABALHOS
        pendencias_query = text("""
            SELECT 
                p.*,
                u1.nome_completo as responsavel_inicio_nome,
                u2.nome_completo as responsavel_fechamento_nome,
                cr.descricao as causa_descricao,
                cr.codigo as causa_codigo
            FROM pendencias p
            LEFT JOIN tipo_usuarios u1 ON p.id_responsavel_inicio = u1.id
            LEFT JOIN tipo_usuarios u2 ON p.id_responsavel_fechamento = u2.id
            LEFT JOIN tipo_causas_retrabalho cr ON p.descricao_pendencia LIKE '%' || cr.codigo || '%'
            WHERE p.numero_os = :os_numero
            ORDER BY p.data_inicio DESC
        """)
        
        pendencias_result = db.execute(pendencias_query, {"os_numero": os_data['os_numero']}).fetchall()
        pendencias_data = [dict(row._mapping) for row in pendencias_result]
        
        # 5. PROGRAMAÇÕES
        programacoes_query = text("""
            SELECT 
                p.*,
                u1.nome_completo as responsavel_nome,
                u2.nome_completo as criado_por_nome,
                s.nome as setor_nome
            FROM programacoes p
            LEFT JOIN tipo_usuarios u1 ON p.responsavel_id = u1.id
            LEFT JOIN tipo_usuarios u2 ON p.criado_por_id = u2.id
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
            WHERE p.id_ordem_servico = :os_id
            ORDER BY p.inicio_previsto DESC
        """)
        
        programacoes_result = db.execute(programacoes_query, {"os_id": os_id}).fetchall()
        programacoes_data = [dict(row._mapping) for row in programacoes_result]
        
        # 6. CÁLCULOS E MÉTRICAS
        metricas = calcular_metricas_os(apontamentos_data, testes_data, pendencias_data, os_data)
        
        # 7. CONSOLIDAR DADOS POR SETOR
        dados_por_setor = consolidar_dados_por_setor(apontamentos_data, testes_data)
        
        # 8. MONTAR RESPOSTA COMPLETA
        relatorio_completo = {
            "os_dados_gerais": os_data,
            "apontamentos_por_setor": dados_por_setor,
            "apontamentos_detalhados": apontamentos_data,
            "resultados_testes": testes_data,
            "pendencias_retrabalhos": pendencias_data,
            "programacoes": programacoes_data,
            "metricas_consolidadas": metricas,
            "resumo_gerencial": gerar_resumo_gerencial(os_data, metricas, dados_por_setor),
            "data_geracao": datetime.now().isoformat()
        }
        
        logger.info(f"Relatório completo gerado para OS {os_id}")
        return relatorio_completo
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório completo para OS {os_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

def calcular_metricas_os(apontamentos: List[Dict], testes: List[Dict], pendencias: List[Dict], os_data: Dict) -> Dict[str, Any]:
    """Calcula métricas consolidadas da OS"""

    # Horas por etapa (baseado nos novos campos)
    horas_por_etapa = {
        "inicial": 0,
        "parcial": 0,
        "final": 0,
        "total": 0
    }

    # Contadores de etapas
    etapas_realizadas = {
        "inicial": 0,
        "parcial": 0,
        "final": 0
    }
    
    # Horas por setor
    horas_por_setor = {}
    
    # Contadores de testes
    testes_aprovados = 0
    testes_reprovados = 0
    testes_pendentes = 0
    
    # Processar apontamentos
    for apt in apontamentos:
        # Calcular horas totais
        if apt['data_hora_inicio'] and apt['data_hora_fim']:
            inicio = datetime.fromisoformat(str(apt['data_hora_inicio']).replace('Z', '+00:00'))
            fim = datetime.fromisoformat(str(apt['data_hora_fim']).replace('Z', '+00:00'))
            horas = (fim - inicio).total_seconds() / 3600

            horas_por_etapa["total"] += int(horas)

            setor = apt.get('setor_nome', 'Não informado')
            if setor not in horas_por_setor:
                horas_por_setor[setor] = 0
            horas_por_setor[setor] += int(horas)

        # Processar etapas específicas
        if apt.get('etapa_inicial'):
            etapas_realizadas["inicial"] += 1
            horas_etapa = float(apt.get('horas_etapa_inicial', 0) or 0)
            horas_por_etapa["inicial"] += int(horas_etapa)

        if apt.get('etapa_parcial'):
            etapas_realizadas["parcial"] += 1
            horas_etapa = float(apt.get('horas_etapa_parcial', 0) or 0)
            horas_por_etapa["parcial"] += int(horas_etapa)

        if apt.get('etapa_final'):
            etapas_realizadas["final"] += 1
            horas_etapa = float(apt.get('horas_etapa_final', 0) or 0)
            horas_por_etapa["final"] += int(horas_etapa)
    
    # Processar testes
    for teste in testes:
        resultado = teste.get('resultado', '').upper()
        if resultado == 'APROVADO':
            testes_aprovados += 1
        elif resultado == 'REPROVADO':
            testes_reprovados += 1
        else:
            testes_pendentes += 1
    
    # Calcular percentuais
    total_testes = len(testes)
    percentual_aprovacao = (testes_aprovados / total_testes * 100) if total_testes > 0 else 0
    
    # Horas orçadas vs realizadas
    horas_orcadas = float(os_data.get('horas_orcadas', 0) or 0)
    horas_realizadas = horas_por_etapa["total"]
    desvio_horas = horas_realizadas - horas_orcadas
    percentual_desvio = (desvio_horas / horas_orcadas * 100) if horas_orcadas > 0 else 0
    
    return {
        "horas_por_etapa": horas_por_etapa,
        "etapas_realizadas": etapas_realizadas,
        "horas_por_setor": horas_por_setor,
        "horas_orcadas": horas_orcadas,
        "horas_realizadas": horas_realizadas,
        "desvio_horas": desvio_horas,
        "percentual_desvio": percentual_desvio,
        "total_testes": total_testes,
        "testes_aprovados": testes_aprovados,
        "testes_reprovados": testes_reprovados,
        "testes_pendentes": testes_pendentes,
        "percentual_aprovacao": percentual_aprovacao,
        "total_pendencias": len(pendencias),
        "pendencias_abertas": len([p for p in pendencias if p.get('status') != 'FECHADA']),
        "total_retrabalhos": len([p for p in pendencias if 'retrabalho' in str(p.get('descricao_pendencia', '')).lower()])
    }

def consolidar_dados_por_setor(apontamentos: List[Dict], testes: List[Dict]) -> Dict[str, Any]:
    """Consolida dados agrupados por setor"""
    
    setores = {}
    
    for apt in apontamentos:
        setor = apt.get('setor_nome', 'Não informado')
        
        if setor not in setores:
            setores[setor] = {
                "nome": setor,
                "departamento": apt.get('setor_departamento', ''),
                "apontamentos": [],
                "horas_total": 0,
                "testes_realizados": 0,
                "usuarios": set()
            }
        
        setores[setor]["apontamentos"].append(apt)
        setores[setor]["usuarios"].add(apt.get('usuario_nome', ''))
        
        # Calcular horas
        if apt['data_hora_inicio'] and apt['data_hora_fim']:
            inicio = datetime.fromisoformat(str(apt['data_hora_inicio']).replace('Z', '+00:00'))
            fim = datetime.fromisoformat(str(apt['data_hora_fim']).replace('Z', '+00:00'))
            horas = (fim - inicio).total_seconds() / 3600
            setores[setor]["horas_total"] += horas
    
    # Contar testes por setor
    for teste in testes:
        setor = teste.get('apontamento_setor', 'Não informado')
        if setor in setores:
            setores[setor]["testes_realizados"] += 1
    
    # Converter sets para listas
    for setor_data in setores.values():
        setor_data["usuarios"] = list(setor_data["usuarios"])
    
    return setores

def gerar_resumo_gerencial(os_data: Dict, metricas: Dict, setores: Dict) -> Dict[str, Any]:
    """Gera resumo executivo para gestores"""
    
    status_os = os_data.get('status_os', 'N/A')
    prioridade = os_data.get('prioridade', 'MEDIA')
    
    # Identificar gargalos
    setor_mais_horas = max(metricas["horas_por_setor"].items(), key=lambda x: x[1]) if metricas["horas_por_setor"] else ("N/A", 0)
    
    # Status geral
    if metricas["percentual_desvio"] > 20:
        status_prazo = "CRÍTICO"
    elif metricas["percentual_desvio"] > 10:
        status_prazo = "ATENÇÃO"
    else:
        status_prazo = "OK"
    
    if metricas["percentual_aprovacao"] < 80:
        status_qualidade = "CRÍTICO"
    elif metricas["percentual_aprovacao"] < 90:
        status_qualidade = "ATENÇÃO"
    else:
        status_qualidade = "OK"
    
    return {
        "status_os": status_os,
        "prioridade": prioridade,
        "status_prazo": status_prazo,
        "status_qualidade": status_qualidade,
        "setores_envolvidos": len(setores),
        "setor_gargalo": setor_mais_horas[0],
        "horas_setor_gargalo": round(setor_mais_horas[1], 2),
        "desvio_percentual": round(metricas["percentual_desvio"], 1),
        "aprovacao_testes": round(metricas["percentual_aprovacao"], 1),
        "pendencias_abertas": metricas["pendencias_abertas"],
        "retrabalhos": metricas["total_retrabalhos"],
        "indicadores_principais": {
            "eficiencia_horas": "OK" if abs(metricas["percentual_desvio"]) <= 10 else "ATENÇÃO",
            "qualidade_testes": "OK" if metricas["percentual_aprovacao"] >= 90 else "ATENÇÃO",
            "gestao_pendencias": "OK" if metricas["pendencias_abertas"] == 0 else "ATENÇÃO"
        }
    }
