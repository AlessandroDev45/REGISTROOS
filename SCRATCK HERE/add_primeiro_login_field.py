#!/usr/bin/env python3
"""
Script para adicionar o campo primeiro_login na tabela tipo_usuarios
"""

import sqlite3
import os
import sys

# Adicionar o diretório backend ao path para importar as configurações
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'registrooficial', 'backend'))

def add_primeiro_login_field():
    """Adiciona o campo primeiro_login na tabela tipo_usuarios se não existir"""
    
    # Caminho para o banco de dados
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(tipo_usuarios)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'primeiro_login' in columns:
            print("✅ Campo 'primeiro_login' já existe na tabela tipo_usuarios")
            return True
        
        # Adicionar a coluna
        print("🔄 Adicionando campo 'primeiro_login' na tabela tipo_usuarios...")
        cursor.execute("""
            ALTER TABLE tipo_usuarios 
            ADD COLUMN primeiro_login BOOLEAN NOT NULL DEFAULT 0
        """)
        
        # Verificar se existem usuários criados pelo admin que precisam trocar senha
        # (usuários com is_approved=1 e data_criacao recente podem ser candidatos)
        cursor.execute("""
            SELECT id, nome_completo, email, data_criacao 
            FROM tipo_usuarios 
            WHERE is_approved = 1
        """)
        
        usuarios = cursor.fetchall()
        print(f"📊 Encontrados {len(usuarios)} usuários aprovados")
        
        # Para este teste, vamos marcar todos os usuários existentes como primeiro_login=0
        # (assumindo que já fizeram login antes)
        cursor.execute("""
            UPDATE tipo_usuarios 
            SET primeiro_login = 0 
            WHERE is_approved = 1
        """)
        
        conn.commit()
        print("✅ Campo 'primeiro_login' adicionado com sucesso!")
        print("✅ Usuários existentes marcados como primeiro_login=0")
        
        # Mostrar estrutura da tabela atualizada
        cursor.execute("PRAGMA table_info(tipo_usuarios)")
        columns = cursor.fetchall()
        print("\n📋 Estrutura atual da tabela tipo_usuarios:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'DEFAULT ' + str(col[4]) if col[4] else ''}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao modificar banco de dados: {e}")
        return False
    finally:
        if conn:
            conn.close()

def test_primeiro_login_functionality():
    """Testa a funcionalidade de primeiro login"""
    
    db_path = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend\registroos_new.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🧪 Testando funcionalidade de primeiro login...")
        
        # Verificar se há usuários com primeiro_login=1
        cursor.execute("""
            SELECT id, nome_completo, email, primeiro_login 
            FROM tipo_usuarios 
            WHERE primeiro_login = 1
        """)
        
        usuarios_primeiro_login = cursor.fetchall()
        print(f"📊 Usuários que precisam trocar senha: {len(usuarios_primeiro_login)}")
        
        for usuario in usuarios_primeiro_login:
            print(f"  - {usuario[1]} ({usuario[2]}) - primeiro_login: {usuario[3]}")
        
        # Verificar estrutura completa
        cursor.execute("""
            SELECT id, nome_completo, email, privilege_level, is_approved, primeiro_login 
            FROM tipo_usuarios 
            ORDER BY id
        """)
        
        todos_usuarios = cursor.fetchall()
        print(f"\n📋 Todos os usuários ({len(todos_usuarios)}):")
        for usuario in todos_usuarios:
            status = "✅ Aprovado" if usuario[4] else "⏳ Pendente"
            primeiro = "🔐 Precisa trocar senha" if usuario[5] else "✅ Senha OK"
            print(f"  - {usuario[1]} ({usuario[2]}) - {usuario[3]} - {status} - {primeiro}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao testar funcionalidade: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando migração do campo primeiro_login...")
    
    if add_primeiro_login_field():
        test_primeiro_login_functionality()
        print("\n✅ Migração concluída com sucesso!")
        print("\n📝 Próximos passos:")
        print("1. Reinicie o backend para aplicar as mudanças no modelo")
        print("2. Teste criando um novo usuário via admin")
        print("3. Faça login com o novo usuário para testar a troca obrigatória de senha")
    else:
        print("\n❌ Falha na migração!")
        sys.exit(1)
