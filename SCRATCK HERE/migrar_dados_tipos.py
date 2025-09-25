#!/usr/bin/env python3
"""
Script para renomear banco e migrar dados das tabelas tipo/tipos
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def renomear_banco():
    """Renomeia o banco para registroos.db"""
    try:
        banco_atual = os.path.join(backend_path, 'registroos_new.db')
        banco_novo = os.path.join(backend_path, 'registroos.db')
        
        # Fazer backup do banco atual se existir
        if os.path.exists(banco_novo):
            backup_path = os.path.join(os.path.dirname(__file__), f'backup_registroos_antigo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
            import shutil
            shutil.copy2(banco_novo, backup_path)
            print(f"✅ Backup do banco antigo criado: {backup_path}")
        
        # Renomear/copiar o banco atual
        import shutil
        shutil.copy2(banco_atual, banco_novo)
        print(f"✅ Banco renomeado para: registroos.db")
        
        return banco_novo
        
    except Exception as e:
        print(f"❌ Erro ao renomear banco: {e}")
        return None

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

def migrar_dados_tabela(banco_antigo, banco_novo, tabela):
    """Migra dados de uma tabela específica"""
    try:
        # Conectar aos dois bancos
        conn_antigo = sqlite3.connect(banco_antigo)
        conn_novo = sqlite3.connect(banco_novo)
        
        cursor_antigo = conn_antigo.cursor()
        cursor_novo = conn_novo.cursor()
        
        # Verificar se a tabela existe no banco antigo
        cursor_antigo.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
        if not cursor_antigo.fetchone():
            print(f"  ⚠️ Tabela {tabela} não existe no banco antigo")
            conn_antigo.close()
            conn_novo.close()
            return 0
        
        # Verificar se a tabela existe no banco novo
        cursor_novo.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
        if not cursor_novo.fetchone():
            print(f"  ⚠️ Tabela {tabela} não existe no banco novo")
            conn_antigo.close()
            conn_novo.close()
            return 0
        
        # Obter estrutura da tabela no banco antigo
        cursor_antigo.execute(f"PRAGMA table_info({tabela})")
        colunas_antigas = [col[1] for col in cursor_antigo.fetchall()]
        
        # Obter estrutura da tabela no banco novo
        cursor_novo.execute(f"PRAGMA table_info({tabela})")
        colunas_novas = [col[1] for col in cursor_novo.fetchall()]
        
        # Encontrar colunas em comum
        colunas_comuns = [col for col in colunas_antigas if col in colunas_novas]
        
        if not colunas_comuns:
            print(f"  ⚠️ Nenhuma coluna em comum entre as tabelas {tabela}")
            conn_antigo.close()
            conn_novo.close()
            return 0
        
        # Buscar dados do banco antigo
        colunas_str = ', '.join(colunas_comuns)
        cursor_antigo.execute(f"SELECT {colunas_str} FROM {tabela}")
        dados = cursor_antigo.fetchall()
        
        if not dados:
            print(f"  ℹ️ Tabela {tabela} está vazia no banco antigo")
            conn_antigo.close()
            conn_novo.close()
            return 0
        
        # Limpar tabela no banco novo
        cursor_novo.execute(f"DELETE FROM {tabela}")
        
        # Inserir dados no banco novo
        placeholders = ', '.join(['?' for _ in colunas_comuns])
        insert_sql = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"
        
        cursor_novo.executemany(insert_sql, dados)
        conn_novo.commit()
        
        registros_migrados = len(dados)
        print(f"  ✅ {registros_migrados} registros migrados")
        
        conn_antigo.close()
        conn_novo.close()
        
        return registros_migrados
        
    except Exception as e:
        print(f"  ❌ Erro ao migrar tabela {tabela}: {e}")
        return 0

def migrar_todas_tabelas_tipos():
    """Migra todas as tabelas que começam com tipo/tipos"""
    try:
        # Caminhos dos bancos
        banco_antigo = os.path.join(backend_path, 'registroos_new.db')
        banco_novo = os.path.join(backend_path, 'registroos.db')

        # Verificar se o banco antigo existe
        if not os.path.exists(banco_antigo):
            print(f"❌ Banco antigo não encontrado: {banco_antigo}")
            return False
        
        print(f"📂 Banco antigo: registroos_new.db")
        print(f"📂 Banco novo: registroos.db")
        
        # Listar tabelas tipos no banco antigo
        tabelas_tipos = listar_tabelas_tipos(banco_antigo)
        
        if not tabelas_tipos:
            print("❌ Nenhuma tabela tipo/tipos encontrada no banco antigo")
            return False
        
        print(f"\n📋 Tabelas encontradas: {len(tabelas_tipos)}")
        for tabela in tabelas_tipos:
            print(f"  - {tabela}")
        
        print(f"\n🔄 Iniciando migração de dados...")
        
        total_registros = 0
        tabelas_migradas = 0
        
        for tabela in tabelas_tipos:
            print(f"\n📋 Migrando tabela: {tabela}")
            registros = migrar_dados_tabela(banco_antigo, banco_novo, tabela)
            if registros > 0:
                total_registros += registros
                tabelas_migradas += 1
        
        print(f"\n🎉 MIGRAÇÃO CONCLUÍDA!")
        print(f"✅ Tabelas migradas: {tabelas_migradas}/{len(tabelas_tipos)}")
        print(f"✅ Total de registros: {total_registros}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

def verificar_dados_migrados():
    """Verifica se os dados foram migrados corretamente"""
    try:
        banco_novo = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco_novo)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificando dados migrados...")
        
        # Listar tabelas tipos
        tabelas_tipos = listar_tabelas_tipos(banco_novo)
        
        for tabela in tabelas_tipos:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            print(f"  📊 {tabela}: {count} registros")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🚀 Renomeando banco e migrando dados das tabelas tipo/tipos...")
    print("=" * 70)
    
    # 1. Renomear banco
    banco_novo = renomear_banco()
    if not banco_novo:
        print("❌ Falha ao renomear banco.")
        return False
    
    # 2. Migrar dados das tabelas tipos
    if not migrar_todas_tabelas_tipos():
        print("❌ Falha na migração de dados.")
        return False
    
    # 3. Verificar dados migrados
    if not verificar_dados_migrados():
        print("❌ Falha na verificação.")
        return False
    
    print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print(f"✅ Banco renomeado para: registroos.db")
    print(f"✅ Dados das tabelas tipo/tipos migrados")
    print(f"✅ Sistema pronto para uso")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
