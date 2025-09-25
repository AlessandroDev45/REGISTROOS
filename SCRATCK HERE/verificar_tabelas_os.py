#!/usr/bin/env python3
"""
Verificar estrutura das tabelas de OS, Cliente e Equipamento
"""

import sqlite3

def verificar_tabelas():
    conn = sqlite3.connect('C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db')
    cursor = conn.cursor()

    print('🔍 Verificando tabelas relacionadas a OS...')

    # Listar todas as tabelas
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table" ORDER BY name')
    tables = cursor.fetchall()

    print('📋 Tabelas disponíveis:')
    for table in tables:
        print(f'  - {table[0]}')

    print()

    # Verificar estrutura das tabelas principais
    tables_to_check = ['ordens_servico', 'clientes', 'equipamentos', 'os', 'cliente', 'equipamento']

    for table_name in tables_to_check:
        try:
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()
            if columns:
                print(f'📊 Estrutura da tabela {table_name}:')
                for col in columns:
                    print(f'  - {col[1]} ({col[2]})')
                print()
        except Exception as e:
            print(f'⚠️ Tabela {table_name} não encontrada')

    conn.close()

if __name__ == "__main__":
    verificar_tabelas()
