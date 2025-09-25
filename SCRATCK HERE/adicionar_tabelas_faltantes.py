#!/usr/bin/env python3
"""
Script para adicionar as tabelas tipo_feriados e tipo_falha e migrar dados
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def criar_tabelas_faltantes():
    """Cria as tabelas tipo_feriados e tipo_falha"""
    try:
        banco_destino = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco_destino)
        cursor = conn.cursor()
        
        print("🔧 Criando tabelas faltantes...")
        
        # Criar tabela tipo_feriados
        sql_feriados = """
        CREATE TABLE IF NOT EXISTS tipo_feriados (
            id INTEGER PRIMARY KEY,
            nome VARCHAR NOT NULL,
            data_feriado DATE NOT NULL,
            tipo VARCHAR,
            ativo BOOLEAN DEFAULT 1,
            data_criacao DATETIME,
            data_ultima_atualizacao DATETIME,
            observacoes TEXT
        )
        """
        
        cursor.execute(sql_feriados)
        print("  ✅ Tabela tipo_feriados criada")
        
        # Criar tabela tipo_falha
        sql_falha = """
        CREATE TABLE IF NOT EXISTS tipo_falha (
            id INTEGER PRIMARY KEY,
            codigo VARCHAR NOT NULL,
            descricao VARCHAR NOT NULL,
            categoria VARCHAR,
            severidade VARCHAR,
            ativo BOOLEAN DEFAULT 1,
            data_criacao DATETIME,
            data_ultima_atualizacao DATETIME,
            id_departamento INTEGER,
            setor VARCHAR,
            observacoes TEXT
        )
        """
        
        cursor.execute(sql_falha)
        print("  ✅ Tabela tipo_falha criada")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def migrar_dados_tabela_especifica(banco_origem, banco_destino, tabela):
    """Migra dados de uma tabela específica"""
    try:
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print(f"\n📋 Migrando tabela: {tabela}")
        
        # Verificar se a tabela existe no banco origem
        cursor_origem.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
        if not cursor_origem.fetchone():
            print(f"  ⚠️ Tabela {tabela} não existe no banco origem")
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
        
        print(f"  📋 Colunas origem: {colunas_origem}")
        print(f"  📋 Colunas destino: {colunas_destino}")
        print(f"  📋 Colunas comuns: {colunas_comuns}")
        
        # Buscar dados do banco origem
        colunas_str = ', '.join(colunas_comuns)
        cursor_origem.execute(f"SELECT {colunas_str} FROM {tabela}")
        dados = cursor_origem.fetchall()
        
        if not dados:
            print(f"  ℹ️ Tabela {tabela} está vazia no banco origem")
            conn_origem.close()
            conn_destino.close()
            return 0
        
        print(f"  📊 Registros encontrados: {len(dados)}")
        
        # Limpar tabela no banco destino
        cursor_destino.execute(f"DELETE FROM {tabela}")
        
        # Inserir dados no banco destino
        placeholders = ', '.join(['?' for _ in colunas_comuns])
        insert_sql = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"
        
        cursor_destino.executemany(insert_sql, dados)
        conn_destino.commit()
        
        registros_migrados = len(dados)
        print(f"  ✅ {registros_migrados} registros migrados")
        
        # Mostrar alguns exemplos
        cursor_destino.execute(f"SELECT * FROM {tabela} LIMIT 3")
        exemplos = cursor_destino.fetchall()
        for i, exemplo in enumerate(exemplos, 1):
            print(f"    📝 Exemplo {i}: {exemplo[:3]}...")
        
        conn_origem.close()
        conn_destino.close()
        
        return registros_migrados
        
    except Exception as e:
        print(f"  ❌ Erro ao migrar tabela {tabela}: {e}")
        return 0

def verificar_resultado_final():
    """Verifica o resultado final de todas as tabelas"""
    try:
        banco_destino = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco_destino)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificação final de todas as tabelas tipo/tipos...")
        
        tabelas_tipo = [
            'tipo_atividade',
            'tipo_causas_retrabalho', 
            'tipo_departamentos',
            'tipo_descricao_atividade',
            'tipo_setores',
            'tipo_usuarios',
            'tipos_maquina',
            'tipos_teste',
            'tipo_feriados',
            'tipo_falha'
        ]
        
        total_registros = 0
        tabelas_com_dados = 0
        
        for tabela in tabelas_tipo:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"  ✅ {tabela}: {count} registros")
                    total_registros += count
                    tabelas_com_dados += 1
                else:
                    print(f"  ⚪ {tabela}: vazia")
            except Exception as e:
                print(f"  ❌ {tabela}: erro - {e}")
        
        print(f"\n📊 RESUMO FINAL:")
        print(f"  📋 Tabelas com dados: {tabelas_com_dados}/{len(tabelas_tipo)}")
        print(f"  📊 Total de registros: {total_registros}")
        
        conn.close()
        return total_registros
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return 0

def main():
    print("🚀 Adicionando tabelas tipo_feriados e tipo_falha...")
    print("=" * 60)
    
    # 1. Criar tabelas faltantes
    if not criar_tabelas_faltantes():
        print("❌ Falha ao criar tabelas")
        return False
    
    # 2. Migrar dados
    banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
    banco_destino = os.path.join(backend_path, 'registroos.db')
    
    print(f"\n📂 Banco origem: {banco_origem}")
    print(f"📂 Banco destino: {banco_destino}")
    
    # Migrar tipo_feriados
    feriados_migrados = migrar_dados_tabela_especifica(banco_origem, banco_destino, 'tipo_feriados')
    
    # Migrar tipo_falha
    falhas_migradas = migrar_dados_tabela_especifica(banco_origem, banco_destino, 'tipo_falha')
    
    # 3. Verificar resultado final
    total_final = verificar_resultado_final()
    
    print(f"\n🎉 PROCESSO CONCLUÍDO!")
    print(f"✅ Tabelas criadas: tipo_feriados, tipo_falha")
    print(f"✅ tipo_feriados: {feriados_migrados} registros migrados")
    print(f"✅ tipo_falha: {falhas_migradas} registros migrados")
    print(f"✅ Total geral no banco: {total_final} registros")
    
    if feriados_migrados > 0 and falhas_migradas > 0:
        print(f"🎯 SUCESSO TOTAL! Todas as tabelas tipo/tipos estão completas.")
    else:
        print(f"⚠️ Algumas tabelas podem estar vazias (normal se não havia dados na origem).")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
