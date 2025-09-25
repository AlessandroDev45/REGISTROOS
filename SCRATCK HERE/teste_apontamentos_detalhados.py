#!/usr/bin/env python3
"""
🧪 TESTE: Endpoint /api/apontamentos-detalhados
Testa se o endpoint está funcionando corretamente após a correção
"""

import requests
import json

def testar_endpoint():
    base_url = "http://localhost:8000"
    
    print("🧪 TESTE: Endpoint /api/apontamentos-detalhados")
    print("=" * 60)
    
    # 1. Fazer login primeiro
    print("\n1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/token", data=login_data)
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            
            # Extrair cookies da resposta
            cookies = login_response.cookies
            
            # 2. Testar endpoint de apontamentos detalhados
            print("\n2. Testando endpoint /api/apontamentos-detalhados...")
            apontamentos_response = requests.get(
                f"{base_url}/api/apontamentos-detalhados",
                cookies=cookies
            )
            
            print(f"   Status Code: {apontamentos_response.status_code}")
            
            if apontamentos_response.status_code == 200:
                apontamentos = apontamentos_response.json()
                print(f"   ✅ Endpoint funcionando! Retornou {len(apontamentos)} apontamentos")
                
                if apontamentos:
                    print("\n📋 Exemplo de apontamento retornado:")
                    primeiro_apontamento = apontamentos[0]
                    for key, value in primeiro_apontamento.items():
                        print(f"   {key}: {value}")
                else:
                    print("   ⚠️ Nenhum apontamento encontrado no banco de dados")
                    
            else:
                print(f"   ❌ Erro no endpoint: {apontamentos_response.status_code}")
                print(f"   Resposta: {apontamentos_response.text}")
                
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

if __name__ == "__main__":
    testar_endpoint()
