#!/usr/bin/env python3
"""
Teste específico para busca da OS 12345
"""

import requests
import json
import time

def fazer_login():
    """Faz login no sistema"""
    session = requests.Session()
    
    # Tentar com diferentes usuários
    credenciais = [
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "user.pcp@registroos.com", "password": "123456"},
        {"username": "supervisor.pcp@registroos.com", "password": "123456"},
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
    
    print("❌ Nenhum login funcionou")
    return None

def testar_busca_os_12345():
    """Testa especificamente a busca da OS 12345"""
    
    print("🚀 TESTE DE BUSCA DA OS 12345")
    print("=" * 50)
    
    # 1. Fazer login
    print("\n1️⃣ FAZENDO LOGIN...")
    session = fazer_login()
    if not session:
        print("❌ Teste interrompido - sem login")
        return False
    
    # 2. Testar endpoint
    print("\n2️⃣ TESTANDO ENDPOINT...")
    try:
        print("🔍 Fazendo requisição para OS 12345...")
        print("   URL: http://localhost:8000/api/desenvolvimento/formulario/os/12345")
        
        start_time = time.time()
        response = session.get(
            "http://localhost:8000/api/desenvolvimento/formulario/os/12345", 
            timeout=180  # 3 minutos para permitir scraping
        )
        end_time = time.time()
        
        print(f"⏱️ Tempo de resposta: {end_time - start_time:.2f} segundos")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCESSO! Dados retornados:")
            print(f"   - ID: {data.get('id')}")
            print(f"   - Número: {data.get('numero_os')}")
            print(f"   - Cliente: {data.get('cliente')}")
            print(f"   - Equipamento: {data.get('equipamento')}")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Fonte: {data.get('fonte', 'banco')}")
            
            if data.get('fonte') == 'scraping':
                print("🎉 SCRAPING FUNCIONOU!")
                print("   A OS foi criada automaticamente via scraping")
            elif data.get('fonte') == 'banco':
                print("📋 OS ENCONTRADA NO BANCO")
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
        print("   Verifique os logs do backend")
        return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def verificar_servidor():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor backend está rodando")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status: {response.status_code}")
            return False
    except:
        print("❌ Servidor backend não está rodando")
        print("   Execute: cd RegistroOS/registrooficial/backend && python -m uvicorn main:app --reload")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE ESPECÍFICO - BUSCA OS 12345")
    print("=" * 50)
    
    # Verificar servidor
    print("\n🔍 VERIFICANDO SERVIDOR...")
    if not verificar_servidor():
        print("❌ Teste interrompido - servidor não disponível")
        return
    
    # Executar teste
    sucesso = testar_busca_os_12345()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    if sucesso:
        print("🎉 TESTE PASSOU!")
        print("   A busca da OS 12345 funcionou corretamente")
        print("   O endpoint está respondendo como esperado")
    else:
        print("❌ TESTE FALHOU!")
        print("   Verifique:")
        print("   - Se o backend está rodando")
        print("   - Se o endpoint está correto")
        print("   - Se o scraping está configurado")
        print("   - Os logs do backend para mais detalhes")

if __name__ == "__main__":
    main()
