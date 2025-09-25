#!/usr/bin/env python3
"""
🔍 VERIFICAR: Apontamentos no banco de dados
Verifica se existem apontamentos na tabela apontamentos_detalhados
"""

import sqlite3
import os

def verificar_apontamentos():
    # Caminho para o banco de dados
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"

    print(f"🔍 Procurando banco de dados em: {db_path}")
    print(f"📁 Caminho absoluto: {os.path.abspath(db_path)}")
    print(f"📋 Arquivo existe: {os.path.exists(db_path)}")

    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        # Tentar outros caminhos possíveis
        alternative_paths = [
            "RegistroOS/registrooficial/backend/app/registroos_new.db",
            "registroos_new.db"
        ]

        for alt_path in alternative_paths:
            print(f"🔍 Tentando: {alt_path}")
            if os.path.exists(alt_path):
                print(f"✅ Encontrado em: {alt_path}")
                db_path = alt_path
                break
        else:
            print("❌ Banco de dados não encontrado em nenhum local")
            return
    
    print("🔍 VERIFICAÇÃO: Apontamentos no banco de dados")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar se a tabela existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='apontamentos_detalhados'
        """)
        
        if not cursor.fetchone():
            print("❌ Tabela 'apontamentos_detalhados' não encontrada")
            return
        
        print("✅ Tabela 'apontamentos_detalhados' encontrada")
        
        # 2. Contar total de apontamentos
        cursor.execute("SELECT COUNT(*) FROM apontamentos_detalhados")
        total = cursor.fetchone()[0]
        print(f"📊 Total de apontamentos: {total}")
        
        if total > 0:
            # 3. Mostrar alguns exemplos
            cursor.execute("""
                SELECT id, numero_os, data_hora_inicio, status_apontamento, 
                       setor, departamento, tipo_atividade
                FROM apontamentos_detalhados 
                ORDER BY id DESC 
                LIMIT 5
            """)
            
            apontamentos = cursor.fetchall()
            print(f"\n📋 Últimos {len(apontamentos)} apontamentos:")
            
            for apt in apontamentos:
                print(f"   ID: {apt[0]} | OS: {apt[1]} | Data: {apt[2]} | Status: {apt[3]}")
                print(f"   Setor: {apt[4]} | Depto: {apt[5]} | Atividade: {apt[6]}")
                print("   " + "-" * 50)
        else:
            print("⚠️ Nenhum apontamento encontrado na tabela")
            
            # Verificar se existem outras tabelas relacionadas
            print("\n🔍 Verificando outras tabelas...")
            
            # Verificar ordens de serviço
            cursor.execute("SELECT COUNT(*) FROM ordens_servico")
            os_count = cursor.fetchone()[0]
            print(f"📋 Ordens de serviço: {os_count}")
            
            # Verificar usuários
            cursor.execute("SELECT COUNT(*) FROM tipo_usuarios")
            users_count = cursor.fetchone()[0]
            print(f"👥 Usuários: {users_count}")
            
            # Verificar setores
            cursor.execute("SELECT COUNT(*) FROM tipo_setores")
            setores_count = cursor.fetchone()[0]
            print(f"🏢 Setores: {setores_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {e}")

if __name__ == "__main__":
    verificar_apontamentos()
