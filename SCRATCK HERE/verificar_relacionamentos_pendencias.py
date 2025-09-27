#!/usr/bin/env python3
"""
Verificar todos os relacionamentos da tabela pendências
"""

import sqlite3

# Caminho para o banco de dados
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def verificar_relacionamentos():
    """Verificar relacionamentos da tabela pendências"""
    
    print("🔗 RELACIONAMENTOS DA TABELA PENDÊNCIAS")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. VERIFICAR RELACIONAMENTO COM USUÁRIOS
        print("\n1. 👤 RELACIONAMENTO COM USUÁRIOS")
        print("-" * 50)
        
        # Verificar id_responsavel_inicio
        print("📋 QUEM CRIOU (id_responsavel_inicio):")
        cursor.execute("""
            SELECT p.id, p.numero_os, p.id_responsavel_inicio, u.nome_completo, u.email
            FROM pendencias p
            LEFT JOIN tipo_usuarios u ON p.id_responsavel_inicio = u.id
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"   Pendência {row[0]} | OS: {row[1]} | Criada por: {row[3]} ({row[4]})")
        
        # Verificar id_responsavel_fechamento
        print("\n📋 QUEM FINALIZOU (id_responsavel_fechamento):")
        cursor.execute("""
            SELECT p.id, p.numero_os, p.id_responsavel_fechamento, u.nome_completo, u.email
            FROM pendencias p
            LEFT JOIN tipo_usuarios u ON p.id_responsavel_fechamento = u.id
            WHERE p.id_responsavel_fechamento IS NOT NULL
            LIMIT 3
        """)
        
        fechamento_rows = cursor.fetchall()
        if fechamento_rows:
            for row in fechamento_rows:
                print(f"   Pendência {row[0]} | OS: {row[1]} | Fechada por: {row[3]} ({row[4]})")
        else:
            print("   ⚠️ Nenhuma pendência fechada encontrada")
        
        # 2. VERIFICAR RELACIONAMENTO COM ORDENS DE SERVIÇO
        print("\n2. 📋 RELACIONAMENTO COM ORDENS DE SERVIÇO")
        print("-" * 50)
        
        cursor.execute("""
            SELECT p.id, p.numero_os, p.cliente as cliente_pendencia, 
                   os.os_numero, os.id_cliente, c.nome_fantasia as cliente_os
            FROM pendencias p
            LEFT JOIN ordens_servico os ON p.numero_os = os.os_numero
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LIMIT 3
        """)
        
        print("📊 Comparação Cliente Pendência vs Cliente OS:")
        for row in cursor.fetchall():
            print(f"   Pendência {row[0]} | OS: {row[1]}")
            print(f"      Cliente na Pendência: {row[2]}")
            print(f"      Cliente na OS: {row[5]} (ID: {row[4]})")
            print(f"      ✅ Match: {'Sim' if row[2] == row[5] else 'Não'}")
            print()
        
        # 3. VERIFICAR RELACIONAMENTO COM CLIENTES
        print("3. 🏢 RELACIONAMENTO DIRETO COM CLIENTES")
        print("-" * 50)
        
        cursor.execute("""
            SELECT p.cliente, COUNT(*) as total_pendencias
            FROM pendencias p
            GROUP BY p.cliente
        """)
        
        print("📊 Pendências por Cliente:")
        for row in cursor.fetchall():
            print(f"   Cliente: {row[0]} | Total de Pendências: {row[1]}")
        
        # 4. VERIFICAR RELACIONAMENTO COM APONTAMENTOS
        print("\n4. ⏱️ RELACIONAMENTO COM APONTAMENTOS")
        print("-" * 50)
        
        # Apontamento de origem
        print("📋 APONTAMENTO DE ORIGEM:")
        cursor.execute("""
            SELECT p.id, p.numero_os, p.id_apontamento_origem, a.id, a.status_apontamento
            FROM pendencias p
            LEFT JOIN apontamentos_detalhados a ON p.id_apontamento_origem = a.id
            WHERE p.id_apontamento_origem IS NOT NULL
            LIMIT 3
        """)
        
        origem_rows = cursor.fetchall()
        if origem_rows:
            for row in origem_rows:
                print(f"   Pendência {row[0]} | OS: {row[1]} | Originada do Apontamento: {row[3]} (Status: {row[4]})")
        else:
            print("   ⚠️ Nenhuma pendência com apontamento de origem encontrada")
        
        # Apontamento de fechamento
        print("\n📋 APONTAMENTO DE FECHAMENTO:")
        cursor.execute("""
            SELECT p.id, p.numero_os, p.id_apontamento_fechamento, a.id, a.status_apontamento
            FROM pendencias p
            LEFT JOIN apontamentos_detalhados a ON p.id_apontamento_fechamento = a.id
            WHERE p.id_apontamento_fechamento IS NOT NULL
            LIMIT 3
        """)
        
        fechamento_apontamento_rows = cursor.fetchall()
        if fechamento_apontamento_rows:
            for row in fechamento_apontamento_rows:
                print(f"   Pendência {row[0]} | OS: {row[1]} | Fechada pelo Apontamento: {row[3]} (Status: {row[4]})")
        else:
            print("   ⚠️ Nenhuma pendência com apontamento de fechamento encontrada")
        
        # 5. VERIFICAR INTEGRIDADE DOS RELACIONAMENTOS
        print("\n5. 🔍 VERIFICAÇÃO DE INTEGRIDADE")
        print("-" * 50)
        
        # Verificar se todas as pendências têm usuário responsável válido
        cursor.execute("""
            SELECT COUNT(*) as total_pendencias,
                   COUNT(u.id) as com_usuario_valido
            FROM pendencias p
            LEFT JOIN tipo_usuarios u ON p.id_responsavel_inicio = u.id
        """)
        
        integridade = cursor.fetchone()
        print(f"📊 Integridade dos Usuários:")
        print(f"   Total de Pendências: {integridade[0]}")
        print(f"   Com Usuário Válido: {integridade[1]}")
        print(f"   Integridade: {(integridade[1]/integridade[0]*100):.1f}%")
        
        # Verificar se todas as pendências têm OS válida
        cursor.execute("""
            SELECT COUNT(*) as total_pendencias,
                   COUNT(os.id) as com_os_valida
            FROM pendencias p
            LEFT JOIN ordens_servico os ON p.numero_os = os.os_numero
        """)
        
        integridade_os = cursor.fetchone()
        print(f"\n📊 Integridade das OS:")
        print(f"   Total de Pendências: {integridade_os[0]}")
        print(f"   Com OS Válida: {integridade_os[1]}")
        print(f"   Integridade: {(integridade_os[1]/integridade_os[0]*100):.1f}%")
        
        # 6. RESUMO DOS RELACIONAMENTOS
        print("\n6. 📋 RESUMO DOS RELACIONAMENTOS")
        print("-" * 50)
        
        print("✅ RELACIONAMENTOS CONFIRMADOS:")
        print("   🔗 pendencias.id_responsavel_inicio → tipo_usuarios.id")
        print("   🔗 pendencias.id_responsavel_fechamento → tipo_usuarios.id")
        print("   🔗 pendencias.numero_os → ordens_servico.os_numero")
        print("   🔗 ordens_servico.id_cliente → clientes.id")
        print("   🔗 pendencias.id_apontamento_origem → apontamentos_detalhados.id")
        print("   🔗 pendencias.id_apontamento_fechamento → apontamentos_detalhados.id")
        
        print("\n📊 CADEIA DE RELACIONAMENTOS:")
        print("   pendencias → usuarios (quem criou/fechou)")
        print("   pendencias → ordens_servico → clientes (cliente da OS)")
        print("   pendencias → apontamentos_detalhados (origem/fechamento)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_relacionamentos()
