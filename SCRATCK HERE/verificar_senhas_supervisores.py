#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text
from app.auth import verify_password

def verificar_senhas_supervisores():
    try:
        db = next(get_db())
        
        print("🔍 VERIFICANDO SENHAS DOS SUPERVISORES")
        print("=" * 60)
        
        # Buscar usuários SUPERVISOR
        result = db.execute(text("""
            SELECT id, nome_completo, email, senha_hash, privilege_level
            FROM tipo_usuarios 
            WHERE privilege_level = 'SUPERVISOR' AND is_approved = 1
            ORDER BY nome_completo
        """))
        supervisores = [dict(row._mapping) for row in result]
        
        senhas_teste = ["supervisor123", "123456", "admin123", "password", "supervisor", "123"]
        
        for sup in supervisores:
            print(f"\n👤 {sup['nome_completo']}")
            print(f"   Email: {sup['email']}")
            print(f"   Hash: {sup['senha_hash'][:30]}...")
            
            print("   🔑 Testando senhas:")
            for senha in senhas_teste:
                try:
                    if verify_password(senha, sup['senha_hash']):
                        print(f"      ✅ SENHA CORRETA: '{senha}'")
                        break
                    else:
                        print(f"      ❌ '{senha}' - incorreta")
                except Exception as e:
                    print(f"      ⚠️ '{senha}' - erro: {e}")
            else:
                print("      🚫 Nenhuma senha testada funcionou")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_senhas_supervisores()
