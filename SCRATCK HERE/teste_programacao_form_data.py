#!/usr/bin/env python3
"""
Teste específico do endpoint programacao-form-data
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Fazer login e obter cookies"""
    login_data = {
        "username": "admin@registroos.com", 
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/token", data=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        return response.cookies
    else:
        print(f"Erro no login: {response.text}")
        return None

def test_programacao_form_data(cookies):
    """Testar endpoint programacao-form-data"""
    print(f"\n{'='*60}")
    print("🔍 TESTE: Endpoint programacao-form-data")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data", cookies=cookies)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Dados recebidos:")
            print(f"  - Setores: {len(data.get('setores', []))}")
            print(f"  - Usuarios: {len(data.get('usuarios', []))}")
            print(f"  - Departamentos: {len(data.get('departamentos', []))}")
            print(f"  - Ordens de Serviço: {len(data.get('ordens_servico', []))}")
            print(f"  - Status Opções: {len(data.get('status_opcoes', []))}")
            
            # Mostrar alguns dados
            if data.get('departamentos'):
                print(f"\nDepartamentos encontrados:")
                for dept in data['departamentos']:
                    print(f"  - {dept.get('nome')} (ID: {dept.get('id')})")
            
            if data.get('setores'):
                print(f"\nPrimeiros 5 setores:")
                for setor in data['setores'][:5]:
                    print(f"  - {setor.get('nome')} - Dept: {setor.get('departamento_nome')} (ID: {setor.get('id')})")
            
            if data.get('usuarios'):
                print(f"\nSupervisores encontrados:")
                for user in data['usuarios']:
                    print(f"  - {user.get('nome_completo')} - Setor: {user.get('setor_nome')} (ID: {user.get('id')})")
            
            return data
        else:
            print(f"Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def test_individual_endpoints(cookies):
    """Testar endpoints individuais para debug"""
    print(f"\n{'='*60}")
    print("🔍 TESTE: Endpoints Individuais")
    
    endpoints = [
        "/api/admin/departamentos/",
        "/api/admin/setores/",
        "/api/pcp/ordens-servico"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            print(f"\n{endpoint}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  Itens: {len(data)}")
                    if data:
                        print(f"  Primeiro item: {list(data[0].keys()) if data[0] else 'Vazio'}")
                else:
                    print(f"  Tipo: {type(data)}")
            else:
                print(f"  Erro: {response.text[:100]}...")
        except Exception as e:
            print(f"  Erro: {e}")

def main():
    """Função principal"""
    print("🧪 TESTE ESPECÍFICO: programacao-form-data")
    print("="*60)
    
    # Login
    cookies = test_login()
    if not cookies:
        print("❌ Falha no login. Abortando.")
        return
    
    # Testar endpoint principal
    data = test_programacao_form_data(cookies)
    
    # Testar endpoints individuais para debug
    test_individual_endpoints(cookies)
    
    print(f"\n{'='*60}")
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
