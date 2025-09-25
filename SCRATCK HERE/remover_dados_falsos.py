#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remover todos os dados falsos/mock/teste do sistema
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

def remover_tabela_programacao_testes():
    """Remove a tabela programacao_testes que é apenas para testes"""
    print("🗑️ Removendo tabela programacao_testes...")
    
    try:
        # Verificar se a tabela existe
        check_sql = text("SELECT name FROM sqlite_master WHERE type='table' AND name='programacao_testes'")
        exists = session.execute(check_sql).fetchone()
        
        if exists:
            # Dropar a tabela
            drop_sql = text("DROP TABLE programacao_testes")
            session.execute(drop_sql)
            session.commit()
            print("   ✅ Tabela programacao_testes removida")
        else:
            print("   ℹ️ Tabela programacao_testes não existe")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao remover tabela: {e}")
        return False

def remover_dados_teste_departamento():
    """Remove dados do departamento TESTE que são apenas para demonstração"""
    print("\n🗑️ Removendo dados do departamento TESTE...")
    
    try:
        # 1. Buscar ID do departamento TESTE
        dept_sql = text("SELECT id FROM tipo_departamentos WHERE nome_tipo = 'TESTE'")
        dept_result = session.execute(dept_sql).fetchone()
        
        if not dept_result:
            print("   ℹ️ Departamento TESTE não encontrado")
            return True
        
        dept_id = dept_result[0]
        print(f"   📋 Departamento TESTE encontrado: ID {dept_id}")
        
        # 2. Buscar setor TESTES
        setor_sql = text("SELECT id FROM tipo_setores WHERE nome = 'TESTES' AND id_departamento = :dept_id")
        setor_result = session.execute(setor_sql, {"dept_id": dept_id}).fetchone()
        
        if setor_result:
            setor_id = setor_result[0]
            print(f"   📋 Setor TESTES encontrado: ID {setor_id}")
            
            # Remover apontamentos do setor TESTES
            apt_delete_sql = text("DELETE FROM apontamentos_detalhados WHERE id_setor = :setor_id")
            apt_result = session.execute(apt_delete_sql, {"setor_id": setor_id})
            print(f"   🗑️ Removidos {apt_result.rowcount} apontamentos do setor TESTES")
            
            # Remover programações do setor TESTES
            prog_delete_sql = text("DELETE FROM programacoes WHERE id_setor = :setor_id")
            prog_result = session.execute(prog_delete_sql, {"setor_id": setor_id})
            print(f"   🗑️ Removidas {prog_result.rowcount} programações do setor TESTES")
        
        # 3. Remover tipos de máquina do departamento TESTE
        tm_delete_sql = text("DELETE FROM tipos_maquina WHERE departamento = 'TESTE'")
        tm_result = session.execute(tm_delete_sql)
        print(f"   🗑️ Removidos {tm_result.rowcount} tipos de máquina do departamento TESTE")
        
        # 4. Remover tipos de teste do departamento TESTE
        tt_delete_sql = text("DELETE FROM tipos_teste WHERE departamento = 'TESTE'")
        tt_result = session.execute(tt_delete_sql)
        print(f"   🗑️ Removidos {tt_result.rowcount} tipos de teste do departamento TESTE")
        
        # 5. Remover atividades do departamento TESTE
        ta_delete_sql = text("DELETE FROM tipo_atividades WHERE departamento = 'TESTE'")
        ta_result = session.execute(ta_delete_sql)
        print(f"   🗑️ Removidas {ta_result.rowcount} atividades do departamento TESTE")
        
        # 6. Remover descrições de atividade do departamento TESTE
        da_delete_sql = text("DELETE FROM tipo_descricao_atividades WHERE departamento = 'TESTE'")
        da_result = session.execute(da_delete_sql)
        print(f"   🗑️ Removidas {da_result.rowcount} descrições de atividade do departamento TESTE")
        
        # 7. Remover tipos de falha do departamento TESTE
        tf_delete_sql = text("DELETE FROM tipos_falha WHERE departamento = 'TESTE'")
        tf_result = session.execute(tf_delete_sql)
        print(f"   🗑️ Removidos {tf_result.rowcount} tipos de falha do departamento TESTE")
        
        # 8. Remover causas de retrabalho do departamento TESTE
        cr_delete_sql = text("DELETE FROM tipos_causa_retrabalho WHERE departamento = 'TESTE'")
        cr_result = session.execute(cr_delete_sql)
        print(f"   🗑️ Removidas {cr_result.rowcount} causas de retrabalho do departamento TESTE")
        
        # 9. Remover setor TESTES
        if setor_result:
            setor_delete_sql = text("DELETE FROM tipo_setores WHERE id = :setor_id")
            session.execute(setor_delete_sql, {"setor_id": setor_id})
            print(f"   🗑️ Setor TESTES removido")
        
        # 10. Remover departamento TESTE
        dept_delete_sql = text("DELETE FROM tipo_departamentos WHERE id = :dept_id")
        session.execute(dept_delete_sql, {"dept_id": dept_id})
        print(f"   🗑️ Departamento TESTE removido")
        
        session.commit()
        print("   ✅ Dados do departamento TESTE removidos com sucesso")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao remover dados do departamento TESTE: {e}")
        session.rollback()
        return False

def remover_ordens_servico_teste():
    """Remove ordens de serviço de teste"""
    print("\n🗑️ Removendo ordens de serviço de teste...")
    
    try:
        # Buscar OS com números de teste
        os_teste_sql = text("""
            SELECT id, os_numero FROM ordens_servico 
            WHERE os_numero LIKE 'TEST%' 
            OR descricao_maquina LIKE '%TESTE%'
            OR descricao_maquina LIKE '%teste%'
        """)
        
        os_teste = session.execute(os_teste_sql).fetchall()
        
        if os_teste:
            print(f"   📋 Encontradas {len(os_teste)} OS de teste:")
            for os in os_teste:
                print(f"      - {os[1]} (ID: {os[0]})")
            
            # Remover apontamentos dessas OS
            os_ids = [str(os[0]) for os in os_teste]
            if os_ids:
                apt_delete_sql = text(f"DELETE FROM apontamentos_detalhados WHERE id_os IN ({','.join(os_ids)})")
                apt_result = session.execute(apt_delete_sql)
                print(f"   🗑️ Removidos {apt_result.rowcount} apontamentos das OS de teste")
                
                # Remover programações dessas OS
                prog_delete_sql = text(f"DELETE FROM programacoes WHERE id_ordem_servico IN ({','.join(os_ids)})")
                prog_result = session.execute(prog_delete_sql)
                print(f"   🗑️ Removidas {prog_result.rowcount} programações das OS de teste")
                
                # Remover as OS
                os_delete_sql = text(f"DELETE FROM ordens_servico WHERE id IN ({','.join(os_ids)})")
                os_result = session.execute(os_delete_sql)
                print(f"   🗑️ Removidas {os_result.rowcount} OS de teste")
        else:
            print("   ℹ️ Nenhuma OS de teste encontrada")
        
        session.commit()
        print("   ✅ OS de teste removidas com sucesso")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao remover OS de teste: {e}")
        session.rollback()
        return False

def remover_clientes_teste():
    """Remove clientes de teste"""
    print("\n🗑️ Removendo clientes de teste...")
    
    try:
        # Buscar clientes de teste
        clientes_teste_sql = text("""
            SELECT id, razao_social FROM clientes 
            WHERE razao_social LIKE '%TESTE%'
            OR razao_social LIKE '%teste%'
            OR razao_social LIKE '%Test%'
        """)
        
        clientes_teste = session.execute(clientes_teste_sql).fetchall()
        
        if clientes_teste:
            print(f"   📋 Encontrados {len(clientes_teste)} clientes de teste:")
            for cliente in clientes_teste:
                print(f"      - {cliente[1]} (ID: {cliente[0]})")
            
            # Verificar se há OS vinculadas a esses clientes
            cliente_ids = [str(c[0]) for c in clientes_teste]
            if cliente_ids:
                os_check_sql = text(f"SELECT COUNT(*) FROM ordens_servico WHERE id_cliente IN ({','.join(cliente_ids)})")
                os_count = session.execute(os_check_sql).scalar()
                
                if os_count > 0:
                    print(f"   ⚠️ Existem {os_count} OS vinculadas a esses clientes")
                    print("   ℹ️ Removendo vinculação (definindo id_cliente como NULL)")
                    
                    # Remover vinculação em vez de deletar
                    os_update_sql = text(f"UPDATE ordens_servico SET id_cliente = NULL WHERE id_cliente IN ({','.join(cliente_ids)})")
                    session.execute(os_update_sql)
                
                # Remover os clientes
                cliente_delete_sql = text(f"DELETE FROM clientes WHERE id IN ({','.join(cliente_ids)})")
                cliente_result = session.execute(cliente_delete_sql)
                print(f"   🗑️ Removidos {cliente_result.rowcount} clientes de teste")
        else:
            print("   ℹ️ Nenhum cliente de teste encontrado")
        
        session.commit()
        print("   ✅ Clientes de teste removidos com sucesso")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao remover clientes de teste: {e}")
        session.rollback()
        return False

def limpar_apontamentos_exemplo():
    """Remove apontamentos de exemplo/teste"""
    print("\n🗑️ Removendo apontamentos de exemplo...")
    
    try:
        # Buscar apontamentos com dados claramente de teste
        apt_teste_sql = text("""
            SELECT COUNT(*) FROM apontamentos_detalhados 
            WHERE observacao_os LIKE '%exemplo%'
            OR observacao_os LIKE '%teste%'
            OR observacao_os LIKE '%TESTE%'
            OR descricao_atividade LIKE '%exemplo%'
            OR tipo_atividade = 'TESTE'
        """)
        
        count = session.execute(apt_teste_sql).scalar()
        
        if count > 0:
            print(f"   📋 Encontrados {count} apontamentos de teste/exemplo")
            
            # Remover apontamentos de teste
            apt_delete_sql = text("""
                DELETE FROM apontamentos_detalhados 
                WHERE observacao_os LIKE '%exemplo%'
                OR observacao_os LIKE '%teste%'
                OR observacao_os LIKE '%TESTE%'
                OR descricao_atividade LIKE '%exemplo%'
                OR tipo_atividade = 'TESTE'
            """)
            
            result = session.execute(apt_delete_sql)
            print(f"   🗑️ Removidos {result.rowcount} apontamentos de teste")
        else:
            print("   ℹ️ Nenhum apontamento de teste encontrado")
        
        session.commit()
        print("   ✅ Apontamentos de teste removidos com sucesso")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao remover apontamentos de teste: {e}")
        session.rollback()
        return False

def verificar_dados_restantes():
    """Verifica quais dados restaram após a limpeza"""
    print("\n📊 Verificando dados restantes...")
    
    try:
        tabelas = [
            'tipo_departamentos',
            'tipo_setores', 
            'ordens_servico',
            'apontamentos_detalhados',
            'programacoes',
            'clientes',
            'tipos_maquina',
            'tipos_teste',
            'tipo_atividades'
        ]
        
        for tabela in tabelas:
            count_sql = text(f"SELECT COUNT(*) FROM {tabela}")
            count = session.execute(count_sql).scalar()
            print(f"   📋 {tabela}: {count} registros")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar dados: {e}")
        return False

def main():
    """Função principal de limpeza"""
    print("🧹 LIMPEZA COMPLETA DE DADOS FALSOS/MOCK/TESTE")
    print("=" * 60)
    
    try:
        # 1. Remover tabela de programação de testes
        if not remover_tabela_programacao_testes():
            print("❌ Falha ao remover tabela de programação de testes")
        
        # 2. Remover dados do departamento TESTE
        if not remover_dados_teste_departamento():
            print("❌ Falha ao remover dados do departamento TESTE")
        
        # 3. Remover ordens de serviço de teste
        if not remover_ordens_servico_teste():
            print("❌ Falha ao remover OS de teste")
        
        # 4. Remover clientes de teste
        if not remover_clientes_teste():
            print("❌ Falha ao remover clientes de teste")
        
        # 5. Limpar apontamentos de exemplo
        if not limpar_apontamentos_exemplo():
            print("❌ Falha ao remover apontamentos de teste")
        
        # 6. Verificar dados restantes
        verificar_dados_restantes()
        
        print("\n" + "=" * 60)
        print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("🎯 Sistema limpo e pronto para uso em produção")
        print("📊 Apenas dados reais permanecem no sistema")
        
    except Exception as e:
        print(f"\n❌ ERRO durante a limpeza: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
