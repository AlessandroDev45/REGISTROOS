#!/usr/bin/env python3
"""
TESTE NOVO ENDPOINT
==================

Teste do novo endpoint dashboard-programacoes.
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

def testar_novo_endpoint(session):
    """Testar novo endpoint"""
    print("\n🔍 Testando novo endpoint...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/dashboard-programacoes")
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Resposta: {data}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ SUCESSO! {len(data)} programações encontradas!")
                return True
            else:
                print(f"⚠️ Endpoint funciona mas retorna vazio")
                return False
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTE NOVO ENDPOINT")
    print("=" * 25)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Testar novo endpoint
    sucesso = testar_novo_endpoint(session)
    
    # 3. Resultado
    if sucesso:
        print(f"\n🎉 NOVO ENDPOINT FUNCIONANDO!")
    else:
        print(f"\n⚠️ Endpoint ainda com problemas")

if __name__ == "__main__":
    main()
