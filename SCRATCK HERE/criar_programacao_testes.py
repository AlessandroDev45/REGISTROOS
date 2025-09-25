#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Programação de Testes para o Departamento TESTE
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Date, Time
from config.database_config import engine, Base
from app.database_models import Departamento, Setor, TipoMaquina, TipoTeste, Usuario

# Modelo para Programação de Testes
class ProgramacaoTeste(Base):
    __tablename__ = "programacao_testes"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    codigo_programacao = Column(String, nullable=False, unique=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    
    # Relacionamentos
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))
    id_setor = Column(Integer, ForeignKey("tipo_setores.id"))
    id_tipo_maquina = Column(Integer, ForeignKey("tipos_maquina.id"))
    
    # Datas e horários
    data_inicio_programada = Column(Date, nullable=False)
    hora_inicio_programada = Column(Time, nullable=False)
    data_fim_programada = Column(Date)
    hora_fim_programada = Column(Time)
    
    # Status e controle
    status = Column(String, default="PROGRAMADO")  # PROGRAMADO, EM_ANDAMENTO, CONCLUIDO, CANCELADO
    prioridade = Column(String, default="NORMAL")  # BAIXA, NORMAL, ALTA, URGENTE
    
    # Responsáveis (sem FK para evitar problemas)
    id_responsavel_programacao = Column(Integer)
    id_responsavel_execucao = Column(Integer)

    # Testes programados (JSON)
    testes_programados = Column(Text)  # JSON com lista de testes

    # Observações
    observacoes_programacao = Column(Text)
    observacoes_execucao = Column(Text)

    # Controle de criação/atualização
    criado_por = Column(Integer)
    data_criacao = Column(DateTime, default=datetime.now)
    data_ultima_atualizacao = Column(DateTime, default=datetime.now)
    
    # Campos de execução
    data_inicio_real = Column(DateTime)
    data_fim_real = Column(DateTime)
    tempo_execucao_minutos = Column(Integer)
    
    # Resultados
    resultado_geral = Column(String)  # APROVADO, REPROVADO, INCONCLUSIVO
    percentual_aprovacao = Column(Integer)  # 0-100

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def criar_tabela_programacao():
    """Cria a tabela de programação de testes"""
    print("🗄️ Criando tabela de programação de testes...")

    try:
        # Dropar tabela se existir (para recriar sem FK problems)
        ProgramacaoTeste.__table__.drop(engine, checkfirst=True)
        print("   🗑️ Tabela anterior removida")

        # Criar a tabela
        ProgramacaoTeste.__table__.create(engine, checkfirst=True)
        print("   ✅ Tabela 'programacao_testes' criada com sucesso")
        return True
    except Exception as e:
        print(f"   ⚠️ Erro ao criar tabela: {e}")
        return False

def obter_dados_departamento_teste():
    """Obtém dados do departamento TESTE para usar na programação"""
    print("📊 Obtendo dados do departamento TESTE...")
    
    # Buscar departamento
    departamento = session.query(Departamento).filter_by(nome_tipo="TESTE").first()
    if not departamento:
        print("   ❌ Departamento TESTE não encontrado")
        return None
    
    # Buscar setor
    setor = session.query(Setor).filter_by(departamento="TESTE").first()
    if not setor:
        print("   ❌ Setor TESTES não encontrado")
        return None
    
    # Buscar tipos de máquina
    tipos_maquina = session.query(TipoMaquina).filter_by(departamento="TESTE").all()
    
    # Buscar tipos de teste
    tipos_teste = session.query(TipoTeste).filter_by(departamento="TESTE").all()
    
    # Buscar usuário admin
    admin_user = session.query(Usuario).filter_by(email="admin@registroos.com").first()
    
    dados = {
        'departamento': departamento,
        'setor': setor,
        'tipos_maquina': tipos_maquina,
        'tipos_teste': tipos_teste,
        'admin_user': admin_user
    }
    
    print(f"   ✅ Dados obtidos: {len(tipos_maquina)} máquinas, {len(tipos_teste)} testes")
    return dados

def criar_programacoes_exemplo(dados):
    """Cria programações de exemplo para o departamento TESTE"""
    print("📅 Criando programações de exemplo...")
    
    # Data base para as programações (próximos dias)
    data_base = datetime.now().date()
    
    programacoes = [
        {
            "codigo": "PROG_TESTE_001",
            "titulo": "Teste Completo - Equipamento A",
            "descricao": "Bateria completa de testes para validação do Equipamento Teste A",
            "tipo_maquina": "EQUIPAMENTO TESTE A",
            "data_inicio": data_base + timedelta(days=1),
            "hora_inicio": "08:00",
            "data_fim": data_base + timedelta(days=1),
            "hora_fim": "17:00",
            "prioridade": "ALTA",
            "testes": ["TESTE FUNCIONAL BÁSICO", "TESTE DE PERFORMANCE", "TESTE DE SEGURANÇA"]
        },
        {
            "codigo": "PROG_TESTE_002", 
            "titulo": "Teste de Durabilidade - Equipamento B",
            "descricao": "Teste de durabilidade prolongado para Equipamento Teste B",
            "tipo_maquina": "EQUIPAMENTO TESTE B",
            "data_inicio": data_base + timedelta(days=2),
            "hora_inicio": "09:00",
            "data_fim": data_base + timedelta(days=4),
            "hora_fim": "16:00",
            "prioridade": "NORMAL",
            "testes": ["TESTE DE DURABILIDADE", "TESTE DE CALIBRAÇÃO"]
        },
        {
            "codigo": "PROG_TESTE_003",
            "titulo": "Validação Rápida - Equipamento C",
            "descricao": "Validação rápida para liberação do Equipamento Teste C",
            "tipo_maquina": "EQUIPAMENTO TESTE C",
            "data_inicio": data_base + timedelta(days=3),
            "hora_inicio": "14:00",
            "data_fim": data_base + timedelta(days=3),
            "hora_fim": "18:00",
            "prioridade": "URGENTE",
            "testes": ["TESTE FUNCIONAL BÁSICO", "TESTE DE SEGURANÇA"]
        },
        {
            "codigo": "PROG_TESTE_004",
            "titulo": "Bateria Completa - Todos Equipamentos",
            "descricao": "Teste comparativo entre todos os equipamentos",
            "tipo_maquina": "EQUIPAMENTO TESTE A",  # Usar o primeiro como referência
            "data_inicio": data_base + timedelta(days=7),
            "hora_inicio": "08:00",
            "data_fim": data_base + timedelta(days=10),
            "hora_fim": "17:00",
            "prioridade": "ALTA",
            "testes": ["TESTE FUNCIONAL BÁSICO", "TESTE DE PERFORMANCE", "TESTE DE SEGURANÇA", "TESTE DE DURABILIDADE", "TESTE DE CALIBRAÇÃO"]
        }
    ]
    
    programacoes_criadas = []
    
    for prog_data in programacoes:
        # Verificar se já existe
        existente = session.query(ProgramacaoTeste).filter_by(
            codigo_programacao=prog_data["codigo"]
        ).first()
        
        if existente:
            print(f"   ✅ {prog_data['codigo']} já existe")
            programacoes_criadas.append(existente)
            continue
        
        # Buscar tipo de máquina
        tipo_maquina = next((tm for tm in dados['tipos_maquina'] if tm.nome_tipo == prog_data["tipo_maquina"]), None)
        if not tipo_maquina:
            print(f"   ❌ Tipo de máquina {prog_data['tipo_maquina']} não encontrado")
            continue
        
        # Buscar IDs dos testes
        testes_ids = []
        for nome_teste in prog_data["testes"]:
            teste = next((t for t in dados['tipos_teste'] if t.nome == nome_teste), None)
            if teste:
                testes_ids.append({
                    "id": teste.id,
                    "nome": teste.nome,
                    "tipo": teste.tipo_teste
                })
        
        # Criar programação
        programacao = ProgramacaoTeste(
            codigo_programacao=prog_data["codigo"],
            titulo=prog_data["titulo"],
            descricao=prog_data["descricao"],
            id_departamento=dados['departamento'].id,
            id_setor=dados['setor'].id,
            id_tipo_maquina=tipo_maquina.id,
            data_inicio_programada=prog_data["data_inicio"],
            hora_inicio_programada=datetime.strptime(prog_data["hora_inicio"], "%H:%M").time(),
            data_fim_programada=prog_data["data_fim"],
            hora_fim_programada=datetime.strptime(prog_data["hora_fim"], "%H:%M").time(),
            status="PROGRAMADO",
            prioridade=prog_data["prioridade"],
            id_responsavel_programacao=dados['admin_user'].id if dados['admin_user'] else 1,
            id_responsavel_execucao=dados['admin_user'].id if dados['admin_user'] else 1,
            testes_programados=json.dumps(testes_ids, ensure_ascii=False),
            observacoes_programacao=f"Programação criada automaticamente para {prog_data['tipo_maquina']}",
            criado_por=dados['admin_user'].id if dados['admin_user'] else 1,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        
        session.add(programacao)
        session.flush()
        programacoes_criadas.append(programacao)
        
        print(f"   ✅ {prog_data['codigo']} criado (ID: {programacao.id})")
    
    return programacoes_criadas

def listar_programacoes():
    """Lista todas as programações criadas"""
    print("\n📋 PROGRAMAÇÕES CRIADAS:")

    programacoes = session.query(ProgramacaoTeste).all()

    if not programacoes:
        print("   ❌ Nenhuma programação encontrada")
        return

    for prog in programacoes:
        print(f"\n   📅 {prog.codigo_programacao} - {prog.titulo}")
        print(f"      Status: {prog.status} | Prioridade: {prog.prioridade}")
        print(f"      Data: {prog.data_inicio_programada} às {prog.hora_inicio_programada}")
        print(f"      Até: {prog.data_fim_programada} às {prog.hora_fim_programada}")

        # Decodificar testes programados
        if prog.testes_programados:
            try:
                testes = json.loads(prog.testes_programados)
                print(f"      Testes: {len(testes)} programados")
                for teste in testes:
                    print(f"         - {teste['nome']} ({teste['tipo']})")
            except:
                print(f"      Testes: {prog.testes_programados}")

        print(f"      Descrição: {prog.descricao}")

def criar_endpoint_programacao():
    """Cria um endpoint de exemplo para consultar programações"""
    print("\n🔗 Criando endpoint de exemplo para programações...")

    endpoint_code = '''
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
'''

    # Salvar código do endpoint em arquivo
    with open("SCRATCK HERE/endpoint_programacao_exemplo.py", "w", encoding="utf-8") as f:
        f.write(endpoint_code)

    print("   ✅ Código do endpoint salvo em 'endpoint_programacao_exemplo.py'")

def main():
    """Função principal"""
    print("🚀 CRIANDO SISTEMA DE PROGRAMAÇÃO DE TESTES")
    print("=" * 60)

    try:
        # 1. Criar tabela
        if not criar_tabela_programacao():
            return

        # 2. Obter dados do departamento TESTE
        dados = obter_dados_departamento_teste()
        if not dados:
            return

        # 3. Criar programações de exemplo
        programacoes = criar_programacoes_exemplo(dados)

        # 4. Commit das alterações
        session.commit()

        # 5. Listar programações criadas
        listar_programacoes()

        # 6. Criar endpoint de exemplo
        criar_endpoint_programacao()

        print("\n" + "=" * 60)
        print("🎯 SISTEMA DE PROGRAMAÇÃO CRIADO COM SUCESSO!")
        print(f"   📅 {len(programacoes)} programações criadas")
        print("   🗄️ Tabela 'programacao_testes' criada")
        print("   🔗 Endpoints de exemplo gerados")
        print("   ✅ Sistema pronto para uso!")

    except Exception as e:
        print(f"\n❌ ERRO durante a criação: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
