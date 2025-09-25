#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text

def verificar_usuarios():
    try:
        db = next(get_db())
        
        # Verificar usuários
        result = db.execute(text("SELECT id, nome_completo, email, nome_usuario, privilege_level FROM tipo_usuarios LIMIT 5"))
        usuarios = [dict(row._mapping) for row in result]
        
        print("👥 Usuários no sistema:")
        for user in usuarios:
            print(f"  ID: {user['id']}")
            print(f"  Nome: {user['nome_completo']}")
            print(f"  Email: {user['email']}")
            print(f"  Username: {user['nome_usuario']}")
            print(f"  Privilege: {user['privilege_level']}")
            print("  ---")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_usuarios()
