#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela ordens_servico
"""

import sqlite3

def verificar_estrutura():
    """Verifica a estrutura da tabela ordens_servico"""
    
    print("🔍 VERIFICANDO ESTRUTURA DA TABELA ordens_servico")
    print("=" * 60)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        print("📋 ESTRUTURA DA TABELA ordens_servico:")
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas = cursor.fetchall()
        
        if colunas:
            print(f"✅ {len(colunas)} colunas encontradas:")
            for i, (cid, nome, tipo, notnull, default, pk) in enumerate(colunas, 1):
                pk_str = " (PK)" if pk else ""
                notnull_str = " NOT NULL" if notnull else ""
                default_str = f" DEFAULT {default}" if default else ""
                print(f"   {i:2d}. {nome:<25} {tipo:<15}{notnull_str}{default_str}{pk_str}")
        else:
            print(f"❌ Tabela ordens_servico não encontrada")
        
        # Verificar se há dados na tabela
        cursor.execute("SELECT COUNT(*) FROM ordens_servico")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total}")
        
        if total > 0:
            # Mostrar alguns exemplos
            cursor.execute("SELECT * FROM ordens_servico LIMIT 3")
            exemplos = cursor.fetchall()
            print(f"\n📋 EXEMPLOS DE DADOS:")
            for i, exemplo in enumerate(exemplos, 1):
                print(f"   Registro {i}: {exemplo[:5]}...")  # Primeiros 5 campos
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    verificar_estrutura()
