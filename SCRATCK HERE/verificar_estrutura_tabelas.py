#!/usr/bin/env python3
"""
Script para verificar a estrutura das tabelas ordens_servico e programacoes
"""

import sqlite3
import os

def verificar_estrutura_tabelas():
    # Procurar pelo banco de dados
    possible_paths = [
        "RegistroOS/registrooficial/backend/registroos_new.db",
        "RegistroOS/registrooficial/backend/app/registroos_new.db",
        "registrooficial/backend/registroos_new.db",
        "registrooficial/backend/app/registroos_new.db",
        "registrooficial/backend/database.db",
        "registrooficial/backend/app/database.db",
        "backend/database.db",
        "database.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Banco de dados não encontrado!")
        return
    
    print(f"✅ Banco encontrado em: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela ordens_servico
        print("\n" + "="*50)
        print("ESTRUTURA DA TABELA: ordens_servico")
        print("="*50)
        
        cursor.execute("PRAGMA table_info(ordens_servico)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"- {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PK' if col[5] else ''}")
        
        # Verificar estrutura da tabela programacoes
        print("\n" + "="*50)
        print("ESTRUTURA DA TABELA: programacoes")
        print("="*50)
        
        cursor.execute("PRAGMA table_info(programacoes)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"- {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PK' if col[5] else ''}")
        
        # Verificar dados de exemplo
        print("\n" + "="*50)
        print("EXEMPLO DE DADOS - ordens_servico (1 registro)")
        print("="*50)
        
        cursor.execute("SELECT * FROM ordens_servico LIMIT 1")
        row = cursor.fetchone()
        if row:
            cursor.execute("PRAGMA table_info(ordens_servico)")
            columns = [col[1] for col in cursor.fetchall()]
            for i, value in enumerate(row):
                print(f"{columns[i]}: {value}")
        else:
            print("Nenhum registro encontrado")
        
        print("\n" + "="*50)
        print("EXEMPLO DE DADOS - programacoes (1 registro)")
        print("="*50)
        
        cursor.execute("SELECT * FROM programacoes LIMIT 1")
        row = cursor.fetchone()
        if row:
            cursor.execute("PRAGMA table_info(programacoes)")
            columns = [col[1] for col in cursor.fetchall()]
            for i, value in enumerate(row):
                print(f"{columns[i]}: {value}")
        else:
            print("Nenhum registro encontrado")
        
        # Verificar campos relacionados a departamento e setor
        print("\n" + "="*50)
        print("CAMPOS RELACIONADOS A DEPARTAMENTO/SETOR")
        print("="*50)
        
        # ordens_servico
        cursor.execute("PRAGMA table_info(ordens_servico)")
        os_columns = [col[1] for col in cursor.fetchall()]
        
        dept_setor_fields_os = [col for col in os_columns if any(keyword in col.lower() for keyword in ['departamento', 'setor', 'supervisor'])]
        print(f"ordens_servico: {dept_setor_fields_os}")
        
        # programacoes
        cursor.execute("PRAGMA table_info(programacoes)")
        prog_columns = [col[1] for col in cursor.fetchall()]
        
        dept_setor_fields_prog = [col for col in prog_columns if any(keyword in col.lower() for keyword in ['departamento', 'setor', 'supervisor'])]
        print(f"programacoes: {dept_setor_fields_prog}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")

if __name__ == "__main__":
    verificar_estrutura_tabelas()
