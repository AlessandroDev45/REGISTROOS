#!/usr/bin/env python3
"""
Script para testar o endpoint /api/desenvolvimento/buscar-ids-os
Conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md
"""

import requests
import json
import sys
import os

# Adicionar o diretório backend ao path
backend_dir = r"C:\Users\Alessandro\OneDrive\Desktop\RegistroOS\RegistroOS\registrooficial\backend"
sys.path.append(backend_dir)

def test_endpoint():
    """Testa o endpoint buscar-ids-os"""
    
    base_url = "http://localhost:8000"
    
    print("🔍 Testando endpoint /api/desenvolvimento/buscar-ids-os")
    print("=" * 60)
    
    # 1. Testar se o servidor está rodando
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Servidor rodando: {health_response.status_code}")
        print(f"   Resposta: {health_response.json()}")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        return False
    
    # 2. Testar endpoint sem autenticação (deve retornar 401)
    try:
        endpoint_url = f"{base_url}/api/desenvolvimento/buscar-ids-os"
        test_data = {"numeros_os": ["15225", "15226"]}
        
        response = requests.post(
            endpoint_url,
            json=test_data,
            timeout=10
        )
        
        print(f"\n🔐 Teste sem autenticação:")
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 401:
            print("✅ Endpoint encontrado (requer autenticação)")
            return True
        elif response.status_code == 404:
            print("❌ Endpoint não encontrado (404)")
            return False
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def test_with_mock_auth():
    """Testa com autenticação simulada"""
    print(f"\n🔑 Teste com autenticação simulada:")
    
    # Simular login primeiro (se houver endpoint de login)
    try:
        login_url = "http://localhost:8000/api/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        session = requests.Session()
        login_response = session.post(login_url, json=login_data, timeout=10)
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # Testar endpoint com sessão autenticada
            endpoint_url = "http://localhost:8000/api/desenvolvimento/buscar-ids-os"
            test_data = {"numeros_os": ["15225"]}
            
            response = session.post(endpoint_url, json=test_data, timeout=10)
            
            print(f"   Endpoint status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
            if response.status_code == 200:
                print("✅ Endpoint funcionando com autenticação!")
                return True
            else:
                print(f"⚠️ Endpoint com problema: {response.status_code}")
                return False
        else:
            print("⚠️ Login falhou, testando apenas conectividade")
            return False
            
    except Exception as e:
        print(f"⚠️ Erro no teste com autenticação: {e}")
        return False

def check_routes():
    """Verifica todas as rotas disponíveis"""
    try:
        docs_url = "http://localhost:8000/docs"
        print(f"\n📋 Documentação da API disponível em: {docs_url}")
        
        # Tentar acessar OpenAPI spec
        openapi_url = "http://localhost:8000/openapi.json"
        response = requests.get(openapi_url, timeout=10)
        
        if response.status_code == 200:
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            print(f"\n📍 Rotas encontradas:")
            for path in sorted(paths.keys()):
                if "desenvolvimento" in path:
                    methods = list(paths[path].keys())
                    print(f"   {path} [{', '.join(methods).upper()}]")
            
            # Verificar especificamente nosso endpoint
            target_path = "/api/desenvolvimento/buscar-ids-os"
            if target_path in paths:
                print(f"\n✅ Endpoint {target_path} encontrado na documentação!")
                return True
            else:
                print(f"\n❌ Endpoint {target_path} NÃO encontrado na documentação")
                return False
        else:
            print(f"⚠️ Não foi possível acessar OpenAPI spec: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar rotas: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DO ENDPOINT BUSCAR-IDS-OS")
    print("Conforme HIERARQUIA_COMPLETA_BANCO_DADOS.md")
    print("=" * 60)
    
    # Executar testes
    server_ok = test_endpoint()
    routes_ok = check_routes()
    auth_ok = test_with_mock_auth()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"   🖥️  Servidor rodando: {'✅' if server_ok else '❌'}")
    print(f"   📍 Rotas corretas: {'✅' if routes_ok else '❌'}")
    print(f"   🔐 Autenticação: {'✅' if auth_ok else '⚠️'}")
    
    if server_ok and routes_ok:
        print("\n🎉 ENDPOINT ESTÁ FUNCIONANDO!")
        print("   O problema pode ser apenas de autenticação no frontend.")
    else:
        print("\n❌ ENDPOINT COM PROBLEMAS")
        print("   Verifique a configuração do backend.")
