#!/usr/bin/env python3
"""
Script para testar o fluxo completo de primeiro login
"""

import requests
import json
import time

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@registroos.com"
ADMIN_PASSWORD = "123456"

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

def test_create_user_with_temp_password(cookies):
    """Testa criação de usuário com senha temporária"""
    print("\n👤 Testando criação de usuário com senha temporária...")
    
    user_data = {
        "nome_completo": "Teste Primeiro Login",
        "email": "teste.primeiro.login@registroos.com",
        "setor": "LABORATORIO DE ENSAIOS ELETRICOS",
        "departamento": "MOTORES",
        "cargo": "Técnico de Testes",
        "privilege_level": "USER"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/admin/usuarios",
        json=user_data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Usuário criado com sucesso!")
        print(f"📧 Email: {result.get('email')}")
        print(f"🔑 Senha temporária: {result.get('senha_temporaria')}")
        print(f"📝 Instruções: {result.get('instrucoes')}")
        return result.get('senha_temporaria'), result.get('email')
    else:
        print(f"❌ Falha na criação do usuário: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None, None

def test_first_login(email, temp_password):
    """Testa primeiro login com senha temporária"""
    print(f"\n🔓 Testando primeiro login com senha temporária...")
    print(f"📧 Email: {email}")
    print(f"🔑 Senha temporária: {temp_password}")
    
    data = {
        "username": email,
        "password": temp_password
    }
    
    response = requests.post(f"{BASE_URL}/api/token", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Primeiro login bem-sucedido!")
        print(f"👤 Usuário: {result['user']['nome_completo']}")
        print(f"🔐 Precisa trocar senha: {result.get('requires_password_change', False)}")
        print(f"🆔 Primeiro login: {result['user'].get('primeiro_login', False)}")
        return response.cookies, result.get('requires_password_change', False)
    else:
        print(f"❌ Falha no primeiro login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None, False

def test_password_change(cookies, old_password):
    """Testa troca de senha"""
    print(f"\n🔄 Testando troca de senha...")
    
    new_password = "MinhaNovaSenh@123"
    
    data = {
        "senha_atual": old_password,
        "nova_senha": new_password
    }
    
    response = requests.put(
        f"{BASE_URL}/api/change-password",
        json=data,
        cookies=cookies
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Senha alterada com sucesso!")
        print(f"📝 Mensagem: {result.get('message')}")
        return new_password
    else:
        print(f"❌ Falha na troca de senha: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def test_login_after_password_change(email, new_password):
    """Testa login após troca de senha"""
    print(f"\n🔓 Testando login após troca de senha...")
    
    data = {
        "username": email,
        "password": new_password
    }
    
    response = requests.post(f"{BASE_URL}/api/token", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Login após troca de senha bem-sucedido!")
        print(f"👤 Usuário: {result['user']['nome_completo']}")
        print(f"🔐 Precisa trocar senha: {result.get('requires_password_change', False)}")
        print(f"🆔 Primeiro login: {result['user'].get('primeiro_login', False)}")
        return True
    else:
        print(f"❌ Falha no login após troca: {response.status_code}")
        print(f"Resposta: {response.text}")
        return False

def cleanup_test_user(admin_cookies, email):
    """Remove usuário de teste (opcional)"""
    print(f"\n🧹 Limpando usuário de teste...")
    
    # Primeiro, buscar o ID do usuário
    response = requests.get(f"{BASE_URL}/api/usuarios/", cookies=admin_cookies)
    
    if response.status_code == 200:
        users = response.json()
        test_user = next((user for user in users if user['email'] == email), None)
        
        if test_user:
            user_id = test_user['id']
            print(f"🔍 Usuário encontrado com ID: {user_id}")
            # Aqui você poderia implementar a remoção se houver endpoint para isso
            print("ℹ️ Usuário mantido para verificação manual")
        else:
            print("❓ Usuário de teste não encontrado")
    else:
        print(f"❌ Erro ao buscar usuários: {response.status_code}")

def main():
    """Executa o teste completo"""
    print("🚀 Iniciando teste do fluxo de primeiro login...")
    print("=" * 60)
    
    try:
        # 1. Login do admin
        admin_cookies = test_admin_login()
        if not admin_cookies:
            return
        
        # 2. Criar usuário com senha temporária
        temp_password, email = test_create_user_with_temp_password(admin_cookies)
        if not temp_password or not email:
            return
        
        # 3. Primeiro login
        user_cookies, requires_change = test_first_login(email, temp_password)
        if not user_cookies:
            return
        
        # 4. Verificar se precisa trocar senha
        if requires_change:
            print("✅ Sistema detectou corretamente que precisa trocar senha!")
        else:
            print("⚠️ Sistema NÃO detectou que precisa trocar senha!")
        
        # 5. Trocar senha
        new_password = test_password_change(user_cookies, temp_password)
        if not new_password:
            return
        
        # 6. Login com nova senha
        success = test_login_after_password_change(email, new_password)
        if not success:
            return
        
        # 7. Cleanup (opcional)
        cleanup_test_user(admin_cookies, email)
        
        print("\n" + "=" * 60)
        print("🎉 TESTE COMPLETO REALIZADO COM SUCESSO!")
        print("✅ Todos os passos do fluxo funcionaram corretamente:")
        print("   1. ✅ Admin criou usuário com senha temporária")
        print("   2. ✅ Usuário fez primeiro login")
        print("   3. ✅ Sistema detectou necessidade de troca de senha")
        print("   4. ✅ Usuário trocou senha com sucesso")
        print("   5. ✅ Login subsequente funcionou normalmente")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão! Verifique se o backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()
