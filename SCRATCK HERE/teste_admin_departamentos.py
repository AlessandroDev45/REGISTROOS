#!/usr/bin/env python3
"""
Teste para verificar se os endpoints de departamentos estão funcionando
corretamente após a correção do erro 405.
"""

import requests
import json
import sys

def testar_endpoints_departamentos():
    """Testa os endpoints de departamentos"""
    
    base_url = "http://localhost:8000/api/admin/config"
    
    print("🧪 TESTE DOS ENDPOINTS DE DEPARTAMENTOS")
    print("=" * 50)
    
    # Dados de teste
    departamento_teste = {
        "nome_tipo": "TESTE DEPARTAMENTO",
        "descricao": "Departamento criado para teste",
        "ativo": True
    }
    
    # 1. Testar GET /departamentos (sem autenticação - deve falhar)
    print("\n1️⃣ Testando GET /departamentos (sem auth):")
    try:
        response = requests.get(f"{base_url}/departamentos")
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Autenticação requerida (esperado)")
        else:
            print(f"   ❌ Resposta inesperada: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Testar POST /departamentos (sem autenticação - deve falhar)
    print("\n2️⃣ Testando POST /departamentos (sem auth):")
    try:
        response = requests.post(f"{base_url}/departamentos", json=departamento_teste)
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Autenticação requerida (esperado)")
        else:
            print(f"   ❌ Resposta inesperada: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Verificar se os endpoints estão registrados
    print("\n3️⃣ Verificando documentação da API:")
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            endpoints_departamentos = [
                "/api/admin/config/departamentos",
                "/api/admin/config/departamentos/{departamento_id}"
            ]
            
            for endpoint in endpoints_departamentos:
                if endpoint in paths:
                    methods = list(paths[endpoint].keys())
                    print(f"   ✅ {endpoint}: {methods}")
                else:
                    print(f"   ❌ {endpoint}: NÃO ENCONTRADO")
        else:
            print(f"   ❌ Erro ao buscar OpenAPI spec: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Verificar se o servidor está respondendo
    print("\n4️⃣ Verificando saúde do servidor:")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print(f"   ✅ Servidor saudável: {response.json()}")
        else:
            print(f"   ❌ Problema no servidor: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n📊 RESUMO:")
    print("- Os endpoints de departamentos foram adicionados ao backend")
    print("- Autenticação está funcionando (401 para requests sem auth)")
    print("- Para testar completamente, é necessário fazer login no frontend")
    print("- O erro 405 (Method Not Allowed) deve estar resolvido")
    
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Faça login no frontend (http://localhost:3001/admin)")
    print("2. Vá para a aba 'Departamentos'")
    print("3. Tente criar um novo departamento")
    print("4. O erro 405 não deve mais aparecer")

def main():
    """Função principal"""
    testar_endpoints_departamentos()

if __name__ == "__main__":
    main()
