#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura da tabela programacoes
"""

import sqlite3

DB_PATH = 'RegistroOS/registrooficial/backend/registroos_new.db'

def verificar_estrutura():
    """Verifica estrutura da tabela programacoes"""
    print("🔍 VERIFICANDO ESTRUTURA DA TABELA programacoes...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura
        cursor.execute("PRAGMA table_info(programacoes)")
        colunas = cursor.fetchall()
        
        print(f"\n📋 COLUNAS DA TABELA programacoes:")
        for coluna in colunas:
            print(f"   - {coluna[1]} ({coluna[2]}) {'NOT NULL' if coluna[3] else 'NULL'}")
        
        # Verificar alguns registros
        cursor.execute("SELECT * FROM programacoes LIMIT 3")
        registros = cursor.fetchall()
        
        print(f"\n📊 REGISTROS EXISTENTES ({len(registros)}):")
        for i, registro in enumerate(registros):
            print(f"   Registro {i+1}: {registro}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura()
