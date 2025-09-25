#!/usr/bin/env python3
"""
Script para migrar manualmente tipo_feriados e tipo_falha
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def migrar_tipo_feriados():
    """Migra dados da tabela tipo_feriados tratando campos diferentes"""
    try:
        banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
        banco_destino = os.path.join(backend_path, 'registroos.db')
        
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print("📋 Migrando tipo_feriados...")
        
        # Buscar dados da origem
        cursor_origem.execute("SELECT * FROM tipo_feriados")
        dados_origem = cursor_origem.fetchall()
        
        # Obter nomes das colunas da origem
        cursor_origem.execute("PRAGMA table_info(tipo_feriados)")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        print(f"  📊 Registros na origem: {len(dados_origem)}")
        print(f"  📋 Colunas origem: {colunas_origem}")
        
        # Limpar tabela destino
        cursor_destino.execute("DELETE FROM tipo_feriados")
        
        # Processar cada registro
        registros_inseridos = 0
        for linha in dados_origem:
            try:
                # Criar dicionário com os dados
                dados_dict = dict(zip(colunas_origem, linha))
                
                # Mapear campos da origem para destino
                nome = dados_dict.get('nome', f"Feriado_{dados_dict.get('id', 'NOVO')}")
                data_feriado = dados_dict.get('data', '2024-01-01')  # Campo obrigatório
                tipo_feriado = dados_dict.get('tipo', 'Nacional')
                ativo = dados_dict.get('ativo', 1)
                
                # Inserir no destino
                sql = """INSERT INTO tipo_feriados 
                        (id, nome, data_feriado, tipo, ativo, data_criacao, data_ultima_atualizacao) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)"""
                
                agora = datetime.now().isoformat()
                cursor_destino.execute(sql, (
                    dados_dict.get('id'),
                    nome,
                    data_feriado,
                    tipo_feriado,
                    ativo,
                    agora,
                    agora
                ))
                
                registros_inseridos += 1
                print(f"  ✅ Registro {registros_inseridos}: {nome} - {data_feriado}")
                
            except Exception as e:
                print(f"  ❌ Erro no registro {linha}: {e}")
        
        conn_destino.commit()
        conn_origem.close()
        conn_destino.close()
        
        print(f"  🎉 {registros_inseridos} registros inseridos em tipo_feriados")
        return registros_inseridos
        
    except Exception as e:
        print(f"❌ Erro ao migrar tipo_feriados: {e}")
        return 0

def migrar_tipo_falha():
    """Migra dados da tabela tipo_falha"""
    try:
        banco_origem = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\app\registroos_new.db"
        banco_destino = os.path.join(backend_path, 'registroos.db')
        
        conn_origem = sqlite3.connect(banco_origem)
        conn_destino = sqlite3.connect(banco_destino)
        
        cursor_origem = conn_origem.cursor()
        cursor_destino = conn_destino.cursor()
        
        print("\n📋 Migrando tipo_falha...")
        
        # Buscar dados da origem
        cursor_origem.execute("SELECT * FROM tipo_falha")
        dados_origem = cursor_origem.fetchall()
        
        # Obter nomes das colunas da origem
        cursor_origem.execute("PRAGMA table_info(tipo_falha)")
        colunas_origem = [col[1] for col in cursor_origem.fetchall()]
        
        print(f"  📊 Registros na origem: {len(dados_origem)}")
        print(f"  📋 Colunas origem: {colunas_origem}")
        
        # Limpar tabela destino
        cursor_destino.execute("DELETE FROM tipo_falha")
        
        # Processar cada registro
        registros_inseridos = 0
        for linha in dados_origem:
            try:
                # Criar dicionário com os dados
                dados_dict = dict(zip(colunas_origem, linha))
                
                # Mapear campos
                codigo = dados_dict.get('codigo', f"F{dados_dict.get('id', '000')}")
                descricao = dados_dict.get('descricao', f"Falha {dados_dict.get('id', 'NOVA')}")
                categoria = dados_dict.get('categoria', 'GERAL')
                severidade = 'MEDIA'  # Valor padrão
                ativo = dados_dict.get('ativo', 1)
                data_criacao = dados_dict.get('data_criacao')
                data_ultima_atualizacao = dados_dict.get('data_ultima_atualizacao')
                
                # Inserir no destino
                sql = """INSERT INTO tipo_falha 
                        (id, codigo, descricao, categoria, severidade, ativo, 
                         data_criacao, data_ultima_atualizacao, setor) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                
                cursor_destino.execute(sql, (
                    dados_dict.get('id'),
                    codigo,
                    descricao,
                    categoria,
                    severidade,
                    ativo,
                    data_criacao,
                    data_ultima_atualizacao,
                    'GERAL'  # setor padrão
                ))
                
                registros_inseridos += 1
                print(f"  ✅ Registro {registros_inseridos}: {codigo} - {descricao}")
                
            except Exception as e:
                print(f"  ❌ Erro no registro {linha}: {e}")
        
        conn_destino.commit()
        conn_origem.close()
        conn_destino.close()
        
        print(f"  🎉 {registros_inseridos} registros inseridos em tipo_falha")
        return registros_inseridos
        
    except Exception as e:
        print(f"❌ Erro ao migrar tipo_falha: {e}")
        return 0

def verificar_resultado():
    """Verifica o resultado final"""
    try:
        banco_destino = os.path.join(backend_path, 'registroos.db')
        conn = sqlite3.connect(banco_destino)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verificação final...")
        
        # Verificar tipo_feriados
        cursor.execute("SELECT COUNT(*) FROM tipo_feriados")
        count_feriados = cursor.fetchone()[0]
        print(f"  📊 tipo_feriados: {count_feriados} registros")
        
        # Verificar tipo_falha
        cursor.execute("SELECT COUNT(*) FROM tipo_falha")
        count_falhas = cursor.fetchone()[0]
        print(f"  📊 tipo_falha: {count_falhas} registros")
        
        # Total geral de todas as tabelas tipo
        tabelas_tipo = [
            'tipo_atividade', 'tipo_causas_retrabalho', 'tipo_departamentos',
            'tipo_descricao_atividade', 'tipo_setores', 'tipo_usuarios',
            'tipos_maquina', 'tipos_teste', 'tipo_feriados', 'tipo_falha'
        ]
        
        total_registros = 0
        tabelas_com_dados = 0
        
        print(f"\n📋 Todas as tabelas tipo/tipos:")
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
        return count_feriados + count_falhas
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return 0

def main():
    print("🚀 Migrando manualmente tipo_feriados e tipo_falha...")
    print("=" * 60)
    
    # Migrar tipo_feriados
    feriados_migrados = migrar_tipo_feriados()
    
    # Migrar tipo_falha
    falhas_migradas = migrar_tipo_falha()
    
    # Verificar resultado
    total_verificado = verificar_resultado()
    
    print(f"\n🎉 MIGRAÇÃO MANUAL CONCLUÍDA!")
    print(f"✅ tipo_feriados: {feriados_migrados} registros")
    print(f"✅ tipo_falha: {falhas_migradas} registros")
    print(f"✅ Total migrado: {feriados_migrados + falhas_migradas} registros")
    
    if feriados_migrados > 0 and falhas_migradas > 0:
        print(f"🎯 SUCESSO TOTAL! Todas as tabelas tipo/tipos estão completas.")
    else:
        print(f"⚠️ Algumas tabelas podem não ter sido migradas completamente.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
