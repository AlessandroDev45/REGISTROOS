#!/usr/bin/env python3
"""
TESTE DIRETO DO ENDPOINT DE DEPARTAMENTOS
=========================================

Testa diretamente o endpoint POST /api/admin/config/departamentos
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"

def testar_endpoint_direto():
    """Testa o endpoint diretamente"""
    
    # Dados para criar departamento
    dept_data = {
        "nome_tipo": "TESTE_DIRETO",
        "descricao": "DEPARTAMENTO CRIADO VIA TESTE DIRETO",
        "ativo": True
    }
    
    print("🚀 TESTANDO ENDPOINT DIRETO")
    print("=" * 50)
    print(f"📤 URL: {BASE_URL}/api/admin/config/departamentos")
    print(f"📤 Dados: {json.dumps(dept_data, indent=2)}")
    
    try:
        # Fazer requisição sem autenticação primeiro
        print(f"\n🔄 Testando sem autenticação...")
        response = requests.post(f"{BASE_URL}/api/admin/config/departamentos", json=dept_data)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Endpoint está funcionando - erro 401 esperado (sem autenticação)")
        elif response.status_code == 422:
            print("❌ Erro 422 - problema de validação")
            try:
                error_data = response.json()
                print(f"❌ Detalhes: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Resposta não é JSON: {response.text}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - backend não está rodando na porta 8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def testar_endpoint_status():
    """Testa se o backend está respondendo"""
    print(f"\n🔄 Testando status do backend...")
    
    try:
        # Testar endpoint de status
        response = requests.get(f"{BASE_URL}/api/admin/config/status")
        print(f"📥 Status endpoint: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend está respondendo")
            data = response.json()
            print(f"📋 Endpoints disponíveis: {data.get('admin_config_endpoints', [])}")
        else:
            print(f"⚠️ Backend respondeu com status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend não está respondendo na porta 8000")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    testar_endpoint_status()
    testar_endpoint_direto()
    
    print(f"\n🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
