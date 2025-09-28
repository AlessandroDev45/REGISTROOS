#!/usr/bin/env python3
"""
Teste do endpoint simples para verificar logs
"""

import requests

BASE_URL = "http://localhost:8000"

def test_simple_endpoint():
    """Testar o endpoint simples"""
    print("🧪 TESTANDO ENDPOINT SIMPLES")
    print("=" * 50)
    
    try:
        response = requests.post(f"{BASE_URL}/api/pcp/test-endpoint", timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ Sucesso!")
            return True
        else:
            print(f"   ❌ Erro")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_simple_endpoint()
