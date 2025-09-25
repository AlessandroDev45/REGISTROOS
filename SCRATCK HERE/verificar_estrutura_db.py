#!/usr/bin/env python3
"""
🔍 VERIFICAR: Estrutura das tabelas
Verifica a estrutura das tabelas no banco de dados
"""

import sqlite3
import os

def verificar_estrutura():
    # Caminho para o banco de dados
    db_path = "RegistroOS/registrooficial/backend/registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    print("🔍 VERIFICAÇÃO: Estrutura das tabelas")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela tipo_setores
        print("\n📋 Estrutura da tabela 'tipo_setores':")
        cursor.execute("PRAGMA table_info(tipo_setores)")
        colunas_setores = cursor.fetchall()
        for col in colunas_setores:
            print(f"   {col[1]} ({col[2]})")
        
        # Verificar estrutura da tabela tipo_usuarios
        print("\n👥 Estrutura da tabela 'tipo_usuarios':")
        cursor.execute("PRAGMA table_info(tipo_usuarios)")
        colunas_usuarios = cursor.fetchall()
        for col in colunas_usuarios:
            print(f"   {col[1]} ({col[2]})")

        # Verificar estrutura da tabela apontamentos_detalhados
        print("\n📊 Estrutura da tabela 'apontamentos_detalhados':")
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas_apontamentos = cursor.fetchall()
        for col in colunas_apontamentos:
            print(f"   {col[1]} ({col[2]})")
        
        # Mostrar alguns dados de exemplo
        print("\n📋 Dados de exemplo - Setores:")
        cursor.execute("SELECT * FROM tipo_setores LIMIT 3")
        setores = cursor.fetchall()
        for setor in setores:
            print(f"   {setor}")
        
        print("\n👥 Dados de exemplo - Usuários:")
        cursor.execute("SELECT * FROM tipo_usuarios LIMIT 3")
        usuarios = cursor.fetchall()
        for usuario in usuarios:
            print(f"   {usuario}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    verificar_estrutura()
