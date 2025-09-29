#!/usr/bin/env python3
"""
Script para testar os endpoints de admin e verificar se estão funcionando
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_endpoints():
    """Testa os endpoints de admin"""
    
    print("🔍 TESTANDO ENDPOINTS DE ADMIN")
    print("=" * 50)
    
    # Dados de login admin
    admin_login = {
        "email": "admin@registroos.com",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    # 1. Fazer login
    print("1. 🔐 Fazendo login como admin...")
    try:
        response = session.post(f"{BASE_URL}/api/auth/login", json=admin_login)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            data = response.json()
            print(f"   👤 Usuário: {data.get('user', {}).get('nome_completo', 'N/A')}")
            print(f"   🔑 Privilege: {data.get('user', {}).get('privilege_level', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {response.text}")
            return
            
    except Exception as e:
        print(f"   💥 Exceção no login: {e}")
        return
    
    # 2. Testar endpoints de admin
    endpoints_to_test = [
        "/api/admin/departamentos",
        "/api/admin/setores", 
        "/api/admin/tipos-maquina",
        "/api/admin/tipos-teste",
        "/api/admin/causas-retrabalho",
        "/api/admin/status"
    ]
    
    print("\n2. 🧪 Testando endpoints de admin...")
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n   📡 GET {endpoint}")
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"      ✅ Retornou lista com {len(data)} itens")
                elif isinstance(data, dict):
                    print(f"      ✅ Retornou objeto com {len(data)} campos")
                else:
                    print(f"      ✅ Retornou: {type(data)}")
            else:
                print(f"      ❌ Erro: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      💥 Exceção: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    test_admin_endpoints()
