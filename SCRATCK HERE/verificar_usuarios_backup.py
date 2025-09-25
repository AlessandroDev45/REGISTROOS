#!/usr/bin/env python3
"""
Script para verificar usuários nos backups e migrar
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_usuarios_backup(backup_file):
    """Verifica usuários em um backup"""
    try:
        if not os.path.exists(backup_file):
            return 0, []
        
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Verificar se existe tabela usuarios
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='usuarios' OR name='tipo_usuarios')")
        tabelas_usuario = [row[0] for row in cursor.fetchall()]
        
        total_usuarios = 0
        usuarios_encontrados = []
        
        for tabela in tabelas_usuario:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Buscar alguns usuários de exemplo
                cursor.execute(f"SELECT email, nome_usuario FROM {tabela} LIMIT 5")
                usuarios = cursor.fetchall()
                
                print(f"  📋 Tabela {tabela}: {count} usuários")
                for email, nome in usuarios:
                    print(f"    - {email} ({nome})")
                    usuarios_encontrados.append((email, nome))
                
                total_usuarios += count
        
        conn.close()
        return total_usuarios, usuarios_encontrados
        
    except Exception as e:
        print(f"  ❌ Erro ao verificar {backup_file}: {e}")
        return 0, []

def migrar_usuarios_backup(backup_file):
    """Migra usuários de um backup específico"""
    try:
        banco_destino = os.path.join(backend_path, 'registroos.db')
        
        conn_origem = sqlite3.connect(backup_file)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print(f"\n🔄 Migrando usuários de {os.path.basename(backup_file)}...")
        
        # Verificar qual tabela de usuários existe no backup
        cursor_origem.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='usuarios' OR name='tipo_usuarios')")
        tabelas_usuario = [row[0] for row in cursor_origem.fetchall()]
        
        if not tabelas_usuario:
            print("  ⚠️ Nenhuma tabela de usuários encontrada")
            return 0
        
        tabela_origem = tabelas_usuario[0]  # Usar a primeira encontrada
        print(f"  📋 Usando tabela origem: {tabela_origem}")
        
        # Obter estrutura da tabela origem
        cursor_origem.execute(f"PRAGMA table_info({tabela_origem})")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        # Obter estrutura da tabela destino
        cursor_destino.execute("PRAGMA table_info(tipo_usuarios)")
        colunas_destino = [col[1] for col in cursor_destino.fetchall()]
        
        # Encontrar colunas em comum
        colunas_comuns = [col for col in colunas_origem if col in colunas_destino]
        
        print(f"  📋 Colunas origem: {len(colunas_origem)}")
        print(f"  📋 Colunas destino: {len(colunas_destino)}")
        print(f"  📋 Colunas comuns: {len(colunas_comuns)}")
        
        if not colunas_comuns:
            print("  ⚠️ Nenhuma coluna em comum")
            return 0
        
        # Buscar dados da origem
        colunas_str = ', '.join(colunas_comuns)
        cursor_origem.execute(f"SELECT {colunas_str} FROM {tabela_origem}")
        dados = cursor_origem.fetchall()
        
        if not dados:
            print("  ⚠️ Nenhum usuário encontrado")
            return 0
        
        print(f"  📊 Usuários encontrados: {len(dados)}")
        
        # Limpar tabela destino
        cursor_destino.execute("DELETE FROM tipo_usuarios")
        
        # Inserir dados
        placeholders = ', '.join(['?' for _ in colunas_comuns])
        insert_sql = f"INSERT INTO tipo_usuarios ({colunas_str}) VALUES ({placeholders})"
        
        cursor_destino.executemany(insert_sql, dados)
        conn_destino.commit()
        
        print(f"  ✅ {len(dados)} usuários migrados!")
        
        # Mostrar alguns exemplos
        cursor_destino.execute("SELECT email, nome_usuario, cargo FROM tipo_usuarios LIMIT 5")
        exemplos = cursor_destino.fetchall()
        
        print(f"  📋 Exemplos migrados:")
        for email, nome, cargo in exemplos:
            print(f"    - {email} ({nome}) - {cargo}")
        
        conn_origem.close()
        conn_destino.close()
        
        return len(dados)
        
    except Exception as e:
        print(f"  ❌ Erro na migração: {e}")
        return 0

def main():
    print("🔍 Verificando usuários nos backups...")
    print("=" * 60)
    
    # Lista de backups para verificar
    backups = [
        'backup_registroos_new_20250921_025006.db',
        'backup_correcao_estrutura_20250921_025331.db',
        'backup_esquema_completo_20250921_025526.db',
        'backup_antes_recriar_20250921_030142.db',
        'backup_antes_recriar_20250921_030151.db',
        'backup_antes_recriar_20250921_030228.db'
    ]
    
    # Verificar também o banco original
    banco_original = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
    if os.path.exists(banco_original):
        backups.insert(0, banco_original)
    
    backup_com_usuarios = None
    max_usuarios = 0
    
    for backup in backups:
        print(f"\n📂 Verificando: {os.path.basename(backup)}")
        total, usuarios = verificar_usuarios_backup(backup)
        
        if total > max_usuarios:
            max_usuarios = total
            backup_com_usuarios = backup
    
    if backup_com_usuarios:
        print(f"\n🎯 Melhor backup: {os.path.basename(backup_com_usuarios)} ({max_usuarios} usuários)")
        
        # Migrar usuários
        usuarios_migrados = migrar_usuarios_backup(backup_com_usuarios)
        
        if usuarios_migrados > 0:
            print(f"\n🎉 MIGRAÇÃO CONCLUÍDA!")
            print(f"✅ {usuarios_migrados} usuários migrados para tipo_usuarios")
            print(f"🔑 Agora você pode fazer login no sistema")
        else:
            print(f"\n❌ Falha na migração de usuários")
    else:
        print(f"\n⚠️ Nenhum backup com usuários encontrado")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
