#!/usr/bin/env python3
"""
Script para migrar a estrutura do banco de dados para a nova especificação
ATENÇÃO: Este script faz backup antes de executar as alterações
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def fazer_backup_database():
    """Faz backup do banco de dados antes da migração"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        if not os.path.exists(db_path):
            print("❌ Banco de dados não encontrado!")
            print(f"Procurando em: {db_path}")
            return False
            
        backup_path = os.path.join(os.path.dirname(__file__), f'backup_registroos_new_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        
        # Copiar arquivo
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def verificar_estrutura_atual():
    """Verifica a estrutura atual do banco"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando estrutura atual...")
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tabelas existentes: {len(tabelas)}")
        for tabela in sorted(tabelas):
            print(f"  - {tabela}")
        
        # Verificar estrutura da ordens_servico
        print("\n📋 Estrutura atual da ordens_servico:")
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas_os = cursor.fetchall()
        for col in colunas_os:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def executar_migracao():
    """Executa a migração usando SQLAlchemy"""
    try:
        print("\n🔄 Executando migração com SQLAlchemy...")
        
        from sqlalchemy import create_engine
        from app.database_models import Base
        
        # Conectar ao banco
        db_path = os.path.join(backend_path, 'registroos_new.db')
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Criar/atualizar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Migração executada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

def verificar_pos_migracao():
    """Verifica se a migração foi bem-sucedida"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificando estrutura pós-migração...")
        
        # Verificar novos campos na ordens_servico
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas_os = [col[1] for col in cursor.fetchall()]
        
        campos_esperados = [
            'id_usuario_testes_iniciais', 'id_usuario_testes_parciais', 
            'id_usuario_testes_finais', 'testes_exclusivo_os', 'status_geral'
        ]
        
        campos_faltando = []
        for campo in campos_esperados:
            if campo not in colunas_os:
                campos_faltando.append(campo)
        
        if campos_faltando:
            print(f"⚠️ Campos ainda faltando: {campos_faltando}")
        else:
            print("✅ Todos os campos esperados estão presentes!")
        
        # Verificar estrutura do apontamentos_detalhados
        cursor.execute("PRAGMA table_info(apontamentos_detalhados)")
        colunas_ap = [col[1] for col in cursor.fetchall()]
        
        campos_ap_esperados = [
            'causa_retrabalho', 'observacao_os', 'servico_de_campo',
            'etapa_inicial', 'etapa_parcial', 'etapa_final'
        ]
        
        campos_ap_faltando = []
        for campo in campos_ap_esperados:
            if campo not in colunas_ap:
                campos_ap_faltando.append(campo)
        
        if campos_ap_faltando:
            print(f"⚠️ Campos faltando em apontamentos_detalhados: {campos_ap_faltando}")
        else:
            print("✅ Apontamentos_detalhados com estrutura correta!")
        
        conn.close()
        return len(campos_faltando) == 0 and len(campos_ap_faltando) == 0
    except Exception as e:
        print(f"❌ Erro na verificação pós-migração: {e}")
        return False

def main():
    print("🚀 Iniciando migração da estrutura do banco de dados...")
    print("=" * 60)
    
    # 1. Fazer backup
    if not fazer_backup_database():
        print("❌ Falha no backup. Abortando migração.")
        return False
    
    # 2. Verificar estrutura atual
    if not verificar_estrutura_atual():
        print("❌ Falha na verificação da estrutura atual.")
        return False
    
    # 3. Executar migração
    if not executar_migracao():
        print("❌ Falha na migração.")
        return False
    
    # 4. Verificar pós-migração
    if not verificar_pos_migracao():
        print("⚠️ Migração executada, mas alguns campos podem estar faltando.")
        return False
    
    print("\n🎉 Migração concluída com sucesso!")
    print("✅ Backup criado")
    print("✅ Estrutura atualizada")
    print("✅ Verificação pós-migração OK")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
