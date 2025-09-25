#!/usr/bin/env python3
"""
Script para verificar a estrutura e dados da tabela tipos_atividade
"""

import sqlite3
import json

def verificar_tabela():
    """Verifica a estrutura e dados da tabela tipos_atividade"""
    
    print("🔍 VERIFICANDO TABELA tipos_atividade")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        db_path = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tipos_atividade'")
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            print("❌ TABELA tipos_atividade NÃO EXISTE!")
            
            # Verificar tabelas similares
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%atividade%'")
            tabelas_similares = cursor.fetchall()
            
            print("🔍 TABELAS SIMILARES ENCONTRADAS:")
            for tabela in tabelas_similares:
                print(f"   - {tabela[0]}")
            
            return
        
        # Verificar estrutura da tabela
        print("📋 ESTRUTURA DA TABELA:")
        cursor.execute("PRAGMA table_info(tipos_atividade)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - PK: {col[5]} - NotNull: {col[3]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM tipos_atividade")
        total = cursor.fetchone()[0]
        print(f"\n📊 TOTAL DE REGISTROS: {total}")
        
        # Contar registros ativos
        cursor.execute("SELECT COUNT(*) FROM tipos_atividade WHERE ativo = 1")
        ativos = cursor.fetchone()[0]
        print(f"📊 REGISTROS ATIVOS: {ativos}")
        
        # Mostrar alguns registros
        print(f"\n📄 PRIMEIROS 5 REGISTROS:")
        cursor.execute("SELECT * FROM tipos_atividade LIMIT 5")
        registros = cursor.fetchall()
        
        for i, reg in enumerate(registros, 1):
            print(f"   {i}. ID: {reg[0]}")
            if len(reg) > 1:
                print(f"      nome_tipo: {reg[1] if len(reg) > 1 else 'N/A'}")
            if len(reg) > 2:
                print(f"      descricao: {reg[2] if len(reg) > 2 else 'N/A'}")
            if len(reg) > 3:
                print(f"      ativo: {reg[3] if len(reg) > 3 else 'N/A'}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e}")

if __name__ == "__main__":
    verificar_tabela()
