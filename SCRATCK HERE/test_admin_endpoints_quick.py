#!/usr/bin/env python3
"""
Teste rápido dos endpoints de admin config
"""

import sys
import os
sys.path.append('C:/Users/Alessandro/OneDrive/Desktop/RegistroOS/RegistroOS/registrooficial/backend')

import requests
import json

# Configuração
BASE_URL = "http://localhost:8000/api/admin"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer test_token"  # Substitua por um token válido se necessário
}

def test_endpoint(method, endpoint, data=None):
    """Testa um endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=HEADERS, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data, timeout=5)
        else:
            print(f"❌ Método {method} não suportado")
            return False
            
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Sucesso")
            return True
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Erro: {str(e)}")
        return False

def main():
    """Testa os principais endpoints"""
    print("🧪 Testando endpoints de admin config...")
    print("=" * 50)
    
    # Endpoints para testar
    endpoints = [
        ("GET", "/departamentos"),
        ("GET", "/setores"),
        ("GET", "/tipos-maquina"),
        ("GET", "/tipos-teste"),
        ("GET", "/tipos-atividade"),
        ("GET", "/descricoes-atividade"),
        ("GET", "/tipos-falha"),
        ("GET", "/causas-retrabalho"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for method, endpoint in endpoints:
        if test_endpoint(method, endpoint):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultado: {success_count}/{total_count} endpoints funcionando")
    
    if success_count == total_count:
        print("🎉 Todos os endpoints estão funcionando!")
    else:
        print("⚠️  Alguns endpoints têm problemas")

if __name__ == "__main__":
    main()
