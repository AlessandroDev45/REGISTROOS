#!/usr/bin/env python3
"""
TESTAR ENDPOINT DE TESTE
=======================

Testa o endpoint de teste para verificar se o roteamento está funcionando.
"""

import requests

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login como admin...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=ADMIN_USER, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_endpoints(session):
    """Testar ambos os endpoints"""
    
    endpoints = [
        "/api/desenvolvimento/test-programacoes",
        "/api/desenvolvimento/minhas-programacoes"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testando {endpoint}...")
        
        try:
            response = session.get(f"{BASE_URL}{endpoint}", timeout=10)
            
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📋 Resposta: {data}")
                except:
                    print(f"📄 Resposta raw: {response.text}")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")

def main():
    """Função principal"""
    print("🔧 TESTAR ENDPOINT DE TESTE")
    print("=" * 40)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Testar endpoints
    testar_endpoints(session)

if __name__ == "__main__":
    main()
