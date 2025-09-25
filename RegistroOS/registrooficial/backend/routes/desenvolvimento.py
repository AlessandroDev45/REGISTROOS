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
if not logger.handlers:
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
        setores = db.query(Setor).filter(Setor.ativo == True).all()
        
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
        if current_user.privilege_level != 'ADMIN':
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
            SELECT a.*, os.os_numero, os.descricao_maquina, os.testes_exclusivo_os,
                   u.nome_completo, u.matricula
            FROM apontamentos_detalhados a
            LEFT JOIN ordens_servico os ON a.id_os = os.id
            LEFT JOIN tipo_usuarios u ON a.id_usuario = u.id
            {where_clause}
            ORDER BY a.data_hora_inicio DESC
            LIMIT 50
        """)

        result = db.execute(sql)
        apontamentos = result.fetchall()

        return [
            {
                "id": row[0],
                "numero_os": row[22] or "",
                "status_os": "EM ANDAMENTO",  # Status padrão
                "cliente": "Cliente não informado",
                "equipamento": row[23] or "",
                "tipo_maquina": "Não informado",
                "tipo_atividade": "Atividade padrão",
                "data_inicio": str(row[5])[:10] if row[5] else None,
                "hora_inicio": str(row[5])[11:16] if row[5] else None,
                "data_fim": str(row[6])[:10] if row[6] else None,
                "hora_fim": str(row[6])[11:16] if row[6] else None,
                "eh_retrabalho": bool(row[10]) if row[10] is not None else False,
                "observacao_geral": row[17] or "",
                "resultado_global": row[7] or "PENDENTE",
                "testes_exclusivo_os": row[24],
                "usuario_nome": row[25] or "",
                "matricula": row[26] or "",
                "status_apontamento": row[7] or "PENDENTE",
                "criado_por": row[18] or "",
                "setor": row[20] or ""
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
                "cliente": apt.cliente or "Cliente não informado",
                "equipamento": apt.equipamento or "Equipamento não informado",
                "data_inicio": apt.data_inicio.isoformat() if apt.data_inicio else None,
                "hora_inicio": apt.hora_inicio,
                "data_fim": apt.data_fim.isoformat() if apt.data_fim else None,
                "hora_fim": apt.hora_fim,
                "tempo_trabalhado": apt.tempo_trabalhado,
                "tipo_atividade": apt.tipo_atividade or "Não informado",
                "descricao_atividade": apt.descricao_atividade or "Não informado",
                "status": "CONCLUIDO" if apt.data_fim else "EM_ANDAMENTO",
                "setor_responsavel": "Não informado"  # Será atualizado via id_setor
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
    Campos como setor e departamento são preenchidos como "Não informado" e atualizados posteriormente.
    """
    try:
        novo_apontamento = ApontamentoDetalhado(
            numero_os=apontamento.numero_os,
            cliente=apontamento.cliente,
            equipamento=apontamento.equipamento,
            tipo_maquina=apontamento.tipo_maquina,
            tipo_atividade=apontamento.tipo_atividade,
            descricao_atividade=apontamento.descricao_atividade,
            data_inicio=apontamento.data_inicio,
            hora_inicio=apontamento.hora_inicio,
            observacao=apontamento.observacao,
            id_usuario=current_user.id,
            setor="Não informado",  # Será atualizado após criação
            departamento="Não informado",  # Será atualizado após criação
            data_criacao=datetime.now()
        )
        
        db.add(novo_apontamento)
        db.commit()
        db.refresh(novo_apontamento)
        
        return {
            "message": "Apontamento criado com sucesso",
            "id": novo_apontamento.id
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

            # Buscar dados relacionados
            cliente_nome = "Cliente não informado"
            equipamento_nome = ""
            tipo_maquina_nome = "Não informado"

            # Buscar cliente
            # Corrigido: id_cliente está na posição 32 (não 52)
            if len(result) > 32 and result[32]:
                cliente_sql = text("SELECT razao_social FROM clientes WHERE id = :id_cliente")
                cliente_result = db.execute(cliente_sql, {"id_cliente": result[32]}).fetchone()
                if cliente_result:
                    cliente_nome = cliente_result[0]

            # Buscar equipamento
            # Corrigido: id_equipamento está na posição 33 (não 53)
            if len(result) > 33 and result[33]:
                equip_sql = text("SELECT descricao FROM equipamentos WHERE id = :id_equipamento")
                equip_result = db.execute(equip_sql, {"id_equipamento": result[33]}).fetchone()
                if equip_result:
                    equipamento_nome = equip_result[0]
            elif len(result) > 38 and result[38]:  # descricao_maquina está na posição 38
                equipamento_nome = result[38]

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
                cliente_nome = "Cliente não informado"
                equipamento_nome = ""
                tipo_maquina_nome = "Não informado"

                # Buscar cliente
                # Corrigido: id_cliente está na posição 32 (não 52)
                if len(result_after_scraping) > 32 and result_after_scraping[32]:
                    cliente_sql = text("SELECT razao_social FROM clientes WHERE id = :id_cliente")
                    cliente_result = db.execute(cliente_sql, {"id_cliente": result_after_scraping[32]}).fetchone()
                    if cliente_result:
                        cliente_nome = cliente_result[0]

                # Buscar equipamento
                # Corrigido: id_equipamento está na posição 33 (não 53)
                if len(result_after_scraping) > 33 and result_after_scraping[33] is not None:
                    equip_sql = text("SELECT descricao FROM equipamentos WHERE id = :id_equipamento")
                    equipamento_result = db.execute(equip_sql, {"id_equipamento": result_after_scraping[33]}).fetchone()
                    if equipamento_result:
                        equipamento_nome = equipamento_result[0]
                elif len(result_after_scraping) > 38 and result_after_scraping[38] is not None:  # descricao_maquina está na posição 38
                    equipamento_nome = result_after_scraping[38]

                # Buscar tipo de máquina
                # Corrigido: id_tipo_maquina está na posição 16 (não 35)
                if len(result_after_scraping) > 16 and result_after_scraping[16]: # id_tipo_maquina
                    tipo_maquina_sql = text("SELECT nome_tipo FROM tipos_maquina WHERE id = :id_tipo_maquina")
                    tipo_maquina_result = db.execute(tipo_maquina_sql, {"id_tipo_maquina": result_after_scraping[16]}).fetchone()
                    if tipo_maquina_result:
                        tipo_maquina_nome = tipo_maquina_result[0]
                
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

        # Filtrar por setor do usuário ou programações que ele criou/é responsável
        where_conditions.append("(p.id_setor = :setor_id OR p.responsavel_id = :user_id OR p.criado_por_id = :user_id)")

        if status:
            where_conditions.append("p.status = :status")
            params["status"] = status

        where_clause = " AND ".join(where_conditions)

        # Buscar programações relacionadas ao usuário e setor
        sql = text(f"""
            SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                   p.fim_previsto, p.status, p.criado_por_id, p.observacoes,
                   p.created_at, p.updated_at, p.id_setor,
                   os.os_numero, os.status_os, os.prioridade, u.nome_completo as responsavel_nome
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
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
                "cliente": "Cliente não informado",
                "equipamento": "Equipamento não informado",
                "prioridade": row[13] or "MEDIA",  # os.prioridade
                "status": row[5] or "PROGRAMADA",  # p.status
                "data_prevista": str(row[3])[:10] if row[3] else None,  # inicio_previsto como data
                "responsavel_atual": row[14] or "Não informado",  # responsavel_nome
                "tempo_estimado": 8,  # valor padrão
                "descricao": row[7] or "Programação automática",  # observacoes
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
                "responsavel_nome": row[14] or "Não informado"
            }
            for row in programacoes
        ]

    except Exception as e:
        print(f"Erro ao buscar programação: {e}")
        return []

# =============================================================================
# ENDPOINTS DE PENDÊNCIAS
# =============================================================================

@router.get("/pendencias", operation_id="dev_get_pendencias")
async def get_pendencias(
    data: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    setor: Optional[str] = Query(None),
    departamento: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Endpoint para obter pendências com filtros opcionais.
    Baseado no nível de privilégio do usuário para definir visibilidade.
    """
    try:
        query = db.query(Pendencia)
        
        # Filtros baseados no privilégio usando id_apontamento_origem
        if current_user.privilege_level in ['SUPERVISOR', 'USER']:  # type: ignore
            # Filtrar por setor através do apontamento origem
            apontamento_ids = db.query(ApontamentoDetalhado.id).filter(
                ApontamentoDetalhado.id_setor == current_user.id_setor
            ).all()
            ids_list = [apt_id[0] for apt_id in apontamento_ids]
            if ids_list:
                query = query.filter(Pendencia.id_apontamento_origem.in_(ids_list))
        elif current_user.privilege_level == 'ADMIN':  # type: ignore
            # Admin pode filtrar por setor através do apontamento
            if setor:
                # Buscar id_setor pelo nome do setor
                setor_obj = db.query(Setor).filter(Setor.nome == setor).first()
                if setor_obj:
                    apontamento_ids = db.query(ApontamentoDetalhado.id).filter(
                        ApontamentoDetalhado.id_setor == setor_obj.id
                    ).all()
                    ids_list = [apt_id[0] for apt_id in apontamento_ids]
                    if ids_list:
                        query = query.filter(Pendencia.id_apontamento_origem.in_(ids_list))
        
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
            setor_nome = "Não informado"
            if pend.id_apontamento_origem is not None:
                apontamento = db.query(ApontamentoDetalhado).filter(
                    ApontamentoDetalhado.id == pend.id_apontamento_origem
                ).first()
                if apontamento:
                    # Buscar setor através do id_setor
                    setor_obj = db.query(Setor).filter(Setor.id == apontamento.id_setor).first()
                    setor_nome = setor_obj.nome if setor_obj else "Não informado"

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
        if programacao.hora_inicio:
            try:
                hora_inicio = datetime.strptime(programacao.hora_inicio, '%H:%M').time()
                inicio_previsto = datetime.combine(programacao.data_programada, hora_inicio)
            except ValueError:
                pass

        fim_previsto = None
        if programacao.hora_fim:
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
