#!/usr/bin/env python3
"""
Teste dos endpoints corrigidos do PCP
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
        # Retornar cookies para usar nas próximas requisições
        return response.cookies
    else:
        print(f"Erro no login: {response.text}")
        return None

def test_endpoints(cookies):
    """Testar os endpoints corrigidos"""
    
    endpoints = [
        "/api/pcp/ordens-servico",
        "/api/pcp/programacoes", 
        "/api/pcp/pendencias",
        "/api/pcp/dashboard/avancado?periodo_dias=30",
        "/api/pcp/alertas",
        "/api/pcp/pendencias/dashboard?periodo_dias=30",
        "/api/pcp/programacao-form-data"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            print(f"\n{'='*50}")
            print(f"Endpoint: {endpoint}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"Retornou lista com {len(data)} itens")
                    if data:
                        print(f"Primeiro item: {list(data[0].keys()) if data[0] else 'Vazio'}")
                elif isinstance(data, dict):
                    print(f"Retornou objeto com chaves: {list(data.keys())}")
                else:
                    print(f"Retornou: {type(data)}")
            else:
                print(f"Erro: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Erro ao testar {endpoint}: {e}")

def test_supervisor_filter():
    """Testar filtro de supervisores de produção"""
    cookies = test_login()
    if not cookies:
        return
        
    try:
        response = requests.get(f"{BASE_URL}/api/pcp/programacao-form-data", cookies=cookies)
        print(f"\n{'='*50}")
        print("TESTE: Filtro de Supervisores de Produção")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            supervisores = data.get('supervisores', [])
            print(f"Total de supervisores retornados: {len(supervisores)}")
            
            for supervisor in supervisores:
                print(f"- {supervisor.get('nome_completo')} (Setor: {supervisor.get('setor_nome')})")
                
            # Verificar se todos são de produção
            producao_count = len([s for s in supervisores if 'PRODUCAO' in str(s.get('setor_nome', '')).upper() or 'LABORATORIO' in str(s.get('setor_nome', '')).upper()])
            print(f"Supervisores de produção/laboratório: {producao_count}/{len(supervisores)}")
            
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro no teste de supervisores: {e}")

if __name__ == "__main__":
    print("🧪 Testando endpoints corrigidos do PCP...")
    
    # Fazer login
    cookies = test_login()
    if not cookies:
        print("❌ Falha no login. Abortando testes.")
        exit(1)
    
    print("✅ Login realizado com sucesso!")
    
    # Testar endpoints
    test_endpoints(cookies)
    
    # Testar filtro específico de supervisores
    test_supervisor_filter()
    
    print(f"\n{'='*50}")
    print("🏁 Testes concluídos!")
