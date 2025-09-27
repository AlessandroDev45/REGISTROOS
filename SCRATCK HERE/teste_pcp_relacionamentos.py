#!/usr/bin/env python3
"""
Script para testar se os relacionamentos Cliente e Equipamento estão funcionando nos endpoints do PCP
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔄 TESTANDO RELACIONAMENTOS CLIENTE E EQUIPAMENTO NO PCP")
    print("=" * 70)
    
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
    
    # 2. Testar PCP → Programações
    print("\n2. Testando PCP → Programações...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            if isinstance(data, list) and len(data) > 0:
                primeiro = data[0]
                cliente = primeiro.get('cliente', 'N/A')
                equipamento = primeiro.get('equipamento', 'N/A')
                os_numero = primeiro.get('os_numero', 'N/A')
                print(f"   📊 OS: {os_numero}")
                print(f"   📊 Cliente: {cliente}")
                print(f"   🔧 Equipamento: {equipamento}")
            else:
                print("   ⚠️ Nenhuma programação encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar PCP → Pendências
    print("\n3. Testando PCP → Pendências...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            if isinstance(data, list) and len(data) > 0:
                primeiro = data[0]
                cliente = primeiro.get('cliente', 'N/A')
                equipamento = primeiro.get('equipamento', 'N/A')
                numero_os = primeiro.get('numero_os', 'N/A')
                print(f"   📊 OS: {numero_os}")
                print(f"   📊 Cliente: {cliente}")
                print(f"   🔧 Equipamento: {equipamento}")
            else:
                print("   ⚠️ Nenhuma pendência encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 TESTE PCP CONCLUÍDO!")
    print("Verifique se Cliente e Equipamento aparecem nos endpoints do PCP.")

if __name__ == "__main__":
    main()
