#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido dos endpoints
"""

import requests

BASE_URL = 'http://localhost:8000'

def main():
    print("🧪 TESTE RÁPIDO DOS ENDPOINTS")
    print("=" * 40)
    
    # Teste simples de conectividade
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        print(f"✅ Servidor respondendo: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return
    
    # Teste de login
    try:
        login_data = {
            "username": "admin@registroos.com",
            "password": "123456"
        }
        
        response = requests.post(f"{BASE_URL}/api/token", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Login: OK")
            cookies = response.cookies
            
            # Teste alguns endpoints principais
            endpoints = [
                "/api/departamentos",
                "/api/setores", 
                "/api/ordens-servico",
                "/api/gestao/dashboard"
            ]
            
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list):
                            print(f"✅ {endpoint}: {len(data)} registros")
                        else:
                            print(f"✅ {endpoint}: OK")
                    else:
                        print(f"❌ {endpoint}: Erro {resp.status_code}")
                except Exception as e:
                    print(f"❌ {endpoint}: {str(e)[:30]}...")
            
        else:
            print(f"❌ Login: Erro {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")

if __name__ == "__main__":
    main()
