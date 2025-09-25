#!/usr/bin/env python3
"""
Script para adicionar campos categoria nas tabelas que precisam
- tipo_atividade
- tipo_descricao_atividade  
- tipo_falha
"""

import sqlite3
import os
import sys

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def adicionar_campo_categoria():
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'registroos_new.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista de tabelas e campos para verificar/adicionar
        tabelas_campos = [
            ('tipo_atividade', 'categoria', 'VARCHAR(50)'),
            ('tipo_descricao_atividade', 'categoria', 'VARCHAR(50)'),
            ('tipo_falha', 'categoria', 'VARCHAR(50)')
        ]
        
        for tabela, campo, tipo_campo in tabelas_campos:
            print(f"\n🔍 Verificando tabela '{tabela}'...")
            
            # Verificar se a tabela existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
            if not cursor.fetchone():
                print(f"⚠️  Tabela '{tabela}' não encontrada, pulando...")
                continue
            
            # Verificar se a coluna já existe
            cursor.execute(f"PRAGMA table_info({tabela})")
            columns = [column[1] for column in cursor.fetchall()]
            
            if campo in columns:
                print(f"✅ Campo '{campo}' já existe na tabela '{tabela}'")
            else:
                print(f"🔄 Adicionando campo '{campo}' na tabela '{tabela}'...")
                try:
                    cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {campo} {tipo_campo} NULL")
                    print(f"✅ Campo '{campo}' adicionado com sucesso na tabela '{tabela}'!")
                except Exception as e:
                    print(f"❌ Erro ao adicionar campo '{campo}' na tabela '{tabela}': {str(e)}")
        
        # Commit das alterações
        conn.commit()
        print(f"\n✅ Todas as alterações foram salvas no banco de dados!")
        
        # Verificar estrutura final
        print(f"\n🔍 Verificando estrutura final das tabelas...")
        for tabela, campo, _ in tabelas_campos:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
            if cursor.fetchone():
                cursor.execute(f"PRAGMA table_info({tabela})")
                columns = [column[1] for column in cursor.fetchall()]
                if campo in columns:
                    print(f"✅ {tabela}.{campo} - OK")
                else:
                    print(f"❌ {tabela}.{campo} - FALTANDO")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando adição de campos categoria...")
    success = adicionar_campo_categoria()
    if success:
        print("\n🎉 Script executado com sucesso!")
    else:
        print("\n💥 Script falhou!")
        sys.exit(1)
