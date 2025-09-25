#!/usr/bin/env python3
import requests
import json

def testar_endpoints():
    base_url = "http://localhost:8000"
    
    print("🔍 Testando endpoints do backend...")
    
    # Testar endpoints sem autenticação primeiro
    endpoints_publicos = [
        "/",
        "/health",
        "/docs"
    ]
    
    for endpoint in endpoints_publicos:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    # Testar endpoints que podem precisar de autenticação
    endpoints_admin = [
        "/api/admin/setores/",
        "/api/admin/departamentos/",
        "/api/admin/status",
        "/api/setores",
        "/api/departamentos"
    ]
    
    print(f"\n🔐 Testando endpoints que podem precisar de autenticação:")
    for endpoint in endpoints_admin:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"  {endpoint}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"  ❌ {endpoint}: {e}")
    
    # Testar endpoint de apontamentos detalhados
    print(f"\n📊 Testando endpoint de apontamentos:")
    try:
        response = requests.get(f"{base_url}/api/apontamentos-detalhados")
        print(f"  /api/apontamentos-detalhados: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ /api/apontamentos-detalhados: {e}")

if __name__ == "__main__":
    testar_endpoints()
