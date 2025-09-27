"""
PCP ROUTES - PLANEJAMENTO E CONTROLE DE PRODUÇÃO
================================================

ENDPOINTS DISPONÍVEIS:
1. GET /api/pcp/ordens-servico - Ordens de serviço para PCP
2. GET /api/pcp/programacao-form-data - DADOS PARA FORMULÁRIO DE PROGRAMAÇÃO (PROBLEMA ATUAL)
3. POST /api/pcp/programacoes - Criar nova programação
4. GET /api/pcp/programacoes - Listar programações
5. GET /api/pcp/pendencias - Listar pendências
6. GET /api/pcp/pendencias/dashboard - Dashboard de pendências

PROBLEMA ATUAL: O endpoint /api/pcp/programacao-form-data não retorna dados do banco.
CAUSA: Conflito com endpoint duplicado em main.py (REMOVIDO)
SOLUÇÃO: Verificar se as consultas SQL estão executando corretamente.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case, literal, text
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel

class AtribuicaoProgramacaoRequest(BaseModel):
    responsavel_id: int
    setor_destino: str
    departamento_destino: str
    data_inicio: str
    data_fim: str
    observacoes: Optional[str] = None
    prioridade: Optional[str] = "NORMAL"

class StatusUpdateRequest(BaseModel):
    status: str

class ProgramacaoEditRequest(BaseModel):
    inicio_previsto: Optional[datetime] = None
    fim_previsto: Optional[datetime] = None
    responsavel_id: Optional[int] = None
    id_setor: Optional[int] = None
    observacoes: Optional[str] = None
    prioridade: Optional[str] = None

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
    id_ordem_servico: Optional[int] = None  # Opcional se os_numero for fornecido
    os_numero: Optional[str] = None  # Novo campo para buscar OS por número
    inicio_previsto: datetime
    fim_previsto: datetime
    id_departamento: Optional[int] = None
    id_setor: Optional[int] = None
    responsavel_id: Optional[int] = None
    observacoes: Optional[str] = None
    prioridade: Optional[str] = "NORMAL"  # Campo prioridade
    status: Optional[str] = "PROGRAMADA"

class FiltragemPCP(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    setor: Optional[str] = None
    departamento: Optional[str] = None
    status_os: Optional[str] = None
    prioridade: Optional[str] = None

# =============================================================================
# ENDPOINTS PRINCIPAIS DO PCP
# =============================================================================

@router.get("/ordens-servico", operation_id="pcp_get_ordens_servico")
async def get_ordens_servico_pcp(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter ordens de serviço disponíveis para PCP"""
    try:
        sql = text("""
            SELECT os.id, os.os_numero, os.descricao_maquina, os.prioridade,
                   os.data_criacao, os.status_os, os.id_setor, os.id_departamento,
                   s.nome as setor_nome, d.nome_tipo as departamento_nome
            FROM ordens_servico os
            LEFT JOIN tipo_setores s ON os.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON os.id_departamento = d.id
            WHERE os.status_os IN ('ABERTA', 'EM_ANDAMENTO', 'PROGRAMADA')
            ORDER BY os.prioridade DESC, os.data_criacao ASC
            LIMIT 100
        """)
        
        result = db.execute(sql)
        ordens = result.fetchall()
        
        return [
            {
                "id": row[0],
                "os_numero": row[1] or "",
                "descricao_servico": row[2] or "",
                "prioridade": row[3] or "NORMAL",
                "data_abertura": str(row[4]) if row[4] else None,
                "status": row[5] or "ABERTA",
                "id_setor": row[6],
                "id_departamento": row[7],
                "setor_nome": row[8] or "Não informado",
                "departamento_nome": row[9] or "Não informado"
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
    print("🔥 [ENDPOINT CHAMADO] /api/pcp/programacao-form-data")
    try:
        print(f"[DEBUG] Iniciando busca de dados do formulário para usuário: {current_user.nome_completo}")

        # Buscar todos os setores (não apenas produção)
        setores_sql = text("""
            SELECT s.id, s.nome, s.id_departamento, d.nome_tipo as departamento_nome
            FROM tipo_setores s
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            ORDER BY s.nome
        """)

        print(f"[DEBUG] Executando consulta de setores...")
        setores_result = db.execute(setores_sql)
        setores_rows = setores_result.fetchall()
        print(f"[DEBUG] Encontrados {len(setores_rows)} setores")

        setores = [
            {
                "id": row[0],
                "nome": row[1],
                "id_departamento": row[2],
                "departamento_nome": row[3] or "Não informado"
            }
            for row in setores_rows
        ]
        
        # Buscar TODOS os supervisores e admins (filtro por setor será feito no frontend)
        usuarios_sql = text("""
            SELECT u.id, u.nome_completo, u.id_setor, s.nome as setor_nome,
                   u.privilege_level, u.trabalha_producao, d.nome_tipo as departamento_nome,
                   u.email, u.matricula, d.id as departamento_id
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE u.privilege_level IN ('SUPERVISOR', 'ADMIN', 'GESTAO')
            ORDER BY d.nome_tipo, s.nome, u.privilege_level DESC, u.nome_completo
        """)

        print(f"[DEBUG] Executando consulta de usuários...")
        usuarios_result = db.execute(usuarios_sql)
        usuarios_rows = usuarios_result.fetchall()
        print(f"[DEBUG] Encontrados {len(usuarios_rows)} usuários")

        usuarios = [
            {
                "id": row[0],
                "nome_completo": row[1],
                "id_setor": row[2],
                "setor": row[3] or "Não informado",
                "privilege_level": row[4],
                "trabalha_producao": bool(row[5]) if row[5] is not None else False,
                "departamento": row[6] or "Não informado",
                "email": row[7] or "",
                "matricula": row[8] or "",
                "departamento_id": row[9],
                # Formatação para dropdown
                "display_name": f"{row[1]} - {row[3] or 'Sem Setor'} ({row[4]})",
                # Indicador se é supervisor do setor
                "is_supervisor_setor": row[4] == 'SUPERVISOR' and bool(row[5])
            }
            for row in usuarios_rows
        ]
        
        # Buscar departamentos
        departamentos_sql = text("""
            SELECT d.id, d.nome_tipo as nome
            FROM tipo_departamentos d
            ORDER BY d.nome_tipo
        """)

        print(f"[DEBUG] Executando consulta de departamentos...")
        departamentos_result = db.execute(departamentos_sql)
        departamentos_rows = departamentos_result.fetchall()
        print(f"[DEBUG] Encontrados {len(departamentos_rows)} departamentos")

        departamentos = [
            {
                "id": row[0],
                "nome": row[1],  # Frontend espera 'nome', não 'nome_tipo'
                "nome_tipo": row[1]  # Manter compatibilidade
            }
            for row in departamentos_rows
        ]

        # Buscar ordens de serviço disponíveis com relacionamentos Cliente e Equipamento
        ordens_sql = text("""
            SELECT os.id, os.os_numero, os.descricao_maquina, os.status_os,
                   c.razao_social as cliente_nome, tm.nome_tipo as tipo_maquina_nome,
                   s.nome as setor_nome, e.descricao as equipamento_descricao,
                   os.prioridade
            FROM ordens_servico os
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            LEFT JOIN tipos_maquina tm ON os.id_tipo_maquina = tm.id
            LEFT JOIN tipo_setores s ON os.id_setor = s.id
            WHERE (os.status_os IS NULL OR os.status_os NOT IN ('TERMINADA - ARQUIVADA', 'RECUSADA - CONFERIDA'))
            ORDER BY os.os_numero DESC
            LIMIT 100
        """)

        print(f"[DEBUG] Executando consulta de ordens de serviço...")
        ordens_result = db.execute(ordens_sql)
        ordens_rows = ordens_result.fetchall()
        print(f"[DEBUG] Encontradas {len(ordens_rows)} ordens de serviço")
        ordens_servico = [
            {
                "id": row[0],
                "os_numero": row[1] or "",
                "descricao_maquina": row[2] or "",
                "status": row[3] or "ABERTA",
                "cliente_nome": row[4] or "Não informado",
                "tipo_maquina_nome": row[5] or "Não informado",
                "setor": row[6] or "Não informado"
            }
            for row in ordens_rows
        ]

        print(f"[DEBUG] RESUMO FINAL:")
        print(f"[DEBUG] - Setores: {len(setores)}")
        print(f"[DEBUG] - Usuários: {len(usuarios)}")
        print(f"[DEBUG] - Departamentos: {len(departamentos)}")
        print(f"[DEBUG] - Ordens de serviço: {len(ordens_servico)}")

        # Verificar se alguma lista está vazia
        if len(setores) == 0:
            print(f"⚠️ [AVISO] Lista de setores está vazia!")
        if len(usuarios) == 0:
            print(f"⚠️ [AVISO] Lista de usuários está vazia!")
        if len(departamentos) == 0:
            print(f"⚠️ [AVISO] Lista de departamentos está vazia!")
        if len(ordens_servico) == 0:
            print(f"⚠️ [AVISO] Lista de ordens de serviço está vazia!")

        resultado = {
            "setores": setores,
            "usuarios": usuarios,
            "departamentos": departamentos,
            "ordens_servico": ordens_servico,
            "status_opcoes": ["PROGRAMADA", "EM_ANDAMENTO", "ENVIADA", "CONCLUIDA", "CANCELADA"]
        }

        print(f"[DEBUG] Retornando resultado com {len(resultado)} chaves")
        return resultado
        
    except Exception as e:
        print(f"❌ [ERRO CRÍTICO] Erro ao buscar dados do formulário: {e}")
        import traceback
        traceback.print_exc()

        # Retornar dados vazios mas com informação do erro
        return {
            "setores": [],
            "usuarios": [],
            "departamentos": [],
            "ordens_servico": [],
            "status_opcoes": ["PROGRAMADA", "EM_ANDAMENTO", "ENVIADA", "CONCLUIDA", "CANCELADA"],
            "erro": str(e)
        }

@router.get("/supervisores-por-setor/{setor_id}", operation_id="pcp_get_supervisores_por_setor")
async def get_supervisores_por_setor(
    setor_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar supervisores de um setor específico que trabalham na produção"""
    try:
        supervisores_sql = text("""
            SELECT u.id, u.nome_completo, u.id_setor, s.nome as setor_nome,
                   u.privilege_level, u.trabalha_producao, d.nome_tipo as departamento_nome,
                   u.email, u.matricula
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            WHERE u.id_setor = :setor_id
            AND u.privilege_level IN ('SUPERVISOR', 'ADMIN', 'GESTAO')
            AND (u.trabalha_producao = 1 OR u.privilege_level = 'ADMIN')
            ORDER BY u.privilege_level DESC, u.nome_completo
        """)

        result = db.execute(supervisores_sql, {"setor_id": setor_id})
        supervisores_rows = result.fetchall()

        supervisores = [
            {
                "id": row[0],
                "nome_completo": row[1],
                "id_setor": row[2],
                "setor": row[3] or "Não informado",
                "privilege_level": row[4],
                "trabalha_producao": bool(row[5]) if row[5] is not None else False,
                "departamento": row[6] or "Não informado",
                "email": row[7] or "",
                "matricula": row[8] or "",
                "display_name": f"{row[1]} - {row[3] or 'Sem Setor'} ({row[4]})"
            }
            for row in supervisores_rows
        ]

        return {
            "supervisores": supervisores,
            "total": len(supervisores),
            "setor_id": setor_id
        }

    except Exception as e:
        print(f"Erro ao buscar supervisores do setor {setor_id}: {e}")
        return {
            "supervisores": [],
            "total": 0,
            "setor_id": setor_id,
            "erro": str(e)
        }

@router.post("/programacoes", operation_id="pcp_create_programacao")
async def create_programacao_pcp(
    programacao_data: ProgramacaoPCPCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Criar nova programação"""
    try:
        # Buscar a ordem de serviço por os_numero se fornecido, senão por id
        if hasattr(programacao_data, 'os_numero') and programacao_data.os_numero:
            ordem_servico = db.query(OrdemServico).filter(
                OrdemServico.os_numero == programacao_data.os_numero
            ).first()

            if not ordem_servico:
                raise HTTPException(status_code=404, detail=f"Ordem de serviço {programacao_data.os_numero} não encontrada")

            # Usar o ID da OS encontrada
            id_ordem_servico = ordem_servico.id
        else:
            # Fallback para id_ordem_servico
            ordem_servico = db.query(OrdemServico).filter(
                OrdemServico.id == programacao_data.id_ordem_servico
            ).first()

            if not ordem_servico:
                raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

            id_ordem_servico = programacao_data.id_ordem_servico
        
        # Buscar o setor para obter o departamento
        setor = db.query(Setor).filter(Setor.id == programacao_data.id_setor).first()
        
        # Preparar histórico inicial
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        historico_inicial = f"[CRIAÇÃO] Programação criada por {current_user.nome_completo} em {timestamp}"
        if programacao_data.responsavel_id:
            responsavel = db.query(Usuario).filter(Usuario.id == programacao_data.responsavel_id).first()
            if responsavel:
                historico_inicial += f"\n[ATRIBUIÇÃO] Atribuída para {responsavel.nome_completo} em {timestamp}"

        # Criar a programação já ENVIADA ao setor (não precisa de envio separado)
        nova_programacao = Programacao(
            id_ordem_servico=id_ordem_servico,  # Usar o ID correto
            id_setor=programacao_data.id_setor,
            responsavel_id=programacao_data.responsavel_id,
            inicio_previsto=programacao_data.inicio_previsto,
            fim_previsto=programacao_data.fim_previsto,
            observacoes=programacao_data.observacoes,
            historico=historico_inicial,
            status="ENVIADA",  # Já vai direto como ENVIADA
            criado_por_id=current_user.id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(nova_programacao)
        
        # Atualizar a ordem de serviço com setor, departamento e prioridade
        update_data = {}
        if setor:
            update_data['id_setor'] = programacao_data.id_setor
            update_data['id_departamento'] = setor.id_departamento

        # Atualizar prioridade se fornecida
        if programacao_data.prioridade:
            update_data['prioridade'] = programacao_data.prioridade

        if update_data:
            db.query(OrdemServico).filter(OrdemServico.id == ordem_servico.id).update(update_data)
        
        db.commit()
        db.refresh(nova_programacao)
        
        return {
            "id": nova_programacao.id,
            "message": "Programação criada com sucesso",
            "id_ordem_servico": nova_programacao.id_ordem_servico,
            "id_setor": nova_programacao.id_setor,
            "status": nova_programacao.status
        }
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar programação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar programação: {str(e)}")

@router.get("/programacoes", operation_id="pcp_get_programacoes")
async def get_programacoes_pcp(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter todas as programações para PCP"""
    try:
        sql = text("""
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor,
                   os.os_numero, u.nome_completo as responsavel_nome,
                   s.nome as setor_nome,
                   c.razao_social as cliente_nome,
                   e.descricao as equipamento_descricao
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            ORDER BY p.inicio_previsto DESC
            LIMIT 100
        """)

        result = db.execute(sql)
        programacoes = result.fetchall()

        return [
            {
                "id": row[0],
                "id_ordem_servico": row[1],
                "responsavel_id": row[2],
                "inicio_previsto": str(row[3]) if row[3] else None,
                "fim_previsto": str(row[4]) if row[4] else None,
                "status": row[5] or "PROGRAMADA",
                "criado_por_id": row[6],
                "observacoes": row[7] or "",
                "created_at": str(row[8]) if row[8] else None,
                "updated_at": str(row[9]) if row[9] else None,
                "id_setor": row[10],
                "os_numero": row[11] or "",
                "responsavel_nome": row[12] or "Não informado",
                "setor_nome": row[13] or "Não informado",
                # Relacionamentos 1:1 conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
                "cliente": row[14] if row[14] else "Não informado",
                "equipamento": row[15] if row[15] else "Não informado"
            }
            for row in programacoes
        ]

    except Exception as e:
        print(f"Erro ao buscar programações PCP: {e}")
        return []

@router.get("/dashboard/avancado", operation_id="pcp_get_dashboard_avancado")
async def get_dashboard_avancado(
    periodo_dias: Optional[int] = Query(30, description="Período em dias para análise"),
    setor_id: Optional[int] = Query(None, description="Filtrar por setor específico"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard avançado do PCP"""
    try:
        return {
            "total_programacoes": 0,
            "programacoes_concluidas": 0,
            "programacoes_pendentes": 0,
            "eficiencia_geral": 0.0,
            "setores": [],
            "alertas": []
        }
    except Exception as e:
        print(f"Erro ao buscar dashboard avançado: {e}")
        return {
            "total_programacoes": 0,
            "programacoes_concluidas": 0,
            "programacoes_pendentes": 0,
            "eficiencia_geral": 0.0,
            "setores": [],
            "alertas": []
        }

@router.get("/alertas", operation_id="pcp_get_alertas")
async def get_alertas_pcp(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter alertas e notificações importantes para o PCP"""
    try:
        return []
    except Exception as e:
        print(f"Erro ao buscar alertas: {e}")
        return []

@router.get("/pendencias", operation_id="pcp_get_pendencias")
async def get_pendencias_pcp(
    status: Optional[str] = Query(None, description="Filtrar por status: ABERTA, FECHADA"),
    setor: Optional[str] = Query(None, description="Filtrar por setor"),
    # prioridade removida - não existe para pendências
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obter pendências do PCP - filtra por departamento do usuário"""
    try:
        # Buscar setor do usuário para filtrar por departamento
        user_setor = db.query(Setor).filter(Setor.id == current_user.id_setor).first()
        departamento_usuario = user_setor.departamento if user_setor else None

        # 🏭 PCP: QUERY SIMPLIFICADA PARA VER TODAS AS PENDÊNCIAS (SEM PRIORIDADE)
        sql = text("""
            SELECT p.id, p.descricao_pendencia, p.status, p.data_inicio,
                   p.data_fechamento, p.id_responsavel_inicio, p.numero_os,
                   p.cliente, p.tipo_maquina, p.descricao_maquina,
                   COALESCE(u.nome_completo, 'Usuário ' || p.id_responsavel_inicio) as responsavel_nome
            FROM pendencias p
            LEFT JOIN tipo_usuarios u ON p.id_responsavel_inicio = u.id
            WHERE 1=1
        """)

        # Adicionar filtros se fornecidos
        conditions = []

        # PCP VÊ TODAS AS PENDÊNCIAS (sem filtro por departamento)
        print(f"🏭 PCP: Mostrando TODAS as pendências (sem filtro por departamento)")
        # Não adicionar filtro por departamento - PCP vê tudo

        if status:
            conditions.append(f"AND p.status = '{status}'")
        if setor:
            conditions.append(f"AND p.numero_os LIKE '%{setor}%'")
        # prioridade removida - não existe para pendências

        if conditions:
            sql = text(str(sql) + " " + " ".join(conditions))

        sql = text(str(sql) + " ORDER BY p.data_inicio DESC LIMIT 100")

        print(f"🏭 PCP SQL Query: {sql}")
        result = db.execute(sql)
        pendencias = result.fetchall()
        print(f"🏭 PCP Pendências encontradas: {len(pendencias)}")

        return [
            {
                "id": row[0],
                "descricao": row[1] or "",
                "status": row[2] or "ABERTA",
                # prioridade removida - não existe para pendências
                "data_abertura": str(row[3]) if row[3] else None,
                "data_fechamento": str(row[4]) if row[4] else None,
                "responsavel_id": row[5],
                "numero_os": row[6] or "",
                "cliente": row[7] or "Não informado",
                "tipo_maquina": row[8] or "Não informado",
                "equipamento": row[9] or "Não informado",
                "responsavel_nome": row[10] or "Não informado"
            }
            for row in pendencias
        ]

    except Exception as e:
        print(f"Erro ao buscar pendências: {e}")
        return []

@router.get("/pendencias/dashboard", operation_id="pcp_get_pendencias_dashboard")
async def get_pendencias_dashboard(
    periodo_dias: Optional[int] = Query(30, description="Período em dias para análise"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard de pendências do PCP"""
    try:
        print(f"🏭 Calculando dashboard de pendências para período: {periodo_dias} dias")

        # 📊 CALCULAR MÉTRICAS REAIS DAS PENDÊNCIAS
        from datetime import datetime, timedelta

        # Data limite para o período
        data_limite = datetime.now() - timedelta(days=periodo_dias)

        # Query simplificada para buscar todas as pendências
        sql = text("""
            SELECT p.id, p.status, p.data_inicio, p.data_fechamento,
                   p.tempo_aberto_horas
            FROM pendencias p
            WHERE 1=1
        """)

        result = db.execute(sql)
        todas_pendencias = result.fetchall()

        print(f"📊 Total de pendências encontradas: {len(todas_pendencias)}")

        # Calcular métricas (SEM prioridade)
        total_pendencias = len(todas_pendencias)
        pendencias_abertas = len([p for p in todas_pendencias if p[1] == 'ABERTA'])
        pendencias_fechadas = len([p for p in todas_pendencias if p[1] == 'FECHADA'])

        # Pendências do período
        pendencias_periodo = len([p for p in todas_pendencias if p[2] and p[2] >= data_limite])

        # Pendências críticas = pendências abertas (sem conceito de prioridade)
        pendencias_criticas = pendencias_abertas

        # Tempo médio de resolução
        pendencias_com_tempo = [p for p in todas_pendencias if p[4] is not None and p[1] == 'FECHADA']
        tempo_medio = sum([p[4] for p in pendencias_com_tempo]) / len(pendencias_com_tempo) if pendencias_com_tempo else 0.0

        # Distribuição por setor (simplificada)
        distribuicao_setor = [
            {"setor": "Geral", "total": total_pendencias}
        ] if total_pendencias > 0 else []

        print(f"✅ Métricas calculadas: {total_pendencias} total, {pendencias_abertas} abertas, {pendencias_fechadas} fechadas")

        return {
            "metricas_gerais": {
                "total_pendencias": total_pendencias,
                "pendencias_abertas": pendencias_abertas,
                "pendencias_fechadas": pendencias_fechadas,
                "pendencias_periodo": pendencias_periodo,
                "pendencias_criticas": pendencias_criticas,
                "tempo_medio_resolucao_horas": round(tempo_medio, 2)
            },
            "distribuicao_prioridade": [],  # Vazio - prioridade não existe para pendências
            "distribuicao_setor": distribuicao_setor,
            "evolucao_7_dias": []  # Implementar depois se necessário
        }
    except Exception as e:
        print(f"❌ Erro ao buscar dashboard de pendências: {e}")
        import traceback
        traceback.print_exc()
        return {
            "metricas_gerais": {
                "total_pendencias": 0,
                "pendencias_abertas": 0,
                "pendencias_fechadas": 0,
                "pendencias_periodo": 0,
                "pendencias_criticas": 0,
                "tempo_medio_resolucao_horas": 0.0
            },
            "distribuicao_prioridade": [],
            "distribuicao_setor": [],
            "evolucao_7_dias": []
        }

@router.post("/programacoes/atribuir", operation_id="pcp_post_programacoes_atribuir")
async def atribuir_programacao(
    dados: AtribuicaoProgramacaoRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atribuir programação a um responsável e setor"""
    try:
        # Verificar se o responsável existe
        responsavel = db.query(Usuario).filter(Usuario.id == dados.responsavel_id).first()
        if not responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Responsável não encontrado"
            )

        # Verificar se o setor existe
        setor = db.query(Setor).filter(
            Setor.nome == dados.setor_destino,
            Setor.departamento == dados.departamento_destino
        ).first()

        if not setor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setor não encontrado"
            )

        # Preparar histórico de atribuição
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        historico_atribuicao = f"[CRIAÇÃO] Programação criada e atribuída por {current_user.nome_completo} em {timestamp}\n[ATRIBUIÇÃO] Atribuída para {responsavel.nome_completo} no setor {dados.setor_destino} em {timestamp}"

        # Buscar programação existente sem responsável (mais recente)
        programacao_existente = db.query(Programacao).filter(
            Programacao.responsavel_id.is_(None),
            Programacao.status == "ENVIADA"
        ).order_by(Programacao.id.desc()).first()

        if programacao_existente:
            # Atualizar programação existente
            programacao_existente.responsavel_id = dados.responsavel_id
            programacao_existente.id_setor = setor.id
            programacao_existente.inicio_previsto = datetime.fromisoformat(dados.data_inicio.replace('Z', '+00:00'))
            programacao_existente.fim_previsto = datetime.fromisoformat(dados.data_fim.replace('Z', '+00:00'))
            programacao_existente.observacoes = dados.observacoes
            programacao_existente.historico = historico_atribuicao
            programacao_existente.updated_at = datetime.now()

            db.commit()
            db.refresh(programacao_existente)
            nova_programacao = programacao_existente
        else:
            # Criar nova programação (já ENVIADA) com OS padrão
            nova_programacao = Programacao(
                responsavel_id=dados.responsavel_id,
                id_setor=setor.id,
                id_ordem_servico=1,  # OS padrão para teste
                inicio_previsto=datetime.fromisoformat(dados.data_inicio.replace('Z', '+00:00')),
                fim_previsto=datetime.fromisoformat(dados.data_fim.replace('Z', '+00:00')),
                observacoes=dados.observacoes,
                historico=historico_atribuicao,
                status="ENVIADA",  # Já vai direto como ENVIADA
                criado_por_id=current_user.id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.add(nova_programacao)
            db.commit()
            db.refresh(nova_programacao)

        db.add(nova_programacao)
        db.commit()
        db.refresh(nova_programacao)

        return {
            "id": nova_programacao.id,
            "responsavel_id": nova_programacao.responsavel_id,
            "setor_destino": dados.setor_destino,
            "departamento_destino": dados.departamento_destino,
            "data_inicio": nova_programacao.inicio_previsto.isoformat(),
            "data_fim": nova_programacao.fim_previsto.isoformat(),
            "status": nova_programacao.status,
            "message": "Programação atribuída com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao atribuir programação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atribuir programação: {str(e)}"
        )

@router.put("/programacoes/{programacao_id}", operation_id="pcp_put_programacao_editar")
async def editar_programacao(
    programacao_id: int,
    dados: AtribuicaoProgramacaoRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Editar programação existente"""
    try:
        # Buscar programação existente
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        # Verificar se o responsável existe
        responsavel = db.query(Usuario).filter(Usuario.id == dados.responsavel_id).first()
        if not responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Responsável não encontrado"
            )

        # Verificar se o setor existe
        setor = db.query(Setor).filter(
            Setor.nome == dados.setor_destino,
            Setor.departamento == dados.departamento_destino
        ).first()

        if not setor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setor não encontrado"
            )

        # Atualizar programação
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'responsavel_id': dados.responsavel_id,
            'id_setor': setor.id,
            'inicio_previsto': datetime.fromisoformat(dados.data_inicio.replace('Z', '+00:00')),
            'fim_previsto': datetime.fromisoformat(dados.data_fim.replace('Z', '+00:00')),
            'observacoes': dados.observacoes,
            'updated_at': datetime.now()
        })

        db.commit()
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()

        return {
            "id": programacao.id if programacao else None,
            "responsavel_id": programacao.responsavel_id if programacao else None,
            "setor_destino": dados.setor_destino,
            "departamento_destino": dados.departamento_destino,
            "data_inicio": programacao.inicio_previsto.isoformat() if programacao is not None and programacao.inicio_previsto is not None else None,
            "data_fim": programacao.fim_previsto.isoformat() if programacao is not None and programacao.fim_previsto is not None else None,
            "status": programacao.status if programacao else None,
            "message": "Programação editada com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao editar programação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao editar programação: {str(e)}"
        )

@router.put("/programacoes/{programacao_id}", operation_id="pcp_put_programacao_editar")
async def editar_programacao(
    programacao_id: int,
    programacao_data: ProgramacaoEditRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Editar programação existente"""
    try:
        # Verificar permissão
        if current_user.privilege_level not in ['ADMIN', 'PCP', 'SUPERVISOR']:
            raise HTTPException(status_code=403, detail="Sem permissão para editar programações")

        # Buscar programação existente
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        # Preparar histórico de edição
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        historico_atual = programacao.historico or ""
        novo_historico = f"{historico_atual}\n[EDIÇÃO] Programação editada por {current_user.nome_completo} em {timestamp}"

        # Atualizar programação apenas com campos fornecidos
        update_data = {
            'historico': novo_historico,
            'updated_at': datetime.now()
        }

        # Adicionar campos opcionais se fornecidos
        if programacao_data.inicio_previsto:
            update_data['inicio_previsto'] = programacao_data.inicio_previsto
        if programacao_data.fim_previsto:
            update_data['fim_previsto'] = programacao_data.fim_previsto
        if programacao_data.observacoes is not None:
            update_data['observacoes'] = programacao_data.observacoes

        # Atualizar responsável se fornecido
        if programacao_data.responsavel_id:
            update_data['responsavel_id'] = programacao_data.responsavel_id
            responsavel = db.query(Usuario).filter(Usuario.id == programacao_data.responsavel_id).first()
            if responsavel:
                novo_historico += f"\n[REATRIBUIÇÃO] Reatribuída para {responsavel.nome_completo} em {timestamp}"
                update_data['historico'] = novo_historico

        # Atualizar setor se fornecido
        if programacao_data.id_setor:
            update_data['id_setor'] = programacao_data.id_setor

        db.query(Programacao).filter(Programacao.id == programacao_id).update(update_data)

        # Atualizar OS se necessário
        if programacao.id_ordem_servico and programacao_data.prioridade:
            db.query(OrdemServico).filter(OrdemServico.id == programacao.id_ordem_servico).update({
                'prioridade': programacao_data.prioridade
            })

        db.commit()

        return {
            "id": programacao_id,
            "message": "Programação editada com sucesso",
            "updated_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao editar programação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao editar programação: {str(e)}"
        )

@router.patch("/programacoes/{programacao_id}/reatribuir", operation_id="pcp_patch_programacao_reatribuir")
async def reatribuir_programacao(
    programacao_id: int,
    dados: AtribuicaoProgramacaoRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reatribuir programação para outro responsável"""
    try:
        # Buscar programação existente
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        # Verificar se o novo responsável existe
        novo_responsavel = db.query(Usuario).filter(Usuario.id == dados.responsavel_id).first()
        if not novo_responsavel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Novo responsável não encontrado"
            )

        # Salvar responsável anterior para histórico
        responsavel_anterior_id = programacao.responsavel_id

        # Preparar histórico de reatribuição
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        historico_atual = programacao.historico or ""
        novo_historico = f"{historico_atual}\n[REATRIBUIÇÃO] De ID {responsavel_anterior_id} para {novo_responsavel.nome_completo} em {timestamp}"

        # Processar novos horários
        novo_inicio = datetime.fromisoformat(dados.data_inicio.replace('Z', '+00:00'))
        novo_fim = datetime.fromisoformat(dados.data_fim.replace('Z', '+00:00'))

        # Se os horários fornecidos são iguais, preservar duração original
        if novo_inicio == novo_fim:
            inicio_original = programacao.inicio_previsto
            fim_original = programacao.fim_previsto

            if inicio_original and fim_original:
                duracao_original = fim_original - inicio_original
                if duracao_original.total_seconds() > 0:
                    novo_fim = novo_inicio + duracao_original
                    print(f"⏰ Preservando duração original: {duracao_original}")
                else:
                    # Se duração original é zero, usar 8h padrão
                    novo_fim = novo_inicio + timedelta(hours=8)
                    print(f"⏰ Aplicando duração padrão: 8h")
            else:
                # Se não há horários originais, usar 8h padrão
                novo_fim = novo_inicio + timedelta(hours=8)
                print(f"⏰ Aplicando duração padrão: 8h")
        else:
            # Supervisor definiu horários específicos - usar os fornecidos
            print(f"⏰ Usando horários definidos pelo supervisor: {novo_inicio} até {novo_fim}")

        # Reatribuir programação
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'responsavel_id': dados.responsavel_id,
            'inicio_previsto': novo_inicio,
            'fim_previsto': novo_fim,
            'observacoes': dados.observacoes,
            'historico': novo_historico,
            'updated_at': datetime.now()
        })

        # Commit para salvar as mudanças
        db.commit()

        # Refresh para obter dados atualizados
        db.refresh(programacao)

        return {
            "id": programacao.id,
            "responsavel_anterior_id": responsavel_anterior_id,
            "novo_responsavel_id": dados.responsavel_id,  # Usar o valor novo
            "novo_responsavel_nome": novo_responsavel.nome_completo,
            "data_reatribuicao": datetime.now().isoformat(),
            "status": programacao.status,
            "message": "Programação reatribuída com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao reatribuir programação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao reatribuir programação: {str(e)}"
        )

@router.post("/programacoes/{programacao_id}/atribuir-multiplos", operation_id="pcp_post_programacao_atribuir_multiplos")
async def atribuir_programacao_multiplos(
    programacao_id: int,
    dados: dict,  # {"responsaveis": [{"id": 1, "observacoes": "..."}, {"id": 2, "observacoes": "..."}]}
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atribuir programação para múltiplos colaboradores (cria cópias)"""
    try:
        # Buscar programação original
        programacao_original = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao_original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        responsaveis = dados.get('responsaveis', [])
        if not responsaveis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lista de responsáveis não pode estar vazia"
            )

        programacoes_criadas = []
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')

        for i, responsavel_data in enumerate(responsaveis):
            responsavel_id = responsavel_data.get('id')
            observacoes_especificas = responsavel_data.get('observacoes', '')

            # Verificar se responsável existe
            responsavel = db.query(Usuario).filter(Usuario.id == responsavel_id).first()
            if not responsavel:
                continue  # Pular responsáveis inválidos

            if i == 0:
                # Primeira atribuição: atualizar programação original
                historico_atribuicao = f"[ATRIBUIÇÃO MÚLTIPLA] Atribuída para {responsavel.nome_completo} (1/{len(responsaveis)}) por {current_user.nome_completo} em {timestamp}"

                programacao_original.responsavel_id = responsavel_id
                programacao_original.observacoes = f"{programacao_original.observacoes or ''}\n{observacoes_especificas}".strip()
                programacao_original.historico = f"{programacao_original.historico or ''}\n{historico_atribuicao}".strip()
                programacao_original.updated_at = datetime.now()

                programacoes_criadas.append({
                    "id": programacao_original.id,
                    "responsavel_id": responsavel_id,
                    "responsavel_nome": responsavel.nome_completo,
                    "tipo": "ORIGINAL"
                })
            else:
                # Demais atribuições: criar cópias
                historico_copia = f"[CÓPIA MÚLTIPLA] Cópia da programação {programacao_id} atribuída para {responsavel.nome_completo} ({i+1}/{len(responsaveis)}) por {current_user.nome_completo} em {timestamp}"

                nova_programacao = Programacao(
                    id_ordem_servico=programacao_original.id_ordem_servico,
                    responsavel_id=responsavel_id,
                    id_setor=programacao_original.id_setor,
                    inicio_previsto=programacao_original.inicio_previsto,
                    fim_previsto=programacao_original.fim_previsto,
                    observacoes=f"{programacao_original.observacoes or ''}\n{observacoes_especificas}".strip(),
                    historico=historico_copia,
                    status="ENVIADA",
                    criado_por_id=current_user.id,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )

                db.add(nova_programacao)
                db.flush()  # Para obter o ID

                programacoes_criadas.append({
                    "id": nova_programacao.id,
                    "responsavel_id": responsavel_id,
                    "responsavel_nome": responsavel.nome_completo,
                    "tipo": "COPIA"
                })

        db.commit()

        return {
            "message": f"Programação atribuída para {len(programacoes_criadas)} colaboradores",
            "programacao_original_id": programacao_id,
            "total_atribuicoes": len(programacoes_criadas),
            "programacoes": programacoes_criadas
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atribuir para múltiplos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atribuir programação: {str(e)}"
        )

@router.delete("/programacoes/{programacao_id}", operation_id="pcp_delete_programacao")
async def cancelar_programacao(
    programacao_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancelar uma programação"""
    try:
        # Buscar programação
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        # Verificar permissões
        if current_user.privilege_level not in ['ADMIN', 'GESTAO', 'SUPERVISOR']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para cancelar programações"
            )

        # Atualizar status para CANCELADA
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'status': 'CANCELADA',
            'updated_at': datetime.now(),
            'observacoes': (programacao.observacoes or '') + f" - CANCELADA por {current_user.nome_completo} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        })

        db.commit()

        return {"message": "Programação cancelada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao cancelar programação: {str(e)}"
        )

@router.patch("/programacoes/{programacao_id}/status", operation_id="pcp_patch_programacao_status")
async def atualizar_status_programacao(
    programacao_id: int,
    status_data: StatusUpdateRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar apenas o status da programação"""
    try:
        # Buscar programação
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        # Validar o status
        status_validos = ["PROGRAMADA", "EM_ANDAMENTO", "ENVIADA", "CONCLUIDA", "CANCELADA"]
        if status_data.status not in status_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status inválido. Status válidos: {', '.join(status_validos)}"
            )

        # Atualizar apenas o status
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'status': status_data.status,
            'updated_at': datetime.now()
        })
        
        # Atualizar observações
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'observacoes': f"{programacao.observacoes or ''} - Status alterado para {status_data.status} por {current_user.nome_completo} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        })

        db.commit()

        return {
            "id": programacao.id,
            "status": programacao.status,
            "message": f"Status da programação atualizado para {status_data.status}"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar status da programação: {str(e)}"
        )

@router.post("/programacoes/{programacao_id}/enviar-setor", operation_id="pcp_post_programacao_enviar_setor")
async def enviar_programacao_setor(
    programacao_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enviar programação para o setor responsável"""
    try:
        # Buscar programação
        programacao = db.query(Programacao).filter(Programacao.id == programacao_id).first()
        if not programacao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Programação não encontrada"
            )

        # Verificar se está no status correto
        if str(programacao.status) != 'PROGRAMADA':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas programações com status PROGRAMADA podem ser enviadas"
            )

        # Atualizar status
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'status': 'ENVIADA_SETOR',
            'updated_at': datetime.now(),
            'observacoes': (programacao.observacoes or '') + f" - ENVIADA para setor por {current_user.nome_completo} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        })

        db.commit()

        return {"message": "Programação enviada para o setor com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar programação: {str(e)}"
        )
