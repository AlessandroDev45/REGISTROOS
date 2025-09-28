#!/usr/bin/env python3
"""
Script para mostrar as colunas exatas das tabelas
"""

import sqlite3

DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def mostrar_colunas_detalhadas(cursor, tabela):
    """Mostrar colunas detalhadas de uma tabela"""
    print(f"\n📋 TABELA: {tabela.upper()}")
    print("-" * 60)
    
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = cursor.fetchall()
    
    print(f"Total de colunas: {len(colunas)}")
    print("\nColunas:")
    
    for col in colunas:
        cid, nome, tipo, not_null, default, pk = col
        pk_str = " (PK)" if pk else ""
        not_null_str = " NOT NULL" if not_null else ""
        default_str = f" DEFAULT {default}" if default else ""
        print(f"  {nome:<25} {tipo:<15}{pk_str}{not_null_str}{default_str}")

def main():
    """Função principal"""
    print("🔍 ESTRUTURA DETALHADA DAS TABELAS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Mostrar estruturas das tabelas principais
        tabelas = ['apontamentos_detalhados', 'pendencias', 'programacoes']
        
        for tabela in tabelas:
            mostrar_colunas_detalhadas(cursor, tabela)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
