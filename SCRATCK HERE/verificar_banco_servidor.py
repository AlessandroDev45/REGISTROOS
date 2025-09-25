#!/usr/bin/env python3
"""
Script para verificar exatamente qual banco o servidor está usando
"""

import sys
import os
import sqlite3

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

def verificar_banco_direto():
    """Verifica o banco diretamente usando a mesma configuração do servidor"""
    try:
        print("🔍 Verificando banco usando a mesma configuração do servidor...")
        
        from config.database_config import DATABASE_URL, db_path, SessionLocal
        from app.database_models import Usuario
        
        print(f"  📂 DATABASE_URL: {DATABASE_URL}")
        print(f"  📂 db_path: {db_path}")
        print(f"  📂 Arquivo existe: {os.path.exists(db_path)}")
        
        if os.path.exists(db_path):
            # Verificar tamanho do arquivo
            size = os.path.getsize(db_path)
            print(f"  📊 Tamanho do arquivo: {size} bytes")
            
            # Verificar com SQLite direto
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = [row[0] for row in cursor.fetchall()]
            print(f"  📋 Tabelas no banco: {len(tabelas)}")
            for tabela in tabelas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"    - {tabela}: {count} registros")
            
            conn.close()
            
            # Verificar com SQLAlchemy (mesma forma que o servidor)
            print(f"\n🔍 Verificando com SQLAlchemy (como o servidor)...")
            db = SessionLocal()
            
            try:
                # Contar usuários
                count = db.query(Usuario).count()
                print(f"  📊 Usuários via SQLAlchemy: {count}")
                
                if count > 0:
                    # Buscar alguns usuários
                    usuarios = db.query(Usuario).limit(3).all()
                    print(f"  📋 Primeiros usuários:")
                    for user in usuarios:
                        print(f"    - {user.email}")
                else:
                    print(f"  ⚠️ Nenhum usuário encontrado via SQLAlchemy")
                    
                    # Verificar se a tabela existe
                    from sqlalchemy import inspect
                    inspector = inspect(db.bind)
                    tabelas_sqlalchemy = inspector.get_table_names()
                    print(f"  📋 Tabelas via SQLAlchemy: {tabelas_sqlalchemy}")
                    
                    if 'tipo_usuarios' in tabelas_sqlalchemy:
                        print(f"  ✅ Tabela tipo_usuarios existe via SQLAlchemy")
                        
                        # Tentar query direta
                        result = db.execute("SELECT COUNT(*) FROM tipo_usuarios")
                        count_direto = result.scalar()
                        print(f"  📊 Usuários via query direta: {count_direto}")
                    else:
                        print(f"  ❌ Tabela tipo_usuarios NÃO existe via SQLAlchemy")
                
            except Exception as e:
                print(f"  ❌ Erro com SQLAlchemy: {e}")
            finally:
                db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def criar_tabelas_se_necessario():
    """Cria as tabelas se elas não existirem"""
    try:
        print(f"\n🔧 Verificando se as tabelas precisam ser criadas...")
        
        from config.database_config import create_tables, engine
        from app.database_models import Base
        
        # Verificar se as tabelas existem
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tabelas_existentes = inspector.get_table_names()
        
        print(f"  📋 Tabelas existentes: {tabelas_existentes}")
        
        if 'tipo_usuarios' not in tabelas_existentes:
            print(f"  ⚠️ Tabela tipo_usuarios não existe - criando tabelas...")
            Base.metadata.create_all(bind=engine)
            print(f"  ✅ Tabelas criadas!")
        else:
            print(f"  ✅ Tabelas já existem")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def main():
    print("🔍 Verificação completa do banco usado pelo servidor...")
    print("=" * 60)
    
    # 1. Verificar banco direto
    verificar_banco_direto()
    
    # 2. Criar tabelas se necessário
    criar_tabelas_se_necessario()
    
    # 3. Verificar novamente
    print(f"\n🔍 Verificação final...")
    verificar_banco_direto()
    
    print(f"\n🎯 Verificação concluída!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
