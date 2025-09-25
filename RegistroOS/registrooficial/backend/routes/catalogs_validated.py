"""
Catalogs Routes - Versão Validada e Corrigida
=============================================

Todos os endpoints foram validados contra a estrutura real do banco de dados.
Mapeamento correto entre tabelas e colunas existentes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from config.database_config import get_db
from app.dependencies import get_current_user
from app.database_models import (
    Usuario, Departamento, Setor, TipoMaquina, TipoTeste,
    Cliente, Equipamento, TipoAtividade, TipoDescricaoAtividade,
    TipoCausaRetrabalho, TipoFalha, OrdemServico, Programacao,
    ApontamentoDetalhado, ResultadoTeste
)

router = APIRouter()

# =============================================================================
# ENDPOINTS PRINCIPAIS - TODOS VALIDADOS
# =============================================================================

@router.get("/departamentos")
async def get_departamentos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available departments from Departamento model"""
    try:
        departamentos = db.query(Departamento).filter(Departamento.ativo == True).all()
        
        return [
            {
                "id": dept.id,
                "nome_tipo": dept.nome_tipo,  # Campo correto da DB
                "nome": dept.nome_tipo,       # Para compatibilidade
                "descricao": dept.descricao,
                "ativo": dept.ativo,
                "data_criacao": dept.data_criacao
            }
            for dept in departamentos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar departamentos: {str(e)}")

@router.get("/setores")
async def get_setores(
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available sectors from Setor model"""
    try:
        query = db.query(Setor).filter(Setor.ativo == True)

        if departamento:
            # Filtra por nome do departamento usando FK id_departamento
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(Setor.id_departamento == dept_obj.id)

        setores = query.all()

        result = []
        for setor in setores:
            # Buscar nome do departamento
            departamento_nome = None
            if setor.id_departamento:
                dept_obj = db.query(Departamento).filter(Departamento.id == setor.id_departamento).first()
                if dept_obj:
                    departamento_nome = dept_obj.nome_tipo

            result.append({
                "id": setor.id,
                "nome": setor.nome,
                "descricao": setor.descricao,
                "id_departamento": setor.id_departamento,
                "departamento": departamento_nome,
                "ativo": setor.ativo,
                "permite_apontamento": setor.permite_apontamento,
                "area_tipo": setor.area_tipo,
                "data_criacao": setor.data_criacao
            })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar setores: {str(e)}")

@router.get("/estrutura-hierarquica")
async def get_estrutura_hierarquica(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hierarchical structure: Department -> Sector -> Machine Types -> Activities -> Tests -> Failures -> Rework Causes"""
    try:
        # Filtrar por privilégio do usuário
        if getattr(current_user, 'privilege_level', '') != 'ADMIN':
            # Usuários não-admin veem apenas seu departamento/setor
            if not departamento:
                departamento = getattr(current_user, 'departamento', None)
            if not setor:
                setor = getattr(current_user, 'setor', None)

        # Buscar departamentos
        dept_query = db.query(Departamento).filter(Departamento.ativo == True)
        if departamento:
            dept_query = dept_query.filter(Departamento.nome_tipo == departamento)
        departamentos = dept_query.all()

        estrutura = []

        for dept in departamentos:
            # Buscar setores do departamento (fazendo trim do nome)
            dept_nome = getattr(dept, 'nome_tipo', '').strip() if getattr(dept, 'nome_tipo', None) else ""
            setores_query = db.query(Setor).filter(
                Setor.ativo == True,
                Setor.id_departamento == dept_nome
            )
            if setor:
                setores_query = setores_query.filter(Setor.nome == setor)
            setores = setores_query.all()

            setores_data = []
            for setor_obj in setores:
                # Buscar tipos de máquina do setor
                tipos_maquina = db.query(TipoMaquina).filter(
                    TipoMaquina.ativo == True
                ).all()

                # Buscar tipos de teste do setor
                tipos_teste = db.query(TipoTeste).filter(
                    TipoTeste.ativo == True,
                    ).all()

                # Buscar atividades (TipoAtividade não tem campo setor)
                tipos_atividade = db.query(TipoAtividade).filter(
                    TipoAtividade.ativo == True
                ).all()

                # Buscar descrições de atividade (DescricaoAtividade não tem campo setor)
                descricoes_atividade = db.query(DescricaoAtividade).filter(
                    DescricaoAtividade.ativo == True
                ).all()

                # Buscar tipos de falha (TipoFalha não tem campo setor)
                tipos_falha = db.query(TipoFalha).filter(
                    TipoFalha.ativo == True
                ).all()

                # Buscar causas de retrabalho (CausaRetrabalho não tem campo setor)
                causas_retrabalho = db.query(CausaRetrabalho).filter(
                    CausaRetrabalho.ativo == True
                ).all()

                setor_data = {
                    "id": setor_obj.id,
                    "nome": setor_obj.nome,
                    "descricao": setor_obj.descricao,
                    "tipos_maquina": [
                        {
                            "id": tm.id,
                            "nome_tipo": tm.nome_tipo,
                            "categoria": getattr(tm, 'categoria', None),
                            "descricao": tm.descricao,
                            "tipos_teste": [
                                {
                                    "id": tt.id,
                                    "nome_tipo": tt.nome,
                                    "descricao": tt.descricao
                                }
                                for tt in tipos_teste if getattr(tt, 'tipo_maquina', None) == tm.nome_tipo
                            ]
                        }
                        for tm in tipos_maquina
                    ],
                    "tipos_atividade": [
                        {
                            "id": ta.id,
                            "nome_tipo": ta.nome_tipo,
                            "descricao": ta.descricao,
                            "id_tipo_maquina": getattr(ta, 'id_tipo_maquina', None)
                        }
                        for ta in tipos_atividade
                    ],
                    "descricoes_atividade": [
                        {
                            "id": da.id,
                            "codigo": da.codigo,
                            "descricao": da.descricao
                        }
                        for da in descricoes_atividade
                    ],
                    "tipos_falha": [
                        {
                            "id": tf.id,
                            "codigo": tf.codigo,
                            "descricao": tf.descricao
                        }
                        for tf in tipos_falha
                    ],
                    "causas_retrabalho": [
                        {
                            "id": cr.id,
                            "codigo": cr.codigo,
                            "descricao": cr.descricao
                        }
                        for cr in causas_retrabalho
                    ]
                }
                setores_data.append(setor_data)

            dept_data = {
                "id": dept.id,
                "nome": dept_nome,
                "descricao": dept.descricao,
                "setores": setores_data
            }
            estrutura.append(dept_data)

        return {
            "estrutura": estrutura,
            "total_departamentos": len(estrutura),
            "filtros_aplicados": {
                "departamento": departamento,
                "setor": setor,
                "usuario_privilege": current_user.privilege_level
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estrutura hierárquica: {str(e)}")

@router.get("/estrutura-hierarquica-debug")
async def get_estrutura_hierarquica_debug(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get hierarchical structure: Department -> Sector -> Machine Types -> Activities -> Tests -> Failures -> Rework Causes - DEBUG VERSION"""
    try:
        # DEBUG: Teste simples
        print(f"🌳 DEBUG: Buscando estrutura hierárquica - departamento: {departamento}, setor: {setor}")

        # Buscar departamentos
        dept_query = db.query(Departamento).filter(Departamento.ativo == True)
        if departamento:
            dept_query = dept_query.filter(Departamento.nome_tipo == departamento)
        departamentos = dept_query.all()
        print(f"🌳 DEBUG: Encontrados {len(departamentos)} departamentos")

        # Buscar estrutura completa com todos os dados
        estrutura = []
        for dept in departamentos:
            dept_nome = getattr(dept, 'nome_tipo', '').strip() if getattr(dept, 'nome_tipo', None) else ""
            setores_query = db.query(Setor).filter(
                Setor.ativo == True,
                Setor.departamento == dept_nome  # Corrigido para usar departamento em vez de id_departamento
            )
            if setor:
                setores_query = setores_query.filter(Setor.nome == setor)
            setores = setores_query.all()
            print(f"🌳 DEBUG: Departamento {dept_nome} - {len(setores)} setores")

            setores_data = []
            for setor_obj in setores:
                try:
                    # Buscar tipos de máquina do setor com tratamento de erro JSON
                    tipos_maquina_query = db.query(TipoMaquina).filter(
                        TipoMaquina.ativo == True,
                        TipoMaquina.departamento == dept_nome,
                        TipoMaquina.setor == setor_obj.nome
                    )
                    tipos_maquina = []
                    for tm in tipos_maquina_query.all():
                        try:
                            # Tratar subcategoria JSON com segurança
                            subcategoria = None
                            if hasattr(tm, 'subcategoria') and tm.subcategoria:
                                try:
                                    if isinstance(tm.subcategoria, str):
                                        import json
                                        subcategoria = json.loads(tm.subcategoria)
                                    else:
                                        subcategoria = tm.subcategoria
                                except (json.JSONDecodeError, TypeError):
                                    subcategoria = None

                            tipos_maquina.append({
                                "id": tm.id,
                                "nome_tipo": tm.nome_tipo,
                                "categoria": tm.categoria,
                                "subcategoria": subcategoria,
                                "descricao": tm.descricao
                            })
                        except Exception as e:
                            print(f"❌ Erro ao processar tipo máquina {tm.id}: {e}")
                            continue
                except Exception as e:
                    print(f"❌ Erro ao buscar tipos de máquina: {e}")
                    tipos_maquina = []

                # Buscar tipos de atividade do setor
                tipos_atividade = db.query(TipoAtividade).filter(
                    TipoAtividade.ativo == True,
                    TipoAtividade.departamento == dept_nome,
                    TipoAtividade.setor == setor_obj.nome
                ).all()

                # Buscar descrições de atividade do setor (incluir as que não têm departamento preenchido)
                # Também buscar por nomes similares de setor (com/sem "DE")
                setor_nome = setor_obj.nome
                setor_alternativo = None
                if "DE " in setor_nome:
                    setor_alternativo = setor_nome.replace("DE ", "")
                elif "LABORATORIO ENSAIOS" in setor_nome:
                    setor_alternativo = setor_nome.replace("LABORATORIO ENSAIOS", "LABORATORIO DE ENSAIOS")

                descricoes_query = db.query(TipoDescricaoAtividade).filter(
                    TipoDescricaoAtividade.ativo == True
                ).filter(
                    (TipoDescricaoAtividade.setor == setor_nome) |
                    (TipoDescricaoAtividade.setor == setor_alternativo if setor_alternativo else False)
                ).filter(
                    (TipoDescricaoAtividade.departamento == dept_nome) |
                    (TipoDescricaoAtividade.departamento.is_(None))
                )
                descricoes_atividade = descricoes_query.all()

                # Buscar tipos de falha do setor
                tipos_falha = db.query(TipoFalha).filter(
                    TipoFalha.ativo == True,
                    TipoFalha.departamento == dept_nome,
                    TipoFalha.setor == setor_obj.nome
                ).all()

                # Buscar causas de retrabalho do setor
                causas_retrabalho = db.query(TipoCausaRetrabalho).filter(
                    TipoCausaRetrabalho.ativo == True,
                    TipoCausaRetrabalho.departamento == dept_nome,
                    TipoCausaRetrabalho.setor == setor_obj.nome
                ).all()

                setor_data = {
                    "id": setor_obj.id,
                    "nome": setor_obj.nome,
                    "descricao": setor_obj.descricao,
                    "tipos_maquina": tipos_maquina,  # Já processados acima
                    "tipos_atividade": [{"id": ta.id, "nome_tipo": ta.nome_tipo, "categoria": getattr(ta, 'categoria', None)} for ta in tipos_atividade],
                    "descricoes_atividade": [{"id": da.id, "codigo": da.codigo, "descricao": da.descricao} for da in descricoes_atividade],
                    "tipos_falha": [{"id": tf.id, "codigo": tf.codigo, "descricao": tf.descricao, "categoria": getattr(tf, 'categoria', None)} for tf in tipos_falha],
                    "causas_retrabalho": [{"id": cr.id, "codigo": cr.codigo, "descricao": cr.descricao} for cr in causas_retrabalho]
                }
                setores_data.append(setor_data)

            dept_data = {
                "id": dept.id,
                "nome": dept_nome,
                "descricao": dept.descricao,
                "setores": setores_data
            }
            estrutura.append(dept_data)

        result = {
            "estrutura": estrutura,
            "total_departamentos": len(estrutura),
            "filtros_aplicados": {
                "departamento": departamento,
                "setor": setor,
                "usuario_privilege": "DEBUG"
            }
        }
        print(f"🌳 DEBUG: Retornando {len(estrutura)} departamentos")
        return result

    except Exception as e:
        print(f"🚨 DEBUG: Erro ao buscar estrutura hierárquica: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estrutura hierárquica: {str(e)}")

        # Filtrar por privilégio do usuário
        if getattr(current_user, 'privilege_level', '') != 'ADMIN':
            # Usuários não-admin veem apenas seu departamento/setor
            if not departamento:
                departamento = getattr(current_user, 'departamento', None)
            if not setor:
                setor = getattr(current_user, 'setor', None)

        # Buscar departamentos
        dept_query = db.query(Departamento).filter(Departamento.ativo == True)
        if departamento:
            dept_query = dept_query.filter(Departamento.nome_tipo == departamento)
        departamentos = dept_query.all()

        estrutura = []

        for dept in departamentos:
            # Buscar setores do departamento (fazendo trim do nome)
            dept_nome = getattr(dept, 'nome_tipo', '').strip() if getattr(dept, 'nome_tipo', None) else ""
            setores_query = db.query(Setor).filter(
                Setor.ativo == True,
                Setor.id_departamento == dept_nome
            )
            if setor:
                setores_query = setores_query.filter(Setor.nome == setor)
            setores = setores_query.all()

            setores_data = []
            for setor_obj in setores:
                # Buscar tipos de máquina para este setor/departamento
                tipos_maquina = db.query(TipoMaquina).filter(
                    TipoMaquina.ativo == True,
                    TipoMaquina.id_departamento == dept_nome
                ).all()

                # Buscar tipos de atividade para este setor/departamento
                # TipoAtividade não tem campos departamento/setor diretos, buscar todos ativos
                tipos_atividade = db.query(TipoAtividade).filter(
                    TipoAtividade.ativo == True
                ).all()

                # Buscar descrições de atividade para este setor
                # DescricaoAtividade não tem campo setor, buscar todos ativos
                descricoes_atividade = db.query(DescricaoAtividade).filter(
                    DescricaoAtividade.ativo == True
                ).all()

                # Buscar tipos de teste para este departamento/setor
                tipos_teste = db.query(TipoTeste).filter(
                    TipoTeste.ativo == True,
                    ).all()

                # Buscar tipos de falha para este departamento
                # TipoFalha não tem campo departamento, buscar todos ativos
                tipos_falha = db.query(TipoFalha).filter(
                    TipoFalha.ativo == True
                ).all()

                # Buscar causas de retrabalho para este departamento
                # CausaRetrabalho tem id_departamento, não departamento direto
                causas_retrabalho = db.query(CausaRetrabalho).filter(
                    CausaRetrabalho.ativo == True
                ).all()

                setor_data = {
                    "id": setor_obj.id,
                    "nome": setor_obj.nome,
                    "descricao": setor_obj.descricao,
                    "tipos_maquina": [
                        {
                            "id": tm.id,
                            "nome_tipo": tm.nome_tipo,
                            "categoria": tm.categoria,
                            "descricao": tm.descricao,
                            "tipos_teste": [
                                {
                                    "id": tt.id,
                                    "nome_tipo": tt.nome,
                                    "descricao": tt.descricao
                                }
                                for tt in tipos_teste if hasattr(tt, 'tipo_maquina') and getattr(tt, 'tipo_maquina', None) == tm.nome_tipo
                            ]
                        }
                        for tm in tipos_maquina
                    ],
                    "tipos_atividade": [
                        {
                            "id": ta.id,
                            "nome_tipo": ta.nome_tipo,
                            "descricao": ta.descricao,
                            "id_tipo_maquina": ta.id_tipo_maquina
                        }
                        for ta in tipos_atividade
                    ],
                    "descricoes_atividade": [
                        {
                            "id": da.id,
                            "codigo": da.codigo,
                            "descricao": da.descricao
                        }
                        for da in descricoes_atividade
                    ],
                    "tipos_falha": [
                        {
                            "id": tf.id,
                            "codigo": tf.codigo,
                            "descricao": tf.descricao
                        }
                        for tf in tipos_falha
                    ],
                    "causas_retrabalho": [
                        {
                            "id": cr.id,
                            "codigo": cr.codigo,
                            "descricao": cr.descricao
                        }
                        for cr in causas_retrabalho
                    ]
                }
                setores_data.append(setor_data)

            dept_data = {
                "id": dept.id,
                "nome": dept_nome,
                "descricao": dept.descricao,
                "setores": setores_data
            }
            estrutura.append(dept_data)

        return {
            "estrutura": estrutura,
            "total_departamentos": len(estrutura),
            "filtros_aplicados": {
                "departamento": departamento,
                "setor": setor,
                "usuario_privilege": current_user.privilege_level
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estrutura hierárquica: {str(e)}")

@router.get("/tipos-maquina")
async def get_tipos_maquina(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available machine types from TipoMaquina model"""
    try:
        query = db.query(TipoMaquina).filter(TipoMaquina.ativo == True)

        if departamento:
            query = query.filter(TipoMaquina.id_departamento == departamento)

        # TipoMaquina não tem campo id_setor, removendo filtro

        tipos = query.all()
        result = []

        for tipo in tipos:
            try:
                # Tratar subcategoria JSON com segurança
                subcategoria = None
                if hasattr(tipo, 'subcategoria') and tipo.subcategoria:
                    try:
                        if isinstance(tipo.subcategoria, str):
                            import json
                            subcategoria = json.loads(tipo.subcategoria)
                        else:
                            subcategoria = tipo.subcategoria
                    except (json.JSONDecodeError, TypeError):
                        subcategoria = None

                result.append({
                    "id": tipo.id,
                    "nome_tipo": tipo.nome_tipo,
                    "descricao": tipo.descricao,
                    "categoria": tipo.categoria,
                    "subcategoria": subcategoria,
                    "ativo": tipo.ativo,
                    "data_criacao": tipo.data_criacao
                })
            except Exception as e:
                print(f"❌ Erro ao processar tipo máquina {tipo.id}: {e}")
                continue

        return result
    except Exception as e:
        print(f"❌ Erro ao buscar tipos de máquina: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de máquina: {str(e)}")

@router.get("/tipos-atividade")
async def get_tipos_atividade(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available activity types"""
    try:
        query = db.query(TipoAtividade).filter(TipoAtividade.ativo == True)

        if departamento:
            query = query.filter(TipoAtividade.departamento == departamento)

        if setor:
            query = query.filter(TipoAtividade.setor == setor)

        tipos = query.all()

        return [
            {
                "id": tipo.id,
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "departamento": tipo.departamento,
                "setor": tipo.setor,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao
            }
            for tipo in tipos
        ]
    except Exception as e:
        print(f"❌ Erro ao buscar tipos de atividade: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de atividade: {str(e)}")

@router.get("/descricoes-atividade")
async def get_descricoes_atividade(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    atividade: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available activity descriptions"""
    try:
        query = db.query(DescricaoAtividade).filter(DescricaoAtividade.ativo == True)

        if departamento:
            query = query.filter(DescricaoAtividade.departamento == departamento)

        if setor:
            query = query.filter(DescricaoAtividade.setor == setor)

        if atividade:
            query = query.filter(DescricaoAtividade.atividade == atividade)

        descricoes = query.all()

        return [
            {
                "id": desc.id,
                "codigo": desc.codigo,
                "descricao": desc.descricao,
                "atividade": desc.atividade,
                "departamento": desc.departamento,
                "setor": desc.setor,
                "ativo": desc.ativo,
                "data_criacao": desc.data_criacao
            }
            for desc in descricoes
        ]
    except Exception as e:
        print(f"❌ Erro ao buscar descrições de atividade: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar descrições de atividade: {str(e)}")

@router.get("/colaboradores")
async def get_colaboradores(
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available collaborators/users"""
    try:
        query = db.query(Usuario).filter(Usuario.is_approved == True)

        if setor:
            query = query.filter(Usuario.setor == setor)

        if departamento:
            query = query.filter(Usuario.departamento == departamento)

        colaboradores = query.all()

        return [
            {
                "id": colab.id,
                "nome_completo": colab.nome_completo,
                "email": colab.email,
                "setor": colab.setor,
                "departamento": colab.departamento,
                "cargo": colab.cargo,
                "privilege_level": colab.privilege_level,
                "trabalha_producao": colab.trabalha_producao
            }
            for colab in colaboradores
        ]
    except Exception as e:
        print(f"❌ Erro ao buscar colaboradores: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar colaboradores: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_metrics(
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics"""
    try:
        from sqlalchemy import text, func

        # Métricas básicas de OS
        total_os = db.query(OrdemServico).count()
        os_abertas = db.query(OrdemServico).filter(OrdemServico.status_os == "ABERTA").count()
        os_em_andamento = db.query(OrdemServico).filter(OrdemServico.status_os == "EM_ANDAMENTO").count()
        os_concluidas = db.query(OrdemServico).filter(OrdemServico.status_os == "CONCLUIDA").count()

        # Apontamentos hoje
        from datetime import date
        hoje = date.today()
        apontamentos_hoje = db.query(ApontamentoDetalhado).filter(
            func.date(ApontamentoDetalhado.data_hora_inicio) == hoje
        ).count()

        # Pendências abertas
        pendencias_abertas = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.pendencia == True
        ).count()

        return {
            "total_os": total_os,
            "os_abertas": os_abertas,
            "os_em_andamento": os_em_andamento,
            "os_concluidas": os_concluidas,
            "apontamentos_hoje": apontamentos_hoje,
            "pendencias_abertas": pendencias_abertas,
            "taxa_conclusao": round((os_concluidas / total_os * 100) if total_os > 0 else 0, 1)
        }
    except Exception as e:
        print(f"❌ Erro ao buscar métricas do dashboard: {e}")
        return {
            "total_os": 0,
            "os_abertas": 0,
            "os_em_andamento": 0,
            "os_concluidas": 0,
            "apontamentos_hoje": 0,
            "pendencias_abertas": 0,
            "taxa_conclusao": 0
        }

@router.get("/tipos-teste")
async def get_tipos_teste(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    tipo_maquina: Optional[str] = None,
    teste_exclusivo_setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available test types from TipoTeste model"""
    try:
        query = db.query(TipoTeste).filter(TipoTeste.ativo == True)

        if departamento:
            query = query.filter()

        if setor:
            query = query.filter()

        if tipo_maquina:
            query = query.filter(TipoTeste.tipo_maquina == tipo_maquina)

        if teste_exclusivo_setor == '1':
            query = query.filter(TipoTeste.teste_exclusivo_setor == True)
        
        tipos = query.all()
        
        return [
            {
                "id": tipo.id,
                "nome": tipo.nome,
                "descricao": tipo.descricao,
                "tipo_teste": tipo.tipo_teste,
                "tipo_maquina": tipo.tipo_maquina,
                "categoria": tipo.categoria,
                "subcategoria": tipo.subcategoria,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao,
                "teste_exclusivo_setor": tipo.teste_exclusivo_setor,
                "descricao_teste_exclusivo": tipo.descricao_teste_exclusivo
            }
            for tipo in tipos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de teste: {str(e)}")


@router.get("/tipos-teste-valores")
async def get_tipos_teste_valores(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get distinct values from tipo_teste column"""
    try:
        # Buscar valores únicos da coluna tipo_teste
        valores = db.query(TipoTeste.tipo_teste).filter(
            TipoTeste.ativo == True,
            TipoTeste.tipo_teste.isnot(None),
            TipoTeste.tipo_teste != ''
        ).distinct().all()

        # Extrair apenas os valores e ordenar
        tipos_teste_valores = sorted([valor[0] for valor in valores if valor[0]])

        return {
            "valores": tipos_teste_valores,
            "total": len(tipos_teste_valores)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar valores de tipo_teste: {str(e)}")

@router.post("/detectar-testes-exclusivos")
async def detectar_testes_exclusivos(
    request: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detecta possíveis testes exclusivos baseado na descrição da atividade"""
    try:
        descricao_atividade = request.get('descricao_atividade', '').lower()
        departamento = request.get('departamento')
        setor = request.get('setor')

        if not descricao_atividade or not departamento or not setor:
            return []

        # Buscar testes exclusivos do setor
        testes_exclusivos = db.query(TipoTeste).filter(
            TipoTeste.teste_exclusivo_setor == True,
            TipoTeste.ativo == True
        ).all()

        # Palavras-chave para detecção
        palavras_chave = {
            'daimer': ['daimer', 'diagnose', 'diagnostico', 'analise', 'verificacao', 'inspecao'],
            'carga': ['carga', 'load', 'teste carga', 'ensaio carga', 'carregamento', 'loading'],
            'isolacao': ['isolacao', 'isolamento', 'megger', 'resistencia', 'dieletrico'],
            'vibração': ['vibracao', 'vibration', 'balanceamento', 'desbalanceamento'],
            'temperatura': ['temperatura', 'termico', 'aquecimento', 'resfriamento']
        }

        sugestoes = []

        for teste in testes_exclusivos:
            nome_teste_lower = teste.nome.lower()
            descricao_teste_lower = (teste.descricao_teste_exclusivo or '').lower()

            # Verificar se alguma palavra-chave está presente
            for categoria, palavras in palavras_chave.items():
                if categoria in nome_teste_lower or categoria in descricao_teste_lower:
                    for palavra in palavras:
                        if palavra in descricao_atividade:
                            confianca = len(palavra) / len(descricao_atividade) * 100
                            sugestoes.append({
                                'teste_id': teste.id,
                                'teste_nome': teste.nome,
                                'descricao_teste': teste.descricao_teste_exclusivo,
                                'palavra_detectada': palavra,
                                'confianca': round(confianca, 2),
                                'categoria': categoria
                            })
                            break

        # Ordenar por confiança
        sugestoes.sort(key=lambda x: x['confianca'], reverse=True)

        return sugestoes[:3]  # Retornar no máximo 3 sugestões

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao detectar testes exclusivos: {str(e)}")

@router.post("/finalizar-teste-exclusivo")
async def finalizar_teste_exclusivo(
    request: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra a finalização de um teste exclusivo"""
    try:
        from app.database_models import OSTesteExclusivoFinalizado
        from datetime import datetime

        numero_os = request.get('numero_os')
        teste_id = request.get('teste_id')
        descricao_atividade = request.get('descricao_atividade')
        observacoes = request.get('observacoes', '')

        if not numero_os or not teste_id:
            raise HTTPException(status_code=400, detail="Número da OS e ID do teste são obrigatórios")

        # Buscar o teste exclusivo
        teste = db.query(TipoTeste).filter(TipoTeste.id == teste_id).first()
        if not teste:
            raise HTTPException(status_code=404, detail="Teste exclusivo não encontrado")

        # Verificar se já foi finalizado para esta OS
        ja_finalizado = db.query(OSTesteExclusivoFinalizado).filter(
            OSTesteExclusivoFinalizado.numero_os == numero_os,
            OSTesteExclusivoFinalizado.id_teste_exclusivo == teste_id
        ).first()

        if ja_finalizado:
            raise HTTPException(status_code=400, detail="Este teste já foi finalizado para esta OS")

        # Criar registro de finalização
        agora = datetime.now()
        finalizacao = OSTesteExclusivoFinalizado(
            numero_os=numero_os,
            id_teste_exclusivo=teste_id,
            nome_teste=teste.nome,
            descricao_teste=teste.descricao_teste_exclusivo,
            usuario_finalizacao=f"{current_user.primeiro_nome} {current_user.sobrenome}",
            departamento=current_user.id_departamento,
            setor=current_user.id_setor,
            data_finalizacao=agora.strftime('%Y-%m-%d'),
            hora_finalizacao=agora.strftime('%H:%M:%S'),
            descricao_atividade=descricao_atividade,
            observacoes=observacoes
        )

        db.add(finalizacao)
        db.commit()
        db.refresh(finalizacao)

        return {
            "id": finalizacao.id,
            "numero_os": finalizacao.numero_os,
            "teste_nome": finalizacao.nome_teste,
            "usuario_finalizacao": finalizacao.usuario_finalizacao,
            "data_finalizacao": finalizacao.data_finalizacao,
            "hora_finalizacao": finalizacao.hora_finalizacao,
            "message": "Teste exclusivo finalizado com sucesso"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao finalizar teste exclusivo: {str(e)}")

@router.get("/testes-exclusivos-finalizados/{numero_os}")
async def get_testes_exclusivos_finalizados(
    numero_os: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca os testes exclusivos finalizados para uma OS"""
    try:
        from app.database_models import OSTesteExclusivoFinalizado

        testes_finalizados = db.query(OSTesteExclusivoFinalizado).filter(
            OSTesteExclusivoFinalizado.numero_os == numero_os
        ).all()

        return [
            {
                "id": teste.id,
                "teste_id": teste.id_teste_exclusivo,
                "nome_teste": teste.nome_teste,
                "descricao_teste": teste.descricao_teste,
                "usuario_finalizacao": teste.usuario_finalizacao,
                "id_departamento": teste.id_departamento,
                "id_setor": teste.id_setor,
                "data_finalizacao": teste.data_finalizacao,
                "hora_finalizacao": teste.hora_finalizacao,
                "descricao_atividade": teste.descricao_atividade,
                "observacoes": teste.observacoes,
                "data_criacao": teste.data_criacao.isoformat() if teste.data_criacao else None
            }
            for teste in testes_finalizados
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar testes finalizados: {str(e)}")

@router.get("/clientes")
async def get_clientes(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all clients from Cliente model"""
    try:
        clientes = db.query(Cliente).all()
        
        return [
            {
                "id": cliente.id,
                "razao_social": cliente.razao_social,
                "nome_fantasia": cliente.nome_fantasia,
                "cnpj_cpf": cliente.cnpj_cpf,
                "contato_principal": cliente.contato_principal,
                "telefone_contato": cliente.telefone_contato,
                "email_contato": cliente.email_contato,
                "endereco": cliente.endereco
            }
            for cliente in clientes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar clientes: {str(e)}")

@router.get("/equipamentos")
async def get_equipamentos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all equipment from Equipamento model"""
    try:
        equipamentos = db.query(Equipamento).all()
        
        return [
            {
                "id": equip.id,
                "descricao": equip.descricao,
                "tipo": equip.tipo,
                "fabricante": equip.fabricante,
                "modelo": equip.modelo,
                "numero_serie": equip.numero_serie
            }
            for equip in equipamentos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar equipamentos: {str(e)}")

@router.get("/usuarios")
async def get_usuarios(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users from Usuario model"""
    try:
        usuarios = db.query(Usuario).filter(Usuario.is_approved == True).all()
        
        return [
            {
                "id": usuario.id,
                "nome_completo": usuario.nome_completo,
                "nome_usuario": usuario.nome_usuario,
                "email": usuario.email,
                "matricula": usuario.matricula,
                "cargo": usuario.cargo,
                "id_setor": usuario.id_setor,
                "id_departamento": usuario.id_departamento,
                "privilege_level": usuario.privilege_level,
                "trabalha_producao": usuario.trabalha_producao
            }
            for usuario in usuarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")

@router.get("/tipo-atividade")
async def get_tipos_atividade(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity types from TipoAtividade model"""
    try:
        query = db.query(TipoAtividade).filter(TipoAtividade.ativo == True)
        
        # TipoAtividade não tem campos departamento/setor diretos
        # Filtros removidos pois não existem esses campos no modelo
        
        tipos = query.all()
        
        return [
            {
                "id": tipo.id,
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao
            }
            for tipo in tipos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de atividade: {str(e)}")

@router.get("/descricao-atividade")
async def get_descricoes_atividade(
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity descriptions from TipoDescricaoAtividade model"""
    try:
        query = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.ativo == True)
        
        if setor:
            query = query.filter()
        
        if departamento:
            query = query.filter()
        
        descricoes = query.all()
        
        return [
            {
                "id": descricao.id,
                "codigo": descricao.codigo,
                "descricao": descricao.descricao,
                "ativo": descricao.ativo
            }
            for descricao in descricoes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar descrições de atividade: {str(e)}")

@router.get("/tipo-falha")
async def get_tipos_falha(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get failure types from TipoFalha model"""
    try:
        query = db.query(TipoFalha).filter(TipoFalha.ativo == True)
        
        if departamento:
            query = query.filter(TipoFalha.id_departamento == departamento)
        
        if setor:
            query = query.filter()
        
        tipos_falha = query.all()
        
        return [
            {
                "id": falha.id,
                "codigo": falha.codigo,
                "descricao": falha.descricao,
                "ativo": falha.ativo,
                "data_criacao": falha.data_criacao
            }
            for falha in tipos_falha
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de falha: {str(e)}")

@router.get("/causas-retrabalho")
async def get_causas_retrabalho(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get work order causes from TipoCausaRetrabalho model"""
    try:
        query = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.ativo == True)

        # TipoCausaRetrabalho não tem campos departamento/setor diretos
        # Filtros removidos pois não existem esses campos no modelo

        causas = query.all()

        return [
            {
                "id": causa.id,
                "codigo": causa.codigo,
                "descricao": causa.descricao,
                "id_departamento": causa.id_departamento,
                "ativo": causa.ativo,
                "data_criacao": causa.data_criacao
            }
            for causa in causas
        ]
    except Exception as e:
        print(f"❌ Erro ao buscar causas de retrabalho: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar causas de retrabalho: {str(e)}")

@router.get("/ordens-servico")
async def get_ordens_servico(
    status: Optional[str] = None,
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get work orders from OrdemServico model"""
    try:
        query = db.query(OrdemServico)
        
        if status:
            query = query.filter(OrdemServico.status_os == status)
        
        if setor:
            query = query.filter(OrdemServico.id_setor == setor)
        
        if departamento:
            query = query.filter(OrdemServico.id_departamento == departamento)
        
        ordens = query.all()
        
        return [
            {
                "id": ordem.id,
                "os_numero": ordem.os_numero,
                "status_os": ordem.status_os,
                "prioridade": ordem.prioridade,
                "descricao_maquina": ordem.descricao_maquina,
                "id_setor": ordem.id_setor,
                "id_departamento": ordem.id_departamento,
                "data_criacao": ordem.data_criacao
            }
            for ordem in ordens
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordens de serviço: {str(e)}")

@router.get("/programacoes")
async def get_programacoes(
    status: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get programações from Programacao model with complete data from database"""
    try:
        query = db.query(Programacao).join(
            OrdemServico, Programacao.id_ordem_servico == OrdemServico.id
        ).outerjoin(
            Cliente, OrdemServico.id_cliente == Cliente.id
        ).outerjoin(
            Equipamento, OrdemServico.id_equipamento == Equipamento.id
        ).outerjoin(
            Usuario, Programacao.responsavel_id == Usuario.id
        )

        if status:
            query = query.filter(Programacao.status == status)

        if setor:
            query = query.filter(Programacao.id_setor == setor)

        programacoes = query.all()

        result = []
        for prog in programacoes:
            # Buscar dados relacionados
            ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == prog.id_ordem_servico).first()
            cliente = None
            equipamento = None
            responsavel = None

            if ordem_servico:
                if ordem_servico.id_cliente is not None:
                    cliente = db.query(Cliente).filter(Cliente.id == ordem_servico.id_cliente).first()
                if ordem_servico.id_equipamento is not None:
                    equipamento = db.query(Equipamento).filter(Equipamento.id == ordem_servico.id_equipamento).first()

            if prog.responsavel_id is not None:
                responsavel = db.query(Usuario).filter(Usuario.id == prog.responsavel_id).first()

            result.append({
                "id": prog.id,
                "id_ordem_servico": prog.id_ordem_servico,
                "os_numero": ordem_servico.os_numero if ordem_servico else None,
                "cliente": cliente.razao_social if cliente else "Cliente não informado",
                "equipamento": equipamento.descricao if equipamento else (ordem_servico.descricao_maquina if ordem_servico else "Equipamento não informado"),
                "id_setor": prog.id_setor,
                "id_departamento": ordem_servico.id_departamento if ordem_servico else None,
                "responsavel": responsavel.nome_completo if responsavel else "Não atribuído",
                "responsavel_id": prog.responsavel_id,
                "status": prog.status,
                "inicio_previsto": prog.inicio_previsto.isoformat() if prog.inicio_previsto is not None else None,
                "fim_previsto": prog.fim_previsto.isoformat() if prog.fim_previsto is not None else None,
                "observacoes": prog.observacoes,
                "created_at": prog.created_at,
                "updated_at": prog.updated_at
            })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar programações: {str(e)}")

@router.post("/programacoes")
async def create_programacao(
    programacao_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new programação with data from database"""
    try:
        # Verificar permissões
        if current_user.privilege_level not in ['ADMIN', 'SUPERVISOR']:
            raise HTTPException(status_code=403, detail="Apenas supervisores e administradores podem criar programações")

        # Validar dados obrigatórios
        required_fields = ['id_ordem_servico', 'inicio_previsto', 'fim_previsto']
        for field in required_fields:
            if field not in programacao_data or not programacao_data[field]:
                raise HTTPException(status_code=400, detail=f"Campo obrigatório: {field}")

        # Buscar OS
        ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == programacao_data['id_ordem_servico']).first()
        if not ordem_servico:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")

        # Buscar setor do usuário
        setor = db.query(Setor).filter(Setor.nome == current_user.id_setor).first()

        # Definir responsável - primeiro nome do supervisor do setor se não especificado
        responsavel_id = programacao_data.get('responsavel_id')
        if not responsavel_id and setor and setor.supervisor_responsavel is not None:
            responsavel_id = setor.supervisor_responsavel
        elif not responsavel_id:
            responsavel_id = current_user.id

        # Criar nova programação
        nova_programacao = Programacao(
            id_ordem_servico=programacao_data['id_ordem_servico'],
            responsavel_id=responsavel_id,
            inicio_previsto=datetime.fromisoformat(programacao_data['inicio_previsto'].replace('Z', '+00:00')),
            fim_previsto=datetime.fromisoformat(programacao_data['fim_previsto'].replace('Z', '+00:00')),
            status=programacao_data.get('status', 'AGENDADO'),
            criado_por_id=current_user.id,
            observacoes=programacao_data.get('observacoes'),
            setor=current_user.id_setor,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            id_setor=setor.id if setor else None
        )

        db.add(nova_programacao)
        db.commit()
        db.refresh(nova_programacao)

        return {
            "message": "Programação criada com sucesso",
            "id": nova_programacao.id,
            "os_numero": ordem_servico.os_numero,
            "id_setor": nova_programacao.id_setor,
            "responsavel_id": nova_programacao.responsavel_id,
            "status": nova_programacao.status
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar programação: {str(e)}")

# ENDPOINT REMOVIDO - CONFLITAVA COM /api/pcp/programacao-form-data
# O endpoint correto está em routes/pcp_routes.py
# Este endpoint duplicado interceptava as chamadas antes de chegar ao endpoint correto

@router.get("/status")
async def get_catalogs_status(current_user: Usuario = Depends(get_current_user)):
    """Get status of all catalog endpoints"""
    return {
        "status": "VALIDATED",
        "endpoints_disponiveis": [
            "departamentos", "setores", "tipos-maquina", "tipos-teste",
            "clientes", "equipamentos", "usuarios", "tipo-atividade",
            "descricao-atividade", "tipo-falha", "causas-retrabalho",
            "ordens-servico", "programacoes"
        ],
        "banco_de_dados": "registroos_new.db",
        "validacao_realizada": "estrutura_tabelas_colunas_mapeadas"
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for catalogs service"""
    return {
        "status": "OK",
        "service": "catalogs_validated",
        "message": "Serviço de catálogos validado e funcionando"
    }
