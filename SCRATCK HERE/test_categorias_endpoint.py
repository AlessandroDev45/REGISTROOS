#!/usr/bin/env python3
"""
Script para testar o endpoint /api/tipos-maquina/categorias
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/test-login/admin@registroos.com"
CATEGORIAS_URL = f"{BASE_URL}/api/tipos-maquina/categorias"

def test_categorias_endpoint():
    """Testa o endpoint de categorias de tipos de máquina"""
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    print("🔐 Fazendo login...")

    try:
        login_response = session.post(LOGIN_URL)
        print(f"Login status: {login_response.status_code}")

        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.text}")
            return

        print("✅ Login realizado com sucesso!")
        
        # Testar endpoint de categorias
        print("\n📋 Testando endpoint de categorias...")
        
        # Teste 1: Sem parâmetros
        print("\n1. Teste sem parâmetros:")
        response = session.get(CATEGORIAS_URL)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            categorias = response.json()
            print(f"Categorias encontradas: {len(categorias)}")
            print(f"Categorias: {categorias}")
        else:
            print(f"❌ Erro: {response.text}")
        
        # Teste 2: Com parâmetro departamento
        print("\n2. Teste com departamento=MOTORES:")
        params = {"departamento": "MOTORES"}
        response = session.get(CATEGORIAS_URL, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            categorias = response.json()
            print(f"Categorias encontradas: {len(categorias)}")
            print(f"Categorias: {categorias}")
        else:
            print(f"❌ Erro: {response.text}")
        
        # Teste 3: Com parâmetros departamento e setor
        print("\n3. Teste com departamento=MOTORES e setor=MECANICA DIA:")
        params = {"departamento": "MOTORES", "setor": "MECANICA DIA"}
        response = session.get(CATEGORIAS_URL, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            categorias = response.json()
            print(f"Categorias encontradas: {len(categorias)}")
            print(f"Categorias: {categorias}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_categorias_endpoint()
