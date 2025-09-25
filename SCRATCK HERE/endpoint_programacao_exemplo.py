
# Adicionar ao arquivo routes/general.py

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
        from datetime import datetime

        # Buscar programação
        programacao = db.query(ProgramacaoTeste).filter(ProgramacaoTeste.id == programacao_id).first()
        if not programacao:
            raise HTTPException(status_code=404, detail="Programação não encontrada")

        # Atualizar status
        novo_status = status_data.get("status")
        if novo_status:
            programacao.status = novo_status

            # Se iniciando, marcar data/hora de início
            if novo_status == "EM_ANDAMENTO":
                programacao.data_inicio_real = datetime.now()

            # Se finalizando, marcar data/hora de fim e calcular tempo
            elif novo_status == "CONCLUIDO":
                programacao.data_fim_real = datetime.now()
                if programacao.data_inicio_real:
                    delta = programacao.data_fim_real - programacao.data_inicio_real
                    programacao.tempo_execucao_minutos = int(delta.total_seconds() / 60)

        # Atualizar outros campos se fornecidos
        if "observacoes_execucao" in status_data:
            programacao.observacoes_execucao = status_data["observacoes_execucao"]

        if "resultado_geral" in status_data:
            programacao.resultado_geral = status_data["resultado_geral"]

        if "percentual_aprovacao" in status_data:
            programacao.percentual_aprovacao = status_data["percentual_aprovacao"]

        programacao.data_ultima_atualizacao = datetime.now()

        db.commit()

        return {
            "message": "Status atualizado com sucesso",
            "programacao_id": programacao.id,
            "novo_status": programacao.status
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")
