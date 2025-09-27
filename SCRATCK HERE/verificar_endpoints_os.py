#!/usr/bin/env python3
"""
VERIFICAR ENDPOINTS DE OS
========================

Testa diferentes endpoints para encontrar OSs no sistema.
"""

import requests

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Credenciais funcionais
TEST_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=TEST_USER, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_endpoints_os(session):
    """Testar diferentes endpoints de OS"""
    endpoints = [
        "/api/os/",
        "/api/pcp/ordens-servico",
        "/api/desenvolvimento/ordens-servico",
        "/api/general/os/",
        "/api/catalogs/ordens-servico"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testando: {endpoint}")
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Lista com {len(data)} itens")
                    if len(data) > 0:
                        primeiro = data[0]
                        print(f"   📋 Primeiro item: {primeiro}")
                        return endpoint, data
                elif isinstance(data, dict):
                    print(f"   ✅ Objeto: {data}")
                    return endpoint, [data]
                else:
                    print(f"   ⚠️ Tipo inesperado: {type(data)}")
            else:
                print(f"   ❌ Erro: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
    
    return None, []

def main():
    """Função principal"""
    print("🧪 VERIFICAR ENDPOINTS DE OS")
    print("=" * 40)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Testar endpoints
    endpoint_funcionando, oss = testar_endpoints_os(session)
    
    if endpoint_funcionando:
        print(f"\n🎉 ENDPOINT FUNCIONANDO: {endpoint_funcionando}")
        print(f"📊 Total de OSs encontradas: {len(oss)}")
        
        if len(oss) > 0:
            print(f"\n📋 PRIMEIRA OS:")
            primeira_os = oss[0]
            for key, value in primeira_os.items():
                print(f"   {key}: {value}")
        
        print(f"\n💡 Use este endpoint no teste: {endpoint_funcionando}")
    else:
        print(f"\n❌ NENHUM ENDPOINT FUNCIONOU")
        print(f"💡 Verifique se existem OSs no sistema")

if __name__ == "__main__":
    main()
