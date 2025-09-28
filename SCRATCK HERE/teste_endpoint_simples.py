#!/usr/bin/env python3
"""
Teste para endpoint simples
"""

import requests

# Configurações
BASE_URL = "http://localhost:8000"
TEST_URL = f"{BASE_URL}/api/desenvolvimento/test-endpoint"

def testar_endpoint_simples():
    """Testar endpoint simples"""
    print(f"🔍 Testando endpoint: {TEST_URL}")
    
    try:
        response = requests.post(TEST_URL)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Endpoint simples")
    print("=" * 40)
    
    testar_endpoint_simples()
    
    print("\n" + "=" * 40)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
