#!/usr/bin/env python3
"""
ADICIONAR CAMPO RESULTADO_GLOBAL - RegistroOS
============================================

Script para adicionar o campo resultado_global na tabela apontamentos_detalhados.
"""

import sqlite3
import os
import sys

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

def adicionar_campo_resultado_global():
    """Adiciona o campo resultado_global na tabela apontamentos_detalhados"""
    
    # Caminho do banco de dados
    db_path = os.path.join(backend_path, 'registroos_new.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    print("🔧 ADICIONANDO CAMPO RESULTADO_GLOBAL")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'resultado_global' in columns:
            print("✅ Campo resultado_global já existe na tabela")
            conn.close()
            return True
        
        # Adicionar a coluna
        print("📝 Adicionando coluna resultado_global...")
        cursor.execute("""
            ALTER TABLE apontamentos_detalhados 
            ADD COLUMN resultado_global TEXT
        """)
        
        # Verificar se foi adicionada
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        if 'resultado_global' in columns_after:
            print("✅ Campo resultado_global adicionado com sucesso!")
            
            # Atualizar registros existentes com valor padrão
            cursor.execute("""
                UPDATE apontamentos_detalhados 
                SET resultado_global = 'PENDENTE' 
                WHERE resultado_global IS NULL
            """)
            
            rows_updated = cursor.rowcount
            print(f"📊 {rows_updated} registros atualizados com valor padrão 'PENDENTE'")
            
            conn.commit()
            print("💾 Alterações salvas no banco de dados")
            
        else:
            print("❌ Erro: Campo não foi adicionado")
            conn.rollback()
            return False
            
    except Exception as e:
        print(f"❌ Erro ao adicionar campo: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    print("\n" + "=" * 50)
    print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO")
    print("\n🎯 RESUMO:")
    print("   - Campo resultado_global: ✅ Adicionado")
    print("   - Tipo: TEXT")
    print("   - Valor padrão: PENDENTE")
    print("   - Registros existentes: ✅ Atualizados")
    print("\n📋 VALORES POSSÍVEIS:")
    print("   - APROVADO")
    print("   - REPROVADO") 
    print("   - APROVADO_COM_RESTRICAO")
    print("   - PENDENTE")
    print("   - EM_ANALISE")
    print("=" * 50)
    
    return True

def verificar_estrutura_tabela():
    """Verifica a estrutura atual da tabela apontamentos_detalhados"""
    
    db_path = os.path.join(backend_path, 'registroos_new.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📋 ESTRUTURA ATUAL DA TABELA apontamentos_detalhados:")
        print("-" * 60)
        
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        columns = cursor.fetchall()
        
        for i, (cid, name, type_, notnull, default, pk) in enumerate(columns, 1):
            pk_marker = " (PK)" if pk else ""
            null_marker = " NOT NULL" if notnull else ""
            default_marker = f" DEFAULT {default}" if default else ""
            print(f"{i:2d}. {name:<25} {type_:<10}{null_marker}{default_marker}{pk_marker}")
        
        print(f"\nTotal de colunas: {len(columns)}")
        
        # Verificar se resultado_global existe
        column_names = [col[1] for col in columns]
        if 'resultado_global' in column_names:
            print("✅ Campo resultado_global: PRESENTE")
        else:
            print("❌ Campo resultado_global: AUSENTE")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    print("🧪 MIGRAÇÃO - ADICIONAR CAMPO RESULTADO_GLOBAL")
    print("=" * 60)
    
    # Verificar estrutura antes
    verificar_estrutura_tabela()
    
    # Adicionar campo
    sucesso = adicionar_campo_resultado_global()
    
    if sucesso:
        # Verificar estrutura depois
        verificar_estrutura_tabela()
    else:
        print("❌ Migração falhou!")
        sys.exit(1)
