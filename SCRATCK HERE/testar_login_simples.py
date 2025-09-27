#!/usr/bin/env python3
"""
TESTE SIMPLES DE LOGIN
======================

Testa o login diretamente no backend
"""

import requests
import json

def testar_login():
    """Testa o login"""
    
    print("🔐 TESTANDO LOGIN SIMPLES")
    print("=" * 40)
    
    # URL do backend
    login_url = "http://localhost:8000/api/login"
    
    # Dados de login
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    print(f"📤 URL: {login_url}")
    print(f"📤 Dados: {json.dumps(login_data, indent=2)}")
    
    try:
        # Fazer requisição de login
        response = requests.post(login_url, json=login_data)
        
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}")
        print(f"📥 Cookies: {dict(response.cookies)}")
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso!")
            try:
                data = response.json()
                print(f"📋 Resposta: {json.dumps(data, indent=2)}")
            except:
                print(f"📋 Resposta (texto): {response.text}")
                
            return response.cookies
            
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def testar_me_endpoint(cookies):
    """Testa o endpoint /api/me"""
    
    print(f"\n👤 TESTANDO ENDPOINT /api/me")
    print("=" * 40)
    
    me_url = "http://localhost:8000/api/me"
    
    try:
        response = requests.get(me_url, cookies=cookies)
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Usuário autenticado!")
            user_data = response.json()
            print(f"📋 Usuário: {user_data.get('nome_completo')}")
            print(f"📋 Email: {user_data.get('email')}")
            print(f"📋 Privilege: {user_data.get('privilege_level')}")
            return user_data
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 TESTE COMPLETO DE LOGIN")
    print("=" * 50)
    
    # 1. Testar login
    cookies = testar_login()
    
    if cookies:
        # 2. Testar endpoint /api/me
        user_data = testar_me_endpoint(cookies)
        
        if user_data:
            print(f"\n🎉 LOGIN FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"\n❌ Login funcionou mas /api/me falhou")
    else:
        print(f"\n❌ LOGIN NÃO ESTÁ FUNCIONANDO")
    
    print(f"\n🏁 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
