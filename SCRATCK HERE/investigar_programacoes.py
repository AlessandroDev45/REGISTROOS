#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Investigar diferenças entre tabelas de programação
"""

import sys
import os
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.database_config import engine

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def verificar_tabelas_programacao():
    """Verificar quais tabelas de programação existem"""
    print("🔍 INVESTIGANDO TABELAS DE PROGRAMAÇÃO")
    print("=" * 60)
    
    try:
        # Listar todas as tabelas que contêm 'programacao'
        tables_sql = text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '%programac%'
            ORDER BY name
        """)
        
        tables = session.execute(tables_sql).fetchall()
        
        print(f"📊 Tabelas encontradas com 'programac': {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            print(f"\n🗄️ TABELA: {table_name}")
            
            # Contar registros
            count_sql = text(f"SELECT COUNT(*) FROM {table_name}")
            count = session.execute(count_sql).scalar()
            print(f"   📊 Registros: {count}")
            
            # Mostrar estrutura da tabela
            pragma_sql = text(f"PRAGMA table_info({table_name})")
            columns = session.execute(pragma_sql).fetchall()
            
            print(f"   📋 Colunas ({len(columns)}):")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
            
            # Se há registros, mostrar alguns
            if count > 0:
                sample_sql = text(f"SELECT * FROM {table_name} LIMIT 3")
                samples = session.execute(sample_sql).fetchall()
                
                print(f"   📄 Primeiros {len(samples)} registros:")
                for i, row in enumerate(samples, 1):
                    print(f"      {i}. {dict(zip([col[1] for col in columns], row))}")
        
        return tables
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return []

def verificar_relacionamentos():
    """Verificar relacionamentos entre tabelas"""
    print("\n🔗 VERIFICANDO RELACIONAMENTOS")
    print("=" * 40)
    
    try:
        # Verificar se há programações na tabela 'programacoes' relacionadas com ordens_servico
        prog_os_sql = text("""
            SELECT 
                p.id as prog_id,
                p.id_ordem_servico,
                p.status,
                p.inicio_previsto,
                p.fim_previsto,
                os.os_numero,
                os.status_os
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            ORDER BY p.id DESC
            LIMIT 5
        """)
        
        result = session.execute(prog_os_sql).fetchall()
        
        print(f"📊 Programações na tabela 'programacoes': {len(result)}")
        
        if result:
            print("   📋 Últimas programações:")
            for row in result:
                print(f"      ID: {row[0]}, OS: {row[5]} (ID: {row[1]}), Status: {row[2]}")
                print(f"         Período: {row[3]} até {row[4]}")
        else:
            print("   ❌ Nenhuma programação encontrada na tabela 'programacoes'")
        
        # Verificar se há programações na tabela 'programacao_testes'
        if session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='programacao_testes'")).fetchone():
            prog_teste_sql = text("""
                SELECT 
                    id, codigo_programacao, titulo, status, prioridade,
                    data_inicio_programada, data_fim_programada
                FROM programacao_testes
                ORDER BY id DESC
                LIMIT 5
            """)
            
            result_teste = session.execute(prog_teste_sql).fetchall()
            
            print(f"\n📊 Programações na tabela 'programacao_testes': {len(result_teste)}")
            
            if result_teste:
                print("   📋 Últimas programações de teste:")
                for row in result_teste:
                    print(f"      ID: {row[0]}, Código: {row[1]}, Título: {row[2]}")
                    print(f"         Status: {row[3]}, Prioridade: {row[4]}")
                    print(f"         Período: {row[5]} até {row[6]}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao verificar relacionamentos: {e}")
        return []

def verificar_endpoints_pcp():
    """Verificar qual tabela o endpoint PCP está usando"""
    print("\n🔗 VERIFICANDO ENDPOINT PCP")
    print("=" * 30)
    
    try:
        # Simular a query do endpoint PCP para programações
        pcp_sql = text("""
            SELECT 
                p.id,
                p.id_ordem_servico,
                p.responsavel_id,
                p.inicio_previsto,
                p.fim_previsto,
                p.status,
                p.observacoes,
                os.os_numero,
                u.nome_completo as responsavel_nome,
                s.nome as setor_nome
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
            ORDER BY p.inicio_previsto DESC
        """)
        
        result = session.execute(pcp_sql).fetchall()
        
        print(f"📊 Query do endpoint PCP retorna: {len(result)} registros")
        
        if result:
            print("   📋 Programações encontradas pelo endpoint:")
            for row in result:
                print(f"      ID: {row[0]}, OS: {row[7]}, Responsável: {row[8]}")
                print(f"         Status: {row[5]}, Período: {row[3]} até {row[4]}")
                print(f"         Setor: {row[9]}, Observações: {row[6]}")
        else:
            print("   ❌ Endpoint PCP não encontra programações")
            print("   🔍 Isso explica por que o formulário mostrava 0 programações")
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao verificar endpoint PCP: {e}")
        return []

def comparar_estruturas():
    """Comparar estruturas das tabelas de programação"""
    print("\n📊 COMPARANDO ESTRUTURAS DAS TABELAS")
    print("=" * 45)
    
    tabelas = ['programacoes', 'programacao_testes']
    
    for tabela in tabelas:
        try:
            # Verificar se a tabela existe
            check_sql = text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabela}'")
            exists = session.execute(check_sql).fetchone()
            
            if exists:
                print(f"\n🗄️ TABELA: {tabela}")
                
                # Mostrar estrutura
                pragma_sql = text(f"PRAGMA table_info({tabela})")
                columns = session.execute(pragma_sql).fetchall()
                
                print(f"   📋 Colunas ({len(columns)}):")
                for col in columns:
                    pk = " (PK)" if col[5] else ""
                    notnull = " NOT NULL" if col[3] else ""
                    default = f" DEFAULT {col[4]}" if col[4] else ""
                    print(f"      - {col[1]}: {col[2]}{pk}{notnull}{default}")
                
                # Contar registros
                count_sql = text(f"SELECT COUNT(*) FROM {tabela}")
                count = session.execute(count_sql).scalar()
                print(f"   📊 Total de registros: {count}")
                
            else:
                print(f"\n❌ TABELA: {tabela} - NÃO EXISTE")
                
        except Exception as e:
            print(f"\n❌ ERRO ao verificar {tabela}: {e}")

def main():
    """Função principal de investigação"""
    print("🕵️ INVESTIGAÇÃO COMPLETA DAS PROGRAMAÇÕES")
    print("=" * 60)
    
    try:
        # 1. Verificar todas as tabelas de programação
        tabelas = verificar_tabelas_programacao()
        
        # 2. Verificar relacionamentos
        relacionamentos = verificar_relacionamentos()
        
        # 3. Verificar endpoint PCP
        endpoint_result = verificar_endpoints_pcp()
        
        # 4. Comparar estruturas
        comparar_estruturas()
        
        print("\n" + "=" * 60)
        print("🎯 CONCLUSÕES DA INVESTIGAÇÃO:")
        
        print(f"\n📊 TABELAS ENCONTRADAS:")
        for table in tabelas:
            print(f"   - {table[0]}")
        
        print(f"\n🔗 RELACIONAMENTOS:")
        if relacionamentos:
            print(f"   ✅ Tabela 'programacoes' tem {len(relacionamentos)} registros")
        else:
            print(f"   ❌ Tabela 'programacoes' está vazia")
        
        print(f"\n🌐 ENDPOINT PCP:")
        if endpoint_result:
            print(f"   ✅ Endpoint encontra {len(endpoint_result)} programações")
        else:
            print(f"   ❌ Endpoint não encontra programações (explica o problema)")
        
        print(f"\n💡 EXPLICAÇÃO:")
        print(f"   1. Existem DUAS tabelas de programação diferentes:")
        print(f"      - 'programacoes': Usada pelo sistema PCP")
        print(f"      - 'programacao_testes': Criada para testes específicos")
        print(f"   2. O endpoint PCP usa a tabela 'programacoes'")
        print(f"   3. As programações que criei antes foram na 'programacao_testes'")
        print(f"   4. Por isso o formulário PCP mostrava 0 programações")
        
    except Exception as e:
        print(f"\n❌ ERRO durante a investigação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
