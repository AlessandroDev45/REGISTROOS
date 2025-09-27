#!/usr/bin/env python3
"""
Verificar estrutura real da tabela de programações no banco
"""

import sqlite3
import os

def main():
    print("🔍 VERIFICANDO TABELA REAL DE PROGRAMAÇÕES")
    print("=" * 60)
    
    # Caminho do banco
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verificar quais tabelas existem com "programac"
        print("1. 🔍 Tabelas com 'programac'...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%programac%'")
        tabelas = cursor.fetchall()
        
        for tabela in tabelas:
            print(f"   📋 Tabela encontrada: {tabela[0]}")
        
        # 2. Verificar estrutura de cada tabela
        for tabela in tabelas:
            nome_tabela = tabela[0]
            print(f"\n2. 📊 Estrutura da tabela '{nome_tabela}':")
            
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas = cursor.fetchall()
            
            for coluna in colunas:
                print(f"   - {coluna[1]} ({coluna[2]}) {'NOT NULL' if coluna[3] else 'NULL'}")
            
            # Verificar dados
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            count = cursor.fetchone()[0]
            print(f"   📊 Total de registros: {count}")
            
            if count > 0:
                print(f"   📋 Primeiros 3 registros:")
                cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
                registros = cursor.fetchall()
                
                for i, registro in enumerate(registros, 1):
                    print(f"      {i}. {registro}")
        
        # 3. Verificar se existe programacao_pcp
        print(f"\n3. 🔍 Verificando 'programacao_pcp'...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='programacao_pcp'")
        pcp_table = cursor.fetchone()
        
        if pcp_table:
            print(f"   ✅ Tabela 'programacao_pcp' existe!")
            
            cursor.execute("PRAGMA table_info(programacao_pcp)")
            colunas = cursor.fetchall()
            
            print(f"   📊 Estrutura:")
            for coluna in colunas:
                print(f"      - {coluna[1]} ({coluna[2]}) {'NOT NULL' if coluna[3] else 'NULL'}")
            
            cursor.execute("SELECT COUNT(*) FROM programacao_pcp")
            count = cursor.fetchone()[0]
            print(f"   📊 Total de registros: {count}")
            
            if count > 0:
                print(f"   📋 Todos os registros:")
                cursor.execute("SELECT * FROM programacao_pcp")
                registros = cursor.fetchall()
                
                for i, registro in enumerate(registros, 1):
                    print(f"      {i}. {registro}")
        else:
            print(f"   ❌ Tabela 'programacao_pcp' NÃO existe!")
        
        # 4. Verificar qual tabela o PCP realmente usa
        print(f"\n4. 🏭 Testando query do PCP...")
        try:
            cursor.execute("""
                SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                       p.fim_previsto, p.status, p.observacoes,
                       os.os_numero
                FROM programacoes p
                LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
                LIMIT 3
            """)
            resultados = cursor.fetchall()
            print(f"   ✅ Query 'programacoes' funciona! {len(resultados)} registros")
            for resultado in resultados:
                print(f"      {resultado}")
        except Exception as e:
            print(f"   ❌ Query 'programacoes' falhou: {e}")
        
        try:
            cursor.execute("""
                SELECT p.id, p.id_ordem_servico, p.responsavel_id, p.inicio_previsto,
                       p.fim_previsto, p.status, p.observacoes,
                       os.os_numero
                FROM programacao_pcp p
                LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
                LIMIT 3
            """)
            resultados = cursor.fetchall()
            print(f"   ✅ Query 'programacao_pcp' funciona! {len(resultados)} registros")
            for resultado in resultados:
                print(f"      {resultado}")
        except Exception as e:
            print(f"   ❌ Query 'programacao_pcp' falhou: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
