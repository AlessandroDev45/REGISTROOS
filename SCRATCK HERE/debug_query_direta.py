#!/usr/bin/env python3
"""
Debug direto da query SQL para verificar o problema
"""

import sqlite3
import sys
import os

# Caminho para o banco de dados
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def test_query_direta():
    """Testar a query SQL diretamente no banco"""
    
    print("🔍 TESTANDO QUERY SQL DIRETAMENTE NO BANCO")
    print("=" * 60)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Verificar se a tabela pendencias existe
        print("\n1. 📋 Verificando tabela pendencias...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pendencias'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("   ✅ Tabela pendencias existe")
        else:
            print("   ❌ Tabela pendencias NÃO existe")
            return
        
        # 2. Verificar estrutura da tabela
        print("\n2. 🏗️ Estrutura da tabela pendencias:")
        cursor.execute("PRAGMA table_info(pendencias)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # 3. Contar total de registros
        print("\n3. 📊 Total de registros na tabela:")
        cursor.execute("SELECT COUNT(*) FROM pendencias")
        total = cursor.fetchone()[0]
        print(f"   Total: {total} pendências")
        
        # 4. Testar a query exata do dashboard
        print("\n4. 🔍 Testando query exata do dashboard:")
        query = """
            SELECT p.id, p.status, p.data_inicio, p.data_fechamento
            FROM pendencias p
            WHERE 1=1
        """
        print(f"   Query: {query.strip()}")
        
        cursor.execute(query)
        results = cursor.fetchall()
        print(f"   Resultados: {len(results)} registros")
        
        if results:
            print("   📋 Primeiros registros:")
            for i, row in enumerate(results[:3], 1):
                print(f"      {i}. ID: {row[0]} | Status: {row[1]} | Data: {row[2]}")
        else:
            print("   ❌ NENHUM RESULTADO RETORNADO!")
        
        # 5. Verificar dados específicos
        print("\n5. 📋 Dados específicos das pendências:")
        cursor.execute("SELECT id, status, data_inicio FROM pendencias LIMIT 5")
        all_pendencias = cursor.fetchall()
        
        for pend in all_pendencias:
            print(f"   ID: {pend[0]} | Status: {pend[1]} | Data: {pend[2]}")
        
        # 6. Testar query com JOIN (como no backend)
        print("\n6. 🔗 Testando query com JOIN:")
        join_query = """
            SELECT p.id, p.status, p.data_inicio, p.data_fechamento,
                   u.nome_completo as responsavel
            FROM pendencias p
            LEFT JOIN tipo_usuarios u ON p.id_responsavel_inicio = u.id
            WHERE 1=1
        """
        
        try:
            cursor.execute(join_query)
            join_results = cursor.fetchall()
            print(f"   ✅ Query com JOIN: {len(join_results)} resultados")
            
            if join_results:
                for i, row in enumerate(join_results[:3], 1):
                    print(f"      {i}. ID: {row[0]} | Status: {row[1]} | Responsável: {row[4]}")
        except Exception as e:
            print(f"   ❌ Erro na query com JOIN: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_direta()
