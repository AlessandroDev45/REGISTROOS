#!/usr/bin/env python3
"""
Script para testar o endpoint buscar-ids-os com autenticação
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 TESTANDO ENDPOINT BUSCAR-IDS-OS")
    print("=" * 50)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }

    try:
        # Usar o endpoint correto de login
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint buscar-ids-os
    print("\n2. Testando endpoint buscar-ids-os...")
    
    test_data = {
        "numeros_os": ["15225", "12345"]
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/desenvolvimento/buscar-ids-os",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint funcionando!")
            print(f"   Mapeamento: {data.get('mapeamento', {})}")
            print(f"   Total encontradas: {data.get('total_encontradas', 0)}")
            print(f"   Total solicitadas: {data.get('total_solicitadas', 0)}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

if __name__ == "__main__":
    main()
