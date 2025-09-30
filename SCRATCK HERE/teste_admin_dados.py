#!/usr/bin/env python3
"""
Teste para verificar se os dados estão sendo carregados corretamente no admin
"""

import requests
import json

# URL base da API
BASE_URL = "http://127.0.0.1:8000/api/admin"

# Headers para autenticação (você pode precisar ajustar)
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer SEU_TOKEN_AQUI"  # Se necessário
}

def test_endpoint(endpoint_name, url):
    """Testa um endpoint específico"""
    print(f"\n🔧 Testando {endpoint_name}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data) if isinstance(data, list) else 1} itens encontrados")
            if isinstance(data, list) and len(data) > 0:
                print(f"Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
            elif not isinstance(data, list):
                print(f"Dados: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detalhes: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Resposta: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")

def main():
    print("🚀 TESTE DOS ENDPOINTS DO ADMIN")
    print("=" * 50)
    
    # Lista de endpoints para testar
    endpoints = [
        ("Departamentos", f"{BASE_URL}/departamentos"),
        ("Setores", f"{BASE_URL}/setores"),
        ("Tipos de Máquina", f"{BASE_URL}/tipos-maquina"),
        ("Tipos de Teste", f"{BASE_URL}/tipos-teste"),
        ("Atividades", f"{BASE_URL}/atividades"),
        ("Descrições de Atividade", f"{BASE_URL}/descricoes-atividade"),
        ("Tipos de Falha", f"{BASE_URL}/falhas"),
        ("Causas de Retrabalho", f"{BASE_URL}/causas-retrabalho"),
    ]
    
    for name, url in endpoints:
        test_endpoint(name, url)
    
    print("\n" + "=" * 50)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
