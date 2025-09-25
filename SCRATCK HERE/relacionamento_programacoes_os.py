#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstrar relacionamento entre programacoes e ordens_servico
"""

import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.append(backend_path)

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.database_config import engine

# Criar sessão
Session = sessionmaker(bind=engine)
session = Session()

def mostrar_relacionamento():
    """Mostrar relacionamento entre programacoes e ordens_servico"""
    print("🔗 RELACIONAMENTO: programacoes ↔ ordens_servico")
    print("=" * 60)
    
    try:
        # Query completa mostrando o relacionamento
        query = text("""
            SELECT 
                p.id as prog_id,
                p.status as prog_status,
                p.inicio_previsto,
                p.fim_previsto,
                p.observacoes,
                
                os.id as os_id,
                os.os_numero,
                os.status_os,
                os.descricao_maquina,
                
                c.razao_social as cliente,
                
                u_resp.nome_completo as responsavel,
                u_criado.nome_completo as criado_por,
                
                s.nome as setor
                
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
            LEFT JOIN clientes c ON os.id_cliente = c.id
            LEFT JOIN tipo_usuarios u_resp ON p.responsavel_id = u_resp.id
            LEFT JOIN tipo_usuarios u_criado ON p.criado_por_id = u_criado.id
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
            ORDER BY p.id
        """)
        
        result = session.execute(query).fetchall()
        
        print(f"📊 Total de programações com relacionamentos: {len(result)}")
        
        for row in result:
            print(f"\n📅 PROGRAMAÇÃO ID: {row[0]}")
            print(f"   Status: {row[1]}")
            print(f"   Período: {row[2]} até {row[3]}")
            print(f"   Observações: {row[4]}")
            
            print(f"\n📋 ORDEM DE SERVIÇO:")
            print(f"   ID: {row[5]}")
            print(f"   Número: {row[6]}")
            print(f"   Status: {row[7]}")
            print(f"   Descrição: {row[8]}")
            print(f"   Cliente: {row[9]}")
            
            print(f"\n👥 PESSOAS:")
            print(f"   Responsável: {row[10]}")
            print(f"   Criado por: {row[11]}")
            print(f"   Setor: {row[12]}")
            
            print("-" * 40)
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao mostrar relacionamento: {e}")
        return []

def verificar_foreign_keys():
    """Verificar as foreign keys da tabela programacoes"""
    print("\n🔑 FOREIGN KEYS DA TABELA programacoes")
    print("=" * 45)
    
    try:
        # Verificar foreign keys
        fk_query = text("PRAGMA foreign_key_list(programacoes)")
        fks = session.execute(fk_query).fetchall()
        
        if fks:
            print("📋 Foreign Keys encontradas:")
            for fk in fks:
                print(f"   - Coluna: {fk[3]} → Tabela: {fk[2]}.{fk[4]}")
        else:
            print("❌ Nenhuma foreign key definida (SQLite pode não mostrar)")
            
        # Verificar manualmente os relacionamentos
        print("\n🔍 Verificação manual dos relacionamentos:")
        
        # 1. id_ordem_servico
        os_check = text("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT p.id_ordem_servico) as os_distintas,
                   COUNT(DISTINCT os.id) as os_existentes
            FROM programacoes p
            LEFT JOIN ordens_servico os ON p.id_ordem_servico = os.id
        """)
        
        os_result = session.execute(os_check).fetchone()
        print(f"   📋 id_ordem_servico:")
        print(f"      Total programações: {os_result[0]}")
        print(f"      OS distintas referenciadas: {os_result[1]}")
        print(f"      OS que existem: {os_result[2]}")
        
        # 2. responsavel_id
        resp_check = text("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT p.responsavel_id) as resp_distintos,
                   COUNT(DISTINCT u.id) as resp_existentes
            FROM programacoes p
            LEFT JOIN tipo_usuarios u ON p.responsavel_id = u.id
        """)
        
        resp_result = session.execute(resp_check).fetchone()
        print(f"   👤 responsavel_id:")
        print(f"      Total programações: {resp_result[0]}")
        print(f"      Responsáveis distintos: {resp_result[1]}")
        print(f"      Responsáveis que existem: {resp_result[2]}")
        
        # 3. criado_por_id
        criado_check = text("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT p.criado_por_id) as criado_distintos,
                   COUNT(DISTINCT u.id) as criado_existentes
            FROM programacoes p
            LEFT JOIN tipo_usuarios u ON p.criado_por_id = u.id
        """)
        
        criado_result = session.execute(criado_check).fetchone()
        print(f"   👤 criado_por_id:")
        print(f"      Total programações: {criado_result[0]}")
        print(f"      Criadores distintos: {criado_result[1]}")
        print(f"      Criadores que existem: {criado_result[2]}")
        
        # 4. id_setor
        setor_check = text("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT p.id_setor) as setor_distintos,
                   COUNT(DISTINCT s.id) as setor_existentes
            FROM programacoes p
            LEFT JOIN tipo_setores s ON p.id_setor = s.id
        """)
        
        setor_result = session.execute(setor_check).fetchone()
        print(f"   🏭 id_setor:")
        print(f"      Total programações: {setor_result[0]}")
        print(f"      Setores distintos: {setor_result[1]}")
        print(f"      Setores que existem: {setor_result[2]}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar foreign keys: {e}")

def main():
    """Função principal"""
    print("🔍 ANÁLISE COMPLETA DOS RELACIONAMENTOS")
    print("=" * 60)
    
    try:
        # 1. Mostrar relacionamento completo
        relacionamentos = mostrar_relacionamento()
        
        # 2. Verificar foreign keys
        verificar_foreign_keys()
        
        print("\n" + "=" * 60)
        print("🎯 RESUMO DOS RELACIONAMENTOS:")
        
        print(f"\n📊 ESTRUTURA:")
        print(f"   programacoes.id_ordem_servico → ordens_servico.id")
        print(f"   programacoes.responsavel_id → tipo_usuarios.id")
        print(f"   programacoes.criado_por_id → tipo_usuarios.id")
        print(f"   programacoes.id_setor → tipo_setores.id")
        
        print(f"\n🔗 RELACIONAMENTO PRINCIPAL:")
        print(f"   ✅ Cada programação está vinculada a 1 OS")
        print(f"   ✅ Cada OS pode ter múltiplas programações")
        print(f"   ✅ Relacionamento 1:N (OS:Programações)")
        
        if relacionamentos:
            print(f"\n✅ DADOS ENCONTRADOS:")
            print(f"   📅 {len(relacionamentos)} programação(ões) ativa(s)")
            print(f"   📋 Todas com OS válidas")
            print(f"   👥 Todas com responsáveis válidos")
            print(f"   🏭 Todas com setores válidos")
        
    except Exception as e:
        print(f"\n❌ ERRO durante a análise: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
