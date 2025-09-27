#!/usr/bin/env python3
"""
Script para verificar quais OSs existem no banco de dados
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 VERIFICANDO OSs EXISTENTES NO BANCO")
    print("=" * 50)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Buscar OSs existentes
    print("\n2. Buscando OSs existentes...")
    
    try:
        # Tentar endpoint de ordens de serviço
        response = session.get(f"{BASE_URL}/api/ordens-servico")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ OSs encontradas!")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"   Total de OSs: {len(data)}")
                print("\n   Primeiras 5 OSs:")
                for i, os in enumerate(data[:5]):
                    numero = os.get('os_numero') or os.get('numero_os') or 'N/A'
                    status = os.get('status_os', 'N/A')
                    print(f"   {i+1}. OS: {numero} - Status: {status}")
                
                # Testar com OS real
                if len(data) > 0:
                    primeira_os = data[0]
                    numero_teste = primeira_os.get('os_numero') or primeira_os.get('numero_os')
                    if numero_teste:
                        print(f"\n3. Testando buscar-ids-os com OS real: {numero_teste}")
                        
                        test_data = {
                            "numeros_os": [numero_teste]
                        }
                        
                        response = session.post(
                            f"{BASE_URL}/api/desenvolvimento/buscar-ids-os",
                            json=test_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   ✅ Teste com OS real funcionou!")
                            print(f"   Mapeamento: {result.get('mapeamento', {})}")
                            print(f"   Dados completos: {result.get('dados_completos', {})}")
                        else:
                            print(f"   ❌ Erro no teste: {response.status_code}")
            else:
                print("   ⚠️ Nenhuma OS encontrada no banco")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

if __name__ == "__main__":
    main()
