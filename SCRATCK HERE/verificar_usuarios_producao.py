#!/usr/bin/env python3
import sys
import os

# Adicionar o caminho do backend ao sys.path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'RegistroOS', 'registrooficial', 'backend')
sys.path.insert(0, backend_path)

from config.database_config import get_db
from sqlalchemy import text

def verificar_usuarios_producao():
    try:
        db = next(get_db())
        
        # Verificar todos os usuários e suas permissões
        result = db.execute(text("""
            SELECT id, nome_completo, email, nome_usuario, privilege_level, 
                   trabalha_producao, id_setor, id_departamento, is_approved
            FROM tipo_usuarios 
            ORDER BY privilege_level, nome_completo
        """))
        usuarios = [dict(row._mapping) for row in result]
        
        print("👥 Análise de Usuários e Acesso ao Desenvolvimento:")
        print("=" * 80)
        
        for user in usuarios:
            print(f"\n📋 {user['nome_completo']}")
            print(f"  Email: {user['email']}")
            print(f"  Username: {user['nome_usuario']}")
            print(f"  Privilege: {user['privilege_level']}")
            print(f"  Trabalha Produção: {user['trabalha_producao']}")
            print(f"  ID Setor: {user['id_setor']}")
            print(f"  ID Departamento: {user['id_departamento']}")
            print(f"  Aprovado: {user['is_approved']}")
            
            # Verificar acesso ao desenvolvimento baseado nas regras
            tem_acesso = False
            motivo = ""
            
            if not user['is_approved']:
                motivo = "❌ Usuário não aprovado"
            elif user['privilege_level'] == 'ADMIN':
                tem_acesso = True
                motivo = "✅ ADMIN - Acesso total"
            elif user['privilege_level'] in ['SUPERVISOR', 'GESTAO']:
                tem_acesso = True
                motivo = "✅ SUPERVISOR/GESTAO - Acesso permitido"
            elif user['privilege_level'] == 'USER':
                if user['trabalha_producao']:
                    tem_acesso = True
                    motivo = "✅ USER com trabalha_producao=True"
                else:
                    motivo = "❌ USER sem trabalha_producao=True"
            else:
                motivo = f"❌ Privilege level '{user['privilege_level']}' não tem acesso"
            
            print(f"  🎯 Acesso Desenvolvimento: {motivo}")
        
        # Estatísticas
        print("\n" + "=" * 80)
        print("📊 ESTATÍSTICAS:")
        
        total_usuarios = len(usuarios)
        aprovados = len([u for u in usuarios if u['is_approved']])
        com_acesso_dev = 0
        
        for user in usuarios:
            if (user['is_approved'] and 
                (user['privilege_level'] in ['ADMIN', 'SUPERVISOR', 'GESTAO'] or 
                 (user['privilege_level'] == 'USER' and user['trabalha_producao']))):
                com_acesso_dev += 1
        
        print(f"  Total de usuários: {total_usuarios}")
        print(f"  Usuários aprovados: {aprovados}")
        print(f"  Com acesso ao desenvolvimento: {com_acesso_dev}")
        
        # Verificar usuários USER sem trabalha_producao
        users_sem_producao = [u for u in usuarios if u['privilege_level'] == 'USER' and not u['trabalha_producao'] and u['is_approved']]
        if users_sem_producao:
            print(f"\n⚠️ USUÁRIOS USER SEM ACESSO (trabalha_producao=False):")
            for user in users_sem_producao:
                print(f"  - {user['nome_completo']} ({user['email']})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    verificar_usuarios_producao()
