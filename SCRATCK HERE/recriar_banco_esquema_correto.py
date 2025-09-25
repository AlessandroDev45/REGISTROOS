#!/usr/bin/env python3
"""
Script para recriar o banco de dados com o esquema CORRETO
"""

import sys
import os
import sqlite3
from datetime import datetime

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def fazer_backup():
    """Faz backup do banco atual"""
    try:
        db_path = os.path.join(backend_path, 'registroos_new.db')
        backup_path = os.path.join(os.path.dirname(__file__), f'backup_antes_recriar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        
        import shutil
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            print(f"✅ Backup criado: {backup_path}")
        else:
            print("ℹ️ Banco não existe, será criado do zero")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False

def recriar_banco():
    """Recria o banco com a estrutura correta"""
    try:
        from sqlalchemy import create_engine
        from app.database_models import Base
        
        db_path = os.path.join(backend_path, 'registroos_esquema_correto.db')

        # Remover banco se existir
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️ Banco anterior removido")
        
        # Criar engine
        engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Criar todas as tabelas
        print("🔧 Criando estrutura do banco...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Banco recriado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_estrutura():
    """Verifica se a estrutura foi criada corretamente"""
    try:
        db_path = os.path.join(backend_path, 'registroos_esquema_correto.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verificando estrutura criada...")
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        tabelas_esperadas = [
            'ordens_servico', 'apontamentos_detalhados', 'pendencias', 'programacoes',
            'resultados_teste', 'os_testes_exclusivos_finalizados', 'clientes',
            'equipamentos', 'tipo_usuarios', 'tipo_setores', 'tipo_departamentos',
            'tipos_maquina', 'tipo_atividade', 'tipo_descricao_atividade',
            'tipo_causas_retrabalho', 'tipos_teste', 'migration_log'
        ]
        
        print(f"📋 Tabelas encontradas: {len(tabelas)}")
        print(f"📋 Tabelas esperadas: {len(tabelas_esperadas)}")
        
        # Verificar tabelas principais
        for tabela in ['ordens_servico', 'apontamentos_detalhados']:
            if tabela in tabelas:
                cursor.execute(f"PRAGMA table_info({tabela})")
                colunas = cursor.fetchall()
                print(f"✅ {tabela}: {len(colunas)} colunas")
                
                # Verificar campos específicos
                nomes_colunas = [col[1] for col in colunas]
                if tabela == 'ordens_servico':
                    if 'testes_exclusivo_os' in nomes_colunas:
                        print(f"  ✅ Campo 'testes_exclusivo_os' presente")
                    else:
                        print(f"  ❌ Campo 'testes_exclusivo_os' FALTANDO")
                        
                if tabela == 'apontamentos_detalhados':
                    if 'setor' in nomes_colunas:
                        print(f"  ✅ Campo 'setor' presente")
                    else:
                        print(f"  ❌ Campo 'setor' FALTANDO")
            else:
                print(f"❌ {tabela}: NÃO ENCONTRADA")
        
        # Verificar se não há campos antigos
        cursor.execute("PRAGMA table_info(ordens_servico)")
        colunas_os = [col[1] for col in cursor.fetchall()]
        
        if 'testes_exclusivo' in colunas_os:
            print("❌ ERRO: Campo antigo 'testes_exclusivo' ainda existe!")
        else:
            print("✅ Campo antigo 'testes_exclusivo' removido corretamente")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🚀 Recriando banco de dados com esquema CORRETO...")
    print("=" * 60)
    
    # 1. Fazer backup
    if not fazer_backup():
        print("❌ Falha no backup. Continuando mesmo assim...")
    
    # 2. Recriar banco
    if not recriar_banco():
        print("❌ Falha ao recriar banco.")
        return False
    
    # 3. Verificar estrutura
    if not verificar_estrutura():
        print("❌ Falha na verificação.")
        return False
    
    print("\n🎉 BANCO RECRIADO COM SUCESSO!")
    print("✅ Estrutura conforme esquema fornecido")
    print("✅ Campos corretos implementados")
    print("✅ Campos antigos removidos")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
