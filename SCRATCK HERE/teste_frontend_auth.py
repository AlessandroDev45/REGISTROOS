#!/usr/bin/env python3
"""
Teste para simular exatamente o que o frontend está fazendo
"""

import requests
import json

def simular_frontend():
    """Simula o comportamento do frontend"""
    
    print("🌐 SIMULANDO COMPORTAMENTO DO FRONTEND")
    print("=" * 50)
    
    # Criar uma sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login como o frontend faria
    print("1️⃣ Fazendo login...")
    login_url = "http://localhost:8000/api/login"
    login_data = {
        "username": "ADMIN",
        "password": "123456"
    }
    
    try:
        login_response = session.post(login_url, json=login_data)
        print(f"   Status login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso!")
            
            # Verificar se há cookies
            cookies = session.cookies
            print(f"   🍪 Cookies recebidos: {dict(cookies)}")
            
            # 2. Tentar criar departamento com a sessão autenticada
            print("\n2️⃣ Tentando criar departamento com sessão autenticada...")
            
            dept_url = "http://localhost:8000/api/admin/config/departamentos"
            dept_data = {
                "nome_tipo": "TESTE FRONTEND",
                "descricao": "Teste via simulação frontend",
                "ativo": True
            }
            
            # Simular exatamente como o axios faz
            headers = {
                "Content-Type": "application/json"
            }
            
            dept_response = session.post(dept_url, json=dept_data, headers=headers)
            print(f"   Status criação: {dept_response.status_code}")
            print(f"   Resposta: {dept_response.text}")
            
            if dept_response.status_code == 200:
                print("   ✅ Departamento criado com sucesso!")
                result = dept_response.json()
                dept_id = result.get("id")
                
                # 3. Limpar - deletar o departamento
                if dept_id:
                    print(f"\n3️⃣ Limpando - deletando departamento {dept_id}...")
                    delete_response = session.delete(f"{dept_url}/{dept_id}")
                    print(f"   Status delete: {delete_response.status_code}")
                    
            elif dept_response.status_code == 422:
                print("   ❌ Erro 422 - Problema de validação!")
                try:
                    error_detail = dept_response.json()
                    print(f"   📄 Detalhes do erro: {json.dumps(error_detail, indent=4)}")
                except:
                    print(f"   📄 Resposta raw: {dept_response.text}")
                    
            elif dept_response.status_code == 401:
                print("   ❌ Erro 401 - Problema de autenticação!")
                
            elif dept_response.status_code == 403:
                print("   ❌ Erro 403 - Problema de permissão!")
                
            else:
                print(f"   ❌ Erro inesperado: {dept_response.status_code}")
                print(f"   📄 Resposta: {dept_response.text}")
                
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   📄 Resposta: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na simulação: {e}")
    
    # 4. Testar outros endpoints admin para comparar
    print(f"\n4️⃣ Testando outros endpoints admin...")
    
    test_endpoints = [
        ("GET", "http://localhost:8000/api/admin/config/sistema", None),
        ("GET", "http://localhost:8000/api/admin/config/departamentos", None),
    ]
    
    for method, url, data in test_endpoints:
        try:
            if method == "GET":
                response = session.get(url)
            elif method == "POST":
                response = session.post(url, json=data)
                
            print(f"   {method} {url}: {response.status_code}")
            
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    print(f"      📄 Erro 422: {json.dumps(error_detail, indent=6)}")
                except:
                    print(f"      📄 Resposta raw: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Erro testando {url}: {e}")

def main():
    """Função principal"""
    simular_frontend()

if __name__ == "__main__":
    main()
