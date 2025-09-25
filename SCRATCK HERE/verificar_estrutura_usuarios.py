#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura da tabela tipo_usuarios
"""

import sqlite3

DB_PATH = 'RegistroOS/registrooficial/backend/registroos_new.db'

def verificar_estrutura():
    """Verifica estrutura da tabela tipo_usuarios"""
    print("🔍 VERIFICANDO ESTRUTURA DA TABELA tipo_usuarios...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar estrutura
        cursor.execute("PRAGMA table_info(tipo_usuarios)")
        colunas = cursor.fetchall()
        
        print(f"\n📋 COLUNAS DA TABELA tipo_usuarios:")
        for coluna in colunas:
            print(f"   - {coluna[1]} ({coluna[2]}) {'NOT NULL' if coluna[3] else 'NULL'}")
        
        # Verificar alguns registros
        cursor.execute("SELECT * FROM tipo_usuarios LIMIT 3")
        registros = cursor.fetchall()
        
        print(f"\n📊 PRIMEIROS 3 REGISTROS:")
        for i, registro in enumerate(registros):
            print(f"   Registro {i+1}: {registro}")
        
        # Verificar supervisores
        cursor.execute("SELECT id, nome_completo, email, privilege_level FROM tipo_usuarios WHERE privilege_level IN ('SUPERVISOR', 'GESTAO')")
        supervisores = cursor.fetchall()
        
        print(f"\n👨‍💼 SUPERVISORES/GESTORES ({len(supervisores)}):")
        for sup in supervisores:
            print(f"   - ID {sup[0]}: {sup[1]} ({sup[3]}) - {sup[2]}")
        
        # Verificar setores
        cursor.execute("SELECT id, nome, departamento FROM tipo_setores LIMIT 5")
        setores = cursor.fetchall()
        
        print(f"\n🏭 SETORES (primeiros 5):")
        for setor in setores:
            print(f"   - ID {setor[0]}: {setor[1]} ({setor[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_estrutura()
