#!/usr/bin/env python3
import requests
import json

def testar_login_normal():
    """Testa login normal usando o endpoint /token"""
    try:
        print("🔐 Testando login normal com admin@registroos.com")
        
        # Dados de login
        login_data = {
            "username": "admin@registroos.com",
            "password": "admin123"  # Senha padrão
        }
        
        # Fazer login usando o endpoint /token
        response = requests.post(
            "http://localhost:8000/api/auth/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login bem-sucedido!")
            
            # Testar acesso ao desenvolvimento
            cookies = response.cookies
            
            dev_response = requests.get(
                "http://localhost:8000/api/desenvolvimento/apontamentos-detalhados",
                cookies=cookies
            )
            
            print(f"Desenvolvimento Status: {dev_response.status_code}")
            
            if dev_response.status_code == 200:
                print("✅ Acesso ao desenvolvimento: PERMITIDO")
                data = dev_response.json()
                print(f"📊 Apontamentos retornados: {len(data)}")
                if data:
                    primeiro = data[0]
                    print(f"  Primeiro apontamento: OS {primeiro.get('numero_os')}, Setor: {primeiro.get('setor')}")
            else:
                print(f"❌ Acesso ao desenvolvimento: NEGADO ({dev_response.status_code})")
                print(f"Erro: {dev_response.text}")
                
        else:
            print(f"❌ Falha no login: {response.status_code}")
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_usuarios_diferentes():
    """Testa login com diferentes usuários"""
    usuarios = [
        ("admin@registroos.com", "admin123"),
        ("supervisor.mecanica_dia@registroos.com", "supervisor123"),
        ("user.mecanica_dia@registroos.com", "user123"),
    ]
    
    for email, senha in usuarios:
        print(f"\n🔐 Testando login: {email}")
        
        login_data = {
            "username": email,
            "password": senha
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/auth/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                print(f"✅ Login bem-sucedido!")
                print(f"  Nome: {user.get('nome_completo')}")
                print(f"  Privilege: {user.get('privilege_level')}")
                print(f"  Trabalha Produção: {user.get('trabalha_producao')}")
                
                # Testar acesso ao desenvolvimento
                cookies = response.cookies
                dev_response = requests.get(
                    "http://localhost:8000/api/desenvolvimento/apontamentos-detalhados",
                    cookies=cookies
                )
                
                if dev_response.status_code == 200:
                    print(f"✅ Acesso ao desenvolvimento: PERMITIDO")
                else:
                    print(f"❌ Acesso ao desenvolvimento: NEGADO ({dev_response.status_code})")
                    
            else:
                print(f"❌ Falha no login: {response.status_code}")
                if response.status_code == 401:
                    print("  Credenciais inválidas")
                elif response.status_code == 403:
                    print("  Usuário não aprovado")
                    
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🧪 TESTE DE LOGIN E ACESSO AO DESENVOLVIMENTO")
    print("=" * 60)
    
    testar_login_normal()
    
    print("\n" + "=" * 60)
    print("🧪 TESTANDO DIFERENTES USUÁRIOS")
    print("=" * 60)
    
    testar_usuarios_diferentes()
