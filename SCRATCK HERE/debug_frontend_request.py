#!/usr/bin/env python3
"""
Script para interceptar e debugar a requisição do frontend
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 DEBUG: INTERCEPTANDO REQUISIÇÃO DO FRONTEND")
    print("=" * 60)
    
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
    
    # 2. Simular exatamente o que o frontend está enviando
    print("\n2. 🎭 Simulando dados do frontend...")
    
    # Dados que o frontend provavelmente está enviando
    frontend_data = {
        "os_numero": "000012345",
        "inicio_previsto": "2025-09-26T10:00",  # Formato datetime-local
        "fim_previsto": "2025-09-26T12:00",
        "id_departamento": 1,
        "id_setor": 42,
        "responsavel_id": 1,
        "observacoes": "Teste do frontend",
        "status": "PROGRAMADA"
    }
    
    print(f"   📊 Dados simulados do frontend:")
    for key, value in frontend_data.items():
        print(f"      {key}: {value}")
    
    # 3. Testar com dados do frontend
    print("\n3. 🚀 Testando com dados do frontend...")
    try:
        response = session.post(
            f"{BASE_URL}/api/pcp/programacoes",
            json=frontend_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print("   ✅ Sucesso!")
            data = response.json()
            print(f"   📊 Resposta: {data}")
        else:
            print(f"   ❌ Erro {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 4. Testar com diferentes formatos de data
    print("\n4. 🕐 Testando diferentes formatos de data...")
    
    formatos_data = [
        ("ISO com Z", "2025-09-26T10:00:00Z", "2025-09-26T12:00:00Z"),
        ("ISO sem Z", "2025-09-26T10:00:00", "2025-09-26T12:00:00"),
        ("ISO com milissegundos", "2025-09-26T10:00:00.000", "2025-09-26T12:00:00.000"),
        ("Formato datetime-local", "2025-09-26T10:00", "2025-09-26T12:00")
    ]
    
    for nome, inicio, fim in formatos_data:
        print(f"\n   🧪 Testando {nome}...")
        test_data = frontend_data.copy()
        test_data["inicio_previsto"] = inicio
        test_data["fim_previsto"] = fim
        
        try:
            response = session.post(
                f"{BASE_URL}/api/pcp/programacoes",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"      ✅ {nome}: Sucesso!")
            else:
                print(f"      ❌ {nome}: Erro {response.status_code}")
                print(f"      📄 {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ {nome}: Erro {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()
