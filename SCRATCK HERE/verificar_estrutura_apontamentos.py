#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura das tabelas apontamentos e pendências
"""

import sqlite3

DB_PATH = 'RegistroOS/registrooficial/backend/registroos_new.db'

def verificar_estrutura():
    """Verifica estrutura das tabelas"""
    print("🔍 VERIFICANDO ESTRUTURAS...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar tabelas relacionadas a apontamentos
        tabelas = ['apontamentos_detalhados', 'pendencias', 'ordens_servico']
        
        for tabela in tabelas:
            print(f"\n📋 TABELA: {tabela}")
            try:
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas = cursor.fetchall()
                
                print(f"   COLUNAS ({len(colunas)}):")
                for coluna in colunas:
                    print(f"      - {coluna[1]} ({coluna[2]})")
                
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"   REGISTROS: {count}")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {tabela} LIMIT 1")
                    exemplo = cursor.fetchone()
                    print(f"   EXEMPLO: {exemplo}")
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    verificar_estrutura()
