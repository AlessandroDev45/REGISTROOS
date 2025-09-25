#!/usr/bin/env python3
"""
Script para verificar dados nos backups
"""

import sqlite3
import os

def verificar_dados_backup(backup_file):
    """Verifica dados nas tabelas tipo/tipos de um backup"""
    try:
        if not os.path.exists(backup_file):
            print(f"❌ Backup não encontrado: {backup_file}")
            return
        
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        print(f"\n📂 Verificando: {os.path.basename(backup_file)}")
        print("-" * 50)
        
        # Listar tabelas tipo/tipos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'tipo%' OR name LIKE 'tipos%') ORDER BY name")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        total_registros = 0
        
        for tabela in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  ✅ {tabela}: {count} registros")
                total_registros += count
            else:
                print(f"  ⚪ {tabela}: vazia")
        
        print(f"📊 Total de registros: {total_registros}")
        
        conn.close()
        return total_registros
        
    except Exception as e:
        print(f"❌ Erro ao verificar {backup_file}: {e}")
        return 0

def main():
    print("🔍 Verificando dados nos backups...")
    
    # Lista de backups para verificar
    backups = [
        'backup_registroos_new_20250921_025006.db',
        'backup_correcao_estrutura_20250921_025331.db',
        'backup_esquema_completo_20250921_025526.db',
        'backup_antes_recriar_20250921_030142.db',
        'backup_antes_recriar_20250921_030151.db',
        'backup_antes_recriar_20250921_030228.db'
    ]
    
    backup_com_dados = None
    max_registros = 0
    
    for backup in backups:
        registros = verificar_dados_backup(backup)
        if registros > max_registros:
            max_registros = registros
            backup_com_dados = backup
    
    if backup_com_dados:
        print(f"\n🎯 Backup com mais dados: {backup_com_dados} ({max_registros} registros)")
        return backup_com_dados
    else:
        print(f"\n⚠️ Nenhum backup com dados encontrado")
        return None

if __name__ == "__main__":
    main()
