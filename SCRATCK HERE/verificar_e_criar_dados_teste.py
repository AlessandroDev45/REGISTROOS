#!/usr/bin/env python3
"""
Script para verificar estrutura do banco e criar dados de teste
Verifica as tabelas existentes e cria pendências e programações
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Caminho para o banco de dados
DB_PATH = "RegistroOS/registrooficial/backend/app/registroos_new.db"

def conectar_banco():
    """Conecta ao banco de dados SQLite"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        print("   Certifique-se de que o caminho está correto")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def verificar_estrutura_banco(conn):
    """Verifica a estrutura das tabelas no banco"""
    print("🔍 Verificando estrutura do banco...")
    
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = [row[0] for row in cursor.fetchall()]
    
    print(f"   📋 Tabelas encontradas: {len(tabelas)}")
    for tabela in sorted(tabelas):
        print(f"      - {tabela}")
    
    # Verificar estrutura das tabelas importantes
    tabelas_importantes = ["ordens_servico", "tipo_usuarios", "pendencias", "programacoes", "apontamentos_detalhados"]
    
    estrutura = {}
    for tabela in tabelas_importantes:
        if tabela in tabelas:
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = cursor.fetchall()
            estrutura[tabela] = [{"nome": col[1], "tipo": col[2], "nao_nulo": col[3]} for col in colunas]
            print(f"\n   📊 Estrutura da tabela '{tabela}':")
            for col in estrutura[tabela]:
                print(f"      - {col['nome']} ({col['tipo']}) {'NOT NULL' if col['nao_nulo'] else ''}")
        else:
            print(f"\n   ❌ Tabela '{tabela}' não encontrada")
    
    return estrutura, tabelas

def buscar_dados_para_teste(conn, tabelas):
    """Busca dados existentes para usar nos testes"""
    print("\n🔍 Buscando dados existentes para teste...")
    
    cursor = conn.cursor()
    dados = {}
    
    # Buscar ordens de serviço
    if "ordens_servico" in tabelas:
        cursor.execute("SELECT * FROM ordens_servico LIMIT 5")
        dados["ordens_servico"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['ordens_servico'])} ordens de serviço encontradas")
    
    # Buscar usuários
    if "tipo_usuarios" in tabelas:
        cursor.execute("SELECT * FROM tipo_usuarios WHERE is_approved = 1 LIMIT 10")
        dados["usuarios"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['usuarios'])} usuários encontrados")
    
    # Buscar clientes se existir
    if "clientes" in tabelas:
        cursor.execute("SELECT * FROM clientes LIMIT 5")
        dados["clientes"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['clientes'])} clientes encontrados")
    
    # Buscar setores se existir
    if "tipo_setores" in tabelas:
        cursor.execute("SELECT * FROM tipo_setores LIMIT 5")
        dados["setores"] = [dict(row) for row in cursor.fetchall()]
        print(f"   ✅ {len(dados['setores'])} setores encontrados")
    
    return dados

def criar_apontamento_origem(conn, os_data, usuario_data, setor_id=1):
    """Cria um apontamento para servir como origem da pendência"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO apontamentos_detalhados 
            (id_os, id_usuario, id_setor, data_hora_inicio, data_hora_fim, 
             status_apontamento, foi_retrabalho, observacao, criado_por, 
             criado_por_email, setor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            os_data["id"],
            usuario_data["id"],
            setor_id,
            datetime.now(),
            datetime.now() + timedelta(hours=8),
            "CONCLUIDO",
            False,
            "Apontamento origem para teste de pendência",
            usuario_data["id"],
            usuario_data.get("email", "teste@teste.com"),
            "TESTE"
        ))
        
        return cursor.lastrowid
        
    except Exception as e:
        print(f"   ❌ Erro ao criar apontamento: {e}")
        return None

def criar_pendencias_teste(conn, dados):
    """Cria pendências de teste"""
    print("\n📋 Criando pendências de teste...")
    
    if not dados.get("ordens_servico") or not dados.get("usuarios"):
        print("❌ Dados insuficientes (OSs ou usuários)")
        return []
    
    cursor = conn.cursor()
    pendencias_criadas = []
    
    tipos_maquina = ["BOMBA_CENTRIFUGA", "MOTOR_ELETRICO", "COMPRESSOR"]
    prioridades = ["NORMAL", "ALTA", "URGENTE"]
    descricoes = [
        "Vazamento no sistema hidráulico",
        "Ruído anormal durante operação", 
        "Temperatura elevada nos rolamentos"
    ]
    
    for i in range(3):
        try:
            os_data = random.choice(dados["ordens_servico"])
            usuario = random.choice(dados["usuarios"])
            
            # Criar apontamento origem
            apontamento_id = criar_apontamento_origem(conn, os_data, usuario)
            if not apontamento_id:
                continue
            
            # Criar pendência
            cursor.execute("""
                INSERT INTO pendencias 
                (numero_os, cliente, data_inicio, id_responsavel_inicio, tipo_maquina,
                 descricao_maquina, descricao_pendencia, status, prioridade,
                 id_apontamento_origem, data_criacao, data_ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_data["os_numero"],
                f"Cliente Teste {i+1}",
                datetime.now(),
                usuario["id"],
                random.choice(tipos_maquina),
                f"Equipamento Teste {i+1}",
                random.choice(descricoes),
                "ABERTA",
                random.choice(prioridades),
                apontamento_id,
                datetime.now(),
                datetime.now()
            ))
            
            pendencia_id = cursor.lastrowid
            pendencias_criadas.append({
                "id": pendencia_id,
                "os_numero": os_data["os_numero"],
                "descricao": random.choice(descricoes)
            })
            
            print(f"   ✅ Pendência {i+1}: ID {pendencia_id} | OS {os_data['os_numero']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar pendência {i+1}: {e}")
    
    conn.commit()
    return pendencias_criadas

def criar_programacoes_teste(conn, dados):
    """Cria programações de teste"""
    print("\n📅 Criando programações de teste...")
    
    if not dados.get("ordens_servico") or not dados.get("usuarios"):
        print("❌ Dados insuficientes (OSs ou usuários)")
        return []
    
    cursor = conn.cursor()
    programacoes_criadas = []
    
    for i in range(2):
        try:
            os_data = random.choice(dados["ordens_servico"])
            usuario_criador = random.choice(dados["usuarios"])
            usuario_responsavel = random.choice(dados["usuarios"])
            
            inicio = datetime.now() + timedelta(days=random.randint(1, 5))
            fim = inicio + timedelta(days=random.randint(1, 3))
            
            cursor.execute("""
                INSERT INTO programacoes 
                (id_ordem_servico, criado_por_id, responsavel_id, observacoes, status,
                 inicio_previsto, fim_previsto, created_at, updated_at, id_setor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_data["id"],
                usuario_criador["id"],
                usuario_responsavel["id"],
                f"Programação de teste #{i+1} - Manutenção preventiva",
                "PROGRAMADA",
                inicio,
                fim,
                datetime.now(),
                datetime.now(),
                dados.get("setores", [{"id": 1}])[0]["id"] if dados.get("setores") else 1
            ))
            
            programacao_id = cursor.lastrowid
            programacoes_criadas.append({
                "id": programacao_id,
                "os_numero": os_data["os_numero"],
                "responsavel": usuario_responsavel.get("nome_completo", "Usuário Teste")
            })
            
            print(f"   ✅ Programação {i+1}: ID {programacao_id} | OS {os_data['os_numero']}")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar programação {i+1}: {e}")
    
    conn.commit()
    return programacoes_criadas

def main():
    """Função principal"""
    print("🚀 Verificando banco e criando dados de teste...")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        # Verificar estrutura
        estrutura, tabelas = verificar_estrutura_banco(conn)
        
        # Buscar dados existentes
        dados = buscar_dados_para_teste(conn, tabelas)
        
        if not dados.get("ordens_servico") or not dados.get("usuarios"):
            print("\n❌ Dados insuficientes no banco.")
            print("   Certifique-se de que há OSs e usuários cadastrados.")
            return
        
        # Criar pendências
        pendencias = criar_pendencias_teste(conn, dados)
        
        # Criar programações
        programacoes = criar_programacoes_teste(conn, dados)
        
        # Resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO")
        print("=" * 60)
        print(f"📋 Pendências criadas: {len(pendencias)}")
        print(f"📅 Programações criadas: {len(programacoes)}")
        
        if pendencias:
            print("\n📋 Pendências:")
            for p in pendencias:
                print(f"   - ID {p['id']}: OS {p['os_numero']}")
        
        if programacoes:
            print("\n📅 Programações:")
            for p in programacoes:
                print(f"   - ID {p['id']}: OS {p['os_numero']}")
        
        print("\n🎉 Dados criados com sucesso!")
        print("\n📝 Para testar:")
        print("1. Reinicie o servidor backend")
        print("2. Acesse a aba 'Pendências'")
        print("3. Teste 'Resolver via Apontamento'")
        print("4. Acesse 'Minhas Programações'")
        print("5. Teste apontamentos com programação ativa")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
