#!/usr/bin/env python3
"""
Teste completo de criação de usuário via admin
Verifica se todos os campos estão sendo salvos corretamente:
- matricula
- id_departamento 
- id_setor
- trabalha_producao
"""

import requests
import json
import sqlite3

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@registroos.com"
ADMIN_PASSWORD = "123456"
DB_PATH = "C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend/registroos_new.db"

def test_admin_login():
    """Testa login do admin"""
    print("🔐 Testando login do admin...")
    
    data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/token", data=data)
    
    if response.status_code == 200:
        print("✅ Login do admin bem-sucedido!")
        return response.cookies
    else:
        print(f"❌ Falha no login do admin: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def buscar_setores_departamentos():
    """Busca setores e departamentos disponíveis"""
    print("\n📋 Buscando setores e departamentos...")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Buscar departamentos
        cursor.execute("SELECT id, nome_tipo FROM tipo_departamentos WHERE ativo = 1")
        departamentos = cursor.fetchall()
        print(f"📁 Departamentos encontrados: {len(departamentos)}")
        for dept in departamentos:
            print(f"   - ID: {dept[0]}, Nome: {dept[1]}")
        
        # Buscar setores
        cursor.execute("SELECT id, nome, departamento FROM tipo_setores WHERE ativo = 1 LIMIT 5")
        setores = cursor.fetchall()
        print(f"🏢 Setores encontrados: {len(setores)}")
        for setor in setores:
            print(f"   - ID: {setor[0]}, Nome: {setor[1]}, Departamento: {setor[2]}")
        
        conn.close()
        
        if departamentos and setores:
            return departamentos[0], setores[0]  # Retorna primeiro de cada
        else:
            return None, None
            
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")
        return None, None

def test_create_user_complete(admin_cookies, departamento, setor):
    """Testa criação completa de usuário"""
    print(f"\n👤 Testando criação de usuário completo...")
    
    user_data = {
        "nome_completo": "TESTE USUARIO COMPLETO",
        "email": "teste.completo.final@registroos.com",
        "matricula": "MAT123456",
        "setor": setor[1],  # nome do setor
        "departamento": departamento[1],  # nome do departamento
        "cargo": "TECNICO DE TESTE",
        "privilege_level": "USER",
        "trabalha_producao": True
    }
    
    print(f"📧 Dados do usuário:")
    print(f"   - Nome: {user_data['nome_completo']}")
    print(f"   - Email: {user_data['email']}")
    print(f"   - Matrícula: {user_data['matricula']}")
    print(f"   - Setor: {user_data['setor']}")
    print(f"   - Departamento: {user_data['departamento']}")
    print(f"   - Cargo: {user_data['cargo']}")
    print(f"   - Trabalha Produção: {user_data['trabalha_producao']}")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/usuarios",
        json=user_data,
        cookies=admin_cookies
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Usuário criado com sucesso!")
        print(f"🆔 ID: {result.get('id')}")
        print(f"📧 Email: {result.get('email')}")
        print(f"🔑 Senha temporária: {result.get('senha_temporaria')}")
        print(f"📝 Matrícula: {result.get('matricula')}")
        print(f"🏢 Setor: {result.get('setor')}")
        print(f"📁 Departamento: {result.get('departamento')}")
        print(f"💼 Cargo: {result.get('cargo')}")
        print(f"🏭 Trabalha Produção: {result.get('trabalha_producao')}")
        print(f"🆔 ID Setor: {result.get('id_setor')}")
        print(f"🆔 ID Departamento: {result.get('id_departamento')}")
        print(f"🔐 Primeiro Login: {result.get('primeiro_login')}")
        
        return result.get('id'), result.get('email')
    else:
        print(f"❌ Falha na criação do usuário: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None, None

def verify_user_in_database(user_id):
    """Verifica se o usuário foi salvo corretamente no banco"""
    print(f"\n🔍 Verificando usuário ID {user_id} no banco de dados...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome_completo, email, matricula, setor, departamento, 
                   cargo, trabalha_producao, id_setor, id_departamento, primeiro_login
            FROM tipo_usuarios 
            WHERE id = ?
        """, (user_id,))
        
        user = cursor.fetchone()
        
        if user:
            print("✅ Usuário encontrado no banco:")
            print(f"   - ID: {user[0]}")
            print(f"   - Nome: {user[1]}")
            print(f"   - Email: {user[2]}")
            print(f"   - Matrícula: {user[3]}")
            print(f"   - Setor: {user[4]}")
            print(f"   - Departamento: {user[5]}")
            print(f"   - Cargo: {user[6]}")
            print(f"   - Trabalha Produção: {user[7]}")
            print(f"   - ID Setor: {user[8]}")
            print(f"   - ID Departamento: {user[9]}")
            print(f"   - Primeiro Login: {user[10]}")
            
            # Verificar se todos os campos importantes estão preenchidos
            issues = []
            if not user[3]:  # matricula
                issues.append("❌ Matrícula não foi salva")
            if not user[8]:  # id_setor
                issues.append("❌ ID Setor não foi salvo")
            if not user[9]:  # id_departamento
                issues.append("❌ ID Departamento não foi salvo")
            if user[7] is None:  # trabalha_producao
                issues.append("❌ Trabalha Produção não foi salvo")
            if user[10] != 1:  # primeiro_login
                issues.append("❌ Primeiro Login não foi marcado como True")
                
            if issues:
                print("\n⚠️ Problemas encontrados:")
                for issue in issues:
                    print(f"   {issue}")
                return False
            else:
                print("\n🎉 Todos os campos foram salvos corretamente!")
                return True
        else:
            print("❌ Usuário não encontrado no banco")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuário no banco: {e}")
        return False

def cleanup_test_user(user_id):
    """Remove o usuário de teste"""
    print(f"\n🧹 Removendo usuário de teste ID {user_id}...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tipo_usuarios WHERE id = ?", (user_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print("✅ Usuário de teste removido com sucesso")
        else:
            print("ℹ️ Usuário não encontrado para remoção")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao remover usuário: {e}")

def main():
    print("🚀 Iniciando teste completo de criação de usuário...")
    print("=" * 60)
    
    # 1. Login do admin
    admin_cookies = test_admin_login()
    if not admin_cookies:
        return
    
    # 2. Buscar setores e departamentos
    departamento, setor = buscar_setores_departamentos()
    if not departamento or not setor:
        print("❌ Não foi possível buscar setores/departamentos")
        return
    
    # 3. Criar usuário
    user_id, user_email = test_create_user_complete(admin_cookies, departamento, setor)
    if not user_id:
        return
    
    # 4. Verificar no banco
    success = verify_user_in_database(user_id)
    
    # 5. Limpar usuário de teste
    cleanup_test_user(user_id)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE COMPLETO REALIZADO COM SUCESSO!")
        print("✅ Todos os campos estão sendo salvos corretamente:")
        print("   ✅ Matrícula")
        print("   ✅ ID Departamento")
        print("   ✅ ID Setor")
        print("   ✅ Trabalha Produção")
        print("   ✅ Primeiro Login")
    else:
        print("❌ TESTE FALHOU!")
        print("⚠️ Alguns campos não estão sendo salvos corretamente")

if __name__ == "__main__":
    main()
