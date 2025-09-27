#!/usr/bin/env python3
"""
Teste para verificar se os endpoints de administração funcionam corretamente
"""

import requests
import json

def testar_endpoints_admin():
    """Testa os endpoints de administração"""
    
    print("🧪 TESTE: Endpoints de Administração")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Fazer login para obter autenticação
    try:
        print("\n1️⃣ Fazendo login...")
        
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
        
        if not login_success:
            print("❌ Não foi possível fazer login. Abortando testes.")
            return
        
        # 2. Testar endpoint de usuários pendentes
        print("\n2️⃣ Testando /api/users/pending-approval...")
        try:
            response = session.get(f"{base_url}/api/users/pending-approval", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint funcionando!")
                
                try:
                    data = response.json()
                    print(f"   📊 Usuários pendentes: {len(data)}")
                    
                    if len(data) > 0:
                        print(f"   👤 Primeiro usuário: {data[0].get('nome_completo', 'N/A')}")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Resposta não é JSON válido")
                    
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 3. Testar endpoint de todos os usuários
        print("\n3️⃣ Testando /api/users/usuarios/...")
        try:
            response = session.get(f"{base_url}/api/users/usuarios/", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint funcionando!")
                
                try:
                    data = response.json()
                    print(f"   📊 Total de usuários: {len(data)}")
                    
                    if len(data) > 0:
                        print(f"   👤 Primeiro usuário: {data[0].get('nome_completo', 'N/A')}")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Resposta não é JSON válido")
                    
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 4. Testar endpoint alternativo de usuários pendentes (admin)
        print("\n4️⃣ Testando /api/admin/usuarios-pendentes...")
        try:
            response = session.get(f"{base_url}/api/admin/usuarios-pendentes", timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Endpoint funcionando!")
                
                try:
                    data = response.json()
                    print(f"   📊 Usuários pendentes (admin): {len(data)}")
                    
                    if len(data) > 0:
                        print(f"   👤 Primeiro usuário: {data[0].get('nome_completo', 'N/A')}")
                    
                except json.JSONDecodeError:
                    print("   ⚠️ Resposta não é JSON válido")
                    
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    except Exception as e:
        print(f"\n❌ Erro geral no teste: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_endpoints_admin()
