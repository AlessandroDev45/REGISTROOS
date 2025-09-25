#!/usr/bin/env python3
"""
Teste direto do endpoint tipos-maquina
"""

import requests
import json

def testar_endpoint():
    """Testa o endpoint tipos-maquina diretamente"""
    
    print("🧪 TESTE: Endpoint /api/tipos-maquina")
    print("=" * 50)
    
    try:
        # URL do endpoint
        url = "http://localhost:8000/api/tipos-maquina"
        
        print(f"📡 Fazendo requisição para: {url}")
        
        # Fazer requisição
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta recebida:")
            print(json.dumps(data[:3] if len(data) > 3 else data, indent=2, ensure_ascii=False))
            print(f"📊 Total de registros: {len(data)}")
            
        elif response.status_code == 401:
            print(f"🔐 Erro de autenticação: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    testar_endpoint()
