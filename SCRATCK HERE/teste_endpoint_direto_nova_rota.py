#!/usr/bin/env python3
"""
Teste direto do endpoint com a nova rota
"""

import requests
import json

def testar_endpoint():
    """Testa o endpoint diretamente"""
    
    print("🔍 TESTANDO ENDPOINT NOVA ROTA")
    print("=" * 50)
    
    try:
        url = "http://localhost:8000/api/formulario/buscar-os/20203"
        print(f"📡 URL: {url}")
        
        print(f"🚀 Fazendo requisição...")
        response = requests.get(url, timeout=180)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ SUCESSO!")
            data = response.json()
            print(f"📊 Dados retornados:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ ERRO {response.status_code}")
            print(f"📄 Resposta: {response.text}")
        
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Requisição demorou mais que 3 minutos")
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    testar_endpoint()
