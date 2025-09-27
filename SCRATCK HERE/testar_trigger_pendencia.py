#!/usr/bin/env python3
"""
Testar o trigger automático para população do campo cliente
"""

import sqlite3
from datetime import datetime

# Caminho para o banco de dados
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def testar_trigger():
    """Testar trigger automático"""
    
    print("🧪 TESTANDO TRIGGER AUTOMÁTICO DE CLIENTE")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. VERIFICAR ORDENS DE SERVIÇO DISPONÍVEIS
        print("\n1. 📋 ORDENS DE SERVIÇO DISPONÍVEIS:")
        print("-" * 40)
        
        cursor.execute("""
            SELECT os.os_numero, c.nome_fantasia, c.id
            FROM ordens_servico os
            JOIN clientes c ON os.id_cliente = c.id
            LIMIT 5
        """)
        
        ordens_disponiveis = cursor.fetchall()
        for os_info in ordens_disponiveis:
            print(f"   OS: {os_info[0]} | Cliente: {os_info[1]} (ID: {os_info[2]})")
        
        # 2. CRIAR NOVA PENDÊNCIA PARA TESTE
        print("\n2. 🆕 CRIANDO NOVA PENDÊNCIA PARA TESTE:")
        print("-" * 40)
        
        # Usar a primeira OS disponível
        if ordens_disponiveis:
            os_teste = ordens_disponiveis[0][0]  # Número da OS
            cliente_esperado = ordens_disponiveis[0][1]  # Nome do cliente
            
            print(f"📝 Criando pendência para OS: {os_teste}")
            print(f"🏢 Cliente esperado: {cliente_esperado}")
            
            # Inserir nova pendência SEM especificar o campo cliente
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            insert_sql = """
                INSERT INTO pendencias (
                    numero_os, cliente, data_inicio, id_responsavel_inicio,
                    tipo_maquina, descricao_maquina, descricao_pendencia,
                    status, data_criacao, data_ultima_atualizacao,
                    setor_origem, departamento_origem
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_sql, (
                os_teste,
                "CLIENTE_TEMPORARIO",  # Será substituído pelo trigger
                now,
                1,  # Admin
                "Equipamento Teste",
                "Teste do Trigger",
                "Pendência criada para testar o trigger automático",
                "ABERTA",
                now,
                now,
                "TESTE",
                "TESTE"
            ))
            
            nova_pendencia_id = cursor.lastrowid
            print(f"✅ Pendência criada com ID: {nova_pendencia_id}")
            
            # 3. VERIFICAR SE O TRIGGER FUNCIONOU
            print("\n3. 🔍 VERIFICANDO SE O TRIGGER FUNCIONOU:")
            print("-" * 40)
            
            cursor.execute("""
                SELECT id, numero_os, cliente
                FROM pendencias
                WHERE id = ?
            """, (nova_pendencia_id,))
            
            pendencia_criada = cursor.fetchone()
            
            if pendencia_criada:
                print(f"📋 Pendência ID: {pendencia_criada[0]}")
                print(f"📋 OS: {pendencia_criada[1]}")
                print(f"🏢 Cliente no banco: '{pendencia_criada[2]}'")
                print(f"🏢 Cliente esperado: '{cliente_esperado}'")
                
                if pendencia_criada[2] == cliente_esperado:
                    print("✅ TRIGGER FUNCIONOU CORRETAMENTE!")
                else:
                    print("❌ Trigger não funcionou - cliente não foi atualizado")
            
            # 4. VERIFICAR TODAS AS PENDÊNCIAS
            print("\n4. 📊 TODAS AS PENDÊNCIAS APÓS TESTE:")
            print("-" * 40)
            
            cursor.execute("""
                SELECT p.id, p.numero_os, p.cliente, p.status
                FROM pendencias p
                ORDER BY p.id
            """)
            
            todas_pendencias = cursor.fetchall()
            for pend in todas_pendencias:
                status_icon = "🟢" if pend[3] == "ABERTA" else "🔴"
                print(f"   {status_icon} ID: {pend[0]} | OS: {pend[1]} | Cliente: {pend[2]} | Status: {pend[3]}")
            
            # 5. LIMPAR DADOS DE TESTE (OPCIONAL)
            print("\n5. 🧹 LIMPEZA DOS DADOS DE TESTE:")
            print("-" * 40)
            
            resposta = input("Deseja remover a pendência de teste? (s/n): ").lower().strip()
            
            if resposta == 's':
                cursor.execute("DELETE FROM pendencias WHERE id = ?", (nova_pendencia_id,))
                print(f"✅ Pendência de teste {nova_pendencia_id} removida")
            else:
                print(f"⚠️ Pendência de teste {nova_pendencia_id} mantida no banco")
            
        else:
            print("❌ Nenhuma OS disponível para teste")
        
        # Commit das mudanças
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ TESTE DO TRIGGER CONCLUÍDO!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    testar_trigger()
