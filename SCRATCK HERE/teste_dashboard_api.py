#!/usr/bin/env python3
"""
Teste para verificar se a API do Dashboard está funcionando corretamente
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
DASHBOARD_URL = f"{BASE_URL}/api/apontamentos-detalhados"

def fazer_login():
    """Fazer login e obter cookies de sessão"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    response = requests.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return response.cookies
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(response.text)
        return None

def testar_endpoint_dashboard(cookies):
    """Testar o endpoint do dashboard"""
    print(f"\n🔍 Testando endpoint: {DASHBOARD_URL}")
    
    try:
        # Teste 1: Sem parâmetros
        print("\n1. Teste sem parâmetros...")
        response = requests.get(DASHBOARD_URL, cookies=cookies)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Retornou {len(data)} apontamentos")
            
            if len(data) > 0:
                print(f"   📋 Primeiro apontamento:")
                primeiro = data[0]
                for key, value in primeiro.items():
                    print(f"      {key}: {value}")
            else:
                print("   ⚠️ Nenhum apontamento retornado")
        else:
            print(f"   ❌ Erro: {response.text}")
            return False
        
        # Teste 2: Com parâmetros de usuário
        print("\n2. Teste com parâmetros de usuário...")
        params = {"usuario_id": 1}
        response = requests.get(DASHBOARD_URL, cookies=cookies, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Com filtro usuário: {len(data)} apontamentos")
        else:
            print(f"   ❌ Erro com filtro: {response.text}")
        
        # Teste 3: Com parâmetros de data
        print("\n3. Teste com parâmetros de data...")
        hoje = datetime.now().strftime('%Y-%m-%d')
        params = {"data_inicio": hoje, "data_fim": hoje}
        response = requests.get(DASHBOARD_URL, cookies=cookies, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Com filtro data: {len(data)} apontamentos")
        else:
            print(f"   ❌ Erro com filtro data: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def testar_endpoints_relacionados(cookies):
    """Testar outros endpoints relacionados"""
    print(f"\n🔍 Testando endpoints relacionados...")
    
    endpoints = [
        "/api/desenvolvimento/minhas-programacoes",
        "/api/desenvolvimento/apontamentos",
        "/api/desenvolvimento/minhas-os"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n   Testando: {endpoint}")
            response = requests.get(f"{BASE_URL}{endpoint}", cookies=cookies)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Retornou {len(data)} itens")
                else:
                    print(f"   ✅ Retornou objeto: {type(data)}")
            else:
                print(f"   ❌ Erro: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def verificar_estrutura_resposta(cookies):
    """Verificar a estrutura da resposta da API"""
    print(f"\n🔍 Verificando estrutura da resposta...")
    
    try:
        response = requests.get(DASHBOARD_URL, cookies=cookies)
        
        if response.status_code == 200:
            data = response.json()
            
            if len(data) > 0:
                print(f"\n📋 Estrutura do primeiro apontamento:")
                primeiro = data[0]
                
                campos_esperados = [
                    'id', 'numero_os', 'data_hora_inicio', 'data_hora_fim',
                    'status_apontamento', 'tipo_atividade', 'nome_tecnico',
                    'setor', 'departamento', 'tempo_trabalhado'
                ]
                
                print(f"   Campos presentes:")
                for campo in campos_esperados:
                    if campo in primeiro:
                        print(f"   ✅ {campo}: {primeiro[campo]}")
                    else:
                        print(f"   ❌ {campo}: AUSENTE")
                
                print(f"\n   Campos extras:")
                for key in primeiro.keys():
                    if key not in campos_esperados:
                        print(f"   ➕ {key}: {primeiro[key]}")
            else:
                print("   ⚠️ Nenhum apontamento para verificar estrutura")
        else:
            print(f"   ❌ Erro ao buscar dados: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def main():
    """Função principal"""
    print("🧪 TESTE: API do Dashboard - Meu Dashboard")
    print("=" * 60)
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        return
    
    # Testar endpoint principal
    sucesso = testar_endpoint_dashboard(cookies)
    
    if sucesso:
        # Verificar estrutura
        verificar_estrutura_resposta(cookies)
        
        # Testar endpoints relacionados
        testar_endpoints_relacionados(cookies)
    
    print("\n" + "=" * 60)
    print("🏁 Teste concluído!")
    
    if not sucesso:
        print("\n💡 Possíveis problemas:")
        print("   1. Endpoint não existe ou mudou de URL")
        print("   2. Problema de autenticação")
        print("   3. Erro no backend")
        print("   4. Banco de dados vazio")

if __name__ == "__main__":
    main()
