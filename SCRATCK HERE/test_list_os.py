#!/usr/bin/env python3
"""
Teste para listar ordens de serviço disponíveis
"""

import requests

BASE_URL = "http://localhost:8000"

def test_list_os():
    """Testar listagem de ordens de serviço"""
    print("🧪 TESTANDO LISTAGEM DE ORDENS DE SERVIÇO")
    print("=" * 50)
    
    # Fazer login primeiro
    login_data = {
        "email": "user.pcp@registroos.com",
        "password": "123456"
    }

    try:
        # Login
        login_response = requests.post(f"{BASE_URL}/api/login", json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return False

        login_json = login_response.json()
        print(f"   Login response keys: {list(login_json.keys())}")

        # Verificar se há token na resposta
        if 'token' in login_json:
            token = login_json["token"]
        elif 'access_token' in login_json:
            token = login_json["access_token"]
        else:
            print(f"   ❌ Token não encontrado na resposta: {login_json}")
            return False
        headers = {"Authorization": f"Bearer {token}"}
        
        # Listar ordens de serviço
        response = requests.get(f"{BASE_URL}/api/pcp/ordens-servico", headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            ordens = response.json()
            print(f"   ✅ Encontradas {len(ordens)} ordens de serviço:")
            for i, os in enumerate(ordens[:5]):  # Mostrar apenas as primeiras 5
                print(f"      {i+1}. OS: {os.get('os_numero', 'N/A')} - Cliente: {os.get('cliente', 'N/A')}")
            
            if len(ordens) > 0:
                print(f"\n   📋 Primeira OS disponível para teste: {ordens[0].get('os_numero', 'N/A')}")
            return True
        else:
            print(f"   ❌ Erro ao listar OS: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_list_os()
