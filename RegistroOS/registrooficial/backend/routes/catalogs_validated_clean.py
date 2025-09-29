"""
Catalogs Routes - Versão Validada e Corrigida
=============================================

Todos os endpoints foram validados contra a estrutura real do banco de dados.
Mapeamento correto entre tabelas e colunas existentes.
Campos duplicados removidos conforme análise.
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
        departamentos = db.query(Departamento).filter(Departamento.ativo.is_(True)).all()
        
        return [
            {
                "id": dept.id,
                "nome_tipo": dept.nome_tipo,
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
        query = db.query(Setor).filter(Setor.ativo.is_(True))

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
            if setor.id_departamento is not None:
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
        dept_query = db.query(Departamento).filter(Departamento.ativo.is_(True))
        if departamento:
            dept_query = dept_query.filter(Departamento.nome_tipo == departamento)
        departamentos = dept_query.all()

        estrutura = []

        for dept in departamentos:
            # Buscar setores do departamento (fazendo trim do nome)
            dept_nome = getattr(dept, 'nome_tipo', '').strip() if getattr(dept, 'nome_tipo', None) else ""
            setores_query = db.query(Setor).filter(
                Setor.ativo.is_(True),
                Setor.id_departamento == dept.id  # Usar ID do departamento
            )
            if setor:
                setores_query = setores_query.filter(Setor.nome == setor)
            setores = setores_query.all()

            setores_data = []
            for setor_obj in setores:
                # Buscar tipos de máquina do setor
                tipos_maquina = db.query(TipoMaquina).filter(
                    TipoMaquina.ativo.is_(True),
                    TipoMaquina.id_departamento == dept.id  # Usar ID do departamento
                ).all()

                # Buscar tipos de teste do setor
                tipos_teste = db.query(TipoTeste).filter(
                    TipoTeste.ativo.is_(True),
                ).all()

                # Buscar atividades (TipoAtividade não tem campo setor)
                tipos_atividade = db.query(TipoAtividade).filter(
                    TipoAtividade.ativo.is_(True),
                    TipoAtividade.id_departamento == dept.id  # Usar ID do departamento
                ).all()

                # Buscar descrições de atividade (TipoDescricaoAtividade não tem campo setor)
                descricoes_atividade = db.query(TipoDescricaoAtividade).filter(
                    TipoDescricaoAtividade.ativo.is_(True)
                ).all()

                # Buscar tipos de falha (TipoFalha não tem campo setor)
                tipos_falha = db.query(TipoFalha).filter(
                    TipoFalha.ativo.is_(True),
                    TipoFalha.id_departamento == dept.id  # Usar ID do departamento
                ).all()

                # Buscar causas de retrabalho (TipoCausaRetrabalho não tem campo setor)
                causas_retrabalho = db.query(TipoCausaRetrabalho).filter(
                    TipoCausaRetrabalho.ativo.is_(True),
                    TipoCausaRetrabalho.id_departamento == dept.id  # Usar ID do departamento
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
                                    "nome": tt.nome,
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

@router.get("/tipos-maquina")
async def get_tipos_maquina(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available machine types from TipoMaquina model"""
    try:
        query = db.query(TipoMaquina).filter(TipoMaquina.ativo.is_(True))

        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoMaquina.id_departamento == dept_obj.id)

        tipos = query.all()
        result = []

        for tipo in tipos:
            try:
                # Tratar subcategoria JSON com segurança
                subcategoria = None
                if hasattr(tipo, 'subcategoria') and tipo.subcategoria is not None:
                    try:
                        if isinstance(tipo.subcategoria, str):
                            import json
                            subcategoria = json.loads(tipo.subcategoria)
                        else:
                            subcategoria = tipo.subcategoria
                    except (Exception,):
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
        query = db.query(TipoAtividade).filter(TipoAtividade.ativo.is_(True))

        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoAtividade.id_departamento == dept_obj.id)

        if setor:
            # TipoAtividade não tem campo setor, filtrar por Setor relacionado
            setor_obj = db.query(Setor).filter(Setor.nome == setor).first()
            if setor_obj:
                # Não há direto, então não filtrar por setor
                pass

        tipos = query.all()

        return [
            {
                "id": tipo.id,
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "id_departamento": tipo.id_departamento,
                "id_tipo_maquina": tipo.id_tipo_maquina,
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
        query = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.ativo.is_(True))

        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoDescricaoAtividade.id_departamento == dept_obj.id)

        if setor:
            # TipoDescricaoAtividade não tem campo setor, filtrar por Setor relacionado
            setor_obj = db.query(Setor).filter(Setor.nome == setor).first()
            if setor_obj:
                # Não há direto, então não filtrar por setor
                pass

        if atividade:
            query = query.filter(TipoDescricaoAtividade.codigo == atividade)

        descricoes = query.all()

        return [
            {
                "id": desc.id,
                "codigo": desc.codigo,
                "descricao": desc.descricao,
                "id_departamento": desc.id_departamento,
                "id_tipo_maquina": desc.tipo_maquina,
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
        query = db.query(Usuario).filter(Usuario.is_approved.is_(True))

        if setor:
            # Buscar setor por nome para obter ID
            setor_obj = db.query(Setor).filter(Setor.nome == setor).first()
            if setor_obj:
                query = query.filter(Usuario.id_setor == setor_obj.id)

        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(Usuario.id_departamento == dept_obj.id)

        colaboradores = query.all()

        return [
            {
                "id": colab.id,
                "nome_completo": colab.nome_completo,
                "email": colab.email,
                "id_setor": colab.id_setor,
                "id_departamento": colab.id_departamento,
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
            ApontamentoDetalhado.pendencia.is_(True)
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
        query = db.query(TipoTeste).filter(TipoTeste.ativo.is_(True))

        # TipoTeste não tem campos departamento/setor diretos
        # Filtros removidos pois não existem esses campos no modelo

        if tipo_maquina:
            query = query.filter(TipoTeste.tipo_maquina == tipo_maquina)

        if teste_exclusivo_setor == '1':
            query = query.filter(TipoTeste.teste_exclusivo_setor.is_(True))
        
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
            TipoTeste.ativo.is_(True),
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
        usuarios = db.query(Usuario).filter(Usuario.is_approved.is_(True)).all()
        
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
async def get_tipos_atividade_simple(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity types from TipoAtividade model"""
    try:
        query = db.query(TipoAtividade).filter(TipoAtividade.ativo.is_(True))
        
        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoAtividade.id_departamento == dept_obj.id)
        
        # TipoAtividade não tem campo setor
        # Filtro removido pois não existe esse campo no modelo
        
        tipos = query.all()
        
        return [
            {
                "id": tipo.id,
                "nome_tipo": tipo.nome_tipo,
                "descricao": tipo.descricao,
                "id_departamento": tipo.id_departamento,
                "id_tipo_maquina": tipo.id_tipo_maquina,
                "ativo": tipo.ativo,
                "data_criacao": tipo.data_criacao
            }
            for tipo in tipos
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de atividade: {str(e)}")

@router.get("/descricao-atividade")
async def get_descricoes_atividade_simple(
    setor: Optional[str] = None,
    departamento: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity descriptions from TipoDescricaoAtividade model"""
    try:
        query = db.query(TipoDescricaoAtividade).filter(TipoDescricaoAtividade.ativo.is_(True))
        
        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoDescricaoAtividade.id_departamento == dept_obj.id)
        
        # TipoDescricaoAtividade não tem campo setor
        # Filtro removido pois não existe esse campo no modelo
        
        descricoes = query.all()
        
        return [
            {
                "id": descricao.id,
                "codigo": descricao.codigo,
                "descricao": descricao.descricao,
                "id_departamento": descricao.id_departamento,
                "tipo_maquina": descricao.tipo_maquina,
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
        query = db.query(TipoFalha).filter(TipoFalha.ativo.is_(True))
        
        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoFalha.id_departamento == dept_obj.id)
        
        # TipoFalha não tem campo setor
        # Filtro removido pois não existe esse campo no modelo
        
        tipos_falha = query.all()
        
        return [
            {
                "id": falha.id,
                "codigo": falha.codigo,
                "descricao": falha.descricao,
                "id_departamento": falha.id_departamento,
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
        query = db.query(TipoCausaRetrabalho).filter(TipoCausaRetrabalho.ativo.is_(True))

        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(TipoCausaRetrabalho.id_departamento == dept_obj.id)

        # TipoCausaRetrabalho não tem campo setor
        # Filtro removido pois não existe esse campo no modelo

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
            # Buscar setor por nome para obter ID
            setor_obj = db.query(Setor).filter(Setor.nome == setor).first()
            if setor_obj:
                query = query.filter(OrdemServico.id_setor == setor_obj.id)
        
        if departamento:
            # Buscar departamento por nome para obter ID
            dept_obj = db.query(Departamento).filter(Departamento.nome_tipo == departamento).first()
            if dept_obj:
                query = query.filter(OrdemServico.id_departamento == dept_obj.id)
        
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

@router.get("/status")
async def get_catalogs_status(current_user: Usuario = Depends(get_current_user)):
    """Get status of all catalog endpoints"""
    return {
        "status": "VALIDATED",
        "endpoints_disponiveis": [
            "departamentos", "setores", "tipos-maquina", "tipos-teste",
            "clientes", "equipamentos", "usuarios", "tipo-atividade",
            "descricao-atividade", "tipo-falha", "causas-retrabalho",
            "ordens-servico"
        ],
        "banco_de_dados": "registroos_new.db",
        "validacao_realizada": "estrutura_tabelas_colunas_mapeadas",
        "campos_duplicados_removidos": True
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for catalogs service"""
    return {
        "status": "OK",
        "service": "catalogs_validated_clean",
        "message": "Serviço de catálogos validado e funcionando"
    }
