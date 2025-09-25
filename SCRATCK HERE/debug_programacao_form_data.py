#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug do endpoint programacao-form-data
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

def debug_setores():
    """Debug dos setores"""
    print("🏭 DEBUG: Verificando setores...")
    
    try:
        # Query original do endpoint
        setores_sql = text("""
            SELECT s.id, s.nome, s.id_departamento, d.nome_tipo as departamento_nome
            FROM tipo_setores s
            LEFT JOIN tipo_departamentos d ON s.id_departamento = d.id
            ORDER BY s.nome
        """)
        
        result = session.execute(setores_sql).fetchall()
        
        print(f"   📊 Total de setores encontrados: {len(result)}")
        
        if result:
            print("   📋 Primeiros 10 setores:")
            for i, row in enumerate(result[:10], 1):
                print(f"      {i}. ID: {row[0]}, Nome: {row[1]}, Dept ID: {row[2]}, Dept Nome: {row[3]}")
        else:
            print("   ❌ Nenhum setor encontrado")
            
            # Verificar se a tabela existe
            check_table = text("SELECT name FROM sqlite_master WHERE type='table' AND name='tipo_setores'")
            table_exists = session.execute(check_table).fetchone()
            
            if table_exists:
                print("   ✅ Tabela tipo_setores existe")
                
                # Verificar se há dados na tabela
                count_sql = text("SELECT COUNT(*) FROM tipo_setores")
                count = session.execute(count_sql).scalar()
                print(f"   📊 Total de registros na tabela: {count}")
            else:
                print("   ❌ Tabela tipo_setores não existe")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar setores: {e}")
        return []

def debug_usuarios():
    """Debug dos usuários"""
    print("\n👥 DEBUG: Verificando usuários...")
    
    try:
        # Query original do endpoint
        usuarios_sql = text("""
            SELECT u.id, u.nome_completo, u.id_setor, s.nome as setor_nome, u.privilege_level, u.trabalha_producao
            FROM tipo_usuarios u
            LEFT JOIN tipo_setores s ON u.id_setor = s.id
            WHERE u.privilege_level IN ('SUPERVISOR', 'ADMIN')
            ORDER BY u.nome_completo
        """)
        
        result = session.execute(usuarios_sql).fetchall()
        
        print(f"   📊 Total de usuários supervisores/admins: {len(result)}")
        
        if result:
            print("   📋 Usuários encontrados:")
            for i, row in enumerate(result, 1):
                print(f"      {i}. ID: {row[0]}, Nome: {row[1]}, Setor ID: {row[2]}, Setor: {row[3]}, Nível: {row[4]}, Produção: {row[5]}")
        else:
            print("   ❌ Nenhum usuário supervisor/admin encontrado")
            
            # Verificar todos os usuários
            all_users_sql = text("SELECT id, nome_completo, privilege_level FROM tipo_usuarios LIMIT 5")
            all_users = session.execute(all_users_sql).fetchall()
            
            if all_users:
                print("   📋 Primeiros 5 usuários (qualquer nível):")
                for row in all_users:
                    print(f"      - ID: {row[0]}, Nome: {row[1]}, Nível: {row[2]}")
            else:
                print("   ❌ Nenhum usuário encontrado na tabela")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar usuários: {e}")
        return []

def debug_departamentos():
    """Debug dos departamentos"""
    print("\n🏢 DEBUG: Verificando departamentos...")
    
    try:
        # Query original do endpoint
        departamentos_sql = text("""
            SELECT d.id, d.nome_tipo as nome
            FROM tipo_departamentos d
            ORDER BY d.nome_tipo
        """)
        
        result = session.execute(departamentos_sql).fetchall()
        
        print(f"   📊 Total de departamentos encontrados: {len(result)}")
        
        if result:
            print("   📋 Departamentos encontrados:")
            for i, row in enumerate(result, 1):
                print(f"      {i}. ID: {row[0]}, Nome: {row[1]}")
                
            # Verificar especificamente o departamento TESTE
            teste_dept = next((row for row in result if row[1] == 'TESTE'), None)
            if teste_dept:
                print(f"   ✅ Departamento TESTE encontrado: ID {teste_dept[0]}")
            else:
                print("   ❌ Departamento TESTE não encontrado")
        else:
            print("   ❌ Nenhum departamento encontrado")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar departamentos: {e}")
        return []

def debug_ordens_servico():
    """Debug das ordens de serviço"""
    print("\n📋 DEBUG: Verificando ordens de serviço...")
    
    try:
        # Query original do endpoint
        os_sql = text("""
            SELECT os.id, os.os_numero, os.status_os, os.descricao_maquina
            FROM ordens_servico os
            WHERE os.status_os IN ('AGUARDANDO', 'EM_ANDAMENTO')
            ORDER BY os.created_at DESC
            LIMIT 10
        """)
        
        result = session.execute(os_sql).fetchall()
        
        print(f"   📊 Total de OS disponíveis: {len(result)}")
        
        if result:
            print("   📋 Ordens de serviço encontradas:")
            for i, row in enumerate(result, 1):
                print(f"      {i}. ID: {row[0]}, Número: {row[1]}, Status: {row[2]}, Descrição: {row[3]}")
        else:
            print("   ❌ Nenhuma OS disponível")
            
            # Verificar se há OS em qualquer status
            all_os_sql = text("SELECT COUNT(*) FROM ordens_servico")
            total_os = session.execute(all_os_sql).scalar()
            print(f"   📊 Total de OS na tabela: {total_os}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar ordens de serviço: {e}")
        return []

def verificar_estrutura_banco():
    """Verifica a estrutura do banco de dados"""
    print("\n🔍 DEBUG: Verificando estrutura do banco...")
    
    try:
        # Listar todas as tabelas
        tables_sql = text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = session.execute(tables_sql).fetchall()
        
        print(f"   📊 Total de tabelas: {len(tables)}")
        
        tabelas_importantes = ['tipo_departamentos', 'tipo_setores', 'tipo_usuarios', 'ordens_servico']
        
        for tabela in tabelas_importantes:
            existe = any(t[0] == tabela for t in tables)
            if existe:
                # Contar registros
                count_sql = text(f"SELECT COUNT(*) FROM {tabela}")
                count = session.execute(count_sql).scalar()
                print(f"   ✅ {tabela}: {count} registros")
            else:
                print(f"   ❌ {tabela}: não existe")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar estrutura: {e}")
        return False

def main():
    """Função principal de debug"""
    print("🔍 DEBUG DO ENDPOINT PROGRAMACAO-FORM-DATA")
    print("=" * 60)
    
    try:
        # 1. Verificar estrutura do banco
        verificar_estrutura_banco()
        
        # 2. Debug de cada componente
        setores = debug_setores()
        usuarios = debug_usuarios()
        departamentos = debug_departamentos()
        ordens_servico = debug_ordens_servico()
        
        print("\n" + "=" * 60)
        print("📊 RESUMO DO DEBUG:")
        print(f"   🏭 Setores: {len(setores)}")
        print(f"   👥 Usuários: {len(usuarios)}")
        print(f"   🏢 Departamentos: {len(departamentos)}")
        print(f"   📋 Ordens de Serviço: {len(ordens_servico)}")
        
        if all([setores, usuarios, departamentos, ordens_servico]):
            print("\n✅ TODOS OS DADOS ESTÃO DISPONÍVEIS")
            print("   O problema pode estar na implementação do endpoint")
        else:
            print("\n❌ ALGUNS DADOS ESTÃO FALTANDO")
            print("   Verifique a população do banco de dados")
        
        # Verificar especificamente o departamento TESTE
        dept_teste = next((d for d in departamentos if d[1] == 'TESTE'), None)
        if dept_teste:
            print(f"\n🎯 DEPARTAMENTO TESTE:")
            print(f"   ID: {dept_teste[0]}")
            print(f"   Nome: {dept_teste[1]}")
            
            # Buscar setores do departamento TESTE
            setores_teste = [s for s in setores if s[3] == 'TESTE']
            print(f"   Setores: {len(setores_teste)}")
            for setor in setores_teste:
                print(f"      - {setor[1]} (ID: {setor[0]})")
        
    except Exception as e:
        print(f"\n❌ ERRO durante o debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
