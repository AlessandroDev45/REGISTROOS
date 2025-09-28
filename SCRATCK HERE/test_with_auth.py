#!/usr/bin/env python3
"""
Teste do endpoint com autenticação
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_with_auth():
    """Testar o endpoint com autenticação"""
    print("🧪 TESTANDO ENDPOINT COM AUTENTICAÇÃO")
    print("=" * 50)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # 1. Fazer login
    print("🔐 Fazendo login...")
    login_data = {
        "username": "user.pcp@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"   Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Erro no login: {login_response.text}")
            return False
        
        print(f"   ✅ Login realizado com sucesso")
        
        # 2. Testar endpoint de programação
        print(f"\n🚀 Testando criação de programação...")
        
        # Dados de teste
        agora = datetime.now()
        inicio = agora + timedelta(hours=1)
        fim = agora + timedelta(hours=9)
        
        dados_programacao = {
            "os_numero": "000020611",  # OS válida no banco (VALE SA)
            "inicio_previsto": inicio.isoformat(),
            "fim_previsto": fim.isoformat(),
            "id_departamento": 1,
            "id_setor": 6,
            "responsavel_id": 9,
            "observacoes": "Teste com autenticação - OS VALE SA",
            "status": "PROGRAMADA"
        }
        
        print(f"📋 Dados de teste:")
        print(json.dumps(dados_programacao, indent=2))
        
        response = session.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=dados_programacao,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ Programação criada com sucesso!")
            data = response.json()
            print(f"   📊 ID: {data.get('id')}")
            return True
        else:
            print(f"   ❌ Erro ao criar programação")
            try:
                error_data = response.json()
                print(f"   🔍 Detalhes: {error_data}")
            except:
                print(f"   📄 Resposta bruta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    test_with_auth()
