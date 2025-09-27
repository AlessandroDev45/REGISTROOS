#!/usr/bin/env python3
"""
Script para testar a comunicação entre programações do PCP e Desenvolvimento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔄 TESTANDO COMUNICAÇÃO ENTRE PROGRAMAÇÕES")
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
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint PCP programações
    print("\n2. Testando endpoint PCP programações...")
    
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint PCP funcionando!")
            print(f"   Total programações PCP: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"   Primeira programação: {data[0].get('os_numero', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 3. Testar endpoint Desenvolvimento programação
    print("\n3. Testando endpoint Desenvolvimento programação...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint Desenvolvimento funcionando!")
            print(f"   Total programações Desenvolvimento: {len(data) if isinstance(data, list) else 'N/A'}")
            if isinstance(data, list) and len(data) > 0:
                print(f"   Primeira programação: {data[0].get('os_numero', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 4. Testar com filtros
    print("\n4. Testando com filtros...")
    
    try:
        # Teste PCP com filtros
        response = session.get(f"{BASE_URL}/api/pcp/programacoes", params={
            "setor": "MECANICA DIA",
            "departamento": "MOTORES"
        })
        print(f"   PCP com filtros: {response.status_code}")
        
        # Teste Desenvolvimento com filtros
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao", params={
            "status": "PROGRAMADA"
        })
        print(f"   Desenvolvimento com filtros: {response.status_code}")
        
    except Exception as e:
        print(f"   ❌ Erro nos testes com filtros: {e}")

if __name__ == "__main__":
    main()
