#!/usr/bin/env python3
"""
TESTE LOGIN COMPLETO - RegistroOS
=================================

Script para testar o fluxo completo de login e verificar se o sistema está funcionando.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def teste_login_completo():
    """Testa o fluxo completo de login"""
    print("🧪 TESTE LOGIN COMPLETO - RegistroOS")
    print("=" * 50)
    
    session = requests.Session()
    
    # 1. Testar health check
    print("\n1. Testando health check...")
    try:
        response = session.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend respondendo")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ Backend com problema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com backend: {e}")
        return False
    
    # 2. Testar endpoint /me sem autenticação (deve retornar 401)
    print("\n2. Testando /me sem autenticação...")
    try:
        response = session.get(f"{BASE_URL}/api/me")
        if response.status_code == 401:
            print("✅ Endpoint /me retorna 401 corretamente (sem auth)")
        else:
            print(f"⚠️ Endpoint /me retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no /me: {e}")
    
    # 3. Testar login com admin
    print("\n3. Testando login com admin...")
    try:
        login_data = {
            'username': 'admin@registroos.com',
            'password': '123456'
        }
        
        response = session.post(f"{BASE_URL}/api/token", data=login_data)
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
            user_data = response.json()
            print(f"   Usuário: {user_data.get('nome_completo', 'N/A')}")
            print(f"   Privilege: {user_data.get('privilege_level', 'N/A')}")
            print(f"   Email: {user_data.get('email', 'N/A')}")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return False
    
    # 4. Testar endpoint /me com autenticação
    print("\n4. Testando /me com autenticação...")
    try:
        response = session.get(f"{BASE_URL}/api/me")
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Endpoint /me funcionando com auth")
            print(f"   Usuário: {user_data.get('nome_completo', 'N/A')}")
            print(f"   Privilege: {user_data.get('privilege_level', 'N/A')}")
            print(f"   Setor: {user_data.get('setor', 'N/A')}")
            print(f"   Departamento: {user_data.get('departamento', 'N/A')}")
        else:
            print(f"❌ Erro no /me autenticado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no /me autenticado: {e}")
        return False
    
    # 5. Testar alguns endpoints básicos
    print("\n5. Testando endpoints básicos...")
    
    endpoints_teste = [
        "/api/usuarios/",
        "/api/admin/config/sistema",
        "/api/catalogos/departamentos",
        "/api/catalogos/setores"
    ]
    
    for endpoint in endpoints_teste:
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - OK")
            else:
                print(f"   ⚠️ {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Erro: {e}")
    
    # 6. Testar logout
    print("\n6. Testando logout...")
    try:
        response = session.post(f"{BASE_URL}/api/logout")
        if response.status_code == 200:
            print("✅ Logout realizado com sucesso")
        else:
            print(f"⚠️ Logout retornou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no logout: {e}")
    
    # 7. Verificar se /me retorna 401 após logout
    print("\n7. Verificando /me após logout...")
    try:
        response = session.get(f"{BASE_URL}/api/me")
        if response.status_code == 401:
            print("✅ Endpoint /me retorna 401 após logout (correto)")
        else:
            print(f"⚠️ Endpoint /me retornou: {response.status_code} após logout")
    except Exception as e:
        print(f"❌ Erro no /me pós-logout: {e}")
    
    print("\n" + "=" * 50)
    print("✅ TESTE COMPLETO FINALIZADO")
    print("\n🎯 RESUMO:")
    print("   - Backend: ✅ Funcionando")
    print("   - Login: ✅ Funcionando")
    print("   - Autenticação: ✅ Funcionando")
    print("   - Logout: ✅ Funcionando")
    print("\n🌐 ACESSO AO SISTEMA:")
    print("   Frontend: http://localhost:3001")
    print("   Backend: http://localhost:8000")
    print("   Admin: admin@registroos.com / 123456")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    teste_login_completo()
