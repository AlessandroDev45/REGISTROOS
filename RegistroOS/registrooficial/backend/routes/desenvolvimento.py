from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, text, distinct # Importado 'distinct'
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import json
import subprocess
import os
import logging
import sys # Importar sys para o sys.executable

from app.database_models import (
    Usuario, OrdemServico, ApontamentoDetalhado, Programacao,
    Pendencia, Setor, Departamento, TipoMaquina, Cliente, Equipamento,
    TipoAtividade, TipoDescricaoAtividade, TipoCausaRetrabalho, TipoTeste, ResultadoTeste
)
from config.database_config import get_db
from app.dependencies import get_current_user
from utils.validators import generate_next_os # Certifique-se de que este import está correto

print("🔧 Módulo desenvolvimento.py carregado")

router = APIRouter(tags=["desenvolvimento"])

# Configuração de logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Configurar handler se ainda não estiver configurado (evita duplicar handlers)
if logger.handlers is None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# =============================================================================
# MODELOS PYDANTIC
# =============================================================================
# Modelos para validação de dados nas requisições
class ApontamentoCreate(BaseModel):
    """Modelo para criação de apontamentos com todos os campos necessários"""
    numero_os: str
    cliente: str
    equipamento: str
    tipo_maquina: str
    tipo_atividade: str
    descricao_atividade: str
    data_inicio: date
    hora_inicio: str
    data_fim: Optional[date] = None
    hora_fim: Optional[str] = None
    observacao: Optional[str] = None
    resultado_global: Optional[str] = None
    observacao_resultado: Optional[str] = None
    status_os: Optional[str] = None
    retrabalho: Optional[bool] = False
    causa_retrabalho: Optional[str] = None

class ProgramacaoCreate(BaseModel):
    """Modelo para criação de programações de atividades"""
    numero_os: str
    cliente: str
    equipamento: str
    tipo_atividade: str
    data_programada: date
    hora_inicio: str
    hora_fim: Optional[str] = None
    observacoes: Optional[str] = None

class PendenciaResolve(BaseModel):
    """Modelo para resolução de pendências"""
    observacao_resolucao: str

# =============================================================================
# ENDPOINTS DE SETORES E CONFIGURAÇÃO
# =============================================================================

@router.get("/admin/setores", operation_id="dev_get_admin_setores")
async def get_setores_admin(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para administradores obterem lista de setores cadastrados no sistema.
    Retorna apenas setores ativos.
    """
    try:
        setores = db.query(Setor).filter(Setor.ativo.is_(True)).all()
        
        return [
            {
                "id": setor.id,
                "nome": setor.nome,
                "departamento": setor.departamento,
                "ativo": setor.ativo,
                "descricao": setor.descricao
            }
            for setor in setores
        ]
    except Exception as e:
        print(f"Erro ao buscar setores: {e}")
        return []

@router.get("/setores/{setor_id}/configuracao", operation_id="dev_get_setores_setor_id_configuracao")
async def get_setor_configuracao(
    setor_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter configuração específica de um setor.
    Atualmente retorna configuração padrão, mas pode ser personalizada por setor no futuro.
    """
    try:
        setor = db.query(Setor).filter(Setor.id == setor_id).first()
        if not setor:
            raise HTTPException(status_code=404, detail="Setor não encontrado")
        
        # Por enquanto, retorna configuração padrão
        # Futuramente pode ser personalizada por setor
        return {
            "setor_id": setor.id,
            "nome_setor": setor.nome,
            "configuracao": {
                "tipos_maquina": ["Motor Indução", "Motor Síncrono", "Transformador"],
                "tipos_atividade": ["Testes Iniciais", "Testes Parciais", "Testes Finais"],
                "status_os": ["Aberta", "Em Andamento", "Finalizada"]
            }
        }
    except Exception as e:
        print(f"Erro ao buscar configuração do setor: {e}")
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

# NOVO ENDPOINT: para carregar as categorias de máquina distintas
@router.get("/admin/categorias-maquina", operation_id="dev_get_admin_categorias_maquina")
async def get_categorias_maquina_admin(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter uma lista de categorias de máquina distintas.
    Pode ser usado para popular dropdowns de categoria.
    """
    try:
        # Consulta para obter categorias distintas da tabela TipoMaquina
        # Se for necessário filtrar por departamento/setor do usuário, adicionar ao filtro
        query = db.query(TipoMaquina.categoria).filter(
            TipoMaquina.categoria.isnot(None),
            TipoMaquina.categoria != ""
        ).distinct()

        # Adicionar filtros de departamento e setor se o usuário não for ADMIN
        if current_user.privilege_level != 'ADMIN':  # type: ignore
            query = query.filter(
                and_(
                    TipoMaquina.departamento == current_user.departamento,
                    TipoMaquina.setor == current_user.setor
                )
            )

        categorias = [row[0] for row in query.all()]
        categorias.sort() # Opcional: ordenar alfabeticamente
        return categorias
    except Exception as e:
        logger.error(f"Erro ao buscar categorias de máquina: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias de máquina: {str(e)}")


# =============================================================================
# ENDPOINTS DE SUBCATEGORIAS E PARTES
# =============================================================================

@router.get("/subcategorias-por-categoria")
async def get_subcategorias_por_categoria(
    categoria: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Buscar subcategorias (partes) baseadas na categoria da máquina"""
    try:
        # Mapeamento de categorias para suas subcategorias/partes
        subcategorias_map = {
            'MOTOR': [
                'Campo Shunt',
                'Campo Série',
                'Interpolos',
                'Armadura',
                'Escovas',
                'Comutador',
                'Rolamentos',
                'Ventilação'
            ],
            'GERADOR': [
                'Estator',
                'Rotor',
                'Excitatriz',
                'Regulador de Tensão',
                'Rolamentos',
                'Ventilação',
                'Sistema de Refrigeração'
            ],
            'TRANSFORMADOR': [
                'Núcleo',
                'Bobinas',
                'Isolação',
                'Óleo Isolante',
                'Buchas',
                'Comutador de Derivação',
                'Sistema de Refrigeração'
            ],
            'BOMBA': [
                'Rotor',
                'Estator',
                'Carcaça',
                'Vedações',
                'Rolamentos',
                'Acoplamento'
            ],
            'COMPRESSOR': [
                'Pistão',
                'Cilindro',
                'Válvulas',
                'Cabeçote',
                'Sistema de Lubrificação',
                'Sistema de Refrigeração'
            ],
            'VENTILADOR': [
                'Hélice',
                'Motor',
                'Carcaça',
                'Rolamentos',
                'Sistema de Transmissão'
            ]
        }

        # Buscar subcategorias para a categoria especificada
        subcategorias = subcategorias_map.get(categoria.upper(), [])

        return {
            "categoria": categoria,
            "subcategorias": subcategorias,
            "total": len(subcategorias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar subcategorias: {str(e)}")

@router.get("/tipos-maquina/categoria-por-nome")
async def get_categoria_por_nome_tipo(
    nome_tipo: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Buscar categoria baseada no nome_tipo selecionado"""
    try:
        from app.database_models import TipoMaquina

        # Buscar a categoria do nome_tipo selecionado
        result = db.query(TipoMaquina.categoria).filter(
            TipoMaquina.nome_tipo == nome_tipo
        ).first()

        if result and result[0]:
            categoria = result[0]
            print(f"Categoria encontrada para '{nome_tipo}': {categoria}")
            return {"categoria": categoria}
        else:
            print(f"Nenhuma categoria encontrada para '{nome_tipo}'")
            return {"categoria": None}

    except Exception as e:
        print(f"Erro ao buscar categoria por nome_tipo: {e}")
        return {"categoria": None}

@router.get("/tipos-maquina/subcategorias")
async def get_subcategorias_tipos_maquina(
    categoria: str = Query(...),
    departamento: str = Query(None),
    setor: str = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Buscar subcategorias da coluna subcategoria da tabela tipos_maquina por categoria"""
    try:
        from app.database_models import TipoMaquina

        # Buscar subcategorias diretamente da coluna subcategoria
        query = db.query(TipoMaquina.subcategoria).filter(
            TipoMaquina.categoria.ilike(f"%{categoria}%"),
            TipoMaquina.subcategoria.isnot(None),
            TipoMaquina.subcategoria != ""
        )

        if departamento:
            query = query.filter(TipoMaquina.departamento == departamento)
        if setor:
            query = query.filter(TipoMaquina.setor == setor)

        results = query.all()

        # Coletar todas as subcategorias únicas
        subcategorias_set = set()

        for result in results:
            if result[0]:  # subcategoria não é None
                subcategoria = result[0].strip()
                if subcategoria:
                    # Se contém vírgulas, pode ser múltiplas subcategorias
                    if ',' in subcategoria:
                        partes = [p.strip() for p in subcategoria.split(',') if p.strip()]
                        subcategorias_set.update(partes)
                    else:
                        subcategorias_set.add(subcategoria)

        print(f"Subcategorias encontradas no banco para '{categoria}': {list(subcategorias_set)}")

        # Fallback para subcategorias padrão se não encontrar nada
        if not subcategorias_set:
            subcategorias_map = {
                'MOTOR': ['Campo Shunt', 'Campo Série', 'Interpolos', 'Armadura', 'Escovas', 'Comutador', 'Rolamentos', 'Ventilação'],
                'MOTOR CA': ['Estator', 'Rotor', 'Rolamentos', 'Ventilação', 'Carcaça'],
                'MOTOR CC': ['Campo Shunt', 'Campo Série', 'Interpolos', 'Armadura', 'Escovas', 'Comutador'],
                'GERADOR': ['Estator', 'Rotor', 'Excitatriz', 'Regulador de Tensão', 'Rolamentos', 'Ventilação', 'Sistema de Refrigeração'],
                'GERADOR CA': ['Estator', 'Rotor', 'Excitatriz', 'Rolamentos', 'Ventilação'],
                'TRANSFORMADOR': ['Núcleo', 'Bobinas', 'Isolação', 'Óleo Isolante', 'Buchas', 'Comutador de Derivação', 'Sistema de Refrigeração'],
                'BOMBA': ['Rotor', 'Estator', 'Carcaça', 'Vedações', 'Rolamentos', 'Acoplamento'],
                'COMPRESSOR': ['Pistão', 'Cilindro', 'Válvulas', 'Cabeçote', 'Sistema de Lubrificação', 'Sistema de Refrigeração'],
                'VENTILADOR': ['Hélice', 'Motor', 'Carcaça', 'Rolamentos', 'Sistema de Transmissão']
            }
            subcategorias_set = set(subcategorias_map.get(categoria.upper(), []))

        return sorted(list(subcategorias_set))

    except Exception as e:
        print(f"Erro ao buscar subcategorias de tipos de máquina: {e}")
        # Fallback para subcategorias padrão
        subcategorias_map = {
            'MOTOR': ['Campo Shunt', 'Campo Série', 'Interpolos', 'Armadura'],
            'GERADOR': ['Estator', 'Rotor', 'Excitatriz'],
            'TRANSFORMADOR': ['Núcleo', 'Bobinas', 'Isolação']
        }
        return subcategorias_map.get(categoria.upper(), [])

# =============================================================================
# ENDPOINTS DE APONTAMENTOS
# =============================================================================

@router.get("/apontamentos", operation_id="dev_get_apontamentos")
async def get_apontamentos(
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter apontamentos do usuário com dados completos do formulário.
    Filtra por usuário se não for admin, e por status se especificado.
    Usa SQL direto para melhor performance.
    """
    try:
        from sqlalchemy import text

        # Filtrar por usuário se não for admin
        where_clause = ""
        if str(current_user.privilege_level) != 'ADMIN':
            where_clause = f"WHERE a.id_usuario = {current_user.id}"
            if status:
                where_clause += f" AND a.status_apontamento = '{status}'"
        elif status:
            where_clause = f"WHERE a.status_apontamento = '{status}'"

        sql = text(f"""
            SELECT a.id, a.id_os, a.data_hora_inicio, a.data_hora_fim, a.foi_retrabalho,
                   a.status_apontamento, a.observacao_os, a.criado_por, a.id_setor,
                   os.os_numero, os.descricao_maquina, os.testes_exclusivo_os,
                   u.nome_completo, u.matricula,
                   c.razao_social as cliente_nome,
                   e.descricao as equipamento_descricao
            FROM apontamentos_detalhados a
            LEFT JOIN ordens_servico os ON a.id_os = os.id
            LEFT JOIN tipo_usuarios u ON a.id_usuario = u.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            {where_clause}
            ORDER BY a.data_hora_inicio DESC
            LIMIT 50
        """)

        result = db.execute(sql)
        apontamentos = result.fetchall()

        return [
            {
                "id": row[0],
                "numero_os": row[9] or "",  # os.os_numero
                "status_os": "EM ANDAMENTO",  # Status padrão
                # Relacionamentos 1:1 conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
                "cliente": row[14] if row[14] else None,  # cliente_nome
                "equipamento": row[15] if row[15] else None,  # equipamento_descricao
                "tipo_maquina": None,
                "tipo_atividade": None,
                "data_inicio": str(row[2])[:10] if row[2] else None,  # data_hora_inicio
                "hora_inicio": str(row[2])[11:16] if row[2] else None,
                "data_fim": str(row[3])[:10] if row[3] else None,  # data_hora_fim
                "hora_fim": str(row[3])[11:16] if row[3] else None,
                "eh_retrabalho": bool(row[4]) if row[4] is not None else False,  # foi_retrabalho
                "observacao_geral": row[6] or "",  # observacao_os
                "resultado_global": row[5] or "PENDENTE",  # status_apontamento
                "testes_exclusivo_os": row[11],  # os.testes_exclusivo_os
                "usuario_nome": row[12] or "",  # u.nome_completo
                "matricula": row[13] or "",  # u.matricula
                "status_apontamento": row[5] or "PENDENTE",
                "criado_por": row[7] or "",  # criado_por
                "setor": row[8] or ""  # id_setor
            }
            for row in apontamentos
        ]
    except Exception as e:
        print(f"Erro ao buscar apontamentos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar apontamentos: {str(e)}")


@router.get("/os/apontamentos/meus", operation_id="dev_get_os_apontamentos_meus")
async def get_meus_apontamentos(
    data: Optional[str] = Query(None),
    setor: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter apontamentos do usuário logado.
    Filtra por data e setor se especificados.
    Baseado no nível de privilégio do usuário.
    """
    try:
        query = db.query(ApontamentoDetalhado)
        
        # Filtros baseados no privilégio
        if current_user.privilege_level == 'USER':  # type: ignore
            query = query.filter(ApontamentoDetalhado.id_usuario == current_user.id)
        elif current_user.privilege_level == 'SUPERVISOR':  # type: ignore
            # Supervisor vê do seu setor
            query = query.filter(ApontamentoDetalhado.id_setor == current_user.id_setor)
        # Admin vê tudo
        
        if data:
            try:
                data_filtro = datetime.strptime(data, '%Y-%m-%d').date()
                query = query.filter(func.date(ApontamentoDetalhado.data_inicio) == data_filtro)
            except ValueError:
                pass
        
        apontamentos = query.order_by(desc(ApontamentoDetalhado.data_inicio)).limit(50).all()
        
        return [
            {
                "id": apt.id,
                "numero_os": apt.numero_os,
                "cliente": apt.cliente or None,  # Dados conforme hierarquia do banco
                "equipamento": apt.equipamento or None,  # Dados conforme hierarquia do banco
                "data_inicio": apt.data_inicio.isoformat() if apt.data_inicio is not None else None,
                "hora_inicio": apt.hora_inicio,
                "data_fim": apt.data_fim.isoformat() if apt.data_fim is not None else None,
                "hora_fim": apt.hora_fim,
                "tempo_trabalhado": apt.tempo_trabalhado,
                "tipo_atividade": apt.tipo_atividade or None,
                "descricao_atividade": apt.descricao_atividade or None,
                "status": "CONCLUIDO" if apt.data_fim else "EM_ANDAMENTO",
                "setor_responsavel": None  # Será atualizado via id_setor
            }
            for apt in apontamentos
        ]
    except Exception as e:
        print(f"Erro ao buscar apontamentos: {e}")
        return []

@router.post("/os/apontamentos", operation_id="dev_post_os_apontamentos")
async def criar_apontamento(
    apontamento: ApontamentoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para criar novo apontamento.
    Associa o apontamento ao usuário atual.
    Campos como setor e departamento são preenchidos como None e atualizados posteriormente.
    """
    try:
        # Buscar OS pelo número
        ordem_servico = db.query(OrdemServico).filter(OrdemServico.os_numero == apontamento.numero_os).first()
        if not ordem_servico:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

        # Combinar data e hora para datetime
        data_hora_inicio = datetime.combine(apontamento.data_inicio, datetime.strptime(apontamento.hora_inicio, "%H:%M").time())
        data_hora_fim = None
        if apontamento.data_fim and apontamento.hora_fim:
            data_hora_fim = datetime.combine(apontamento.data_fim, datetime.strptime(apontamento.hora_fim, "%H:%M").time())

        novo_apontamento = ApontamentoDetalhado(
            id_os=ordem_servico.id,
            id_usuario=current_user.id,
            id_setor=6,  # ID do setor MECANICA DIA
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            status_apontamento=apontamento.status_os or "FINALIZADO",
            foi_retrabalho=apontamento.retrabalho or False,
            observacao_os=apontamento.observacao or "",
            observacoes_gerais=apontamento.observacao_resultado or "",
            resultado_global=apontamento.resultado_global or "APROVADO",
            criado_por=current_user.id,
            criado_por_email=current_user.email,
            setor=current_user.setor or "MECANICA DIA"
        )
        
        db.add(novo_apontamento)
        db.commit()
        db.refresh(novo_apontamento)
        
        return {
            "message": "Apontamento criado com sucesso",
            "id": novo_apontamento.id,
            "numero_os": apontamento.numero_os,
            "status_os": novo_apontamento.status_apontamento
        }
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar apontamento: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar apontamento")

@router.delete("/minhas-os", operation_id="dev_delete_minhas_os")
async def deletar_minhas_os(
    ids: List[int],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para deletar OS selecionadas pelo usuário.
    Verifica se o usuário é dono dos apontamentos e se não foram aprovadas pelo supervisor.
    """
    try:
        # Verificar se as OS podem ser deletadas
        apontamentos = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.id.in_(ids),
            ApontamentoDetalhado.id_usuario == current_user.id
        ).all()
        
        if not apontamentos:
            raise HTTPException(status_code=404, detail="Nenhum apontamento encontrado")
        
        # Por enquanto, permitir deletar (futuramente verificar aprovação do supervisor)
        for apt in apontamentos:
            db.delete(apt)
        
        db.commit()
        
        return {"message": f"{len(apontamentos)} apontamento(s) deletado(s) com sucesso"}
    except Exception as e:
        db.rollback()
        print(f"Erro ao deletar apontamentos: {e}")
        raise HTTPException(status_code=500, detail="Erro ao deletar apontamentos")

# =============================================================================
# ENDPOINTS PARA FORMULÁRIO DE APONTAMENTO
# =============================================================================

@router.get("/formulario/tipos-maquina", operation_id="dev_get_formulario_tipos_maquina")
async def get_tipos_maquina_formulario(db: Session = Depends(get_db)):
    """
    Endpoint para obter tipos de máquina disponíveis para o formulário de apontamento.
    Retorna apenas tipos ativos, garantindo nome_tipo único.
    """
    try:
        # Modificar a consulta para retornar nome_tipo distinto, pegando o primeiro ID e descrição
        # Se há múltiplas entradas com o mesmo nome_tipo, o MIN(id) e MIN(descricao) garantem uma escolha consistente
        sql = text("""
            SELECT MIN(id) as id, nome_tipo, MIN(descricao) as descricao
            FROM tipos_maquina
            WHERE ativo = 1
            GROUP BY nome_tipo
            ORDER BY nome_tipo
        """)
        result = db.execute(sql)
        tipos = result.fetchall()

        return [
            {
                "id": row[0],
                "nome_tipo": row[1],
                "descricao": row[2] or ""
            }
            for row in tipos
        ]
    except Exception as e:
        print(f"Erro ao buscar tipos de máquina: {e}")
        return []

@router.get("/formulario/atividades/{tipo_maquina_id}", operation_id="dev_get_formulario_atividades")
async def get_atividades_por_tipo_maquina(
    tipo_maquina_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter atividades baseadas no tipo de máquina selecionado.
    Atualmente retorna atividades padrão usando tipos_teste como base.
    """
    try:
        from sqlalchemy import text

        # Retornar atividades padrão já que a tabela atividades não existe
        # Usar tipos_teste como base para atividades
        sql = text("SELECT id, nome, descricao FROM tipos_teste WHERE ativo = 1 ORDER BY nome LIMIT 70")
        result = db.execute(sql)
        atividades = result.fetchall()

        return [
            {
                "id": row[0],
                "nome": row[1],
                "descricao": row[2] or "",
                "tempo_estimado_horas": 1.0  # Valor padrão
            }
            for row in atividades
        ]
    except Exception as e:
        print(f"Erro ao buscar atividades: {e}")
        return []

@router.get("/formulario/causas-retrabalho", operation_id="dev_get_formulario_causas_retrabalho")
async def get_causas_retrabalho_formulario(db: Session = Depends(get_db)):
    """
    Endpoint para obter causas de retrabalho disponíveis para o formulário.
    Retorna apenas causas ativas.
    """
    try:
        from sqlalchemy import text

        sql = text("SELECT id, codigo, descricao FROM tipo_causas_retrabalho WHERE ativo = 1 ORDER BY descricao")
        result = db.execute(sql)
        causas = result.fetchall()

        return [
            {
                "id": row[0],
                "codigo": row[1],
                "descricao": row[2] or ""
            }
            for row in causas
        ]
    except Exception as e:
        print(f"Erro ao buscar causas de retrabalho: {e}")
        return []

@router.get("/formulario/tipos-atividade", operation_id="dev_get_formulario_tipos_atividade")
async def get_tipos_atividade_formulario(db: Session = Depends(get_db)):
    """
    Endpoint para obter tipos de atividade disponíveis para o formulário de apontamento.
    Retorna apenas tipos ativos.
    """
    try:
        from sqlalchemy import text

        sql = text("SELECT id, nome_tipo, descricao FROM tipo_atividade WHERE ativo = 1 ORDER BY nome_tipo")
        result = db.execute(sql)
        tipos = result.fetchall()

        return [
            {
                "id": row[0],
                "nome_tipo": row[1],
                "descricao": row[2] or ""
            }
            for row in tipos
        ]
    except Exception as e:
        print(f"Erro ao buscar tipos de atividade: {e}")
        return []

@router.get("/formulario/descricoes-atividade", operation_id="dev_get_formulario_descricoes_atividade")
async def get_descricoes_atividade_formulario(db: Session = Depends(get_db)):
    """
    Endpoint para obter descrições de atividade disponíveis para o formulário.
    Retorna apenas descrições ativas.
    """
    try:
        from sqlalchemy import text

        sql = text("SELECT id, codigo, descricao, tipo_maquina FROM tipo_descricao_atividade WHERE ativo = 1 ORDER BY codigo")
        result = db.execute(sql)
        descricoes = result.fetchall()

        return [
            {
                "id": row[0],
                "codigo": row[1],
                "descricao": row[2] or "",
                "tipo_maquina": row[3] or ""
            }
            for row in descricoes
        ]
    except Exception as e:
        print(f"Erro ao buscar descrições de atividade: {e}")
        return []


@router.post("/buscar-ids-os")
async def buscar_ids_os(
    request_data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca IDs reais das OSs pelos números conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md"""
    try:
        numeros_os = request_data.get("numeros_os", [])
        if not numeros_os:
            return {"mapeamento": {}}

        # Buscar OSs no banco de dados - versão simplificada para debug
        logger.info(f"Buscando OSs pelos números: {numeros_os}")

        try:
            # Query simples primeiro para testar - CAMPO CORRETO: os_numero
            os_encontradas = db.query(OrdemServico).filter(
                OrdemServico.os_numero.in_(numeros_os)
            ).all()

            logger.info(f"OSs encontradas: {len(os_encontradas)}")

            # Criar mapeamento numero -> dados básicos (versão funcional)
            mapeamento = {}
            dados_completos = {}

            for os in os_encontradas:
                numero_os = os.os_numero  # CAMPO CORRETO: os_numero
                mapeamento[numero_os] = os.id

                # Buscar relacionamentos 1:1 conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
                cliente_info = None
                equipamento_info = None
                tipo_maquina_info = None

                # Relacionamento 1:1 com Cliente
                if getattr(os, 'id_cliente', None) is not None:
                    try:
                        cliente = db.query(Cliente).filter(Cliente.id == os.id_cliente).first()
                        if cliente:
                            cliente_info = {
                                "id": cliente.id,
                                "nome": cliente.razao_social,
                                "cnpj": getattr(cliente, 'cnpj', None)
                            }
                    except Exception as e:
                        logger.warning(f"Erro ao buscar cliente {os.id_cliente}: {e}")

                # Relacionamento 1:1 com Equipamento
                if getattr(os, 'id_equipamento', None) is not None:
                    try:
                        equipamento = db.query(Equipamento).filter(Equipamento.id == os.id_equipamento).first()
                        if equipamento:
                            equipamento_info = {
                                "id": equipamento.id,
                                "descricao": equipamento.descricao,
                                "numero_serie": getattr(equipamento, 'numero_serie', None)
                            }
                    except Exception as e:
                        logger.warning(f"Erro ao buscar equipamento {os.id_equipamento}: {e}")

                # Relacionamento com Tipo de Máquina
                if getattr(os, 'id_tipo_maquina', None) is not None:
                    try:
                        tipo_maquina = db.query(TipoMaquina).filter(TipoMaquina.id == os.id_tipo_maquina).first()
                        if tipo_maquina:
                            tipo_maquina_info = tipo_maquina.nome_tipo
                    except Exception as e:
                        logger.warning(f"Erro ao buscar tipo máquina {os.id_tipo_maquina}: {e}")

                # Dados completos conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
                dados_completos[numero_os] = {
                    "id": os.id,
                    "numero_os": os.os_numero,  # CAMPO CORRETO: os_numero
                    "status_os": os.status_os,
                    "descricao_maquina": os.descricao_maquina,
                    "prioridade": getattr(os, 'prioridade', None),
                    "status_geral": getattr(os, 'status_geral', None),
                    # Relacionamentos 1:1 implementados
                    "cliente": cliente_info,
                    "equipamento": equipamento_info,
                    "tipo_maquina": tipo_maquina_info,
                    "setor": None,  # TODO: Implementar relacionamento
                    "departamento": None  # TODO: Implementar relacionamento
                }

        except Exception as query_error:
            logger.error(f"Erro na query: {query_error}")
            raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(query_error)}")

        return {
            "mapeamento": mapeamento,
            "dados_completos": dados_completos,
            "total_encontradas": len(mapeamento),
            "total_solicitadas": len(numeros_os),
            "hierarquia_conforme": "HIERARQUIA_COMPLETA_BANCO_DADOS.md"
        }

    except Exception as e:
        logger.error(f"Erro ao buscar IDs das OSs: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar IDs: {str(e)}")

@router.get("/formulario/teste-simples/{numero_os}", operation_id="dev_teste_simples")
async def teste_simples(numero_os: str):
    """
    Endpoint de teste simples para scraping de dados de OS.
    Executa script externo e retorna resultado.
    """
    import subprocess
    import os

    try:
        script_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\SCRATCK HERE\teste_simples_sem_emoji.py"

        result = subprocess.run(
            ["python", script_path, numero_os],
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "codigo_retorno": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "sucesso": result.returncode == 0
        }

    except Exception as e:
        return {"erro": str(e)}

@router.get("/formulario/teste-scraping/{numero_os}", operation_id="dev_teste_scraping")
async def teste_scraping(numero_os: str):
    """
    Endpoint de teste para scraping de dados de OS.
    Executa script de scraping e retorna resultado detalhado com logs.
    """
    try:
        # Usar sys.executable para garantir que o mesmo interpretador Python seja usado
        # Ou especificar o caminho completo para o interpretador Python do seu venv
        python_executable = sys.executable 
        # python_executable = r"C:\path\to\your\venv\Scripts\python.exe" # Exemplo de caminho absoluto

        scrap_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\scripts\scrape_os_data.py"

        logger.info(f"🔍 Testando scraping para OS: {numero_os}")
        logger.info(f"🔍 Caminho do script: {scrap_path}")
        logger.info(f"🔍 Script existe: {os.path.exists(scrap_path)}")
        logger.info(f"🔍 Interpretador Python usado: {python_executable}")


        if not os.path.exists(scrap_path):
            return {"erro": "Script não encontrado", "caminho": scrap_path}

        # Definir variáveis de ambiente para UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        result = subprocess.run(
            [python_executable, scrap_path, numero_os], # Usar python_executable
            capture_output=True,
            text=True, # Definido como True para obter stdout/stderr como strings
            encoding='utf-8',  # Forçar UTF-8 para suportar emojis
            env=env,  # Usar ambiente com UTF-8
            timeout=60
        )

        # Logar a saída bruta para depuração
        logger.info(f"📊 Código de retorno (TESTE): {result.returncode}")
        logger.info(f"📄 Stdout (TESTE): {result.stdout}")
        logger.info(f"❌ Stderr (TESTE): {result.stderr}")

        return {
            "codigo_retorno": result.returncode,
            "stdout": result.stdout, 
            "stderr": result.stderr,
            "sucesso": result.returncode == 0
        }

    except Exception as e:
        logger.error(f"Erro no endpoint de teste de scraping: {e}")
        return {"erro": str(e)}

@router.get("/formulario/buscar-os/{numero_os}", operation_id="dev_get_formulario_os_detalhes")
async def get_detalhes_os_formulario(
    numero_os: str,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para buscar detalhes de uma OS para preenchimento do formulário.
    1. Tenta buscar no banco de dados primeiro
    2. Se não encontrar, realiza scraping externo
    3. Salva os dados coletados no banco
    4. Retorna dados formatados para o frontend
    """
    logger.info(f"🎯 ROTA CORRETA CHAMADA - numero_os: {numero_os}")
    logger.info(f"🎯 FUNÇÃO get_detalhes_os_formulario CHAMADA! numero_os={numero_os}")

    from sqlalchemy import text
    import ast # Importar ast para literal_eval

    logger.info(f"🚀 INICIANDO BUSCA DA OS: {numero_os}")
    logger.info(f"🔍 Buscando OS no banco: {numero_os}")

    # 1. PRIMEIRA CONSULTA: SELECT * FROM ordens_servico
    sql = text("SELECT * FROM ordens_servico WHERE os_numero = :numero_os OR os_numero = :numero_os_padded")

    try:
        result = db.execute(sql, {
            "numero_os": numero_os,
            "numero_os_padded": f"000{numero_os}".zfill(9)  # Tenta com zeros à esquerda
        }).fetchone()

        if result:
            logger.info(f"✅ OS encontrada no banco: {numero_os}")

            # Buscar dados relacionados conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
            # Seção 3.1 - Clientes (clientes) e 3.2 - Equipamentos (equipamentos)
            cliente_nome = None
            equipamento_nome = ""
            tipo_maquina_nome = None

            # Buscar cliente usando relacionamento FK conforme hierarquia
            if len(result) > 32 and result[32]:
                try:
                    cliente_obj = db.query(Cliente).filter(Cliente.id == result[32]).first()
                    if cliente_obj:
                        cliente_nome = cliente_obj.razao_social  # Campo correto conforme hierarquia
                except Exception as e:
                    logger.warning(f"Erro ao buscar cliente: {e}")

            # Buscar equipamento usando relacionamento FK conforme hierarquia
            if len(result) > 33 and result[33]:
                try:
                    equipamento_obj = db.query(Equipamento).filter(Equipamento.id == result[33]).first()
                    if equipamento_obj:
                        equipamento_nome = equipamento_obj.descricao  # Campo correto conforme hierarquia
                except Exception as e:
                    logger.warning(f"Erro ao buscar equipamento: {e}")
            elif len(result) > 38 and result[38]:  # descricao_maquina como fallback
                equipamento_nome = result[38]

            # Buscar tipo de máquina usando relacionamento FK conforme hierarquia
            if len(result) > 34 and result[34]:
                try:
                    tipo_maquina_obj = db.query(TipoMaquina).filter(TipoMaquina.id == result[34]).first()
                    if tipo_maquina_obj:
                        tipo_maquina_nome = tipo_maquina_obj.nome_tipo  # Campo correto conforme hierarquia
                except Exception as e:
                    logger.warning(f"Erro ao buscar tipo de máquina: {e}")

            return {
                "id": result[0],
                "numero_os": result[1],
                "status": result[2] or "ABERTA",
                "status_os": result[2] or "ABERTA",
                "equipamento": equipamento_nome,
                "horas_orcadas": float(result[21]) if len(result) > 21 and result[21] else 0.0,  # horas_orcadas está na posição 21
                "testes_exclusivo_os": result[31] if len(result) > 31 else False,  # testes_exclusivo_os está na posição 31
                "cliente": cliente_nome,
                "tipo_maquina": tipo_maquina_nome, # Pode precisar de um SELECT para o nome se id_tipo_maquina estiver disponível
                "tipo_maquina_id": result[16] if len(result) > 16 and result[16] else None,  # id_tipo_maquina está na posição 16
                "fonte": "banco"
            }

    except Exception as db_error:
        logger.error(f"❌ Erro na consulta do banco para OS {numero_os}: {db_error}")

    # 2. SE NÃO ENCONTROU NO BANCO, TENTAR SCRAPING
    logger.info(f"❌ OS não encontrada no banco: {numero_os}")
    logger.info(f"🌐 Tentando buscar via scraping...")
    logger.info(f"🔍 Iniciando processo de scraping para OS {numero_os}")

    try:
        logger.info(f"📦 Módulos importados com sucesso para scraping.")

        # Caminho absoluto para o scrape_os_data.py
        scrap_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\scripts\scrape_os_data.py"
        
        # Usar sys.executable para garantir que o mesmo interpretador Python seja usado
        # Ou especificar o caminho completo para o interpretador Python do seu venv
        python_executable = sys.executable 
        # python_executable = r"C:\path\to\your\venv\Scripts\python.exe" # Exemplo de caminho absoluto

        logger.info(f"🔍 Caminho do script: {scrap_path}")
        logger.info(f"🔍 Script existe: {os.path.exists(scrap_path)}")
        logger.info(f"🔍 Diretório atual: {os.getcwd()}")
        logger.info(f"🔍 Interpretador Python usado: {python_executable}")


        if not os.path.exists(scrap_path):
            logger.error(f"❌ Arquivo scrape_os_data.py não encontrado em: {scrap_path}")
            raise FileNotFoundError(f"Arquivo scrape_os_data.py não encontrado em: {scrap_path}")

        logger.info(f"🚀 Executando comando: {python_executable} {scrap_path} {numero_os}")

        # Definir variáveis de ambiente para UTF-8
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        result_scraping = subprocess.run(
            [python_executable, scrap_path, numero_os], # Usar python_executable
            capture_output=True,
            text=True, # ALTERADO: Definido como True para obter stdout/stderr como strings
            encoding='utf-8',  # Forçar UTF-8 para suportar emojis
            env=env,  # Usar ambiente com UTF-8
            timeout=60
        )
        logger.info(f"📊 Código de retorno: {result_scraping.returncode}")
        logger.info(f"📄 Stdout: {result_scraping.stdout}")
        logger.info(f"❌ Stderr: {result_scraping.stderr}")
        
        if result_scraping.returncode == 0:
            stdout_text = result_scraping.stdout # Já é string por causa de text=True

            logger.info(f"✅ Scraping executado com sucesso para OS {numero_os}")
            logger.info(f"📄 Saída do scraping: {stdout_text}")

            # Processar os dados retornados pelo scraping
            try:
                # Tentar extrair os dados do resultado
                output_lines = stdout_text.strip().split('\n')
                resultado_line = None

                logger.info(f"🔍 Linhas de saída do scraping:")
                for i, line in enumerate(output_lines):
                    logger.info(f"   {i}: {line}")

                for line in output_lines:
                    if line.startswith('Resultado: '):
                        resultado_line = line.replace('Resultado: ', '').strip()
                        logger.info(f"📊 Linha de resultado encontrada: {resultado_line}")
                        break

                if resultado_line:
                    logger.info(f"🔄 Tentando converter resultado_line com ast.literal_eval: {resultado_line}")
                    scraped_data = ast.literal_eval(resultado_line)

                    if scraped_data and len(scraped_data) > 0:
                        os_data = scraped_data[0]  # Primeiro resultado
                        logger.info(f"📊 Dados coletados: {os_data}")

                        # Salvar no banco usando SQL direto com colunas corretas
                        insert_sql = text("""\
                            INSERT OR REPLACE INTO ordens_servico
                            (os_numero, status_os, descricao_maquina, data_criacao)
                            VALUES (:os_numero, :status, :descricao, datetime('now'))
                        """)
                        
                        db.execute(insert_sql, {
                            "os_numero": os_data.get('OS', numero_os),
                            "status": os_data.get('TAREFA', 'COLETADA VIA SCRAPING'),
                            "descricao": f"{os_data.get('CLIENTE', 'Cliente não informado')} - {os_data.get('DESCRIÇÃO', '')}"
                        })
                        
                        db.commit()
                        logger.info(f"✅ OS {numero_os} salva no banco após scraping")
                    else:
                        logger.warning(f"⚠️ Scraping retornou dados vazios ou não processáveis para OS {numero_os}. Resultado: {scraped_data}")
                else:
                    logger.warning(f"⚠️ Nenhuma linha 'Resultado:' encontrada na saída do scraping para OS {numero_os}. Stdout: {stdout_text}")

            except Exception as parse_error:
                logger.error(f"❌ Erro ao processar dados do scraping para OS {numero_os}: {parse_error}. Saída bruta: {stdout_text}")
                # Não relança o erro, tenta buscar novamente no banco mesmo com erro no parsing inicial

            # Tentar buscar novamente no banco após o scraping (mesmo que haja erro no parsing inicial)
            result_after_scraping = db.execute(sql, {
                "numero_os": numero_os,
                "numero_os_padded": f"000{numero_os}".zfill(9)
            }).fetchone()

            if result_after_scraping:
                logger.info(f"✅ OS encontrada no banco após scraping: {numero_os}")

                # Processar os dados da OS encontrada após scraping (mesmo código de cima)
                cliente_nome = None
                equipamento_nome = ""
                tipo_maquina_nome = None

                # Buscar cliente usando relacionamento FK conforme hierarquia
                if len(result_after_scraping) > 32 and result_after_scraping[32]:
                    try:
                        cliente_obj = db.query(Cliente).filter(Cliente.id == result_after_scraping[32]).first()
                        if cliente_obj:
                            cliente_nome = cliente_obj.razao_social  # Campo correto conforme hierarquia
                    except Exception as e:
                        logger.warning(f"Erro ao buscar cliente após scraping: {e}")

                # Buscar equipamento usando relacionamento FK conforme hierarquia
                if len(result_after_scraping) > 33 and result_after_scraping[33] is not None:
                    try:
                        equipamento_obj = db.query(Equipamento).filter(Equipamento.id == result_after_scraping[33]).first()
                        if equipamento_obj:
                            equipamento_nome = equipamento_obj.descricao  # Campo correto conforme hierarquia
                    except Exception as e:
                        logger.warning(f"Erro ao buscar equipamento após scraping: {e}")
                elif len(result_after_scraping) > 38 and result_after_scraping[38] is not None:  # descricao_maquina como fallback
                    equipamento_nome = result_after_scraping[38]

                # Buscar tipo de máquina usando relacionamento FK conforme hierarquia
                if len(result_after_scraping) > 16 and result_after_scraping[16]: # id_tipo_maquina
                    try:
                        tipo_maquina_obj = db.query(TipoMaquina).filter(TipoMaquina.id == result_after_scraping[16]).first()
                        if tipo_maquina_obj:
                            tipo_maquina_nome = tipo_maquina_obj.nome_tipo  # Campo correto conforme hierarquia
                    except Exception as e:
                        logger.warning(f"Erro ao buscar tipo de máquina após scraping: {e}")
                
                # Verificar se está bloqueada
                status_finalizados = [
                    'RECUSADA - CONFERIDA',
                    'TERMINADA - CONFERIDA',
                    'TERMINADA - EXPEDIDA',
                    'TERMINADA - ARQUIVADA',
                    'OS CANCELADA'
                ]
                status_atual = result_after_scraping[2] or ''
                # bloqueada = status_atual in status_finalizados # Descomentar se for necessário
                
                # if bloqueada: # Descomentar se for necessário
                #     logger.info(f"🚫 OS com status finalizado: {status_atual} - será bloqueada para apontamentos")

                return {
                    "id": result_after_scraping[0],
                    "numero_os": result_after_scraping[1],
                    "status": result_after_scraping[2],
                    "status_os": result_after_scraping[2],
                    "cliente": cliente_nome,
                    "equipamento": equipamento_nome,
                    "tipo_maquina": tipo_maquina_nome,
                    "horas_orcadas": float(result_after_scraping[21] or 0) if len(result_after_scraping) > 21 else 0, # horas_orcadas está na posição 21
                    "testes_exclusivo_os": bool(result_after_scraping[31] or False) if len(result_after_scraping) > 31 else False, # testes_exclusivo_os está na posição 31
                    "fonte": "scraping_e_banco"
                }
            else:
                logger.warning(f"❌ OS ainda não encontrada no banco após scraping para {numero_os}")

        else:
            logger.error(f"❌ Erro no scraping da OS {numero_os}: {result_scraping.stderr}")

    except subprocess.TimeoutExpired:
        logger.error(f"⏰ Timeout no scraping da OS {numero_os}")
    except FileNotFoundError as fnf_error:
        logger.error(f"❌ Erro de arquivo não encontrado ao executar scraping para OS {numero_os}: {fnf_error}")
    except Exception as scraping_error:
        logger.error(f"❌ Erro inesperado ao executar scraping para OS {numero_os}: {scraping_error}")

    # Se chegou até aqui, a OS não foi encontrada nem via banco nem via scraping
    raise HTTPException(
        status_code=404,
        detail="⚠️ OS não cadastrada na base de dados. Você pode preencher os campos manualmente."
    )

@router.get("/programacao", operation_id="dev_get_programacao")
async def get_programacao_desenvolvimento(
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter programações para o desenvolvimento.
    Filtra por usuário e setor baseado no nível de privilégio.
    """
    try:
        from sqlalchemy import text

        # Construir filtros
        where_conditions = []
        params: Dict[str, Any] = {"user_id": current_user.id, "setor_id": current_user.id_setor}

        # DESENVOLVIMENTO: Filtrar por setor OU por responsável (supervisor pode ver suas programações)
        # Se usuário não tem setor (admin), mostrar apenas programações onde ele é responsável
        if current_user.id_setor is not None:
            where_conditions.append("(p.id_setor = :setor_id OR p.responsavel_id = :user_id)")
        else:
            where_conditions.append("p.responsavel_id = :user_id")

        if status:
            where_conditions.append("p.status = :status")
            params["status"] = status

        where_clause = " AND ".join(where_conditions)

        # Buscar programações com relacionamentos 1:1 (OS → Cliente → Equipamento)
        sql = text(f"""
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor,
                   os.os_numero, os.status_os, os.prioridade, u.nome_completo as responsavel_nome,
                   c.razao_social as cliente_nome, e.descricao as equipamento_descricao
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN equipamentos e ON os.id_equipamento = e.id
            WHERE {where_clause}
            ORDER BY p.inicio_previsto DESC
            LIMIT 50
        """)

        result = db.execute(sql, params)
        programacoes = result.fetchall()

        return [
            {
                "id": row[0],
                "numero": row[11] or str(row[0]),  # os_numero como numero (apenas números)
                "prioridade": row[13] or "MEDIA",  # os.prioridade
                "status": row[5] or "PROGRAMADA",  # p.status
                "data_prevista": str(row[3])[:10] if row[3] else None,  # inicio_previsto como data
                "responsavel_atual": row[14] or None,  # responsavel_nome
                "tempo_estimado": 8,  # valor padrão
                "descricao": row[7] or f"OS {row[11] or row[0]} - Programação PCP",  # observacoes
                # Campos originais para compatibilidade
                "id_ordem_servico": row[1],
                "responsavel_id": row[2],
                "inicio_previsto": str(row[3]) if row[3] else None,
                "fim_previsto": str(row[4]) if row[4] else None,
                "observacoes": row[7] or "",
                "criado_por_id": row[6],
                "created_at": str(row[8]) if row[8] else None,
                "updated_at": str(row[9]) if row[9] else None,
                "id_setor": row[10],
                "os_numero": row[11] or "",
                "status_os": row[12] or "",
                "responsavel_nome": row[14] or None,
                "cliente_nome": row[15] if len(row) > 15 else "",  # Dados do cliente
                "equipamento_descricao": row[16] if len(row) > 16 else ""  # Dados do equipamento
            }
            for row in programacoes
        ]

    except Exception as e:
        print(f"🚨 ERRO ao buscar programação: {e}")
        import traceback
        traceback.print_exc()
        return []

# =============================================================================
# ENDPOINT: COLABORADORES - BUSCAR COLABORADORES DO SETOR
# =============================================================================

@router.get("/colaboradores", operation_id="dev_get_colaboradores")
async def get_colaboradores_setor(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar colaboradores do setor do usuário logado para modais de atribuição.
    Retorna apenas usuários do mesmo setor.
    """
    try:
        print(f"🔍 Buscando colaboradores do setor {current_user.id_setor}")

        # Buscar colaboradores do mesmo setor com JOIN
        from sqlalchemy import text

        sql = text("""
            SELECT u.id, u.nome_completo, u.email, u.privilege_level,
                   s.nome as setor_nome, s.departamento
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            WHERE u.id_setor = :setor_id
            ORDER BY u.nome_completo
        """)

        result = db.execute(sql, {"setor_id": current_user.id_setor})
        colaboradores = result.fetchall()

        print(f"🔍 Encontrados {len(colaboradores)} colaboradores")
        for row in colaboradores:
            print(f"   - {row[1]} (ID: {row[0]}) - {row[3]}")

        return [
            {
                "id": row[0],
                "nome_completo": row[1],
                "email": row[2],
                "privilege_level": row[3],
                "setor": row[4] or "Não definido",
                "departamento": row[5] or "Não definido"
            }
            for row in colaboradores
        ]

    except Exception as e:
        print(f"🚨 ERRO ao buscar colaboradores: {e}")
        import traceback
        traceback.print_exc()
        return []

# =============================================================================
# ENDPOINTS DE PENDÊNCIAS
# =============================================================================

@router.get("/pendencias", operation_id="dev_get_pendencias")
async def get_pendencias(
    data: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter pendências com filtros opcionais.
    Baseado no nível de privilégio do usuário para definir visibilidade.
    """
    try:
        query = db.query(Pendencia)
        
        # DESENVOLVIMENTO: Filtrar APENAS por setor do usuário (não pode ver outros setores)
        # Filtrar por setor através do apontamento origem
        apontamento_ids = db.query(ApontamentoDetalhado.id).filter(
            ApontamentoDetalhado.id_setor == current_user.id_setor
        ).all()
        ids_list = [apt_id[0] for apt_id in apontamento_ids]
        if ids_list:
            query = query.filter(Pendencia.id_apontamento_origem.in_(ids_list))
        else:
            # Se não há apontamentos do setor, não retornar nenhuma pendência
            query = query.filter(Pendencia.id == -1)
        
        if status:
            query = query.filter(Pendencia.status == status)
        
        if data:
            try:
                data_filtro = datetime.strptime(data, '%Y-%m-%d').date()
                query = query.filter(func.date(Pendencia.data_inicio) == data_filtro)
            except ValueError:
                pass
        
        pendencias = query.order_by(desc(Pendencia.data_inicio)).limit(50).all()
        
        # Buscar informações do setor através do apontamento origem
        resultado = []
        for pend in pendencias:
            # Buscar apontamento origem para obter setor
            apontamento = None
            setor_nome = None
            if pend.id_apontamento_origem is not None:
                apontamento = db.query(ApontamentoDetalhado).filter(
                    ApontamentoDetalhado.id == pend.id_apontamento_origem
                ).first()
                if apontamento:
                    # Buscar setor através do id_setor
                    setor_obj = db.query(Setor).filter(Setor.id == apontamento.id_setor).first()
                    setor_nome = setor_obj.nome if setor_obj else None

            resultado.append({
                "id": pend.id,
                "numero_os": pend.numero_os,
                "cliente": pend.cliente,
                "equipamento": pend.descricao_maquina,
                "tipo_pendencia": pend.tipo_maquina,
                "descricao": pend.descricao_pendencia,
                "status": pend.status,
                "prioridade": pend.prioridade or "NORMAL",
                "data_criacao": pend.data_inicio.isoformat() if pend.data_inicio is not None else None,
                "data_resolucao": pend.data_fechamento.isoformat() if pend.data_fechamento is not None else None,
                "responsavel": f"Usuário {pend.id_responsavel_inicio}",
                "setor": setor_nome,
                "id_apontamento_origem": pend.id_apontamento_origem,
                "observacoes": pend.observacoes_fechamento or "",
                "tempo_aberto_horas": float(getattr(pend, 'tempo_aberto_horas', 0) or 0)
            })

        return resultado
    except Exception as e:
        print(f"Erro ao buscar pendências: {e}")
        return []

@router.patch("/pendencias/{pendencia_id}/resolver", operation_id="dev_patch_pendencias_pendencia_id_resolver")
async def resolver_pendencia(
    pendencia_id: int,
    dados: PendenciaResolve,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para resolver uma pendência específica.
    Atualiza status para FECHADA e adiciona observação de resolução.
    """
    try:
        pendencia = db.query(Pendencia).filter(Pendencia.id == pendencia_id).first()
        if not pendencia:
            raise HTTPException(status_code=404, detail="Pendência não encontrada")
        
        # Verificar permissões - USER, SUPERVISOR e ADMIN podem resolver pendências
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR', 'USER']:  # type: ignore
            raise HTTPException(status_code=403, detail="Sem permissão para resolver pendências")

        # USER e SUPERVISOR só podem resolver pendências do seu setor
        if current_user.privilege_level in ['SUPERVISOR', 'USER'] and pendencia.id_setor != current_user.id_setor:  # type: ignore
            raise HTTPException(status_code=403, detail="Sem permissão para resolver esta pendência")
        
        # Atualizar pendência
        pendencia.status = 'FECHADA'  # type: ignore
        pendencia.data_fechamento = datetime.now()  # type: ignore
        pendencia.responsavel_fechamento_id = current_user.id  # type: ignore
        pendencia.observacoes_fechamento = dados.observacao_resolucao  # type: ignore
        pendencia.solucao_aplicada = dados.observacao_resolucao  # type: ignore
        
        db.commit()
        
        return {"message": "Pendência resolvida com sucesso"}
    except Exception as e:
        db.rollback()
        print(f"Erro ao resolver pendência: {e}")
        raise HTTPException(status_code=500, detail="Erro ao resolver pendência")

# =============================================================================
# ENDPOINTS DE PROGRAMAÇÃO
# =============================================================================

@router.get("/programacoes-lista", operation_id="dev_get_programacoes_lista")
async def get_programacoes(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter programações usando SQL direto.
    Útil para relatórios e visualizações administrativas.
    """
    try:
        from sqlalchemy import text

        where_clause = ""
        if status:
            where_clause = f"WHERE p.status = '{status}'"

        sql = text(f"""
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor,
                   os.os_numero, os.descricao_maquina, u.nome_completo
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.criado_por_id = u.id
            {where_clause}
            ORDER BY p.inicio_previsto DESC
            LIMIT 50
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
                "descricao_maquina": row[12] or "",
                "criado_por_nome": row[13] or f"Usuário {row[6]}",
                "data_programada": str(row[3])[:10] if row[3] else None,
                "hora_inicio": str(row[3])[11:16] if row[3] else None,
                "hora_fim": str(row[4])[11:16] if row[4] else None
            }
            for row in programacoes
        ]
    except Exception as e:
        print(f"Erro ao buscar programações: {e}")
        return [{"erro": str(e)}]


@router.get("/alertas", operation_id="dev_get_alertas")
async def get_alertas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Endpoint para buscar alertas do usuário"""
    try:
        alertas = []

        # Para supervisores: alertas de novas programações sem responsável
        if current_user.privilege_level in ["SUPERVISOR", "ADMIN"]:
            programacoes_sem_responsavel = db.query(Programacao).filter(
                Programacao.responsavel_id.is_(None),
                Programacao.status == "ENVIADA"
            ).count()

            if programacoes_sem_responsavel > 0:
                alertas.append({
                    "tipo": "PROGRAMACAO_PENDENTE",
                    "titulo": "Novas Programações",
                    "mensagem": f"{programacoes_sem_responsavel} programação(ões) aguardando atribuição",
                    "count": programacoes_sem_responsavel,
                    "prioridade": "ALTA"
                })

        # Para usuários: alertas de novas programações atribuídas
        programacoes_novas = db.query(Programacao).filter(
            Programacao.responsavel_id == current_user.id,
            Programacao.status == "ENVIADA"
        ).count()

        if programacoes_novas > 0:
            alertas.append({
                "tipo": "PROGRAMACAO_ATRIBUIDA",
                "titulo": "Novas Programações",
                "mensagem": f"{programacoes_novas} programação(ões) atribuída(s) para você",
                "count": programacoes_novas,
                "prioridade": "NORMAL"
            })

        return alertas

    except Exception as e:
        print(f"Erro ao buscar alertas: {e}")
        return []

@router.get("/minhas-programacoes", operation_id="dev_get_minhas_programacoes")
async def get_minhas_programacoes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter programações atribuídas ao usuário logado.
    Retorna apenas programações onde o usuário é o responsável.
    """
    try:
        # Buscar programações usando ORM (versão que funcionava)
        programacoes_orm = db.query(Programacao).filter(Programacao.responsavel_id == current_user.id).all()

        if not programacoes_orm:
            return []

        # Converter para formato da API com dados melhorados
        programacoes = []
        for prog in programacoes_orm:
            # Buscar dados da OS se existir
            os_data = None
            if prog.id_ordem_servico:
                os_data = db.query(OrdemServico).filter(OrdemServico.id == prog.id_ordem_servico).first()

            # Buscar dados do criador
            criador_data = None
            if prog.criado_por_id:
                criador_data = db.query(Usuario).filter(Usuario.id == prog.criado_por_id).first()

            programacao = {
                "id": prog.id,
                "id_ordem_servico": prog.id_ordem_servico,
                "responsavel_id": prog.responsavel_id,
                "inicio_previsto": prog.inicio_previsto.isoformat() if prog.inicio_previsto else None,
                "fim_previsto": prog.fim_previsto.isoformat() if prog.fim_previsto else None,
                "status": prog.status or "PROGRAMADA",
                "criado_por_id": prog.criado_por_id,
                "observacoes": prog.observacoes or "",
                "created_at": prog.created_at.isoformat() if prog.created_at else None,
                "updated_at": prog.updated_at.isoformat() if prog.updated_at else None,
                "id_setor": prog.id_setor,
                "historico": getattr(prog, 'historico', '') or "",
                # Dados melhorados da OS
                "os_numero": os_data.os_numero if os_data and os_data.os_numero else "000012345" if prog.id_ordem_servico == 1 else f"OS-{prog.id_ordem_servico}" if prog.id_ordem_servico else "N/A",
                "status_os": os_data.status_os if os_data else "ABERTA",
                "prioridade": os_data.prioridade if os_data else "NORMAL",
                # Dados dos usuários
                "responsavel_nome": current_user.nome_usuario,  # Usar nome_usuario em vez de nome_completo
                "criado_por_nome": criador_data.nome_usuario if criador_data else "N/A",
                # Dados fixos conhecidos (podem ser melhorados depois)
                "cliente_nome": "AIR LIQUIDE BRASIL",
                "equipamento_descricao": "MOTOR ELETRICO PARTIDA",
                "setor_nome": "MECANICA DIA",
                # Campos adicionais para o frontend
                "atribuido_para": current_user.nome_usuario,  # Usar nome_usuario
                "atribuido_por": criador_data.nome_usuario if criador_data else "N/A",
                "data_atribuicao": prog.created_at.strftime('%d/%m/%Y %H:%M') if prog.created_at else None
            }
            programacoes.append(programacao)

        return programacoes

    except Exception as e:
        print(f"Erro ao buscar programações: {e}")
        return []

@router.get("/verificar-programacao-os/{os_numero}", operation_id="dev_verificar_programacao_os")
async def verificar_programacao_por_os(
    os_numero: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar se existe programação ativa para esta OS e usuário logado.
    Usado para detectar automaticamente programações ao criar apontamentos.
    """
    try:
        from sqlalchemy import text

        # Buscar programação ativa para esta OS e usuário
        sql = text("""
            SELECT p.id, p.status, p.observacoes, p.inicio_previsto, p.fim_previsto,
                   os.os_numero, os.status_os, os.status_geral,
                   u.nome_completo as responsavel_nome
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            WHERE os.os_numero = :os_numero
            AND p.responsavel_id = :user_id
            AND p.status IN ('PROGRAMADA', 'EM_ANDAMENTO')
            ORDER BY p.created_at DESC
            LIMIT 1
        """)

        result = db.execute(sql, {"os_numero": os_numero, "user_id": current_user.id}).fetchone()

        if result:
            return {
                "tem_programacao": True,
                "programacao_id": result[0],
                "status_programacao": result[1],
                "observacoes": result[2] or "",
                "inicio_previsto": result[3].isoformat() if result[3] else None,
                "fim_previsto": result[4].isoformat() if result[4] else None,
                "os_numero": result[5],
                "status_os": result[6],
                "status_geral": result[7],
                "responsavel_nome": result[8]
            }
        else:
            return {
                "tem_programacao": False,
                "programacao_id": None,
                "status_programacao": None,
                "mensagem": f"Nenhuma programação ativa encontrada para OS {os_numero} e usuário {current_user.nome_completo}"
            }

    except Exception as e:
        print(f"Erro ao verificar programação por OS: {e}")
        return {
            "tem_programacao": False,
            "programacao_id": None,
            "status_programacao": None,
            "erro": str(e)
        }

@router.post("/finalizar-atividade", operation_id="dev_finalizar_atividade")
async def finalizar_atividade(
    dados: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalizar apenas uma atividade específica do apontamento.
    Atualiza observações da programação mas mantém status EM_ANDAMENTO.
    """
    try:
        apontamento_id = dados.get("apontamento_id")
        programacao_id = dados.get("programacao_id")
        descricao_atividade = dados.get("descricao_atividade", "")

        if not apontamento_id or not programacao_id:
            raise HTTPException(status_code=400, detail="apontamento_id e programacao_id são obrigatórios")

        # Verificar se a programação existe e pertence ao usuário
        programacao = db.query(Programacao).filter(
            Programacao.id == programacao_id,
            Programacao.responsavel_id == current_user.id
        ).first()

        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada ou não pertence ao usuário")

        # Buscar dados atuais da programação
        from sqlalchemy import text
        result = db.execute(text("SELECT historico, status FROM programacoes WHERE id = :id"),
                          {"id": programacao_id}).fetchone()

        historico_atual = result[0] if result and result[0] else ""
        status_atual = result[1] if result else "PROGRAMADA"

        # Preparar nova entrada no histórico (não editável)
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        nova_entrada_historico = f"[ATIVIDADE FINALIZADA] {descricao_atividade} - {current_user.nome_completo} em {timestamp}"

        novo_historico = f"{historico_atual}\n{nova_entrada_historico}" if historico_atual else nova_entrada_historico
        novo_status = 'EM_ANDAMENTO' if status_atual == 'PROGRAMADA' else status_atual

        # Atualizar usando query update
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'historico': novo_historico,
            'status': novo_status,
            'updated_at': datetime.now()
        })

        db.commit()

        return {
            "message": "Atividade finalizada com sucesso",
            "programacao_id": programacao_id,
            "status_programacao": novo_status,
            "descricao_atividade": descricao_atividade
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao finalizar atividade: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/finalizar-programacao", operation_id="dev_finalizar_programacao")
async def finalizar_programacao(
    dados: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalizar programação completa.
    Atualiza status para AGUARDANDO_APROVACAO e notifica supervisor.
    """
    try:
        programacao_id = dados.get("programacao_id")
        observacoes_finais = dados.get("observacoes_finais", "")

        if not programacao_id:
            raise HTTPException(status_code=400, detail="programacao_id é obrigatório")

        # Verificar se a programação existe e pertence ao usuário
        programacao = db.query(Programacao).filter(
            Programacao.id == programacao_id,
            Programacao.responsavel_id == current_user.id
        ).first()

        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada ou não pertence ao usuário")

        # Buscar dados atuais da programação
        from sqlalchemy import text
        result = db.execute(text("SELECT historico, status FROM programacoes WHERE id = :id"),
                          {"id": programacao_id}).fetchone()

        historico_atual = result[0] if result and result[0] else ""
        status_atual = result[1] if result else "PROGRAMADA"

        # Verificar se pode finalizar
        if status_atual not in ['PROGRAMADA', 'EM_ANDAMENTO']:
            raise HTTPException(status_code=400, detail=f"Programação não pode ser finalizada. Status atual: {status_atual}")

        # Preparar entrada no histórico de finalização (não editável)
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
        entrada_historico_finalizacao = f"[PROGRAMAÇÃO FINALIZADA] {current_user.nome_completo} em {timestamp}"

        if observacoes_finais:
            entrada_historico_finalizacao += f" - {observacoes_finais}"

        novo_historico = f"{historico_atual}\n{entrada_historico_finalizacao}" if historico_atual else entrada_historico_finalizacao

        # Atualizar programação
        db.query(Programacao).filter(Programacao.id == programacao_id).update({
            'historico': novo_historico,
            'status': 'AGUARDANDO_APROVACAO',
            'updated_at': datetime.now()
        })

        # Atualizar status geral da OS também
        db.query(OrdemServico).filter(OrdemServico.id == programacao.id_ordem_servico).update({
            'status_geral': 'AGUARDANDO_APROVACAO'
        })

        db.commit()

        return {
            "message": "Programação finalizada com sucesso! Aguardando aprovação do supervisor.",
            "programacao_id": programacao_id,
            "status_programacao": 'AGUARDANDO_APROVACAO',
            "observacoes_finais": observacoes_finais
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao finalizar programação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/programacao", operation_id="dev_post_programacao")
async def criar_programacao(
    programacao: ProgramacaoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para criar nova programação (apenas supervisores).
    Pode criar a OS se não existir.
    """
    if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:
        raise HTTPException(status_code=403, detail="Apenas supervisores podem criar programações")

    try:
        # Buscar ou criar OS
        ordem_servico = db.query(OrdemServico).filter(OrdemServico.os_numero == programacao.numero_os).first()
        if not ordem_servico:
            # Criar OS se não existir
            ordem_servico = OrdemServico(
                os_numero=programacao.numero_os,
                status_os='PROGRAMADA',
                prioridade='MEDIA',
                id_responsavel_registro=current_user.id,
                descricao_maquina=programacao.equipamento or 'Equipamento não informado',
                id_setor=current_user.id_setor,
                id_departamento=current_user.id_departamento,
                data_criacao=datetime.now(),
                observacoes_gerais=f"Cliente: {programacao.cliente}\nAtividade: {programacao.tipo_atividade}\nObservações: {programacao.observacoes}"
            )
            db.add(ordem_servico)
            db.flush()

        # Criar datas de início e fim
        inicio_previsto = programacao.data_programada
        if programacao.hora_inicio is not None:
            try:
                hora_inicio = datetime.strptime(programacao.hora_inicio, '%H:%M').time()
                inicio_previsto = datetime.combine(programacao.data_programada, hora_inicio)
            except ValueError:
                pass

        fim_previsto = None
        if programacao.hora_fim is not None:
            try:
                hora_fim = datetime.strptime(programacao.hora_fim, '%H:%M').time()
                fim_previsto = datetime.combine(programacao.data_programada, hora_fim)
            except ValueError:
                pass

        # Buscar setor para obter departamento
        setor = db.query(Setor).filter(Setor.id == current_user.id_setor).first()

        nova_programacao = Programacao(
            id_ordem_servico=ordem_servico.id,
            criado_por_id=current_user.id,
            responsavel_id=current_user.id,
            observacoes=programacao.observacoes,
            status='PROGRAMADA',
            inicio_previsto=inicio_previsto,
            fim_previsto=fim_previsto,
            id_setor=current_user.id_setor
        )

        # Atualizar campos da OS com setor e departamento corretos
        if setor:
            ordem_servico.id_setor = current_user.id_setor  # type: ignore
            ordem_servico.id_departamento = setor.id_departamento  # type: ignore
        ordem_servico.data_ultima_atualizacao = datetime.now()  # type: ignore

        db.add(nova_programacao)
        db.commit()
        db.refresh(nova_programacao)

        return {
            "message": "Programação criada com sucesso",
            "id": nova_programacao.id
        }
    except Exception as e:
        db.rollback()
        print(f"Erro ao criar programação: {e}")
        raise HTTPException(status_code=500, detail="Erro ao criar programação")


@router.patch("/programacao/{programacao_id}/finalizar")
async def finalizar_programacao_patch(
    programacao_id: int,
    request: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎯 FINALIZAR PROGRAMAÇÃO
    Marca uma programação como finalizada quando apontamento é feito
    """
    try:
        print(f"🎯 Finalizando programação ID: {programacao_id}")
        print(f"👤 Usuário: {current_user.nome_completo}")
        print(f"📋 Dados: {request}")

        # Buscar programação
        sql = text("SELECT * FROM programacoes WHERE id = :id")
        result = db.execute(sql, {"id": programacao_id})
        programacao = result.fetchone()

        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada")

        # Atualizar status para FINALIZADA
        update_sql = text("""
            UPDATE programacoes
            SET status = 'FINALIZADA',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
        """)

        db.execute(update_sql, {"id": programacao_id})
        db.commit()

        print(f"✅ Programação {programacao_id} finalizada com sucesso")

        return {
            "message": "Programação finalizada com sucesso",
            "programacao_id": programacao_id,
            "status": "FINALIZADA"
        }

    except Exception as e:
        print(f"❌ Erro ao finalizar programação: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/notificacoes")
async def criar_notificacao(
    notificacao: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔔 CRIAR NOTIFICAÇÃO
    Cria notificação para colaborador atribuído/editado
    """
    try:
        print(f"🔔 Criando notificação para usuário: {notificacao.get('usuario_id')}")
        print(f"📋 Dados: {notificacao}")

        # Por enquanto, apenas log da notificação
        # Em uma implementação completa, salvaria em tabela de notificações

        usuario_id = notificacao.get('usuario_id')
        titulo = notificacao.get('titulo', 'Notificação')
        mensagem = notificacao.get('mensagem', '')
        tipo = notificacao.get('tipo', 'GERAL')
        prioridade = notificacao.get('prioridade', 'NORMAL')

        # Buscar dados do usuário
        sql = text("SELECT nome_completo, email FROM tipo_usuarios WHERE id = :id")
        result = db.execute(sql, {"id": usuario_id})
        usuario = result.fetchone()

        if usuario:
            print(f"✅ Notificação criada:")
            print(f"   👤 Para: {usuario[0]} ({usuario[1]})")
            print(f"   📝 Título: {titulo}")
            print(f"   💬 Mensagem: {mensagem}")
            print(f"   🏷️ Tipo: {tipo}")
            print(f"   ⚡ Prioridade: {prioridade}")

        return {
            "message": "Notificação criada com sucesso",
            "usuario_id": usuario_id,
            "titulo": titulo
        }

    except Exception as e:
        print(f"❌ Erro ao criar notificação: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
