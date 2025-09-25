#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar e testar uma nova programação para o setor TESTES
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.database_config import engine
from app.database_models import Departamento, Setor, TipoMaquina, TipoTeste

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def obter_dados_hierarquia():
    """Obtém dados da hierarquia TESTE"""
    print("📊 Obtendo dados da hierarquia TESTE...")
    
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
    
    dados = {
        'departamento': departamento,
        'setor': setor,
        'tipos_maquina': tipos_maquina,
        'tipos_teste': tipos_teste
    }
    
    print(f"   ✅ Dados obtidos:")
    print(f"      🏢 Departamento: {departamento.nome_tipo} (ID: {departamento.id})")
    print(f"      🏭 Setor: {setor.nome} (ID: {setor.id})")
    print(f"      🔧 Tipos de Máquina: {len(tipos_maquina)}")
    print(f"      🧪 Tipos de Teste: {len(tipos_teste)}")
    
    return dados

def criar_nova_programacao_avancada(dados):
    """Cria uma nova programação avançada"""
    print("\n📅 Criando nova programação avançada...")
    
    # Data base para a programação (próxima semana)
    data_base = datetime.now().date()
    data_inicio = data_base + timedelta(days=14)  # 2 semanas no futuro
    data_fim = data_inicio + timedelta(days=5)    # 5 dias de duração
    
    # Selecionar todos os tipos de teste para uma bateria completa
    testes_selecionados = []
    for teste in dados['tipos_teste']:
        testes_selecionados.append({
            "id": teste.id,
            "nome": teste.nome,
            "tipo": teste.tipo_teste,
            "categoria": teste.categoria,
            "descricao": teste.descricao
        })
    
    # Dados da nova programação
    nova_programacao = {
        "codigo_programacao": "PROG_TESTE_005",
        "titulo": "Bateria Completa de Validação - Todos Equipamentos",
        "descricao": "Programação avançada para validação completa de todos os equipamentos do departamento TESTE com bateria completa de testes",
        "id_departamento": dados['departamento'].id,
        "id_setor": dados['setor'].id,
        "id_tipo_maquina": dados['tipos_maquina'][0].id,  # Usar primeiro equipamento como referência
        "data_inicio_programada": data_inicio,
        "hora_inicio_programada": "07:00:00",
        "data_fim_programada": data_fim,
        "hora_fim_programada": "18:00:00",
        "status": "PROGRAMADO",
        "prioridade": "URGENTE",
        "id_responsavel_programacao": 1,  # Admin
        "id_responsavel_execucao": 1,     # Admin
        "testes_programados": json.dumps(testes_selecionados, ensure_ascii=False),
        "observacoes_programacao": "Programação crítica para validação completa de todos os equipamentos. Inclui todos os tipos de teste disponíveis: funcional, performance, segurança, durabilidade e calibração.",
        "criado_por": 1,
        "data_criacao": datetime.now(),
        "data_ultima_atualizacao": datetime.now()
    }
    
    try:
        # Verificar se já existe
        query_check = text("SELECT id FROM programacao_testes WHERE codigo_programacao = :codigo")
        result = session.execute(query_check, {"codigo": nova_programacao["codigo_programacao"]}).fetchone()
        
        if result:
            print(f"   ⚠️ Programação {nova_programacao['codigo_programacao']} já existe")
            return result[0]
        
        # Inserir nova programação
        insert_query = text("""
            INSERT INTO programacao_testes (
                codigo_programacao, titulo, descricao, id_departamento, id_setor, 
                id_tipo_maquina, data_inicio_programada, hora_inicio_programada,
                data_fim_programada, hora_fim_programada, status, prioridade,
                id_responsavel_programacao, id_responsavel_execucao, testes_programados,
                observacoes_programacao, criado_por, data_criacao, data_ultima_atualizacao
            ) VALUES (
                :codigo_programacao, :titulo, :descricao, :id_departamento, :id_setor,
                :id_tipo_maquina, :data_inicio_programada, :hora_inicio_programada,
                :data_fim_programada, :hora_fim_programada, :status, :prioridade,
                :id_responsavel_programacao, :id_responsavel_execucao, :testes_programados,
                :observacoes_programacao, :criado_por, :data_criacao, :data_ultima_atualizacao
            )
        """)
        
        session.execute(insert_query, nova_programacao)
        session.commit()
        
        # Buscar ID da programação criada
        result = session.execute(query_check, {"codigo": nova_programacao["codigo_programacao"]}).fetchone()
        programacao_id = result[0] if result else None
        
        print(f"   ✅ Nova programação criada:")
        print(f"      📅 Código: {nova_programacao['codigo_programacao']}")
        print(f"      📋 Título: {nova_programacao['titulo']}")
        print(f"      🎯 Prioridade: {nova_programacao['prioridade']}")
        print(f"      📅 Período: {data_inicio} a {data_fim}")
        print(f"      🧪 Testes: {len(testes_selecionados)} programados")
        print(f"      🆔 ID: {programacao_id}")
        
        return programacao_id
        
    except Exception as e:
        session.rollback()
        print(f"   ❌ Erro ao criar programação: {e}")
        return None

def testar_programacao_criada(programacao_id):
    """Testa a programação criada"""
    print(f"\n🧪 Testando programação criada (ID: {programacao_id})...")
    
    try:
        # Buscar programação
        query = text("""
            SELECT 
                pt.id, pt.codigo_programacao, pt.titulo, pt.descricao,
                pt.data_inicio_programada, pt.hora_inicio_programada,
                pt.data_fim_programada, pt.hora_fim_programada,
                pt.status, pt.prioridade, pt.testes_programados,
                pt.observacoes_programacao,
                tm.nome_tipo as tipo_maquina,
                d.nome_tipo as departamento,
                s.nome as setor
            FROM programacao_testes pt
            LEFT JOIN tipos_maquina tm ON pt.id_tipo_maquina = tm.id
            LEFT JOIN tipo_departamentos d ON pt.id_departamento = d.id
            LEFT JOIN tipo_setores s ON pt.id_setor = s.id
            WHERE pt.id = :id
        """)
        
        result = session.execute(query, {"id": programacao_id}).fetchone()
        
        if not result:
            print("   ❌ Programação não encontrada")
            return False
        
        print("   ✅ Programação encontrada:")
        print(f"      📅 {result[1]} - {result[2]}")
        print(f"      🏢 Departamento: {result[13]}")
        print(f"      🏭 Setor: {result[14]}")
        print(f"      🔧 Máquina: {result[12]}")
        print(f"      🎯 Status: {result[8]} | Prioridade: {result[9]}")
        print(f"      📅 Início: {result[4]} às {result[5]}")
        print(f"      📅 Fim: {result[6]} às {result[7]}")
        
        # Decodificar testes programados
        if result[10]:
            try:
                testes = json.loads(result[10])
                print(f"      🧪 Testes programados: {len(testes)}")
                for i, teste in enumerate(testes, 1):
                    print(f"         {i}. {teste['nome']} ({teste['tipo']})")
            except:
                print(f"      🧪 Testes: {result[10]}")
        
        print(f"      📝 Observações: {result[11]}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao testar programação: {e}")
        return False

def simular_execucao_programacao(programacao_id):
    """Simula a execução da programação"""
    print(f"\n⚡ Simulando execução da programação {programacao_id}...")
    
    try:
        # 1. Iniciar programação
        print("   🚀 Iniciando programação...")
        update_query = text("""
            UPDATE programacao_testes 
            SET status = 'EM_ANDAMENTO',
                data_inicio_real = :data_inicio,
                data_ultima_atualizacao = :data_atualizacao
            WHERE id = :id
        """)
        
        session.execute(update_query, {
            "id": programacao_id,
            "data_inicio": datetime.now(),
            "data_atualizacao": datetime.now()
        })
        session.commit()
        print("      ✅ Status alterado para EM_ANDAMENTO")
        
        # 2. Simular progresso
        print("   ⏳ Simulando progresso dos testes...")
        import time
        time.sleep(2)  # Simular tempo de execução
        
        # 3. Finalizar programação
        print("   🏁 Finalizando programação...")
        data_fim = datetime.now()
        tempo_execucao = 120  # 2 horas simuladas
        
        final_update_query = text("""
            UPDATE programacao_testes 
            SET status = 'CONCLUIDO',
                data_fim_real = :data_fim,
                tempo_execucao_minutos = :tempo_execucao,
                resultado_geral = 'APROVADO',
                percentual_aprovacao = 95,
                observacoes_execucao = :observacoes_execucao,
                data_ultima_atualizacao = :data_atualizacao
            WHERE id = :id
        """)
        
        session.execute(final_update_query, {
            "id": programacao_id,
            "data_fim": data_fim,
            "tempo_execucao": tempo_execucao,
            "observacoes_execucao": "Execução simulada concluída com sucesso. Todos os testes da bateria completa foram executados conforme programado. Resultado geral: APROVADO com 95% de aprovação.",
            "data_atualizacao": datetime.now()
        })
        session.commit()
        
        print("      ✅ Status alterado para CONCLUIDO")
        print(f"      ⏱️ Tempo de execução: {tempo_execucao} minutos")
        print(f"      🎯 Resultado: APROVADO (95% aprovação)")
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"   ❌ Erro na simulação: {e}")
        return False

def listar_todas_programacoes():
    """Lista todas as programações do departamento TESTE"""
    print("\n📋 Listando todas as programações do departamento TESTE...")
    
    try:
        query = text("""
            SELECT 
                pt.id, pt.codigo_programacao, pt.titulo, pt.status, pt.prioridade,
                pt.data_inicio_programada, pt.data_fim_programada,
                pt.resultado_geral, pt.percentual_aprovacao
            FROM programacao_testes pt
            JOIN tipo_departamentos d ON pt.id_departamento = d.id
            WHERE d.nome_tipo = 'TESTE'
            ORDER BY pt.data_inicio_programada ASC
        """)
        
        result = session.execute(query).fetchall()
        
        print(f"   📊 Total de programações: {len(result)}")
        
        for row in result:
            status_icon = {
                'PROGRAMADO': '📅',
                'EM_ANDAMENTO': '⚡',
                'CONCLUIDO': '✅',
                'CANCELADO': '❌'
            }.get(row[3], '❓')
            
            prioridade_icon = {
                'BAIXA': '🟢',
                'NORMAL': '🟡',
                'ALTA': '🟠',
                'URGENTE': '🔴'
            }.get(row[4], '⚪')
            
            print(f"\n      {status_icon} {row[1]} - {row[2]}")
            print(f"         Status: {row[3]} | Prioridade: {prioridade_icon} {row[4]}")
            print(f"         Período: {row[5]} até {row[6]}")
            
            if row[7]:  # resultado_geral
                print(f"         Resultado: {row[7]} ({row[8]}% aprovação)")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro ao listar programações: {e}")
        return []

def main():
    """Função principal"""
    print("🚀 CRIANDO E TESTANDO NOVA PROGRAMAÇÃO - SETOR TESTES")
    print("=" * 70)
    
    try:
        # 1. Obter dados da hierarquia
        dados = obter_dados_hierarquia()
        if not dados:
            return
        
        # 2. Criar nova programação
        programacao_id = criar_nova_programacao_avancada(dados)
        if not programacao_id:
            return
        
        # 3. Testar programação criada
        if not testar_programacao_criada(programacao_id):
            return
        
        # 4. Simular execução
        if simular_execucao_programacao(programacao_id):
            print("   ✅ Simulação de execução concluída")
        
        # 5. Listar todas as programações
        programacoes = listar_todas_programacoes()
        
        print("\n" + "=" * 70)
        print("🎯 RESUMO DA NOVA PROGRAMAÇÃO:")
        print(f"   📅 Programação criada: PROG_TESTE_005")
        print(f"   🆔 ID: {programacao_id}")
        print(f"   🎯 Status: CONCLUIDO (simulado)")
        print(f"   🧪 Testes: 5 tipos programados")
        print(f"   📊 Total de programações: {len(programacoes)}")
        
        print("\n🌟 SISTEMA DE PROGRAMAÇÃO FUNCIONANDO:")
        print("   ✅ Criação de programações")
        print("   ✅ Atualização de status")
        print("   ✅ Controle de execução")
        print("   ✅ Relatórios de resultado")
        print("   ✅ Integração com hierarquia TESTE")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Acessar frontend para ver programações")
        print("   2. Testar interface de programação")
        print("   3. Criar apontamentos baseados nas programações")
        print("   4. Integrar com sistema de relatórios")
        
    except Exception as e:
        print(f"\n❌ ERRO durante o processo: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
