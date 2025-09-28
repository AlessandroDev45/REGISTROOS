#!/usr/bin/env python3
"""
Script para verificar as tabelas do banco de dados
"""

import sqlite3
import os

DB_PATH = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"

def verificar_tabelas():
    """Verificar todas as tabelas do banco"""
    print("🔍 Verificando tabelas do banco...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tabelas = cursor.fetchall()
        
        print(f"📊 Encontradas {len(tabelas)} tabelas:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        
        # Verificar tabelas específicas que precisamos
        tabelas_necessarias = [
            'apontamento_detalhado', 'pendencia', 'programacao', 
            'ordem_servico', 'ordens_servico', 'apontamentos'
        ]
        
        print(f"\n🎯 Verificando tabelas necessárias:")
        for tabela_nome in tabelas_necessarias:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela_nome,))
            existe = cursor.fetchone()
            if existe:
                print(f"   ✅ {tabela_nome} - EXISTE")
                
                # Mostrar estrutura da tabela
                cursor.execute(f"PRAGMA table_info({tabela_nome})")
                colunas = cursor.fetchall()
                print(f"      Colunas ({len(colunas)}):")
                for coluna in colunas[:5]:  # Mostrar apenas as primeiras 5
                    print(f"         - {coluna[1]} ({coluna[2]})")
                if len(colunas) > 5:
                    print(f"         ... e mais {len(colunas) - 5} colunas")
            else:
                print(f"   ❌ {tabela_nome} - NÃO EXISTE")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")

if __name__ == "__main__":
    verificar_tabelas()
