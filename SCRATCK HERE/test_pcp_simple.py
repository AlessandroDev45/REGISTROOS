#!/usr/bin/env python3
"""
Teste do endpoint de teste PCP
"""

import requests

BASE_URL = "http://localhost:8000"

def test_pcp_simple():
    """Testar o endpoint de teste PCP"""
    print("🧪 TESTANDO ENDPOINT DE TESTE PCP")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/test", timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ Endpoint de teste funcionando!")
            return True
        else:
            print(f"   ❌ Erro no endpoint de teste")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_pcp_simple()
