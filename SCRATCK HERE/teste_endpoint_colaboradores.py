#!/usr/bin/env python3
"""
Teste direto do endpoint de colaboradores
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 TESTE: ENDPOINT COLABORADORES")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint direto
    print("\n2. 🎯 Testando endpoint direto:")
    
    endpoints_to_test = [
        "/api/desenvolvimento/colaboradores",
        "/desenvolvimento/colaboradores",
        "/api/desenvolvimento/colaboradores/",
        "/desenvolvimento/colaboradores/"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n   🔗 Testando: {BASE_URL}{endpoint}")
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Sucesso! {len(data)} colaboradores")
                
                if data:
                    for i, colab in enumerate(data[:3], 1):
                        nome = colab.get('nome_completo', 'N/A')
                        setor = colab.get('setor', 'N/A')
                        print(f"         {i}. {nome} - {setor}")
                else:
                    print("      📋 Lista vazia")
                    
            elif response.status_code == 404:
                print(f"      ❌ 404 Not Found")
            else:
                print(f"      ❌ Erro: {response.status_code}")
                print(f"      📄 Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    # 3. Verificar rotas disponíveis
    print("\n3. 🔍 Verificando rotas disponíveis:")
    try:
        response = session.get(f"{BASE_URL}/docs")
        print(f"   📋 Docs disponíveis em: {BASE_URL}/docs")
        print(f"   Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao acessar docs: {e}")
    
    # 4. Testar outros endpoints de desenvolvimento
    print("\n4. 🔧 Outros endpoints de desenvolvimento:")
    
    dev_endpoints = [
        "/api/desenvolvimento/programacao",
        "/api/desenvolvimento/pendencias",
        "/api/desenvolvimento/apontamentos"
    ]
    
    for endpoint in dev_endpoints:
        try:
            print(f"\n   🔗 Testando: {endpoint}")
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Sucesso! {len(data)} registros")
            else:
                print(f"      ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
