#!/usr/bin/env python3
"""
Teste do endpoint de criação de programação
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_programacao_endpoint():
    """Testar o endpoint de criação de programação"""
    print("🧪 TESTANDO ENDPOINT DE CRIAÇÃO DE PROGRAMAÇÃO")
    print("=" * 50)
    
    # Dados de teste
    agora = datetime.now()
    inicio = agora + timedelta(hours=1)
    fim = agora + timedelta(hours=9)
    
    dados_programacao = {
        "os_numero": "000020511",
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "id_departamento": 1,
        "id_setor": 6,
        "responsavel_id": 9,
        "observacoes": "Teste de criação via script",
        "status": "PROGRAMADA"
    }
    
    print(f"📋 Dados de teste:")
    print(json.dumps(dados_programacao, indent=2))
    
    # Primeiro, tentar fazer login para obter cookies de autenticação
    print(f"\n🔐 Fazendo login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    try:
        # Login
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"   Status do login: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   ❌ Erro no login: {login_response.text}")
            return False
        
        print(f"   ✅ Login realizado com sucesso")
        
        # Testar endpoint de programação
        print(f"\n🚀 Testando criação de programação...")
        response = session.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=dados_programacao,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
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
    test_programacao_endpoint()
