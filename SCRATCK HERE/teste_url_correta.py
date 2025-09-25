#!/usr/bin/env python3
"""
Teste com a URL correta do endpoint
"""

import requests
import json

def fazer_login():
    """Faz login no sistema"""
    session = requests.Session()
    
    credenciais = [
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "user.pcp@registroos.com", "password": "123456"},
    ]
    
    for cred in credenciais:
        try:
            print(f"🔐 Tentando login: {cred['username']}")
            response = session.post("http://localhost:8000/api/login", json=cred, timeout=10)
            if response.status_code == 200:
                print(f"✅ Login OK: {cred['username']}")
                return session
            else:
                print(f"❌ Login falhou: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            continue
    
    return None

def testar_endpoint_correto():
    """Testa o endpoint com a URL correta"""
    
    print("🚀 TESTE COM URL CORRETA")
    print("=" * 40)
    
    # 1. Fazer login
    print("\n1️⃣ FAZENDO LOGIN...")
    session = fazer_login()
    if not session:
        print("❌ Teste interrompido - sem login")
        return False
    
    # 2. Testar endpoint com URL correta
    print("\n2️⃣ TESTANDO ENDPOINT COM URL CORRETA...")
    try:
        # URL correta baseada na documentação OpenAPI
        url = "http://localhost:8000/api/formulario/os/12345"
        print(f"🔍 URL: {url}")
        
        response = session.get(url, timeout=180)  # 3 minutos para scraping
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("🎉 SUCESSO! Dados retornados:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Número: {data.get('numero_os')}")
            print(f"   - Cliente: {data.get('cliente')}")
            print(f"   - Equipamento: {data.get('equipamento')}")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Fonte: {data.get('fonte', 'banco')}")
            
            if data.get('fonte') == 'scraping':
                print("\n🎯 SCRAPING FUNCIONOU!")
                print("   A OS foi criada automaticamente via scraping")
            elif data.get('fonte') == 'banco':
                print("\n📋 OS ENCONTRADA NO BANCO")
                print("   A OS já existia no banco de dados")
            
            return True
            
        elif response.status_code == 404:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', 'Erro desconhecido')
                print(f"❌ OS não encontrada: {error_msg}")
                
                if "⚠️ OS não cadastrada na base de dados" in error_msg:
                    print("✅ Mensagem de erro CORRETA!")
                    if "AGUARDE CONSULTA VIA WEB" in error_msg:
                        print("   Tipo: AGUARDE CONSULTA VIA WEB")
                    elif "Você pode preencher os campos manualmente" in error_msg:
                        print("   Tipo: Preencher manualmente")
                else:
                    print("⚠️ Mensagem de erro diferente do esperado")
                
            except:
                print(f"❌ Erro 404: {response.text[:200]}")
            return False
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Detalhes: {error_data.get('detail', 'Sem detalhes')}")
            except:
                print(f"   Resposta: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT - Requisição demorou mais de 3 minutos")
        print("   Isso pode indicar que o scraping está rodando")
        return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE COM URL CORRETA DO ENDPOINT")
    print("=" * 50)
    
    sucesso = testar_endpoint_correto()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    if sucesso:
        print("🎉 ENDPOINT FUNCIONANDO!")
        print("   A URL correta é: /api/formulario/os/{numero_os}")
        print("   O scraping automático está funcionando")
    else:
        print("❌ ENDPOINT COM PROBLEMAS")
        print("   Verifique:")
        print("   - Se o scraping está configurado")
        print("   - Se o arquivo .env existe")
        print("   - Os logs do backend para mais detalhes")

if __name__ == "__main__":
    main()
