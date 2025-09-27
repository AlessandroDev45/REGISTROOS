#!/usr/bin/env python3
"""
Teste para verificar se o endpoint /api/users/usuarios/ funciona corretamente
"""

import requests
import json

def testar_endpoint_usuarios():
    """Testa o endpoint de usuários"""
    
    print("🧪 TESTE: Endpoint /api/users/usuarios/")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Testar sem autenticação (deve retornar 401)
    try:
        print("\n1️⃣ Testando sem autenticação...")
        response = requests.get(f"{base_url}/api/users/usuarios/", timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Endpoint encontrado (requer autenticação)")
        elif response.status_code == 404:
            print("   ❌ Endpoint não encontrado (404)")
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
    
    # 2. Testar endpoint de login para obter token
    try:
        print("\n2️⃣ Testando login para obter autenticação...")
        
        # Credenciais de teste
        credenciais = [
            {"username": "admin@registroos.com", "password": "admin123"},
            {"username": "user.pcp@registroos.com", "password": "123456"},
        ]
        
        session = requests.Session()
        login_success = False
        
        for cred in credenciais:
            try:
                print(f"   🔐 Tentando login: {cred['username']}")
                
                response = session.post(
                    f"{base_url}/api/login", 
                    json=cred, 
                    timeout=10
                )
                
                print(f"   Status login: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Login realizado com sucesso!")
                    login_success = True
                    break
                else:
                    print(f"   ❌ Falha no login: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Erro no login: {e}")
        
        # 3. Testar endpoint com autenticação
        if login_success:
            print("\n3️⃣ Testando endpoint com autenticação...")
            
            try:
                response = session.get(f"{base_url}/api/users/usuarios/", timeout=10)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Endpoint funcionando com autenticação!")
                    
                    # Tentar parsear JSON
                    try:
                        data = response.json()
                        print(f"   📊 Dados recebidos: {len(data)} usuários")
                        
                        if len(data) > 0:
                            print(f"   👤 Primeiro usuário: {data[0].get('nome_completo', 'N/A')}")
                        
                    except json.JSONDecodeError:
                        print("   ⚠️ Resposta não é JSON válido")
                        print(f"   Resposta: {response.text[:200]}")
                        
                else:
                    print(f"   ❌ Erro no endpoint: {response.status_code}")
                    print(f"   Resposta: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao testar endpoint autenticado: {e}")
        else:
            print("\n3️⃣ ❌ Não foi possível testar com autenticação (login falhou)")
    
    except Exception as e:
        print(f"\n2️⃣ ❌ Erro geral no teste de login: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_endpoint_usuarios()
