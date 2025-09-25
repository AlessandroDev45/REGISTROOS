#!/usr/bin/env python3
"""
Testar login com usuário admin
"""

import requests
import json

def testar_login_admin():
    """Testa login com diferentes combinações para o admin"""
    
    # Credenciais para testar
    credenciais = [
        {"username": "admin@registroos.com", "password": "admin123"},
        {"username": "ADMIN", "password": "admin123"},
        {"username": "admin@registroos.com", "password": "123456"},
        {"username": "ADMIN", "password": "123456"},
        {"username": "admin@registroos.com", "password": "admin"},
        {"username": "ADMIN", "password": "admin"},
    ]
    
    session = requests.Session()
    
    for cred in credenciais:
        try:
            print(f"🔐 Testando: {cred['username']} / {cred['password']}")
            response = session.post("http://localhost:8000/api/login", json=cred, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ LOGIN SUCESSO: {cred['username']} / {cred['password']}")
                
                # Testar endpoint de status do scraping
                print("🔍 Testando status do scraping...")
                response = session.get("http://localhost:8000/api/desenvolvimento/scraping/status", timeout=10)
                
                if response.status_code == 200:
                    status = response.json()
                    print("📊 Status do sistema de scraping:")
                    print(f"   - Scraping disponível: {status.get('scraping_disponivel')}")
                    print(f"   - Script existe: {status.get('script_existe')}")
                    print(f"   - Arquivo .env existe: {status.get('env_existe')}")
                    print(f"   - Variáveis configuradas: {status.get('variaveis_configuradas')}")
                else:
                    print(f"❌ Erro ao verificar status do scraping: {response.status_code}")
                
                return session
            else:
                print(f"❌ Falhou: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("❌ Nenhuma credencial funcionou")
    return None

if __name__ == "__main__":
    testar_login_admin()
