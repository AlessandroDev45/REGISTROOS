#!/usr/bin/env python3
"""
Script para debugar o erro 422 na criação de departamentos
"""

import requests
import json
import sys

def debug_422_error():
    """Debug do erro 422"""
    
    print("🐛 DEBUG DO ERRO 422 - CRIAÇÃO DE DEPARTAMENTO")
    print("=" * 60)
    
    # URL do endpoint
    url = "http://localhost:8000/api/admin/config/departamentos"
    
    # Dados que o frontend está enviando (baseado no log)
    frontend_data = {
        "nome_tipo": "TESTE",
        "descricao": "TESTE", 
        "ativo": True
    }
    
    print(f"📤 Testando endpoint: {url}")
    print(f"📄 Dados enviados: {json.dumps(frontend_data, indent=2)}")
    
    # Teste 1: Sem autenticação (deve dar 401)
    print(f"\n1️⃣ Teste sem autenticação:")
    try:
        response = requests.post(url, json=frontend_data)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Erro 401 esperado (sem autenticação)")
        else:
            print(f"   ❌ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 2: Verificar se o endpoint existe
    print(f"\n2️⃣ Verificando se o endpoint existe:")
    try:
        # Tentar OPTIONS para ver se o endpoint existe
        response = requests.options(url)
        print(f"   Status OPTIONS: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Endpoint existe")
        else:
            print(f"   ❌ Problema com endpoint: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição OPTIONS: {e}")
    
    # Teste 3: Verificar documentação da API
    print(f"\n3️⃣ Verificando documentação da API:")
    try:
        docs_response = requests.get("http://localhost:8000/openapi.json")
        if docs_response.status_code == 200:
            openapi_spec = docs_response.json()
            paths = openapi_spec.get("paths", {})
            
            endpoint_path = "/api/admin/config/departamentos"
            if endpoint_path in paths:
                endpoint_info = paths[endpoint_path]
                print(f"   ✅ Endpoint encontrado na documentação")
                
                if "post" in endpoint_info:
                    post_info = endpoint_info["post"]
                    print(f"   📋 POST endpoint existe")
                    
                    # Verificar schema do request body
                    if "requestBody" in post_info:
                        request_body = post_info["requestBody"]
                        print(f"   📄 Request body definido: {json.dumps(request_body, indent=4)}")
                    else:
                        print(f"   ❌ Request body não definido")
                        
                    # Verificar responses
                    if "responses" in post_info:
                        responses = post_info["responses"]
                        print(f"   📊 Responses definidas: {list(responses.keys())}")
                        
                        if "422" in responses:
                            print(f"   ⚠️ Response 422 definida: {responses['422']}")
                    
                else:
                    print(f"   ❌ POST method não encontrado")
            else:
                print(f"   ❌ Endpoint não encontrado na documentação")
                print(f"   📋 Endpoints disponíveis: {list(paths.keys())}")
        else:
            print(f"   ❌ Erro ao buscar documentação: {docs_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar documentação: {e}")
    
    # Teste 4: Verificar se há problemas com o modelo
    print(f"\n4️⃣ Testando variações dos dados:")
    
    test_cases = [
        {
            "name": "Dados mínimos",
            "data": {"nome_tipo": "TESTE"}
        },
        {
            "name": "Sem ativo (deve usar padrão)",
            "data": {"nome_tipo": "TESTE", "descricao": "TESTE"}
        },
        {
            "name": "Com ID (pode causar problema)",
            "data": {"id": 999, "nome_tipo": "TESTE", "descricao": "TESTE", "ativo": True}
        },
        {
            "name": "String vazia na descrição",
            "data": {"nome_tipo": "TESTE", "descricao": "", "ativo": True}
        },
        {
            "name": "Descrição null",
            "data": {"nome_tipo": "TESTE", "descricao": None, "ativo": True}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   🧪 {test_case['name']}:")
        print(f"      Dados: {json.dumps(test_case['data'], indent=6)}")
        
        try:
            response = requests.post(url, json=test_case['data'])
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 422:
                print(f"      ❌ Erro 422: {response.text}")
            elif response.status_code == 401:
                print(f"      ✅ Erro 401 (autenticação) - dados válidos")
            else:
                print(f"      📄 Resposta: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")
    
    print(f"\n📊 CONCLUSÕES:")
    print("- Se todos os testes dão 401, o problema é só autenticação")
    print("- Se algum teste dá 422, há problema de validação nos dados")
    print("- Se o endpoint não existe, há problema de roteamento")
    
    print(f"\n🔧 PRÓXIMOS PASSOS:")
    print("1. Se o problema é autenticação, verificar cookies/tokens no frontend")
    print("2. Se o problema é validação, ajustar o modelo Pydantic ou dados")
    print("3. Se o problema é roteamento, verificar se o endpoint está registrado")

def main():
    """Função principal"""
    debug_422_error()

if __name__ == "__main__":
    main()
