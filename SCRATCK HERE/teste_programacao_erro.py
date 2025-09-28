#!/usr/bin/env python3
"""
Teste para reproduzir erro 500 em programação
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/token"
PROGRAMACAO_URL = f"{BASE_URL}/api/pcp/programacoes"

def fazer_login():
    """Fazer login e obter cookies de sessão"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    response = requests.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200:
        print("✅ Login realizado com sucesso!")
        return response.cookies
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def testar_programacao(cookies):
    """Testar criação de programação"""
    
    # Dados exatos do frontend
    dados_programacao = {
        "os_numero": "000020611",
        "inicio_previsto": "2025-09-22T21:46",
        "fim_previsto": "2025-09-23T21:46",
        "id_departamento": 1,
        "id_setor": 6,
        "responsavel_id": 9,
        "observacoes": "SDAFADSTETWEQRWE ",
        "status": "PROGRAMADA"
    }
    
    print(f"\n🔍 Testando criação de programação:")
    print(f"📋 Dados: {json.dumps(dados_programacao, indent=2)}")
    
    try:
        response = requests.post(
            PROGRAMACAO_URL, 
            cookies=cookies,
            json=dados_programacao,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📋 Resposta completa: {response.text}")
        
        if response.status_code == 500:
            try:
                error_detail = response.json()
                print(f"🔍 Detalhes do erro 500:")
                print(f"   - Detail: {error_detail.get('detail', 'N/A')}")
            except:
                print("❌ Não foi possível parsear detalhes do erro")
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE: Reproduzir erro 500 em programação")
    print("=" * 60)
    
    cookies = fazer_login()
    if not cookies:
        return
    
    testar_programacao(cookies)
    
    print("\n" + "=" * 60)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    main()
