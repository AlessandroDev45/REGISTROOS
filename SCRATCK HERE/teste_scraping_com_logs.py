#!/usr/bin/env python3
"""
Teste do scraping com logs detalhados
"""

import requests
import json
import time

def fazer_login():
    """Faz login no sistema"""
    session = requests.Session()
    
    # Tentar com usuário que sabemos que funciona
    credenciais = [
        {"username": "user.pcp@registroos.com", "password": "123456"},
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "supervisor.pcp@registroos.com", "password": "123456"},
    ]
    
    for cred in credenciais:
        try:
            print(f"🔐 Tentando login: {cred['username']}")
            response = session.post("http://localhost:8000/api/login", json=cred, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Login OK: {cred['username']}")
                data = response.json()
                print(f"   Token: {data.get('access_token', 'N/A')[:20]}...")
                return session
            else:
                print(f"❌ Login falhou: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Erro: {error_data.get('detail', 'Sem detalhes')}")
                except:
                    print(f"   Resposta: {response.text[:100]}")
                    
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            continue
    
    return None

def testar_scraping_com_logs():
    """Testa o scraping e mostra os logs do backend"""
    
    print("🚀 TESTE DE SCRAPING COM LOGS")
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
        # URL correta
        url = "http://localhost:8000/api/formulario/os/12345"
        print(f"🔍 URL: {url}")
        print(f"⏰ Iniciando requisição às {time.strftime('%H:%M:%S')}")
        print("⚠️ AGUARDE... O scraping pode demorar alguns minutos...")
        
        start_time = time.time()
        response = session.get(url, timeout=300)  # 5 minutos
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
        print("⏰ TIMEOUT - Requisição demorou mais de 5 minutos")
        print("   O scraping pode estar rodando mas demorou muito")
        print("   Verifique os logs do backend para ver o progresso")
        return False
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DE SCRAPING COM LOGS DETALHADOS")
    print("=" * 60)
    
    print("📋 INSTRUÇÕES:")
    print("   1. Certifique-se de que o backend está rodando")
    print("   2. Monitore os logs do backend durante o teste")
    print("   3. O teste pode demorar alguns minutos")
    print("   4. Procure por mensagens de debug no backend")
    
    input("\n⏸️ Pressione ENTER para continuar...")
    
    sucesso = testar_scraping_com_logs()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL:")
    if sucesso:
        print("🎉 SCRAPING FUNCIONOU!")
        print("   O endpoint está executando o scraping corretamente")
    else:
        print("❌ SCRAPING FALHOU!")
        print("   VERIFIQUE OS LOGS DO BACKEND PARA:")
        print("   - Mensagens de debug do scraping")
        print("   - Erros de importação do módulo")
        print("   - Problemas com o arquivo .env")
        print("   - Erros do ChromeDriver")
        print("   - Problemas de conexão com o site")

if __name__ == "__main__":
    main()
