#!/usr/bin/env python3
"""
Script para copiar dados das tabelas tipo/tipos do registroos_new.db
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def migrar_dados_tabela(banco_origem, banco_destino, tabela):
    """Migra dados de uma tabela específica"""
    try:
        # Conectar aos dois bancos
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        # Verificar se a tabela existe no banco origem
        cursor_origem.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
        if not cursor_origem.fetchone():
            print(f"  ⚠️ Tabela {tabela} não existe no banco origem")
            conn_origem.close()
            conn_destino.close()
            return 0
        
        # Verificar se a tabela existe no banco destino
        cursor_destino.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
        if not cursor_destino.fetchone():
            print(f"  ⚠️ Tabela {tabela} não existe no banco destino")
            conn_origem.close()
            conn_destino.close()
            return 0
        
        # Obter estrutura da tabela no banco origem
        cursor_origem.execute(f"PRAGMA table_info({tabela})")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        # Obter estrutura da tabela no banco destino
        cursor_destino.execute(f"PRAGMA table_info({tabela})")
        colunas_destino = [col[1] for col in cursor_destino.fetchall()]
        
        # Encontrar colunas em comum
        colunas_comuns = [col for col in colunas_origem if col in colunas_destino]
        
        if not colunas_comuns:
            print(f"  ⚠️ Nenhuma coluna em comum entre as tabelas {tabela}")
            conn_origem.close()
            conn_destino.close()
            return 0
        
        # Buscar dados do banco origem
        colunas_str = ', '.join(colunas_comuns)
        cursor_origem.execute(f"SELECT {colunas_str} FROM {tabela}")
        dados = cursor_origem.fetchall()
        
        if not dados:
            print(f"  ℹ️ Tabela {tabela} está vazia no banco origem")
            conn_origem.close()
            conn_destino.close()
            return 0
        
        # Limpar tabela no banco destino
        cursor_destino.execute(f"DELETE FROM {tabela}")
        
        # Inserir dados no banco destino
        placeholders = ', '.join(['?' for _ in colunas_comuns])
        insert_sql = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"
        
        cursor_destino.executemany(insert_sql, dados)
        conn_destino.commit()
        
        registros_migrados = len(dados)
        print(f"  ✅ {registros_migrados} registros migrados")
        
        conn_origem.close()
        conn_destino.close()
        
        return registros_migrados
        
    except Exception as e:
        print(f"  ❌ Erro ao migrar tabela {tabela}: {e}")
        return 0

def listar_tabelas_tipos(db_path):
    """Lista todas as tabelas que começam com 'tipo' ou 'tipos'"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'tipo%' OR name LIKE 'tipos%') ORDER BY name")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return tabelas
        
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return []

def main():
    print("🚀 Copiando dados das tabelas tipo/tipos do registroos_new.db...")
    print("=" * 70)
    
    # Caminhos dos bancos
    banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
    banco_destino = os.path.join(backend_path, 'registroos.db')
    
    # Verificar se os bancos existem
    if not os.path.exists(banco_origem):
        print(f"❌ Banco origem não encontrado: {banco_origem}")
        return False
    
    if not os.path.exists(banco_destino):
        print(f"❌ Banco destino não encontrado: {banco_destino}")
        return False
    
    print(f"📂 Banco origem: {banco_origem}")
    print(f"📂 Banco destino: {banco_destino}")
    
    # Listar tabelas tipos no banco origem
    tabelas_tipos = listar_tabelas_tipos(banco_origem)
    
    if not tabelas_tipos:
        print("❌ Nenhuma tabela tipo/tipos encontrada no banco origem")
        return False
    
    print(f"\n📋 Tabelas encontradas: {len(tabelas_tipos)}")
    for tabela in tabelas_tipos:
        print(f"  - {tabela}")
    
    # Verificar dados no banco origem
    print(f"\n🔍 Verificando dados no banco origem...")
    conn_origem = sqlite3.connect(banco_origem)
    cursor_origem = conn_origem.cursor()
    
    total_registros_origem = 0
    for tabela in tabelas_tipos:
        cursor_origem.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = cursor_origem.fetchone()[0]
        if count > 0:
            print(f"  ✅ {tabela}: {count} registros")
            total_registros_origem += count
        else:
            print(f"  ⚪ {tabela}: vazia")
    
    conn_origem.close()
    
    if total_registros_origem == 0:
        print("⚠️ Nenhum dado encontrado nas tabelas tipo/tipos do banco origem")
        return False
    
    print(f"📊 Total de registros a migrar: {total_registros_origem}")
    
    # Fazer backup do banco destino
    backup_path = os.path.join(os.path.dirname(__file__), f'backup_registroos_antes_copia_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
    import shutil
    shutil.copy2(banco_destino, backup_path)
    print(f"✅ Backup do banco destino criado: {os.path.basename(backup_path)}")
    
    print(f"\n🔄 Iniciando migração de dados...")
    
    total_migrados = 0
    tabelas_migradas = 0
    
    for tabela in tabelas_tipos:
        print(f"\n📋 Migrando tabela: {tabela}")
        registros = migrar_dados_tabela(banco_origem, banco_destino, tabela)
        if registros > 0:
            total_migrados += registros
            tabelas_migradas += 1
    
    print(f"\n🎉 MIGRAÇÃO CONCLUÍDA!")
    print(f"✅ Tabelas migradas: {tabelas_migradas}/{len(tabelas_tipos)}")
    print(f"✅ Total de registros migrados: {total_migrados}")
    
    # Verificar dados no banco destino
    print(f"\n🔍 Verificando dados no banco destino...")
    conn_destino = sqlite3.connect(banco_destino)
    cursor_destino = conn_destino.cursor()
    
    for tabela in tabelas_tipos:
        cursor_destino.execute(f"SELECT COUNT(*) FROM {tabela}")
        count = cursor_destino.fetchone()[0]
        if count > 0:
            print(f"  ✅ {tabela}: {count} registros")
        else:
            print(f"  ⚪ {tabela}: vazia")
    
    conn_destino.close()
    
    print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"✅ Dados copiados do registroos_new.db")
    print(f"✅ Banco registroos.db atualizado")
    print(f"✅ Sistema pronto para uso")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
