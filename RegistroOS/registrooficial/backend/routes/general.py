from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional
from datetime import datetime as dt
import sys
import os
from pathlib import Path
from pydantic import BaseModel
from app.database_models import Usuario, OrdemServico, ApontamentoDetalhado, ResultadoTeste, Pendencia, TipoTeste
from config.database_config import get_db
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "RegistroOS API"}

@router.get("/test-endpoint")
async def test_endpoint():
    return {"message": "Endpoint de teste funcionando", "timestamp": "2025-01-16 22:50"}

@router.get("/check-development-access/{sector}")
async def check_development_access(
    sector: str,
    current_user: Usuario = Depends(get_current_user)
):
    """Check if user has access to development sector"""
    try:
        # For now, allow access to all sectors for authenticated users
        # In the future, this can be enhanced with specific sector permissions
        has_access = current_user.is_approved and current_user.privilege_level in ['USER', 'SUPERVISOR', 'GESTAO', 'ADMIN', 'PCP']

        return {
            "has_access": has_access,
            "user_id": current_user.id,
            "user_privilege": current_user.privilege_level,
            "sector": sector
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking access: {str(e)}")

@router.post("/save-apontamento")
async def save_apontamento(
    apontamento_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save apontamento with test results"""
    try:
        # Validate OS exists or create if not found
        os_numero = apontamento_data.get("inpNumOS")
        if not os_numero:
            raise HTTPException(status_code=400, detail="Número da OS é obrigatório")

        ordem_servico = db.query(OrdemServico).filter(OrdemServico.os_numero == os_numero).first()
        if not ordem_servico:
            # Criar OS automaticamente se não existir
            ordem_servico = OrdemServico(
                os_numero=os_numero,
                status_os="AGUARDANDO",
                prioridade="NORMAL",
                descricao_maquina=f"OS criada automaticamente via apontamento - {apontamento_data.get('inpCliente', 'Cliente não informado')}",
                id_setor=current_user.id_setor if hasattr(current_user, 'id_setor') else 1,
                id_departamento=current_user.id_departamento if hasattr(current_user, 'id_departamento') else 1,
                criado_por=current_user.id,
                id_responsavel_registro=current_user.id,
                data_criacao=dt.now(),
                # Campos específicos da OS
                horas_orcadas=float(apontamento_data.get("horasOrcadas", 0)) if apontamento_data.get("horasOrcadas") else 0
            )
            db.add(ordem_servico)
            db.flush()  # Get the ID
        else:
            # Se OS existe, atualizar campos específicos se fornecidos
            if "horasOrcadas" in apontamento_data and apontamento_data.get("horasOrcadas"):
                ordem_servico.horas_orcadas = float(apontamento_data.get("horasOrcadas", 0))  # type: ignore

        # Create ApontamentoDetalhado
        apontamento = ApontamentoDetalhado(
            id_os=ordem_servico.id,
            id_usuario=current_user.id,
            id_setor=current_user.id_setor if hasattr(current_user, 'id_setor') else 1,
            data_hora_inicio=dt.strptime(apontamento_data["inpData"], "%Y-%m-%d") if apontamento_data.get("inpData") else dt.now(),
            data_hora_fim=dt.strptime(apontamento_data["inpDataFim"], "%Y-%m-%d") if apontamento_data.get("inpDataFim") else None,
            status_apontamento="CONCLUIDO" if apontamento_data.get("inpDataFim") else "EM_ANDAMENTO",
            foi_retrabalho=apontamento_data.get("inpRetrabalho", False),
            causa_retrabalho=apontamento_data.get("selTipoCausaRetrabalho"),
            observacao_os=apontamento_data.get("observacao"),
            observacoes_gerais=apontamento_data.get("observacao_geral"),
            resultado_global=apontamento_data.get("resultado_global"),
            criado_por=current_user.id,
            criado_por_email=current_user.email,
            setor=current_user.setor if hasattr(current_user, 'setor') else None
        )

        db.add(apontamento)
        db.flush()  # Get the ID for test results

        # Save test results if provided with validation
        testes = apontamento_data.get("testes", {})
        observacoes_testes = apontamento_data.get("observacoes_testes", {})

        for teste_id, resultado in testes.items():
            # Validação: Se teste selecionado, resultado é obrigatório
            if not resultado or resultado not in ["APROVADO", "REPROVADO", "INCONCLUSIVO"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Teste {teste_id} selecionado mas sem resultado válido definido"
                )

            observacao = observacoes_testes.get(teste_id, "")

            # Validação: Observação obrigatória para REPROVADO e INCONCLUSIVO
            if resultado in ["REPROVADO", "INCONCLUSIVO"] and not observacao.strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"Observação obrigatória para teste {teste_id} com resultado {resultado}"
                )

            resultado_teste = ResultadoTeste(
                id_apontamento=apontamento.id,
                id_teste=teste_id,
                resultado=resultado,
                observacao=observacao
            )
            db.add(resultado_teste)

        # Processar testes exclusivos selecionados
        testes_exclusivos_selecionados = apontamento_data.get("testes_exclusivos_selecionados", {})
        if testes_exclusivos_selecionados:
            import json
            from datetime import datetime

            # Buscar testes exclusivos selecionados
            testes_selecionados_ids = [int(teste_id) for teste_id, selecionado in testes_exclusivos_selecionados.items() if selecionado]

            if testes_selecionados_ids:
                # Buscar dados dos testes
                testes_dados = db.query(TipoTeste).filter(TipoTeste.id.in_(testes_selecionados_ids)).all()

                # Preparar dados JSON
                agora = datetime.now()
                testes_json = {
                    "testes": [
                        {
                            "id": teste.id,
                            "nome": teste.nome,
                            "descricao": teste.descricao_teste_exclusivo or teste.nome,
                            "usuario": f"{current_user.primeiro_nome} {current_user.sobrenome}",
                            "setor": current_user.setor,
                            "departamento": current_user.departamento,
                            "data": agora.strftime('%Y-%m-%d'),
                            "hora": agora.strftime('%H:%M:%S')
                        }
                        for teste in testes_dados
                    ]
                }

                # Salvar na coluna testes_exclusivo_os da OS
                ordem_servico.testes_exclusivo_os_os = json.dumps(testes_json, ensure_ascii=False)

        db.commit()

        return {
            "message": "Apontamento salvo com sucesso",
            "apontamento_id": apontamento.id
        }

    except Exception as e:
        db.rollback()
        print(f"[ERROR] save_apontamento - Exception: {str(e)}")
        print(f"[ERROR] save_apontamento - Exception type: {type(e).__name__}")
        import traceback
        print(f"[ERROR] save_apontamento - Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar apontamento: {str(e)}")

@router.post("/save-apontamento-with-pendencia")
async def save_apontamento_with_pendencia(
    apontamento_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save apontamento and create pendencia"""
    try:
        # Validate OS exists or create if not found
        os_numero = apontamento_data.get("inpNumOS")
        if not os_numero:
            raise HTTPException(status_code=400, detail="Número da OS é obrigatório")

        ordem_servico = db.query(OrdemServico).filter(OrdemServico.os_numero == os_numero).first()
        if not ordem_servico:
            # Criar OS automaticamente se não existir
            ordem_servico = OrdemServico(
                os_numero=os_numero,
                status_os="AGUARDANDO",
                prioridade="NORMAL",
                descricao_maquina=f"OS criada automaticamente via apontamento - {apontamento_data.get('inpCliente', 'Cliente não informado')}",
                id_setor=current_user.id_setor if hasattr(current_user, 'id_setor') else 1,
                id_departamento=current_user.id_departamento if hasattr(current_user, 'id_departamento') else 1,
                criado_por=current_user.id,
                id_responsavel_registro=current_user.id,
                data_criacao=dt.now(),
                # Campos específicos da OS
                horas_orcadas=float(apontamento_data.get("horasOrcadas", 0)) if apontamento_data.get("horasOrcadas") else 0
            )
            db.add(ordem_servico)
            db.flush()  # Para obter o ID

        # Create ApontamentoDetalhado
        apontamento = ApontamentoDetalhado(
            id_os=ordem_servico.id,
            id_usuario=current_user.id,
            id_setor=current_user.id_setor if hasattr(current_user, 'id_setor') else 1,
            data_hora_inicio=dt.strptime(apontamento_data["inpData"], "%Y-%m-%d") if apontamento_data.get("inpData") else dt.now(),
            data_hora_fim=dt.strptime(apontamento_data["inpDataFim"], "%Y-%m-%d") if apontamento_data.get("inpDataFim") else None,
            status_apontamento="PENDENTE",
            foi_retrabalho=apontamento_data.get("inpRetrabalho", False),
            causa_retrabalho=apontamento_data.get("selTipoCausaRetrabalho"),
            observacao_os=apontamento_data.get("observacao"),
            observacoes_gerais=apontamento_data.get("observacao_geral"),
            resultado_global=apontamento_data.get("resultado_global"),
            criado_por=current_user.id,
            criado_por_email=current_user.email,
            setor=current_user.setor if hasattr(current_user, 'setor') else None
        )

        db.add(apontamento)
        db.flush()  # Get the ID for test results and pendencia

        # Verificar se existe programação ativa para esta OS e usuário
        from sqlalchemy import text
        sql_programacao = text("""
            SELECT p.id, p.status, p.observacoes
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            WHERE os.os_numero = :os_numero
            AND p.responsavel_id = :user_id
            AND p.status IN ('PROGRAMADA', 'EM_ANDAMENTO')
            ORDER BY p.created_at DESC
            LIMIT 1
        """)

        programacao_result = db.execute(sql_programacao, {
            "os_numero": os_numero,
            "user_id": current_user.id
        }).fetchone()

        programacao_finalizada = False
        if programacao_result:
            programacao_id = programacao_result[0]

            # Atualizar programação para FINALIZADA
            sql_update_prog = text("""
                UPDATE programacoes
                SET status = 'FINALIZADA',
                    updated_at = CURRENT_TIMESTAMP,
                    observacoes = COALESCE(observacoes, '') || :nova_observacao,
                    historico = COALESCE(historico, '') || :nova_entrada_historico
                WHERE id = :programacao_id
            """)

            timestamp = dt.now().strftime('%d/%m/%Y %H:%M')
            nova_observacao = f"\n[FINALIZADA] Programação finalizada automaticamente via apontamento com pendência #{apontamento.id} em {timestamp} por {current_user.nome_completo}"
            nova_entrada_historico = f"\n[FINALIZADA] Status alterado para FINALIZADA por {current_user.nome_completo} em {timestamp} via apontamento com pendência #{apontamento.id}"

            db.execute(sql_update_prog, {
                "programacao_id": programacao_id,
                "nova_observacao": nova_observacao,
                "nova_entrada_historico": nova_entrada_historico
            })

            programacao_finalizada = True

        # Save test results if provided
        testes = apontamento_data.get("testes", {})
        observacoes_testes = apontamento_data.get("observacoes_testes", {})

        for teste_id, resultado in testes.items():
            observacao = observacoes_testes.get(teste_id, "")
            resultado_teste = ResultadoTeste(
                id_apontamento=apontamento.id,
                id_teste=teste_id,
                resultado=resultado,
                observacao=observacao
            )
            db.add(resultado_teste)

        # Create Pendencia
        pendencia_descricao = apontamento_data.get("pendencia_descricao", "Pendência criada a partir do apontamento")
        pendencia_prioridade = apontamento_data.get("pendencia_prioridade", "NORMAL")

        pendencia = Pendencia(
            numero_os=os_numero,
            cliente="Cliente não informado",  # Será preenchido via relacionamento depois
            tipo_maquina="Tipo não informado",  # Será preenchido via relacionamento depois
            descricao_maquina=ordem_servico.descricao_maquina or "Equipamento não informado",
            descricao_pendencia=pendencia_descricao,
            prioridade=pendencia_prioridade,
            id_responsavel_inicio=current_user.id,
            id_apontamento_origem=apontamento.id,
            status='ABERTA',
            data_inicio=dt.now()  # Campo obrigatório
        )

        db.add(pendencia)

        # Processar testes exclusivos selecionados
        testes_exclusivos_selecionados = apontamento_data.get("testes_exclusivos_selecionados", {})
        if testes_exclusivos_selecionados:
            import json
            from datetime import datetime

            # Buscar testes exclusivos selecionados
            testes_selecionados_ids = [int(teste_id) for teste_id, selecionado in testes_exclusivos_selecionados.items() if selecionado]

            if testes_selecionados_ids:
                # Buscar dados dos testes
                testes_dados = db.query(TipoTeste).filter(TipoTeste.id.in_(testes_selecionados_ids)).all()

                # Preparar dados JSON
                agora = datetime.now()
                testes_json = {
                    "testes": [
                        {
                            "id": teste.id,
                            "nome": teste.nome,
                            "descricao": teste.descricao_teste_exclusivo or teste.nome,
                            "usuario": current_user.nome_completo,
                            "setor": current_user.setor,
                            "departamento": current_user.departamento,
                            "data": agora.strftime('%Y-%m-%d'),
                            "hora": agora.strftime('%H:%M:%S')
                        }
                        for teste in testes_dados
                    ]
                }

                # Salvar na coluna testes_exclusivo_os da OS
                ordem_servico.testes_exclusivo_os_os = json.dumps(testes_json, ensure_ascii=False)

        db.commit()

        response_data = {
            "message": "Apontamento e pendência salvos com sucesso",
            "apontamento_id": apontamento.id,
            "pendencia_id": pendencia.id,
            "numero_os": os_numero
        }

        if programacao_finalizada:
            response_data["programacao_finalizada"] = True
            response_data["message"] = "Apontamento e pendência salvos, programação finalizada com sucesso"

        return response_data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar apontamento: {str(e)}")

@router.get("/pendencias")
async def listar_pendencias(
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar pendências com filtros"""
    try:
        query = db.query(Pendencia)

        # Filtros
        if status:
            query = query.filter(Pendencia.status == status)
        if prioridade:
            query = query.filter(Pendencia.prioridade == prioridade)

        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Pendencia.data_inicio.desc())

        pendencias = query.all()

        # Converter para formato de resposta
        result = []
        for pendencia in pendencias:
            result.append({
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
                "responsavel_inicio_id": pendencia.id_responsavel_inicio,
                "responsavel_fechamento_id": pendencia.id_responsavel_fechamento,
                "apontamento_origem_id": pendencia.id_apontamento_origem,
                "solucao_aplicada": pendencia.solucao_aplicada,
                "observacoes_fechamento": pendencia.observacoes_fechamento
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar pendências: {str(e)}")

@router.put("/pendencias/{pendencia_id}")
async def atualizar_pendencia(
    pendencia_id: int,
    pendencia_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualizar pendência (resolver, fechar, etc.)"""
    try:
        pendencia = db.query(Pendencia).filter(Pendencia.id == pendencia_id).first()
        if not pendencia:
            raise HTTPException(status_code=404, detail="Pendência não encontrada")

        # Atualizar campos permitidos
        if "status" in pendencia_data:
            pendencia.status = pendencia_data["status"]
        if "prioridade" in pendencia_data:
            pendencia.prioridade = pendencia_data["prioridade"]
        if "solucao_aplicada" in pendencia_data:
            pendencia.solucao_aplicada = pendencia_data["solucao_aplicada"]
        if "observacoes_fechamento" in pendencia_data:
            pendencia.observacoes_fechamento = pendencia_data["observacoes_fechamento"]

        # Se estiver fechando a pendência
        if pendencia_data.get("status") == "FECHADA":
            pendencia.data_fechamento = dt.now()  # type: ignore
            pendencia.id_responsavel_fechamento = current_user.id

        db.commit()

        return {
            "message": "Pendência atualizada com sucesso",
            "pendencia_id": pendencia.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar pendência: {str(e)}")

@router.get("/os/apontamentos/meus")
async def get_meus_apontamentos(
    data: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar apontamentos do usuário atual"""
    try:
        query = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.id_usuario == current_user.id
        )

        # Filtrar por data se fornecida
        if data:
            try:
                from datetime import datetime
                data_filtro = datetime.strptime(data, "%Y-%m-%d").date()
                query = query.filter(func.date(ApontamentoDetalhado.data_hora_inicio) == data_filtro)
            except:
                pass  # Ignorar erro de formato de data

        # Filtrar por setor se fornecido
        if setor and current_user.privilege_level in ["ADMIN", "SUPERVISOR"]:
            query = query.filter(ApontamentoDetalhado.setor == setor)

        apontamentos = query.order_by(ApontamentoDetalhado.data_hora_inicio.desc()).all()

        # Converter para formato de resposta
        result = []
        for apt in apontamentos:
            # Buscar OS manualmente
            os = db.query(OrdemServico).filter(OrdemServico.id == apt.id_os).first()
            numero_os = os.os_numero if os else "N/A"

            result.append({
                "id": apt.id,
                "numero_os": numero_os,
                "data_inicio": apt.data_hora_inicio.isoformat() if apt.data_hora_inicio is not None else None,
                "data_fim": apt.data_hora_fim.isoformat() if apt.data_hora_fim is not None else None,
                "status": apt.status_apontamento,
                "observacoes": apt.observacao_os,
                "setor": "N/A",  # Será atualizado via id_setor
                "foi_retrabalho": apt.foi_retrabalho
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar apontamentos: {str(e)}")

@router.get("/os/")
async def get_ordens_servico(
    numero: Optional[str] = None,  # Mudado de numero_os para numero
    numero_os: Optional[str] = None,  # Manter compatibilidade
    cliente: Optional[str] = None,
    status: Optional[str] = None,
    setor: Optional[str] = None,  # Adicionar filtro por setor
    page: int = 1,
    per_page: int = 50,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buscar ordens de serviço"""
    try:
        from sqlalchemy import text

        # Usar SQL direto para melhor performance e incluir dados relacionados
        where_conditions = []
        params = {}

        # FILTRO OBRIGATÓRIO: Apenas números de até 5 caracteres (ex: 20203, 12345)
        where_conditions.append("os.os_numero NOT LIKE '%-%' AND LENGTH(os.os_numero) <= 5 AND os.os_numero GLOB '[0-9]*'")

        # Aplicar filtros adicionais
        numero_filtro = numero or numero_os  # Aceitar ambos os parâmetros
        if numero_filtro:
            where_conditions.append("os.os_numero LIKE :numero")
            params['numero'] = f"%{numero_filtro}%"

        if status:
            where_conditions.append("os.status_os = :status")
            params['status'] = status

        if setor:
            # Buscar por nome do setor ou ID
            if setor.isdigit():
                where_conditions.append("os.id_setor = :setor")
                params['setor'] = int(setor)
            else:
                where_conditions.append("s.nome = :setor")
                params['setor'] = setor

        where_clause = "WHERE " + " AND ".join(where_conditions)

        # Calcular offset para paginação
        offset = (page - 1) * per_page
        params['limit'] = per_page
        params['offset'] = offset

        # Consulta para contar total de registros
        count_sql = text(f"""
            SELECT COUNT(DISTINCT os.id)
            FROM ordens_servico os
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN tipos_maquina tm ON os.id_tipo_maquina = tm.id
            LEFT JOIN tipo_setores s ON os.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON os.id_departamento = d.id
            {where_clause}
        """)

        total_count = db.execute(count_sql, params).scalar()

        # Consulta principal com paginação
        sql = text(f"""
            SELECT DISTINCT
                os.id,
                os.os_numero,
                os.status_os,
                os.prioridade,
                os.data_criacao,
                os.descricao_maquina,
                s.nome as setor_nome,
                d.nome as departamento_nome,
                c.razao_social as cliente_nome,
                tm.nome_tipo as tipo_maquina_nome
            FROM ordens_servico os
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN tipos_maquina tm ON os.id_tipo_maquina = tm.id
            LEFT JOIN tipo_setores s ON os.id_setor = s.id
            LEFT JOIN tipo_departamentos d ON os.id_departamento = d.id
            {where_clause}
            ORDER BY os.data_criacao DESC
            LIMIT :limit OFFSET :offset
        """)

        result_rows = db.execute(sql, params).fetchall()

        # Converter para formato de resposta
        result = []
        for row in result_rows:
            result.append({
                "id": row[0],
                "os_numero": row[1] or "N/A",
                "status_geral": row[2] or "N/A",  # Mudado para status_geral para compatibilidade com frontend
                "status": row[2] or "N/A",  # Manter ambos para compatibilidade
                "prioridade": row[3] or "NORMAL",
                "data_criacao": str(row[4]) if row[4] else None,
                "equipamento": row[5] or "N/A",
                "setor": row[6] or "N/A",
                "departamento": row[7] or "N/A",
                "cliente": row[8] or "N/A",
                "tipo_maquina": row[9] or "N/A",
                "data_entrada": str(row[4]) if row[4] else None,  # Alias para data_criacao
                "responsavel": "N/A"  # Campo não disponível no modelo atual
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordens de serviço: {str(e)}")

@router.get("/user-info")
async def get_user_info(current_user: Usuario = Depends(get_current_user)):
    """Retorna informações completas do usuário logado para o formulário"""
    try:
        return {
            "id": current_user.id,
            "nome_completo": current_user.nome_completo,
            "email": current_user.email,
            "matricula": current_user.matricula if hasattr(current_user, 'matricula') else None,
            "cargo": current_user.cargo if hasattr(current_user, 'cargo') else None,
            "setor": current_user.setor if hasattr(current_user, 'setor') else None,
            "departamento": current_user.departamento if hasattr(current_user, 'departamento') else None,
            "privilege_level": current_user.privilege_level if hasattr(current_user, 'privilege_level') else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter dados do usuário: {str(e)}")

# Modelo para requisição de scraping
class ScrapingRequest(BaseModel):
    numero_os: str

@router.post("/scraping/consulta-os")
async def consultar_os_scraping(
    request: ScrapingRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executa scraping para consultar dados de uma OS específica
    """
    try:
        # Validar número da OS
        numero_os = request.numero_os.strip()
        if not numero_os:
            raise HTTPException(status_code=400, detail="Número da OS é obrigatório")

        # Caminho para o script de scraping
        script_path = Path(__file__).parent.parent / "scripts" / "scrape_os_data.py"
        if not script_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Script de scraping não encontrado"
            )

        # Adicionar o caminho do script ao sys.path para importação
        scripts_dir = str(script_path.parent)
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)

        try:
            # Importar e executar a função de scraping
            from scrape_os_data import execute_scraping  # type: ignore

            print(f"🚀 Executando scraping para OS: {numero_os}")
            scraped_data = execute_scraping(numero_os)

            if scraped_data:
                return {
                    "success": True,
                    "data": scraped_data,
                    "message": f"Dados coletados com sucesso para OS {numero_os}"
                }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"Nenhum dado encontrado para OS {numero_os}"
                }

        except Exception as scraping_error:
            print(f"❌ Erro durante scraping: {scraping_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro durante execução do scraping: {str(scraping_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado: {str(e)}"
        )

@router.get("/tipos-maquina/categorias")
async def get_categorias_maquina(
    departamento: Optional[str] = None,
    setor: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna categorias únicas de tipos de máquina filtradas por departamento e setor"""
    try:
        from app.database_models import TipoMaquina

        query = db.query(TipoMaquina.categoria).distinct()

        if departamento:
            query = query.filter(TipoMaquina.departamento == departamento)

        if setor:
            query = query.filter(TipoMaquina.setor == setor)

        categorias = [row[0] for row in query.all() if row[0]]

        # Se não encontrar categorias com filtros, retornar todas
        if not categorias and (departamento or setor):
            query = db.query(TipoMaquina.categoria).distinct()
            categorias = [row[0] for row in query.all() if row[0]]

        return categorias

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar categorias: {str(e)}")

@router.get("/programacao-testes")
async def listar_programacao_testes(
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    data_inicio: Optional[str] = None,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista programações de teste com filtros"""
    try:
        from sqlalchemy import text

        # Query base
        query = """
            SELECT
                pt.id,
                pt.codigo_programacao,
                pt.titulo,
                pt.descricao,
                pt.data_inicio_programada,
                pt.hora_inicio_programada,
                pt.data_fim_programada,
                pt.hora_fim_programada,
                pt.status,
                pt.prioridade,
                pt.testes_programados,
                tm.nome_tipo as tipo_maquina,
                d.nome_tipo as departamento,
                s.nome as setor
            FROM programacao_testes pt
            LEFT JOIN tipos_maquina tm ON pt.id_tipo_maquina = tm.id
            LEFT JOIN tipo_departamentos d ON pt.id_departamento = d.id
            LEFT JOIN tipo_setores s ON pt.id_setor = s.id
            WHERE 1=1
        """

        params = {}

        if status:
            query += " AND pt.status = :status"
            params['status'] = status

        if prioridade:
            query += " AND pt.prioridade = :prioridade"
            params['prioridade'] = prioridade

        if data_inicio:
            query += " AND pt.data_inicio_programada >= :data_inicio"
            params['data_inicio'] = data_inicio

        query += " ORDER BY pt.data_inicio_programada ASC"

        result = db.execute(text(query), params).fetchall()

        programacoes = []
        for row in result:
            programacoes.append({
                "id": row[0],
                "codigo": row[1],
                "titulo": row[2],
                "descricao": row[3],
                "data_inicio": str(row[4]),
                "hora_inicio": str(row[5]),
                "data_fim": str(row[6]),
                "hora_fim": str(row[7]),
                "status": row[8],
                "prioridade": row[9],
                "testes_programados": row[10],
                "tipo_maquina": row[11],
                "departamento": row[12],
                "setor": row[13]
            })

        return programacoes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar programações: {str(e)}")

@router.put("/programacao-testes/{programacao_id}/status")
async def atualizar_status_programacao(
    programacao_id: int,
    status_data: Dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza status de uma programação"""
    try:
        from sqlalchemy import text

        # Buscar programação
        query = text("SELECT * FROM programacao_testes WHERE id = :id")
        result = db.execute(query, {"id": programacao_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Programação não encontrada")

        # Preparar dados para atualização
        update_data = {}

        # Atualizar status
        novo_status = status_data.get("status")
        if novo_status:
            update_data["status"] = novo_status

            # Se iniciando, marcar data/hora de início
            if novo_status == "EM_ANDAMENTO":
                update_data["data_inicio_real"] = dt.now()

            # Se finalizando, marcar data/hora de fim e calcular tempo
            elif novo_status == "CONCLUIDO":
                update_data["data_fim_real"] = dt.now()
                # Calcular tempo se houver data de início
                if result[19]:  # data_inicio_real
                    delta = update_data["data_fim_real"] - result[19]
                    update_data["tempo_execucao_minutos"] = int(delta.total_seconds() / 60)

        # Atualizar outros campos se fornecidos
        if "observacoes_execucao" in status_data:
            update_data["observacoes_execucao"] = status_data["observacoes_execucao"]

        if "resultado_geral" in status_data:
            update_data["resultado_geral"] = status_data["resultado_geral"]

        if "percentual_aprovacao" in status_data:
            update_data["percentual_aprovacao"] = status_data["percentual_aprovacao"]

        update_data["data_ultima_atualizacao"] = dt.now()

        # Construir query de update
        set_clauses = []
        params = {"id": programacao_id}

        for field, value in update_data.items():
            set_clauses.append(f"{field} = :{field}")
            params[field] = value

        update_query = text(f"""
            UPDATE programacao_testes
            SET {', '.join(set_clauses)}
            WHERE id = :id
        """)

        db.execute(update_query, params)
        db.commit()

        return {
            "message": "Status atualizado com sucesso",
            "programacao_id": programacao_id,
            "novo_status": novo_status
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")

@router.get("/apontamentos/{apontamento_id}/relatorio-completo")
async def get_relatorio_completo_apontamento(
    apontamento_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gera relatório completo de um apontamento"""
    try:
        # Buscar apontamento
        apontamento = db.query(ApontamentoDetalhado).filter(
            ApontamentoDetalhado.id == apontamento_id
        ).first()

        if not apontamento:
            raise HTTPException(status_code=404, detail="Apontamento não encontrado")

        # Buscar OS relacionada
        os = db.query(OrdemServico).filter(OrdemServico.id == apontamento.id_os).first()

        # Buscar resultados de testes
        resultados_testes = db.query(ResultadoTeste).filter(
            ResultadoTeste.id_apontamento == apontamento_id
        ).all()

        # Buscar dados dos testes
        testes_detalhes = []
        for resultado in resultados_testes:
            teste = db.query(TipoTeste).filter(TipoTeste.id == resultado.id_teste).first()
            if teste:
                testes_detalhes.append({
                    "id": teste.id,
                    "nome": teste.nome,
                    "tipo": teste.tipo_teste,
                    "resultado": resultado.resultado,
                    "observacao": resultado.observacao or "Sem observações"
                })

        # Montar relatório
        relatorio = {
            "apontamento": {
                "id": apontamento.id,
                "data_inicio": apontamento.data_hora_inicio.isoformat() if apontamento.data_hora_inicio is not None else None,
                "data_fim": apontamento.data_hora_fim.isoformat() if apontamento.data_hora_fim is not None else None,
                "status": apontamento.status_apontamento,
                "foi_retrabalho": apontamento.foi_retrabalho,
                "causa_retrabalho": apontamento.causa_retrabalho,
                "observacao_os": apontamento.observacao_os,
                "observacoes_gerais": apontamento.observacoes_gerais,
                "resultado_global": apontamento.resultado_global,
                "setor": apontamento.setor,
                "criado_por_email": apontamento.criado_por_email
            },
            "ordem_servico": {
                "numero": os.os_numero if os else "N/A",
                "status": os.status_os if os else "N/A",
                "descricao_maquina": os.descricao_maquina if os else "N/A",
                "prioridade": os.prioridade if os else "N/A"
            },
            "testes_realizados": testes_detalhes,
            "resumo": {
                "total_testes": len(testes_detalhes),
                "testes_aprovados": len([t for t in testes_detalhes if t["resultado"] == "APROVADO"]),
                "testes_reprovados": len([t for t in testes_detalhes if t["resultado"] == "REPROVADO"]),
                "testes_inconclusivos": len([t for t in testes_detalhes if t["resultado"] == "INCONCLUSIVO"]),
                "percentual_aprovacao": round(
                    (len([t for t in testes_detalhes if t["resultado"] == "APROVADO"]) / len(testes_detalhes) * 100)
                    if testes_detalhes else 0, 2
                )
            },
            "gerado_em": dt.now().isoformat(),
            "gerado_por": current_user.email
        }

        return relatorio

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")