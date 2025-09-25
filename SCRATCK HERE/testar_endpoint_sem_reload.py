#!/usr/bin/env python3
"""
Teste do endpoint com servidor sem auto-reload
"""

import requests
import json
import time

def fazer_login():
    """Faz login no sistema"""
    session = requests.Session()
    
    credenciais = {"username": "admin@registroos.com", "password": "admin123"}
    
    try:
        print(f"🔐 Fazendo login: {credenciais['username']}")
        response = session.post("http://localhost:8000/api/login", json=credenciais, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Login OK")
            return session
        else:
            print(f"❌ Login falhou: {response.status_code}")
            return None
                    
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def testar_endpoint_completo():
    """Testa o endpoint completo com scraping"""
    
    print("🚀 TESTE DO ENDPOINT COM SCRAPING")
    print("=" * 50)
    
    # 1. Fazer login
    print("\n1️⃣ FAZENDO LOGIN...")
    session = fazer_login()
    if not session:
        print("❌ Teste interrompido - sem login")
        return False
    
    # 2. Testar endpoint
    print("\n2️⃣ TESTANDO ENDPOINT COM SCRAPING...")
    try:
        url = "http://localhost:8000/api/formulario/os/12345"
        print(f"🔍 URL: {url}")
        print(f"⏰ Iniciando requisição às {time.strftime('%H:%M:%S')}")
        print("⚠️ AGUARDE... O scraping pode demorar alguns minutos...")
        print("📋 IMPORTANTE: NÃO REINICIE O SERVIDOR DURANTE O TESTE!")
        
        start_time = time.time()
        response = session.get(url, timeout=600)  # 10 minutos
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"⏱️ Tempo total: {duration:.2f} segundos")
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
                print("\n🎯 SCRAPING FUNCIONOU VIA ENDPOINT!")
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
                        print("   ⚠️ ISSO INDICA QUE O SCRAPING FALHOU!")
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
        print("⏰ TIMEOUT - Requisição demorou mais de 10 minutos")
        print("   O scraping pode estar rodando mas demorou muito")
        return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DO ENDPOINT SEM AUTO-RELOAD")
    print("=" * 60)
    
    print("📋 INSTRUÇÕES IMPORTANTES:")
    print("   1. PARE o servidor atual (Ctrl+C)")
    print("   2. Inicie o servidor SEM auto-reload:")
    print("      uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload")
    print("   3. Execute este teste")
    print("   4. NÃO TOQUE NO SERVIDOR durante o teste")
    
    input("\n⏸️ Pressione ENTER quando o servidor estiver rodando SEM auto-reload...")
    
    sucesso = testar_endpoint_completo()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    if sucesso:
        print("🎉 ENDPOINT COM SCRAPING FUNCIONOU!")
        print("   O problema era o auto-reload do servidor")
        print("   Solução: Configurar timeout adequado")
    else:
        print("❌ ENDPOINT AINDA TEM PROBLEMAS!")
        print("   Verifique os logs do servidor")

if __name__ == "__main__":
    main()
