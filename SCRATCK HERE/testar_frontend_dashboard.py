#!/usr/bin/env python3
"""
Testa o frontend do Dashboard simulando requisições do navegador
"""

import requests
import json

BASE_URL = "http://localhost:3001"
API_URL = "http://localhost:8000"

def testar_frontend_dashboard():
    """Testa o frontend do Dashboard"""
    print("🌐 Testando Frontend Dashboard...")
    
    session = requests.Session()
    
    # 1. Verificar se o frontend está acessível
    print("\n1. 🏠 Testando acesso ao frontend...")
    try:
        response = session.get(f"{BASE_URL}")
        if response.status_code == 200:
            print(f"   ✅ Frontend acessível: {response.status_code}")
        else:
            print(f"   ❌ Frontend com problema: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao acessar frontend: {e}")
        return
    
    # 2. Testar proxy para API
    print("\n2. 🔗 Testando proxy para API...")
    try:
        # Testar endpoint de health através do proxy
        response = session.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print(f"   ✅ Proxy funcionando: {response.json()}")
        else:
            print(f"   ❌ Proxy com problema: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro no proxy: {e}")
    
    # 3. Testar login através do frontend
    print("\n3. 🔑 Testando login através do frontend...")
    try:
        # Fazer login automático através do proxy
        response = session.post(f"{BASE_URL}/api/test-login/admin@registroos.com")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Login via frontend: {user_data['user']['nome_completo']}")
            
            # Verificar se o cookie foi definido
            cookies = session.cookies.get_dict()
            if 'access_token' in cookies:
                print(f"   ✅ Cookie de autenticação definido")
            else:
                print(f"   ⚠️ Cookie de autenticação não encontrado")
                print(f"   🍪 Cookies disponíveis: {list(cookies.keys())}")
        else:
            print(f"   ❌ Falha no login via frontend: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro no login via frontend: {e}")
    
    # 4. Testar endpoints do Dashboard através do proxy
    print("\n4. 📊 Testando endpoints do Dashboard via proxy...")
    
    endpoints = [
        "/api/apontamentos-detalhados",
        "/api/pcp/programacoes", 
        "/api/pcp/pendencias",
        "/api/departamentos",
        "/api/setores"
    ]
    
    for endpoint in endpoints:
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {endpoint}: {len(data)} itens (via proxy)")
                else:
                    print(f"   ✅ {endpoint}: OK (via proxy)")
            elif response.status_code == 401:
                print(f"   🔐 {endpoint}: Não autenticado (via proxy)")
            else:
                print(f"   ❌ {endpoint}: Erro {response.status_code} (via proxy)")
                
        except Exception as e:
            print(f"   ❌ {endpoint}: Exceção {e}")
    
    # 5. Comparar com acesso direto à API
    print("\n5. 🔄 Comparando com acesso direto à API...")
    
    # Fazer login direto na API
    api_session = requests.Session()
    try:
        login_response = api_session.post(f"{API_URL}/api/test-login/admin@registroos.com")
        if login_response.status_code == 200:
            print("   ✅ Login direto na API funcionando")
            
            # Testar um endpoint diretamente
            direct_response = api_session.get(f"{API_URL}/api/apontamentos-detalhados")
            proxy_response = session.get(f"{BASE_URL}/api/apontamentos-detalhados")
            
            print(f"   📊 API Direta: Status {direct_response.status_code}")
            print(f"   📊 Via Proxy: Status {proxy_response.status_code}")
            
            if direct_response.status_code == 200 and proxy_response.status_code != 200:
                print("   ⚠️ PROBLEMA: API direta funciona, mas proxy não!")
            elif direct_response.status_code == 200 and proxy_response.status_code == 200:
                print("   ✅ Ambos funcionando corretamente")
            else:
                print("   ❌ Problemas em ambos os acessos")
                
        else:
            print(f"   ❌ Login direto na API falhou: {login_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro no teste direto da API: {e}")

def verificar_configuracao_proxy():
    """Verifica a configuração do proxy no package.json"""
    print("\n6. ⚙️ Verificando configuração do proxy...")
    
    import os
    
    package_json_path = "RegistroOS/registrooficial/frontend/package.json"
    
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            if 'proxy' in package_data:
                print(f"   ✅ Proxy configurado: {package_data['proxy']}")
            else:
                print("   ❌ Proxy não configurado no package.json")
                
            # Verificar scripts
            if 'scripts' in package_data:
                scripts = package_data['scripts']
                if 'start' in scripts:
                    print(f"   📜 Script start: {scripts['start']}")
                    
        except Exception as e:
            print(f"   ❌ Erro ao ler package.json: {e}")
    else:
        print(f"   ❌ package.json não encontrado: {package_json_path}")

def sugerir_solucoes():
    """Sugere soluções baseadas nos problemas encontrados"""
    print("\n💡 SOLUÇÕES PARA O DASHBOARD:")
    print("=" * 60)
    
    print("1. 🔐 SE O PROBLEMA É AUTENTICAÇÃO:")
    print("   - Acesse http://localhost:3001/login")
    print("   - Faça login com um usuário válido")
    print("   - Verifique se o cookie está sendo definido")
    
    print("\n2. 🌐 SE O PROBLEMA É PROXY:")
    print("   - Verifique se o proxy está configurado no package.json")
    print("   - Reinicie o servidor frontend (npm start)")
    print("   - Confirme se o backend está na porta 8000")
    
    print("\n3. 📊 SE O PROBLEMA É NO DASHBOARD:")
    print("   - Abra o console do navegador (F12)")
    print("   - Verifique erros JavaScript")
    print("   - Verifique a aba Network para ver requisições falhando")
    
    print("\n4. 🔧 SOLUÇÕES GERAIS:")
    print("   - Limpe o cache do navegador (Ctrl+Shift+R)")
    print("   - Reinicie ambos os servidores")
    print("   - Verifique se não há conflitos de porta")
    
    print("\n5. 🚀 COMANDOS PARA REINICIAR:")
    print("   Backend: cd RegistroOS/registrooficial/backend && python main.py")
    print("   Frontend: cd RegistroOS/registrooficial/frontend && npm start")

def main():
    """Função principal"""
    print("🚨 TESTE COMPLETO DO FRONTEND DASHBOARD")
    print("=" * 60)
    
    testar_frontend_dashboard()
    verificar_configuracao_proxy()
    sugerir_solucoes()
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\nSe o problema persistir:")
    print("1. Verifique o console do navegador")
    print("2. Teste fazer login manual")
    print("3. Reinicie os servidores")

if __name__ == "__main__":
    main()
