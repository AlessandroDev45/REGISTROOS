#!/usr/bin/env python3
"""
Teste direto do endpoint sem autenticação para debug
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_direct_endpoint():
    """Testar o endpoint diretamente"""
    print("🧪 TESTANDO ENDPOINT DIRETAMENTE")
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
        "observacoes": "Teste direto sem auth",
        "status": "PROGRAMADA"
    }
    
    print(f"📋 Dados de teste:")
    print(json.dumps(dados_programacao, indent=2))
    
    # Testar endpoint diretamente
    print(f"\n🚀 Testando endpoint diretamente...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=dados_programacao,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Resposta: {response.text}")
        
        if response.status_code == 200:
            print(f"   ✅ Sucesso!")
            data = response.json()
            print(f"   📊 ID: {data.get('id')}")
            return True
        elif response.status_code == 401:
            print(f"   🔐 Erro de autenticação (esperado)")
            return False
        else:
            print(f"   ❌ Erro inesperado")
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
    test_direct_endpoint()
