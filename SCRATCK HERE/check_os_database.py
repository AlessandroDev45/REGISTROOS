#!/usr/bin/env python3
"""
Verificar ordens de serviço no banco de dados
"""

import sqlite3
import os

DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def check_ordens_servico():
    """Verificar ordens de serviço disponíveis no banco"""
    print("🔍 VERIFICANDO ORDENS DE SERVIÇO NO BANCO DE DADOS")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ordem%';")
        tables = cursor.fetchall()
        print(f"📋 Tabelas relacionadas a ordem: {tables}")
        
        # Tentar diferentes nomes de tabela
        possible_tables = ['ordens_servico', 'ordem_servico', 'os', 'OrdemServico']
        
        for table_name in possible_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"✅ Tabela '{table_name}' encontrada com {count} registros")
                
                # Buscar algumas ordens de serviço
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                print(f"📊 Colunas: {columns}")
                print(f"📋 Primeiras 5 ordens:")
                for i, row in enumerate(rows, 1):
                    print(f"   {i}. {dict(zip(columns, row))}")
                
                # Procurar especificamente por os_numero
                if 'os_numero' in columns:
                    cursor.execute(f"SELECT os_numero FROM {table_name} LIMIT 10;")
                    os_numbers = cursor.fetchall()
                    print(f"🔢 Números de OS disponíveis: {[os[0] for os in os_numbers]}")
                
                break
                
            except sqlite3.OperationalError as e:
                if "no such table" not in str(e):
                    print(f"❌ Erro ao consultar tabela '{table_name}': {e}")
                continue
        else:
            print("❌ Nenhuma tabela de ordens de serviço encontrada")
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            all_tables = cursor.fetchall()
            print(f"📋 Todas as tabelas no banco: {[t[0] for t in all_tables]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco de dados: {e}")

if __name__ == "__main__":
    check_ordens_servico()
