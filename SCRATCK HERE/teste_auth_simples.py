#!/usr/bin/env python3
"""
Teste simples para verificar autenticação e endpoint /me
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def main():
    print("🧪 TESTE SIMPLES: Autenticação e endpoint /me")
    print("=" * 60)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Teste 1: Login
    print("\n1. Testando login...")
    try:
        login_data = {
            'username': 'admin@registroos.com',
            'password': '123456'
        }
        
        response = session.post(f"{BASE_URL}/api/token", data=login_data)
        print(f"   Status do login: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {e}")
        return
    
    # Teste 2: Endpoint /me
    print("\n2. Testando endpoint /me...")
    try:
        response = session.get(f"{BASE_URL}/api/me")
        print(f"   Status do /me: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("   ✅ Endpoint /me funcionando")
            print(f"   Usuário: {user_data.get('nome_completo', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
            print(f"   Privilege: {user_data.get('privilege_level', 'N/A')}")
            print(f"   Setor: {user_data.get('setor', 'N/A')}")
            print(f"   Departamento: {user_data.get('departamento', 'N/A')}")
            print(f"   Trabalha Produção: {user_data.get('trabalha_producao', 'N/A')}")
        else:
            print(f"   ❌ Erro no /me: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição /me: {e}")
    
    # Teste 3: Endpoint programacao-form-data
    print("\n3. Testando endpoint programacao-form-data...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint programacao-form-data funcionando")
            print(f"   Setores: {len(data.get('setores', []))}")
            print(f"   Usuários: {len(data.get('usuarios', []))}")
            print(f"   Departamentos: {len(data.get('departamentos', []))}")
        else:
            print(f"   ❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n🏁 Teste concluído!")

if __name__ == "__main__":
    main()
