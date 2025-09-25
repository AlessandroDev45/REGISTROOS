#!/usr/bin/env python3
"""
Script para verificar as tabelas do banco de dados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend'))

from config.database_config import get_db
from sqlalchemy import text

def main():
    print("🔍 Verificando tabelas do banco de dados...")
    
    try:
        db = next(get_db())
        
        # Listar todas as tabelas
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result]
        
        print(f"\n📊 Total de tabelas encontradas: {len(tables)}")
        print("\n📋 Lista de todas as tabelas:")
        for table in sorted(tables):
            print(f"  - {table}")
        
        # Buscar tabelas relacionadas a departamentos
        dept_tables = [t for t in tables if 'depart' in t.lower()]
        print(f"\n🏢 Tabelas relacionadas a departamentos:")
        for table in dept_tables:
            print(f"  - {table}")
        
        # Verificar estrutura da tabela tipo_setores
        print(f"\n🏭 Estrutura da tabela 'tipo_setores':")
        result = db.execute(text("PRAGMA table_info(tipo_setores)"))
        columns = list(result)
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar se existe tabela de departamentos
        if 'tipo_departamentos' in tables:
            print(f"\n🏢 Estrutura da tabela 'tipo_departamentos':")
            result = db.execute(text("PRAGMA table_info(tipo_departamentos)"))
            columns = list(result)
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print(f"\n⚠️ Tabela 'tipo_departamentos' não encontrada!")
            
        # Verificar outras possíveis tabelas de departamentos
        possible_dept_tables = ['departamentos', 'tipo_departamento', 'departamento']
        for table_name in possible_dept_tables:
            if table_name in tables:
                print(f"\n🏢 Estrutura da tabela '{table_name}':")
                result = db.execute(text(f"PRAGMA table_info({table_name})"))
                columns = list(result)
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                break
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
