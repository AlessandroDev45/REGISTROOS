#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar nomes corretos das tabelas no banco
"""

import sqlite3

BANCOS = [
    'RegistroOS/registrooficial/backend/database.db',
    'RegistroOS/registrooficial/backend/registroos.db',
    'RegistroOS/registrooficial/backend/registroos_new.db',
    'RegistroOS/registrooficial/backend/app/registroos_new.db'
]

def verificar_tabelas():
    """Verifica tabelas existentes nos bancos"""
    print("🔍 VERIFICANDO TABELAS NOS BANCOS...")

    for db_path in BANCOS:
        print(f"\n📁 BANCO: {db_path}")

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tabelas = cursor.fetchall()

            print(f"   📊 TABELAS ENCONTRADAS ({len(tabelas)}):")
            for tabela in tabelas:
                print(f"      - {tabela[0]}")

            if len(tabelas) > 0:
                # Verificar estrutura das tabelas relacionadas
                tabelas_interesse = ['usuarios', 'tipo_usuarios', 'setores', 'tipo_setores', 'programacoes', 'pendencias', 'apontamentos', 'ordens_servico']

                for nome_tabela in tabelas_interesse:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
                        count = cursor.fetchone()[0]
                        print(f"      ✅ {nome_tabela}: {count} registros")
                    except:
                        pass

            conn.close()

        except Exception as e:
            print(f"   ❌ Erro ao conectar: {e}")

    # Determinar qual banco usar
    print(f"\n🎯 BANCO RECOMENDADO:")
    for db_path in BANCOS:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()

            if len(tabelas) > 5:  # Banco com mais tabelas
                print(f"   ✅ {db_path} ({len(tabelas)} tabelas)")
                return db_path

            conn.close()
        except:
            pass

    return BANCOS[0]  # Fallback

if __name__ == "__main__":
    banco_recomendado = verificar_tabelas()
    print(f"\n💡 USAR BANCO: {banco_recomendado}")
