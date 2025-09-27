#!/usr/bin/env python3
"""
Script para inserir dados de teste diretamente no banco SQLite
Cria pendências e programações usando dados reais existentes
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Caminho para o banco de dados
DB_PATH = "registrooficial/backend/app/database.db"

def conectar_banco():
    """Conecta ao banco de dados SQLite"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def buscar_dados_existentes(conn):
    """Busca dados existentes no banco"""
    print("🔍 Buscando dados existentes no banco...")
    
    dados = {
        "ordens_servico": [],
        "usuarios": [],
        "clientes": [],
        "equipamentos": [],
        "setores": []
    }
    
    cursor = conn.cursor()
    
    try:
        # Buscar ordens de serviço
        cursor.execute("SELECT * FROM ordens_servico LIMIT 10")
        dados["ordens_servico"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['ordens_servico'])} ordens de serviço encontradas")
        
        # Buscar usuários
        cursor.execute("SELECT * FROM tipo_usuarios WHERE is_approved = 1 LIMIT 20")
        dados["usuarios"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['usuarios'])} usuários encontrados")
        
        # Buscar clientes
        cursor.execute("SELECT * FROM clientes LIMIT 10")
        dados["clientes"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['clientes'])} clientes encontrados")
        
        # Buscar equipamentos
        cursor.execute("SELECT * FROM equipamentos LIMIT 10")
        dados["equipamentos"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['equipamentos'])} equipamentos encontrados")
        
        # Buscar setores
        cursor.execute("SELECT * FROM tipo_setores LIMIT 10")
        dados["setores"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['setores'])} setores encontrados")
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
    
    return dados

def criar_apontamentos_origem(conn, dados):
    """Cria apontamentos para servir como origem das pendências"""
    print("📝 Criando apontamentos de origem...")
    
    cursor = conn.cursor()
    apontamentos_criados = []
    
    for i in range(5):
        try:
            os_data = random.choice(dados["ordens_servico"])
            usuario = random.choice(dados["usuarios"])
            setor = random.choice(dados["setores"]) if dados["setores"] else None
            
            apontamento_data = {
                "id_os": os_data["id"],
                "id_usuario": usuario["id"],
                "id_setor": setor["id"] if setor else 1,
                "data_hora_inicio": datetime.now(),
                "data_hora_fim": datetime.now() + timedelta(hours=8),
                "status_apontamento": "CONCLUIDO",
                "foi_retrabalho": False,
                "observacao": f"Apontamento origem para pendência {i+1}",
                "criado_por": usuario["id"],
                "criado_por_email": usuario.get("email", "teste@teste.com"),
                "setor": setor["nome"] if setor else "TESTE"
            }
            
            cursor.execute("""
                INSERT INTO apontamentos_detalhados 
                (id_os, id_usuario, id_setor, data_hora_inicio, data_hora_fim, 
                 status_apontamento, foi_retrabalho, observacao, criado_por, 
                 criado_por_email, setor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                apontamento_data["id_os"],
                apontamento_data["id_usuario"],
                apontamento_data["id_setor"],
                apontamento_data["data_hora_inicio"],
                apontamento_data["data_hora_fim"],
                apontamento_data["status_apontamento"],
                apontamento_data["foi_retrabalho"],
                apontamento_data["observacao"],
                apontamento_data["criado_por"],
                apontamento_data["criado_por_email"],
                apontamento_data["setor"]
            ))
            
            apontamento_id = cursor.lastrowid
            apontamentos_criados.append({
                "id": apontamento_id,
                "os_numero": os_data["os_numero"],
                "usuario_id": usuario["id"]
            })
            
            print(f"   ✅ Apontamento {i+1} criado: ID {apontamento_id}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar apontamento {i+1}: {e}")
    
    conn.commit()
    return apontamentos_criados

def criar_pendencias_teste(conn, dados, apontamentos):
    """Cria pendências de teste"""
    print("📋 Criando pendências de teste...")
    
    cursor = conn.cursor()
    pendencias_criadas = []
    
    tipos_maquina = ["BOMBA_CENTRIFUGA", "MOTOR_ELETRICO", "COMPRESSOR", "TURBINA", "GERADOR"]
    prioridades = ["BAIXA", "NORMAL", "ALTA", "URGENTE"]
    descricoes = [
        "Vazamento identificado no sistema hidráulico",
        "Ruído anormal durante operação",
        "Temperatura elevada nos rolamentos",
        "Vibração excessiva detectada",
        "Falha no sistema de controle"
    ]
    
    for i, apontamento in enumerate(apontamentos):
        try:
            cliente = random.choice(dados["clientes"]) if dados["clientes"] else {"razao_social": "Cliente Teste"}
            equipamento = random.choice(dados["equipamentos"]) if dados["equipamentos"] else {"nome": "Equipamento Teste"}
            
            pendencia_data = {
                "numero_os": apontamento["os_numero"],
                "cliente": cliente.get("razao_social", "Cliente Teste"),
                "data_inicio": datetime.now(),
                "id_responsavel_inicio": apontamento["usuario_id"],
                "tipo_maquina": random.choice(tipos_maquina),
                "descricao_maquina": equipamento.get("nome", f"Equipamento Teste {i+1}"),
                "descricao_pendencia": random.choice(descricoes),
                "status": "ABERTA",
                "prioridade": random.choice(prioridades),
                "id_apontamento_origem": apontamento["id"],
                "data_criacao": datetime.now(),
                "data_ultima_atualizacao": datetime.now()
            }
            
            cursor.execute("""
                INSERT INTO pendencias 
                (numero_os, cliente, data_inicio, id_responsavel_inicio, tipo_maquina,
                 descricao_maquina, descricao_pendencia, status, prioridade,
                 id_apontamento_origem, data_criacao, data_ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pendencia_data["numero_os"],
                pendencia_data["cliente"],
                pendencia_data["data_inicio"],
                pendencia_data["id_responsavel_inicio"],
                pendencia_data["tipo_maquina"],
                pendencia_data["descricao_maquina"],
                pendencia_data["descricao_pendencia"],
                pendencia_data["status"],
                pendencia_data["prioridade"],
                pendencia_data["id_apontamento_origem"],
                pendencia_data["data_criacao"],
                pendencia_data["data_ultima_atualizacao"]
            ))
            
            pendencia_id = cursor.lastrowid
            pendencias_criadas.append({
                "id": pendencia_id,
                "numero_os": pendencia_data["numero_os"],
                "descricao": pendencia_data["descricao_pendencia"]
            })
            
            print(f"   ✅ Pendência {i+1} criada: ID {pendencia_id} | OS {pendencia_data['numero_os']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar pendência {i+1}: {e}")
    
    conn.commit()
    return pendencias_criadas

def criar_programacoes_teste(conn, dados):
    """Cria programações de teste"""
    print("📅 Criando programações de teste...")
    
    cursor = conn.cursor()
    programacoes_criadas = []
    
    # Buscar usuários PCP/ADMIN
    usuarios_pcp = [u for u in dados["usuarios"] if u.get("privilege_level") in ["ADMIN", "SUPERVISOR"]]
    if not usuarios_pcp:
        usuarios_pcp = dados["usuarios"][:3]
    
    for i in range(3):
        try:
            os_data = random.choice(dados["ordens_servico"])
            usuario_pcp = random.choice(usuarios_pcp)
            usuario_responsavel = random.choice(dados["usuarios"])
            setor = random.choice(dados["setores"]) if dados["setores"] else None
            
            inicio_previsto = datetime.now() + timedelta(days=random.randint(1, 7))
            fim_previsto = inicio_previsto + timedelta(days=random.randint(1, 5))
            
            programacao_data = {
                "id_ordem_servico": os_data["id"],
                "criado_por_id": usuario_pcp["id"],
                "responsavel_id": usuario_responsavel["id"],
                "observacoes": f"Programação de teste #{i+1} - Manutenção preventiva programada",
                "status": "PROGRAMADA",
                "inicio_previsto": inicio_previsto,
                "fim_previsto": fim_previsto,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "id_setor": setor["id"] if setor else 1
            }
            
            cursor.execute("""
                INSERT INTO programacoes 
                (id_ordem_servico, criado_por_id, responsavel_id, observacoes, status,
                 inicio_previsto, fim_previsto, created_at, updated_at, id_setor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                programacao_data["id_ordem_servico"],
                programacao_data["criado_por_id"],
                programacao_data["responsavel_id"],
                programacao_data["observacoes"],
                programacao_data["status"],
                programacao_data["inicio_previsto"],
                programacao_data["fim_previsto"],
                programacao_data["created_at"],
                programacao_data["updated_at"],
                programacao_data["id_setor"]
            ))
            
            programacao_id = cursor.lastrowid
            programacoes_criadas.append({
                "id": programacao_id,
                "os_numero": os_data["os_numero"],
                "responsavel": usuario_responsavel.get("nome_completo", "Usuário Teste")
            })
            
            print(f"   ✅ Programação {i+1} criada: ID {programacao_id} | OS {os_data['os_numero']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar programação {i+1}: {e}")
    
    conn.commit()
    return programacoes_criadas

def main():
    """Função principal"""
    print("🚀 Iniciando inserção de dados de teste...")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        # Buscar dados existentes
        dados = buscar_dados_existentes(conn)
        
        if not dados["ordens_servico"] or not dados["usuarios"]:
            print("❌ Dados insuficientes no banco. Certifique-se de que há OSs e usuários cadastrados.")
            return
        
        print("\n" + "=" * 60)
        
        # Criar apontamentos de origem
        apontamentos = criar_apontamentos_origem(conn, dados)
        
        print("\n" + "=" * 60)
        
        # Criar pendências
        pendencias = criar_pendencias_teste(conn, dados, apontamentos)
        
        print("\n" + "=" * 60)
        
        # Criar programações
        programacoes = criar_programacoes_teste(conn, dados)
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DA INSERÇÃO DE DADOS")
        print("=" * 60)
        print(f"📝 Apontamentos criados: {len(apontamentos)}")
        print(f"📋 Pendências criadas: {len(pendencias)}")
        print(f"📅 Programações criadas: {len(programacoes)}")
        
        if pendencias:
            print("\n📋 Pendências criadas:")
            for p in pendencias:
                print(f"   - ID: {p['id']} | OS: {p['numero_os']} | {p['descricao'][:50]}...")
        
        if programacoes:
            print("\n📅 Programações criadas:")
            for p in programacoes:
                print(f"   - ID: {p['id']} | OS: {p['os_numero']} | Responsável: {p['responsavel']}")
        
        print("\n🎉 Dados de teste inseridos com sucesso!")
        print("\nPara testar:")
        print("1. Reinicie o servidor backend")
        print("2. Acesse a aba 'Pendências' para ver as pendências criadas")
        print("3. Teste o botão 'Resolver via Apontamento'")
        print("4. Acesse a aba 'Programação' para ver as programações")
        print("5. Teste a criação de apontamentos para OSs com programação")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
