#!/usr/bin/env python3
"""
Script para consultar todos os dados da tabela tipos_maquina
"""

import sqlite3

def consultar_tipos_maquina():
    """Consulta todos os dados da tabela tipos_maquina"""
    
    print("🔍 CONSULTANDO TABELA tipos_maquina")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Executar SELECT * FROM tipos_maquina
        print("📋 EXECUTANDO: SELECT * FROM tipos_maquina")
        cursor.execute("SELECT * FROM tipos_maquina")
        registros = cursor.fetchall()
        
        # Obter nomes das colunas
        cursor.execute("PRAGMA table_info(tipos_maquina)")
        colunas_info = cursor.fetchall()
        nomes_colunas = [col[1] for col in colunas_info]
        
        print(f"📊 TOTAL DE REGISTROS: {len(registros)}")
        print(f"📊 COLUNAS: {', '.join(nomes_colunas)}")
        
        print(f"\n📄 TODOS OS REGISTROS:")
        for i, reg in enumerate(registros, 1):
            print(f"\n   {i}. REGISTRO ID {reg[0]}:")
            for j, valor in enumerate(reg):
                if j < len(nomes_colunas):
                    print(f"      {nomes_colunas[j]}: {valor}")
        
        # Consulta específica para nome_tipo
        print(f"\n🔍 CONSULTANDO APENAS nome_tipo:")
        cursor.execute("SELECT id, nome_tipo FROM tipos_maquina ORDER BY nome_tipo")
        nomes = cursor.fetchall()
        
        for i, (id_reg, nome) in enumerate(nomes, 1):
            print(f"   {i}. ID: {id_reg}, Nome: {nome}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao consultar tipos de máquina: {e}")

if __name__ == "__main__":
    consultar_tipos_maquina()
