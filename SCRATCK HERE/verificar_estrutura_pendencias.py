#!/usr/bin/env python3
"""
Verificar estrutura da tabela pendências
"""

import sqlite3

# Caminho para o banco de dados
DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def verificar_estrutura():
    """Verificar estrutura da tabela pendências"""
    
    print("📋 ESTRUTURA DA TABELA PENDÊNCIAS")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(pendencias)")
        columns = cursor.fetchall()
        
        print(f"📊 Total de colunas: {len(columns)}")
        print()
        
        for i, col in enumerate(columns, 1):
            col_name = col[1]
            col_type = col[2]
            not_null = "Não" if col[3] == 0 else "Sim"
            default_val = col[4] if col[4] is not None else "NULL"
            is_pk = "Sim" if col[5] == 1 else "Não"
            
            print(f"{i:2d}. {col_name:30} | {col_type:15} | NOT NULL: {not_null:3} | PK: {is_pk}")
        
        print("\n" + "=" * 60)
        print("🔍 CAMPOS DE AUDITORIA IDENTIFICADOS:")
        print("=" * 60)
        
        auditoria_fields = []
        for col in columns:
            col_name = col[1].lower()
            if any(keyword in col_name for keyword in ['data_', 'criado', 'responsavel', 'fechamento', 'inicio', 'atualizacao']):
                auditoria_fields.append((col[1], col[2]))
        
        if auditoria_fields:
            for field_name, field_type in auditoria_fields:
                print(f"✅ {field_name:30} | {field_type}")
        else:
            print("❌ Nenhum campo de auditoria encontrado")
        
        # Verificar dados de exemplo
        print("\n" + "=" * 60)
        print("📋 EXEMPLO DE DADOS (Primeira pendência):")
        print("=" * 60)
        
        cursor.execute("SELECT * FROM pendencias LIMIT 1")
        sample_data = cursor.fetchone()
        
        if sample_data:
            for i, (col_info, value) in enumerate(zip(columns, sample_data)):
                col_name = col_info[1]
                print(f"{col_name:30} = {value}")
        else:
            print("❌ Nenhum dado encontrado na tabela")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura()
