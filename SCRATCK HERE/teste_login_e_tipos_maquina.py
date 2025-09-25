#!/usr/bin/env python3
"""
Teste para fazer login e testar o endpoint tipos-maquina
"""

import requests
import json

def fazer_login():
    """Faz login usando o endpoint correto e retorna o cookie"""
    try:
        login_url = "http://localhost:8000/api/token"
        
        # Dados do login no formato form-data
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        print("🔐 Fazendo login...")
        response = requests.post(
            login_url, 
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"📊 Status do login: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar se há cookie de autenticação
            cookies = response.cookies
            print(f"✅ Login realizado com sucesso")
            print(f"🍪 Cookies recebidos: {dict(cookies)}")
            return cookies
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro durante o login: {e}")
        return None

def testar_tipos_maquina(cookies):
    """Testa o endpoint tipos-maquina com autenticação"""
    
    print("\n🧪 TESTE: Endpoint /api/tipos-maquina")
    print("=" * 50)
    
    try:
        # URL do endpoint
        url = "http://localhost:8000/api/tipos-maquina"
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição com cookies
        response = requests.get(url, cookies=cookies, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida:")
            print(f"📊 Total de registros: {len(data)}")
            
            if len(data) > 0:
                print(f"🔍 Primeiro registro:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            
            return True
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def testar_causas_retrabalho(cookies):
    """Testa o endpoint causas-retrabalho com autenticação"""
    
    print("\n🧪 TESTE: Endpoint /api/causas-retrabalho")
    print("=" * 50)
    
    try:
        # URL do endpoint
        url = "http://localhost:8000/api/causas-retrabalho"
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição com cookies
        response = requests.get(url, cookies=cookies, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida:")
            print(f"📊 Total de registros: {len(data)}")
            
            if len(data) > 0:
                print(f"🔍 Primeiro registro:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False))
            
            return True
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def main():
    """Função principal"""
    
    print("🧪 TESTE COMPLETO: Login + Endpoints")
    print("=" * 60)
    
    # Fazer login
    cookies = fazer_login()
    if not cookies:
        print("❌ Não foi possível fazer login. Teste abortado.")
        return
    
    # Testar endpoints
    sucesso_tipos = testar_tipos_maquina(cookies)
    sucesso_causas = testar_causas_retrabalho(cookies)
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   Login: ✅")
    print(f"   Tipos Máquina: {'✅' if sucesso_tipos else '❌'}")
    print(f"   Causas Retrabalho: {'✅' if sucesso_causas else '❌'}")
    
    if sucesso_tipos and sucesso_causas:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"   O frontend deve funcionar agora.")
        print(f"   Acesse: http://localhost:3001")
        print(f"   Faça login e teste a OS 12345")
    else:
        print(f"\n❌ ALGUNS TESTES FALHARAM!")
        print(f"   Verifique os logs do backend para mais detalhes.")

if __name__ == "__main__":
    main()
