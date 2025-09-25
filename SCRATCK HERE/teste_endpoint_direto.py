#!/usr/bin/env python3
"""
Teste direto do endpoint sem autenticação para debug
"""

import requests
import json

def testar_endpoint_direto():
    """Testa o endpoint diretamente"""
    
    print("🔍 TESTE DIRETO DO ENDPOINT")
    print("=" * 40)
    
    # Testar sem autenticação primeiro para ver o erro
    try:
        print("\n1️⃣ Testando sem autenticação...")
        response = requests.get("http://localhost:8000/api/desenvolvimento/formulario/os/12345", timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint existe (erro de autenticação esperado)")
            try:
                data = response.json()
                print(f"Mensagem: {data.get('detail', 'Sem detalhes')}")
            except:
                print(f"Resposta: {response.text[:100]}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            try:
                data = response.json()
                print(f"Dados: {json.dumps(data, indent=2)}")
            except:
                print(f"Resposta: {response.text[:200]}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    
    # Testar endpoint de health
    try:
        print("\n2️⃣ Testando endpoint de health...")
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor está funcionando")
        else:
            print("⚠️ Servidor com problemas")
    except:
        print("❌ Endpoint de health não responde")
    
    # Testar endpoint de docs
    try:
        print("\n3️⃣ Testando endpoint de docs...")
        response = requests.get("http://localhost:8000/docs", timeout=10)
        print(f"Docs Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Documentação disponível")
        else:
            print("⚠️ Documentação com problemas")
    except:
        print("❌ Endpoint de docs não responde")
    
    return True

def verificar_estrutura_endpoints():
    """Verifica a estrutura dos endpoints"""
    
    print("\n4️⃣ Verificando estrutura de endpoints...")
    
    endpoints_para_testar = [
        "/api/desenvolvimento/formulario/os/12345",
        "/api/desenvolvimento/",
        "/api/",
        "/docs",
        "/api/health"
    ]
    
    for endpoint in endpoints_para_testar:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
        except:
            print(f"   {endpoint}: ❌ Erro")

def main():
    """Função principal"""
    print("🧪 TESTE DIRETO DO ENDPOINT")
    print("=" * 50)
    
    sucesso = testar_endpoint_direto()
    
    if sucesso:
        verificar_estrutura_endpoints()
    
    print("\n" + "=" * 50)
    print("📊 CONCLUSÃO:")
    print("   Se o endpoint retorna 401, está funcionando")
    print("   Se retorna 404, há problema na rota")
    print("   Se não conecta, servidor não está rodando")

if __name__ == "__main__":
    main()
