#!/usr/bin/env python3
"""
Teste simples para forçar logs do erro 422
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
APONTAMENTO_URL = f"{BASE_URL}/api/desenvolvimento/os/apontamentos"

def fazer_login():
    """Fazer login e obter cookies de sessão"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    response = requests.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return response.cookies
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_endpoint_simples(cookies):
    """Testar com dados super simples"""
    print(f"\n🔍 Testando endpoint: {APONTAMENTO_URL}")
    
    dados_simples = {
        "numero_os": "SIMPLES-001"
    }
    
    print(f"📋 Dados simples: {dados_simples}")
    
    try:
        response = requests.post(
            APONTAMENTO_URL, 
            cookies=cookies,
            json=dados_simples,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE SIMPLES: Forçar logs do erro")
    print("=" * 50)
    
    cookies = fazer_login()
    if not cookies:
        return
    
    testar_endpoint_simples(cookies)
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
