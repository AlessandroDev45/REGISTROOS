#!/usr/bin/env python3
"""
Script para migrar as tabelas restantes
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def migrar_dados_tabela_seguro(banco_origem, banco_destino, tabela):
    """Migra dados de uma tabela específica com tratamento de erros"""
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
        
        # Para tipo_setores, vamos tratar o campo departamento
        if tabela == 'tipo_setores':
            # Ajustar dados para o novo esquema
            dados_ajustados = []
            for linha in dados:
                linha_lista = list(linha)
                # Se departamento está None, colocar string vazia
                for i, col in enumerate(colunas_comuns):
                    if col == 'departamento' and linha_lista[i] is None:
                        linha_lista[i] = ''
                dados_ajustados.append(tuple(linha_lista))
            dados = dados_ajustados
        
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
        try:
            conn_origem.close()
            conn_destino.close()
        except:
            pass
        return 0

def main():
    print("🚀 Migrando tabelas restantes...")
    print("=" * 50)
    
    # Caminhos dos bancos
    banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
    banco_destino = os.path.join(backend_path, 'registroos.db')
    
    # Tabelas que queremos migrar (que existem no novo esquema)
    tabelas_para_migrar = [
        'tipo_setores',
        'tipo_usuarios', 
        'tipos_maquina',
        'tipos_teste'
    ]
    
    print(f"📂 Banco origem: {banco_origem}")
    print(f"📂 Banco destino: {banco_destino}")
    print(f"📋 Tabelas para migrar: {tabelas_para_migrar}")
    
    total_migrados = 0
    tabelas_migradas = 0
    
    for tabela in tabelas_para_migrar:
        print(f"\n📋 Migrando tabela: {tabela}")
        registros = migrar_dados_tabela_seguro(banco_origem, banco_destino, tabela)
        if registros > 0:
            total_migrados += registros
            tabelas_migradas += 1
    
    print(f"\n🎉 MIGRAÇÃO CONCLUÍDA!")
    print(f"✅ Tabelas migradas: {tabelas_migradas}/{len(tabelas_para_migrar)}")
    print(f"✅ Total de registros migrados: {total_migrados}")
    
    # Verificar dados finais
    print(f"\n🔍 Verificação final...")
    conn_destino = sqlite3.connect(banco_destino)
    cursor_destino = conn_destino.cursor()
    
    todas_tabelas = [
        'tipo_atividade',
        'tipo_causas_retrabalho', 
        'tipo_departamentos',
        'tipo_descricao_atividade',
        'tipo_setores',
        'tipo_usuarios',
        'tipos_maquina',
        'tipos_teste'
    ]
    
    total_final = 0
    for tabela in todas_tabelas:
        try:
            cursor_destino.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor_destino.fetchone()[0]
            if count > 0:
                print(f"  ✅ {tabela}: {count} registros")
                total_final += count
            else:
                print(f"  ⚪ {tabela}: vazia")
        except Exception as e:
            print(f"  ❌ {tabela}: erro - {e}")
    
    conn_destino.close()
    
    print(f"\n📊 Total de registros no banco: {total_final}")
    print(f"🎉 PROCESSO CONCLUÍDO!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
