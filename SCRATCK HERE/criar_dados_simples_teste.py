#!/usr/bin/env python3
"""
Script simples para criar pendências e programações de teste
Usa apenas dados existentes no banco
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Caminho para o banco de dados
DB_PATH = "RegistroOS/registrooficial/backend/app/registroos_new.db"

def conectar_banco():
    """Conecta ao banco de dados SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def criar_os_simples(conn, usuarios):
    """Cria OSs simples para teste"""
    print("📋 Criando OSs simples para teste...")
    
    cursor = conn.cursor()
    os_criadas = []
    
    for i in range(5):
        try:
            usuario = random.choice(usuarios)
            os_numero = f"TEST{datetime.now().year}{i+1:04d}"
            
            cursor.execute("""
                INSERT INTO ordens_servico 
                (os_numero, descricao_maquina, status_os, id_responsavel_registro, 
                 data_criacao, data_ultima_atualizacao, criado_por, prioridade, 
                 horas_orcadas, id_setor, id_departamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                os_numero,
                f"Equipamento Teste {i+1} - Bomba Centrífuga",
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
                "os_numero": os_numero
            })
            
            print(f"   ✅ OS {i+1}: {os_numero} (ID: {os_id})")
            
        except Exception as e:
            print(f"   ❌ Erro ao criar OS {i+1}: {e}")
    
    conn.commit()
    return os_criadas

def criar_apontamentos_origem(conn, os_criadas, usuarios):
    """Cria apontamentos para servir como origem das pendências"""
    print("📝 Criando apontamentos de origem...")
    
    cursor = conn.cursor()
    apontamentos_criados = []
    
    for i, os_data in enumerate(os_criadas[:3]):  # Primeiras 3 OSs
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
                "BOMBA_CENTRIFUGA",
                "MANUTENCAO",
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

def criar_pendencias_teste(conn, apontamentos):
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
            cursor.execute("""
                INSERT INTO pendencias 
                (numero_os, cliente, data_inicio, id_responsavel_inicio, tipo_maquina,
                 descricao_maquina, descricao_pendencia, status, prioridade,
                 id_apontamento_origem, data_criacao, data_ultima_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                apontamento["os_numero"],
                f"Cliente Teste {i+1}",
                datetime.now() - timedelta(hours=random.randint(1, 48)),
                apontamento["usuario_id"],
                random.choice(tipos_maquina),
                f"Equipamento Teste {i+1}",
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
            # Buscar usuário PCP/ADMIN
            usuario_criador = next((u for u in usuarios if u.get("privilege_level") in ["ADMIN", "SUPERVISOR"]), usuarios[0])
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
                f"Programação de teste #{i+1} - Manutenção preventiva programada",
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
    print("🚀 Criando dados simples de teste...")
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
        
        # Criar OSs simples
        os_criadas = criar_os_simples(conn, usuarios)
        
        if not os_criadas:
            print("❌ Não foi possível criar OSs")
            return
        
        # Criar apontamentos e pendências
        apontamentos = criar_apontamentos_origem(conn, os_criadas, usuarios)
        pendencias = criar_pendencias_teste(conn, apontamentos)
        
        # Criar programações
        programacoes = criar_programacoes_teste(conn, os_criadas, usuarios)
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS DADOS CRIADOS")
        print("=" * 60)
        print(f"📋 Ordens de Serviço: {len(os_criadas)}")
        print(f"📝 Apontamentos: {len(apontamentos)}")
        print(f"📋 Pendências: {len(pendencias)}")
        print(f"📅 Programações: {len(programacoes)}")
        
        if pendencias:
            print("\n📋 Pendências criadas:")
            for p in pendencias:
                print(f"   - ID {p['id']}: OS {p['os_numero']}")
                print(f"     {p['descricao'][:60]}...")
        
        if programacoes:
            print("\n📅 Programações criadas:")
            for p in programacoes:
                print(f"   - ID {p['id']}: OS {p['os_numero']}")
                print(f"     Responsável: {p['responsavel']}")
        
        print("\n🎉 Dados de teste criados com sucesso!")
        print("\n📝 Para testar as funcionalidades implementadas:")
        print("1. Reinicie o servidor backend")
        print("2. Acesse a aba 'Pendências' para ver as pendências criadas")
        print("3. Teste o botão '📝 Resolver via Apontamento'")
        print("4. Acesse 'Minhas Programações' para ver as programações")
        print("5. Teste a criação de apontamentos para OSs com programação ativa")
        print("6. Verifique se os botões mudam para 'Salvar Apontamento/Programação'")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()
