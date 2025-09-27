#!/usr/bin/env python3
"""
DEBUG DA AUTENTICAÇÃO
====================

Verifica se a autenticação via cookies está funcionando
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"

def fazer_login_completo():
    """Faz login e retorna cookies"""
    
    print("🔐 FAZENDO LOGIN COMPLETO")
    print("=" * 40)
    
    # Dados de login
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    print(f"📤 Dados de login: {login_data}")
    
    try:
        # Fazer login
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"📥 Status login: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso!")
            
            # Verificar cookies
            cookies = response.cookies
            print(f"🍪 Cookies recebidos: {dict(cookies)}")
            
            # Verificar resposta
            try:
                login_response = response.json()
                print(f"📋 Resposta do login: {json.dumps(login_response, indent=2)}")
            except:
                print(f"📋 Resposta não é JSON: {response.text}")
            
            return cookies
            
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def testar_endpoint_me(cookies):
    """Testa o endpoint /api/me com cookies"""
    
    print(f"\n🔍 TESTANDO ENDPOINT /api/me")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/me", cookies=cookies)
        print(f"📥 Status /api/me: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Usuário autenticado com sucesso!")
            print(f"📋 Dados do usuário:")
            print(f"   Nome: {user_data.get('nome_completo')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Privilege: {user_data.get('privilege_level')}")
            print(f"   Setor: {user_data.get('setor')}")
            return user_data
        else:
            print(f"❌ Erro no /api/me: {response.status_code}")
            print(f"❌ Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def testar_endpoint_departamentos(cookies):
    """Testa o endpoint de criação de departamentos com cookies"""
    
    print(f"\n🏭 TESTANDO CRIAÇÃO DE DEPARTAMENTO")
    print("=" * 40)
    
    # Dados para criar departamento
    dept_data = {
        "nome_tipo": "TESTE_AUTH",
        "descricao": "DEPARTAMENTO CRIADO PARA TESTE DE AUTH",
        "ativo": True
    }
    
    print(f"📤 Dados do departamento: {json.dumps(dept_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/config/departamentos", 
            json=dept_data, 
            cookies=cookies
        )
        
        print(f"📥 Status criação: {response.status_code}")
        print(f"📥 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Departamento criado com sucesso!")
            return response.json()
        elif response.status_code == 400:
            print("⚠️ Departamento já existe (esperado)")
            return None
        elif response.status_code == 401:
            print("❌ Erro de autenticação - cookies não funcionaram")
            return None
        elif response.status_code == 403:
            print("❌ Erro de permissão - usuário não é admin")
            return None
        elif response.status_code == 422:
            print("❌ Erro 422 - problema de validação")
            try:
                error_data = response.json()
                print(f"❌ Detalhes: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Resposta não é JSON: {response.text}")
            return None
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 DEBUG COMPLETO DA AUTENTICAÇÃO")
    print("=" * 60)
    
    # 1. Fazer login
    cookies = fazer_login_completo()
    if not cookies:
        print("❌ Não foi possível fazer login - parando teste")
        return
    
    # 2. Testar endpoint /api/me
    user_data = testar_endpoint_me(cookies)
    if not user_data:
        print("❌ Não foi possível obter dados do usuário - parando teste")
        return
    
    # 3. Testar criação de departamento
    result = testar_endpoint_departamentos(cookies)
    
    print(f"\n🎉 DEBUG CONCLUÍDO!")
    
    if result:
        print("✅ Todos os testes passaram - autenticação está funcionando!")
    else:
        print("❌ Algum teste falhou - há problema na autenticação ou permissões")

if __name__ == "__main__":
    main()
