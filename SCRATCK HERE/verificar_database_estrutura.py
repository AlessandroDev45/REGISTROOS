#!/usr/bin/env python3
"""
Script para verificar a estrutura real da database e comparar com frontend/backend
"""

import sqlite3
import json

DB_PATH = "RegistroOS/registrooficial/backend/registroos_new.db"

def verificar_tabela(cursor, nome_tabela):
    """Verifica a estrutura de uma tabela"""
    print(f"\n📋 TABELA: {nome_tabela}")
    print("=" * 50)
    
    # Verificar se a tabela existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (nome_tabela,))
    if not cursor.fetchone():
        print(f"❌ Tabela {nome_tabela} não existe!")
        return
    
    # Obter estrutura da tabela
    cursor.execute(f"PRAGMA table_info({nome_tabela})")
    colunas = cursor.fetchall()
    
    print("🏗️  ESTRUTURA:")
    for col in colunas:
        print(f"   {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
    
    # Obter alguns dados de exemplo
    cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
    dados = cursor.fetchall()
    
    if dados:
        print(f"\n📊 DADOS DE EXEMPLO ({len(dados)} registros):")
        colunas_nomes = [col[1] for col in colunas]
        for i, linha in enumerate(dados):
            print(f"   Registro {i+1}:")
            for j, valor in enumerate(linha):
                if j < len(colunas_nomes):
                    print(f"      {colunas_nomes[j]}: {valor}")
    else:
        print("\n📊 DADOS: Tabela vazia")

def main():
    print("🔍 VERIFICAÇÃO DA ESTRUTURA DA DATABASE")
    print("=" * 60)
    
    try:
        # Conectar à database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabelas principais para verificar
        tabelas = [
            'tipo_departamentos',
            'setores', 
            'tipos_maquina',
            'tipos_teste',
            'tipo_atividade',
            'descricoes_atividade',
            'tipos_falha',
            'causas_retrabalho'
        ]
        
        for tabela in tabelas:
            verificar_tabela(cursor, tabela)
        
        # Verificar todas as tabelas disponíveis
        print(f"\n📚 TODAS AS TABELAS NA DATABASE:")
        print("=" * 50)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        todas_tabelas = cursor.fetchall()
        for tabela in todas_tabelas:
            print(f"   - {tabela[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar database: {e}")

if __name__ == "__main__":
    main()
