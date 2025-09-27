#!/usr/bin/env python3
"""
Script completo para criar dados de teste
Cria clientes, OSs, pendências e programações
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
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def criar_clientes_teste(conn):
    """Cria clientes de teste"""
    print("🏢 Criando clientes de teste...")
    
    cursor = conn.cursor()
    clientes_criados = []
    
    clientes_dados = [
        {"razao_social": "Empresa Teste A Ltda", "nome_fantasia": "Teste A", "cnpj_cpf": "11.111.111/0001-11"},
        {"razao_social": "Indústria Teste B S.A.", "nome_fantasia": "Teste B", "cnpj_cpf": "22.222.222/0001-22"},
        {"razao_social": "Companhia Teste C", "nome_fantasia": "Teste C", "cnpj_cpf": "33.333.333/0001-33"}
    ]
    
    for i, cliente_data in enumerate(clientes_dados):
        try:
            cursor.execute("""
                INSERT INTO clientes 
                (razao_social, nome_fantasia, cnpj_cpf, contato_principal, 
                 telefone_contato, email_contato, data_criacao, data_ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente_data["razao_social"],
                cliente_data["nome_fantasia"],
                cliente_data["cnpj_cpf"],
                f"Contato {i+1}",
                f"(11) 9999-{i+1:04d}",
                f"contato{i+1}@teste.com",
                datetime.now(),
                datetime.now()
            ))
            
            cliente_id = cursor.lastrowid
            clientes_criados.append({
                "id": cliente_id,
                "razao_social": cliente_data["razao_social"]
            })
            
            print(f"   ✅ Cliente {i+1}: {cliente_data['razao_social']} (ID: {cliente_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar cliente {i+1}: {e}")
    
    conn.commit()
    return clientes_criados

def criar_equipamentos_teste(conn):
    """Cria equipamentos de teste"""
    print("🔧 Criando equipamentos de teste...")
    
    cursor = conn.cursor()
    equipamentos_criados = []
    
    equipamentos_dados = [
        {"nome": "Bomba Centrífuga BC-001", "tipo": "BOMBA_CENTRIFUGA"},
        {"nome": "Motor Elétrico ME-002", "tipo": "MOTOR_ELETRICO"},
        {"nome": "Compressor CP-003", "tipo": "COMPRESSOR"}
    ]
    
    for i, equip_data in enumerate(equipamentos_dados):
        try:
            cursor.execute("""
                INSERT INTO equipamentos 
                (nome, tipo, descricao, data_criacao, data_ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?)
            """, (
                equip_data["nome"],
                equip_data["tipo"],
                f"Equipamento de teste {i+1}",
                datetime.now(),
                datetime.now()
            ))
            
            equipamento_id = cursor.lastrowid
            equipamentos_criados.append({
                "id": equipamento_id,
                "nome": equip_data["nome"]
            })
            
            print(f"   ✅ Equipamento {i+1}: {equip_data['nome']} (ID: {equipamento_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar equipamento {i+1}: {e}")
    
    conn.commit()
    return equipamentos_criados

def criar_ordens_servico_teste(conn, clientes, equipamentos, usuarios):
    """Cria ordens de serviço de teste"""
    print("📋 Criando ordens de serviço de teste...")
    
    cursor = conn.cursor()
    os_criadas = []
    
    for i in range(5):
        try:
            cliente = random.choice(clientes)
            equipamento = random.choice(equipamentos)
            usuario = random.choice(usuarios)
            
            os_numero = f"OS{datetime.now().year}{i+1:04d}"
            
            cursor.execute("""
                INSERT INTO ordens_servico 
                (os_numero, id_cliente, id_equipamento, descricao_maquina, status_os,
                 id_responsavel_registro, data_criacao, data_ultima_atualizacao,
                 criado_por, prioridade, horas_orcadas, id_setor, id_departamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_numero,
                cliente["id"],
                equipamento["id"],
                f"Manutenção em {equipamento['nome']}",
                "ABERTA",
                usuario["id"],
                datetime.now(),
                datetime.now(),
                usuario["id"],
                random.choice(["BAIXA", "MEDIA", "ALTA"]),
                random.uniform(8.0, 40.0),
                usuario.get("id_setor", 1),
                usuario.get("id_departamento", 1)
            ))
            
            os_id = cursor.lastrowid
            os_criadas.append({
                "id": os_id,
                "os_numero": os_numero,
                "cliente": cliente["razao_social"],
                "equipamento": equipamento["nome"]
            })
            
            print(f"   ✅ OS {i+1}: {os_numero} - {cliente['razao_social']} (ID: {os_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar OS {i+1}: {e}")
    
    conn.commit()
    return os_criadas

def criar_apontamentos_origem(conn, os_criadas, usuarios):
    """Cria apontamentos para servir como origem das pendências"""
    print("📝 Criando apontamentos de origem...")
    
    cursor = conn.cursor()
    apontamentos_criados = []
    
    for i, os_data in enumerate(os_criadas[:3]):  # Criar apontamentos para as primeiras 3 OSs
        try:
            usuario = random.choice(usuarios)
            
            cursor.execute("""
                INSERT INTO apontamentos_detalhados 
                (id_os, id_usuario, id_setor, data_hora_inicio, data_hora_fim, 
                 status_apontamento, foi_retrabalho, criado_por, criado_por_email,
                 tipo_maquina, tipo_atividade, descricao_atividade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_data["id"],
                usuario["id"],
                usuario.get("id_setor", 1),
                datetime.now() - timedelta(hours=8),
                datetime.now(),
                "CONCLUIDO",
                False,
                usuario["nome_completo"],
                usuario["email"],
                "MANUTENCAO",
                "PREVENTIVA",
                f"Apontamento origem para OS {os_data['os_numero']}"
            ))
            
            apontamento_id = cursor.lastrowid
            apontamentos_criados.append({
                "id": apontamento_id,
                "os_id": os_data["id"],
                "os_numero": os_data["os_numero"],
                "usuario_id": usuario["id"]
            })
            
            print(f"   ✅ Apontamento {i+1}: OS {os_data['os_numero']} (ID: {apontamento_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar apontamento {i+1}: {e}")
    
    conn.commit()
    return apontamentos_criados

def criar_pendencias_teste(conn, apontamentos, os_criadas):
    """Cria pendências de teste"""
    print("📋 Criando pendências de teste...")
    
    cursor = conn.cursor()
    pendencias_criadas = []
    
    tipos_maquina = ["BOMBA_CENTRIFUGA", "MOTOR_ELETRICO", "COMPRESSOR"]
    prioridades = ["NORMAL", "ALTA", "URGENTE"]
    descricoes = [
        "Vazamento identificado no sistema hidráulico - necessário substituir vedações",
        "Ruído anormal durante operação - verificar rolamentos e alinhamento",
        "Temperatura elevada nos mancais - necessário análise térmica"
    ]
    
    for i, apontamento in enumerate(apontamentos):
        try:
            os_data = next(os for os in os_criadas if os["id"] == apontamento["os_id"])
            
            cursor.execute("""
                INSERT INTO pendencias 
                (numero_os, cliente, data_inicio, id_responsavel_inicio, tipo_maquina,
                 descricao_maquina, descricao_pendencia, status, prioridade,
                 id_apontamento_origem, data_criacao, data_ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                apontamento["os_numero"],
                os_data["cliente"],
                datetime.now() - timedelta(hours=random.randint(1, 48)),
                apontamento["usuario_id"],
                random.choice(tipos_maquina),
                os_data["equipamento"],
                descricoes[i % len(descricoes)],
                "ABERTA",
                random.choice(prioridades),
                apontamento["id"],
                datetime.now(),
                datetime.now()
            ))
            
            pendencia_id = cursor.lastrowid
            pendencias_criadas.append({
                "id": pendencia_id,
                "os_numero": apontamento["os_numero"],
                "descricao": descricoes[i % len(descricoes)]
            })
            
            print(f"   ✅ Pendência {i+1}: OS {apontamento['os_numero']} (ID: {pendencia_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar pendência {i+1}: {e}")
    
    conn.commit()
    return pendencias_criadas

def criar_programacoes_teste(conn, os_criadas, usuarios):
    """Cria programações de teste"""
    print("📅 Criando programações de teste...")
    
    cursor = conn.cursor()
    programacoes_criadas = []
    
    # Usar as últimas 2 OSs para programações
    for i, os_data in enumerate(os_criadas[-2:]):
        try:
            usuario_criador = random.choice([u for u in usuarios if u.get("privilege_level") in ["ADMIN", "SUPERVISOR"]])
            if not usuario_criador:
                usuario_criador = random.choice(usuarios)
            
            usuario_responsavel = random.choice(usuarios)
            
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
                f"Programação de teste #{i+1} - Manutenção preventiva programada para {os_data['equipamento']}",
                "PROGRAMADA",
                inicio,
                fim,
                datetime.now(),
                datetime.now(),
                usuario_responsavel.get("id_setor", 1)
            ))
            
            programacao_id = cursor.lastrowid
            programacoes_criadas.append({
                "id": programacao_id,
                "os_numero": os_data["os_numero"],
                "responsavel": usuario_responsavel["nome_completo"]
            })
            
            print(f"   ✅ Programação {i+1}: OS {os_data['os_numero']} (ID: {programacao_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar programação {i+1}: {e}")
    
    conn.commit()
    return programacoes_criadas

def main():
    """Função principal"""
    print("🚀 Criando dados completos de teste...")
    print("=" * 60)
    
    # Conectar ao banco
    conn = conectar_banco()
    if not conn:
        return
    
    try:
        # Buscar usuários existentes
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tipo_usuarios WHERE is_approved = 1 LIMIT 10")
        usuarios = [dict(row) for row in cursor.fetchall()]
        
        if not usuarios:
            print("❌ Nenhum usuário encontrado no banco")
            return
        
        print(f"👥 {len(usuarios)} usuários encontrados")
        
        # Criar dados base
        clientes = criar_clientes_teste(conn)
        equipamentos = criar_equipamentos_teste(conn)
        os_criadas = criar_ordens_servico_teste(conn, clientes, equipamentos, usuarios)
        
        # Criar apontamentos e pendências
        apontamentos = criar_apontamentos_origem(conn, os_criadas, usuarios)
        pendencias = criar_pendencias_teste(conn, apontamentos, os_criadas)
        
        # Criar programações
        programacoes = criar_programacoes_teste(conn, os_criadas, usuarios)
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("=" * 60)
        print(f"🏢 Clientes: {len(clientes)}")
        print(f"🔧 Equipamentos: {len(equipamentos)}")
        print(f"📋 Ordens de Serviço: {len(os_criadas)}")
        print(f"📝 Apontamentos: {len(apontamentos)}")
        print(f"📋 Pendências: {len(pendencias)}")
        print(f"📅 Programações: {len(programacoes)}")
        
        if pendencias:
            print("\n📋 Pendências criadas:")
            for p in pendencias:
                print(f"   - ID {p['id']}: OS {p['os_numero']}")
        
        if programacoes:
            print("\n📅 Programações criadas:")
            for p in programacoes:
                print(f"   - ID {p['id']}: OS {p['os_numero']} - {p['responsavel']}")
        
        print("\n🎉 Todos os dados de teste foram criados com sucesso!")
        print("\n📝 Para testar as funcionalidades:")
        print("1. Reinicie o servidor backend")
        print("2. Acesse a aba 'Pendências' para ver as pendências criadas")
        print("3. Teste o botão 'Resolver via Apontamento'")
        print("4. Acesse 'Minhas Programações' para ver as programações")
        print("5. Teste a criação de apontamentos para OSs com programação ativa")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
