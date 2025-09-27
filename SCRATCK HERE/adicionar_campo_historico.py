#!/usr/bin/env python3
"""
ADICIONAR CAMPO HISTÓRICO À TABELA PROGRAMACOES
==============================================

Adiciona o campo 'historico' à tabela programacoes para separar
observações editáveis do histórico não editável.
"""

import sqlite3
import os

def adicionar_campo_historico():
    """Adicionar campo histórico à tabela programacoes"""
    
    # Caminho do banco de dados
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura atual da tabela programacoes...")
        
        # Verificar se o campo já existe
        cursor.execute("PRAGMA table_info(programacoes)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        print(f"📋 Colunas atuais: {colunas}")
        
        if 'historico' in colunas:
            print("ℹ️ Campo 'historico' já existe na tabela programacoes")
            return True
        
        print("➕ Adicionando campo 'historico' à tabela programacoes...")
        
        # Adicionar o campo histórico
        cursor.execute("ALTER TABLE programacoes ADD COLUMN historico TEXT")
        
        print("✅ Campo 'historico' adicionado com sucesso!")
        
        # Migrar dados existentes das observações para histórico
        print("🔄 Migrando dados existentes...")
        
        cursor.execute("""
            UPDATE programacoes 
            SET historico = CASE 
                WHEN observacoes IS NOT NULL AND observacoes != '' 
                THEN '[MIGRAÇÃO] ' || observacoes 
                ELSE '[CRIAÇÃO] Programação criada'
            END
            WHERE historico IS NULL
        """)
        
        rows_updated = cursor.rowcount
        print(f"✅ {rows_updated} registros migrados!")
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(programacoes)")
        colunas_finais = [col[1] for col in cursor.fetchall()]
        
        print(f"📋 Colunas finais: {colunas_finais}")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar campo: {e}")
        return False

def verificar_programacoes():
    """Verificar algumas programações após a migração"""
    
    db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📋 Verificando programações após migração...")
        
        cursor.execute("""
            SELECT id, observacoes, historico, status, created_at
            FROM programacoes 
            ORDER BY id DESC 
            LIMIT 5
        """)
        
        programacoes = cursor.fetchall()
        
        for prog in programacoes:
            print(f"\n📋 Programação ID {prog[0]}:")
            print(f"   Observações: {prog[1] or 'Vazio'}")
            print(f"   Histórico: {prog[2] or 'Vazio'}")
            print(f"   Status: {prog[3] or 'N/A'}")
            print(f"   Criado em: {prog[4] or 'N/A'}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar programações: {e}")

def main():
    """Função principal"""
    print("🔧 ADICIONAR CAMPO HISTÓRICO À TABELA PROGRAMACOES")
    print("=" * 60)
    
    # 1. Adicionar campo
    sucesso = adicionar_campo_historico()
    
    if sucesso:
        # 2. Verificar resultado
        verificar_programacoes()
        
        print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("   1. Reiniciar o backend para aplicar as mudanças")
        print("   2. Testar a funcionalidade de histórico")
        print("   3. Verificar se as programações aparecem no dashboard")
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        print("💡 Verifique os erros acima e tente novamente")

if __name__ == "__main__":
    main()
