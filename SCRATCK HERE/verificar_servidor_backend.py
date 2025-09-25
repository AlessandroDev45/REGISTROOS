#!/usr/bin/env python3
"""
Verificar se o servidor backend está rodando e funcionando
"""

import requests
import json
import time

def verificar_servidor():
    """Verifica se o servidor está rodando"""
    
    print("🔍 VERIFICANDO SERVIDOR BACKEND")
    print("=" * 40)
    
    # 1. Testar health
    try:
        print("\n1️⃣ Testando endpoint de health...")
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Servidor está rodando")
        else:
            print("   ❌ Servidor com problemas")
            return False
    except Exception as e:
        print(f"   ❌ Servidor não responde: {e}")
        return False
    
    # 2. Testar docs
    try:
        print("\n2️⃣ Testando documentação...")
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Documentação disponível")
        else:
            print("   ⚠️ Documentação com problemas")
    except Exception as e:
        print(f"   ❌ Documentação não responde: {e}")
    
    # 3. Testar endpoint específico
    try:
        print("\n3️⃣ Testando endpoint de desenvolvimento...")
        response = requests.get("http://localhost:8000/api/desenvolvimento/formulario/os/12345", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Endpoint existe (erro de autenticação)")
            return True
        elif response.status_code == 404:
            print("   ❌ Endpoint não encontrado")
            try:
                data = response.json()
                print(f"   Detalhes: {data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:100]}")
            return False
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")
            try:
                data = response.json()
                print(f"   Dados: {json.dumps(data, indent=2)[:200]}")
            except:
                print(f"   Resposta: {response.text[:100]}")
            return True
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
        return False

def listar_endpoints_disponiveis():
    """Lista endpoints disponíveis via OpenAPI"""
    
    try:
        print("\n4️⃣ Listando endpoints disponíveis...")
        response = requests.get("http://localhost:8000/openapi.json", timeout=10)
        
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            desenvolvimento_paths = []
            for path, methods in paths.items():
                if 'desenvolvimento' in path:
                    for method in methods.keys():
                        desenvolvimento_paths.append(f"{method.upper()} {path}")
            
            if desenvolvimento_paths:
                print("   ✅ Endpoints de desenvolvimento encontrados:")
                for endpoint in desenvolvimento_paths:
                    print(f"      - {endpoint}")
            else:
                print("   ❌ Nenhum endpoint de desenvolvimento encontrado")
                
            # Procurar especificamente pelo endpoint de formulário
            formulario_found = False
            for path in paths.keys():
                if 'formulario/os' in path:
                    print(f"   ✅ Endpoint de formulário encontrado: {path}")
                    formulario_found = True
                    break
            
            if not formulario_found:
                print("   ❌ Endpoint de formulário NÃO encontrado")
                
        else:
            print(f"   ❌ Erro ao obter OpenAPI: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao listar endpoints: {e}")

def testar_com_autenticacao():
    """Testa com autenticação"""
    
    print("\n5️⃣ Testando com autenticação...")
    
    # Tentar fazer login
    credenciais = [
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "user.pcp@registroos.com", "password": "123456"},
    ]
    
    for cred in credenciais:
        try:
            print(f"   🔐 Tentando login: {cred['username']}")
            session = requests.Session()
            response = session.post("http://localhost:8000/api/login", json=cred, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Login OK: {cred['username']}")
                
                # Testar endpoint com autenticação
                print("   🔍 Testando endpoint com autenticação...")
                response = session.get("http://localhost:8000/api/desenvolvimento/formulario/os/12345", timeout=30)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   🎉 ENDPOINT FUNCIONANDO!")
                    data = response.json()
                    print(f"   Dados: {json.dumps(data, indent=2)[:300]}")
                    return True
                else:
                    try:
                        data = response.json()
                        print(f"   Erro: {data.get('detail', 'Sem detalhes')}")
                    except:
                        print(f"   Resposta: {response.text[:100]}")
                
                break
            else:
                print(f"   ❌ Login falhou: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro no login: {e}")
    
    return False

def main():
    """Função principal"""
    print("🧪 VERIFICAÇÃO COMPLETA DO SERVIDOR")
    print("=" * 50)
    
    servidor_ok = verificar_servidor()
    
    if servidor_ok:
        listar_endpoints_disponiveis()
        endpoint_ok = testar_com_autenticacao()
        
        print("\n" + "=" * 50)
        print("📊 RESULTADO FINAL:")
        if endpoint_ok:
            print("🎉 TUDO FUNCIONANDO!")
            print("   O endpoint está respondendo corretamente")
        else:
            print("⚠️ SERVIDOR OK, MAS ENDPOINT COM PROBLEMAS")
            print("   Verifique:")
            print("   - Se o endpoint está registrado corretamente")
            print("   - Se há erros no código do endpoint")
            print("   - Os logs do servidor para mais detalhes")
    else:
        print("\n" + "=" * 50)
        print("❌ SERVIDOR COM PROBLEMAS")
        print("   Inicie o servidor com:")
        print("   cd RegistroOS/registrooficial/backend")
        print("   python -m uvicorn main:app --reload")

if __name__ == "__main__":
    main()
