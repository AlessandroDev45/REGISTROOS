#!/usr/bin/env python3
"""
Script para corrigir a estrutura final das tabelas
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def fazer_backup():
    """Faz backup antes das correções"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        backup_path = os.path.join(os.path.dirname(__file__), f'backup_correcao_estrutura_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def corrigir_ordens_servico():
    """Corrige a estrutura da tabela ordens_servico"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Corrigindo tabela ordens_servico...")
        
        # Verificar se o campo antigo existe e tem dados
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'testes_exclusivo' in colunas and 'testes_exclusivo_os' in colunas:
            print("🔄 Migrando dados de testes_exclusivo para testes_exclusivo_os...")
            
            # Migrar dados do campo antigo para o novo (apenas se o novo estiver vazio)
            cursor.execute("""
                UPDATE ordens_servico 
                SET testes_exclusivo_os = testes_exclusivo 
                WHERE testes_exclusivo IS NOT NULL 
                AND (testes_exclusivo_os IS NULL OR testes_exclusivo_os = '')
            """)
            
            rows_updated = cursor.rowcount
            print(f"✅ {rows_updated} registros migrados")
            
            # Como SQLite não suporta DROP COLUMN diretamente, vamos criar uma nova tabela
            print("🔄 Recriando tabela sem o campo antigo...")
            
            # 1. Criar tabela temporária com a estrutura correta
            cursor.execute("""
                CREATE TABLE ordens_servico_new (
                    id INTEGER PRIMARY KEY,
                    os_numero VARCHAR(50) NOT NULL,
                    status_os VARCHAR(50),
                    prioridade VARCHAR(20) DEFAULT 'MEDIA',
                    id_responsavel_registro INTEGER,
                    id_responsavel_pcp INTEGER,
                    id_responsavel_final INTEGER,
                    data_inicio_prevista DATETIME,
                    data_fim_prevista DATETIME,
                    data_criacao DATETIME,
                    data_ultima_atualizacao DATETIME,
                    criado_por INTEGER,
                    status_geral VARCHAR(50),
                    valor_total_previsto DECIMAL(15,2),
                    valor_total_real DECIMAL(15,2),
                    observacoes_gerais TEXT,
                    id_tipo_maquina INTEGER,
                    custo_total_real DECIMAL(15,2),
                    horas_previstas DECIMAL(10,2),
                    horas_reais DECIMAL(10,2),
                    data_programacao DATETIME,
                    horas_orcadas DECIMAL(10,2) DEFAULT 0,
                    testes_iniciais_finalizados BOOLEAN DEFAULT 0,
                    testes_parciais_finalizados BOOLEAN DEFAULT 0,
                    testes_finais_finalizados BOOLEAN DEFAULT 0,
                    data_testes_iniciais_finalizados DATETIME,
                    data_testes_parciais_finalizados DATETIME,
                    data_testes_finais_finalizados DATETIME,
                    id_usuario_testes_iniciais INTEGER,
                    id_usuario_testes_parciais INTEGER,
                    id_usuario_testes_finais INTEGER,
                    testes_exclusivo_os TEXT,
                    id_cliente INTEGER,
                    id_equipamento INTEGER,
                    id_setor INTEGER,
                    id_departamento INTEGER,
                    inicio_os DATETIME,
                    fim_os DATETIME,
                    descricao_maquina TEXT
                )
            """)
            
            # 2. Copiar dados (excluindo o campo antigo)
            cursor.execute("""
                INSERT INTO ordens_servico_new (
                    id, os_numero, status_os, prioridade, id_responsavel_registro,
                    id_responsavel_pcp, id_responsavel_final, data_inicio_prevista,
                    data_fim_prevista, data_criacao, data_ultima_atualizacao,
                    criado_por, status_geral, valor_total_previsto, valor_total_real,
                    observacoes_gerais, id_tipo_maquina, custo_total_real,
                    horas_previstas, horas_reais, data_programacao, horas_orcadas,
                    testes_iniciais_finalizados, testes_parciais_finalizados,
                    testes_finais_finalizados, data_testes_iniciais_finalizados,
                    data_testes_parciais_finalizados, data_testes_finais_finalizados,
                    id_usuario_testes_iniciais, id_usuario_testes_parciais,
                    id_usuario_testes_finais, testes_exclusivo_os, id_cliente,
                    id_equipamento, id_setor, id_departamento, inicio_os,
                    fim_os, descricao_maquina
                )
                SELECT 
                    id, os_numero, status_os, prioridade, id_responsavel_registro,
                    id_responsavel_pcp, id_responsavel_final, data_inicio_prevista,
                    data_fim_prevista, data_criacao, data_ultima_atualizacao,
                    criado_por, status_geral, valor_total_previsto, valor_total_real,
                    observacoes_gerais, id_tipo_maquina, custo_total_real,
                    horas_previstas, horas_reais, data_programacao, horas_orcadas,
                    testes_iniciais_finalizados, testes_parciais_finalizados,
                    testes_finais_finalizados, data_testes_iniciais_finalizados,
                    data_testes_parciais_finalizados, data_testes_finais_finalizados,
                    id_usuario_testes_iniciais, id_usuario_testes_parciais,
                    id_usuario_testes_finais, testes_exclusivo_os, id_cliente,
                    id_equipamento, id_setor, id_departamento, inicio_os,
                    fim_os, descricao_maquina
                FROM ordens_servico
            """)
            
            # 3. Remover tabela antiga e renomear nova
            cursor.execute("DROP TABLE ordens_servico")
            cursor.execute("ALTER TABLE ordens_servico_new RENAME TO ordens_servico")
            
            print("✅ Tabela ordens_servico corrigida!")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir ordens_servico: {e}")
        return False

def corrigir_apontamentos_detalhados():
    """Corrige a estrutura da tabela apontamentos_detalhados"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 Corrigindo tabela apontamentos_detalhados...")
        
        # Verificar se o campo setor está faltando
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'setor' not in colunas:
            print("➕ Adicionando campo 'setor' à tabela apontamentos_detalhados...")
            cursor.execute("ALTER TABLE apontamentos_detalhados ADD COLUMN setor VARCHAR(100)")
            print("✅ Campo 'setor' adicionado!")
        else:
            print("ℹ️ Campo 'setor' já existe na tabela apontamentos_detalhados")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir apontamentos_detalhados: {e}")
        return False

def verificar_correcoes():
    """Verifica se as correções foram aplicadas corretamente"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificando correções...")
        
        # Verificar ordens_servico
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas_os = [col[1] for col in cursor.fetchall()]
        
        tem_antigo = 'testes_exclusivo' in colunas_os
        tem_novo = 'testes_exclusivo_os' in colunas_os
        
        print(f"📋 ordens_servico:")
        print(f"  - Campo antigo 'testes_exclusivo': {'❌ AINDA EXISTE' if tem_antigo else '✅ REMOVIDO'}")
        print(f"  - Campo novo 'testes_exclusivo_os': {'✅ EXISTE' if tem_novo else '❌ FALTANDO'}")
        print(f"  - Total de colunas: {len(colunas_os)}")
        
        # Verificar apontamentos_detalhados
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas_ap = [col[1] for col in cursor.fetchall()]
        
        tem_setor = 'setor' in colunas_ap
        
        print(f"\n📋 apontamentos_detalhados:")
        print(f"  - Campo 'setor': {'✅ EXISTE' if tem_setor else '❌ FALTANDO'}")
        print(f"  - Total de colunas: {len(colunas_ap)}")
        
        conn.close()
        
        # Status geral
        sucesso_os = not tem_antigo and tem_novo
        sucesso_ap = tem_setor
        
        if sucesso_os and sucesso_ap:
            print("\n🎉 TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
            return True
        else:
            print(f"\n⚠️ Algumas correções falharam:")
            if not sucesso_os:
                print("  - ordens_servico ainda tem problemas")
            if not sucesso_ap:
                print("  - apontamentos_detalhados ainda tem problemas")
            return False
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🔧 Corrigindo estrutura final das tabelas...")
    print("=" * 60)
    
    # 1. Fazer backup
    if not fazer_backup():
        print("❌ Falha no backup. Abortando correções.")
        return False
    
    # 2. Corrigir ordens_servico
    if not corrigir_ordens_servico():
        print("❌ Falha na correção da ordens_servico.")
        return False
    
    # 3. Corrigir apontamentos_detalhados
    if not corrigir_apontamentos_detalhados():
        print("❌ Falha na correção da apontamentos_detalhados.")
        return False
    
    # 4. Verificar correções
    if not verificar_correcoes():
        print("❌ Verificação das correções falhou.")
        return False
    
    print("\n🎉 Estrutura do banco corrigida com sucesso!")
    print("✅ Backup criado")
    print("✅ ordens_servico corrigida")
    print("✅ apontamentos_detalhados corrigida")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
