#!/usr/bin/env python3
"""
Script para testar se os relacionamentos Cliente e Equipamento estão funcionando em todos os endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔄 TESTANDO RELACIONAMENTOS CLIENTE E EQUIPAMENTO EM TODOS OS ENDPOINTS")
    print("=" * 80)
    
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
    
    # 2. Testar Desenvolvimento → Programação
    print("\n2. Testando Desenvolvimento → Programação...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            if isinstance(data, list) and len(data) > 0:
                primeiro = data[0]
                cliente = primeiro.get('cliente', 'N/A')
                equipamento = primeiro.get('equipamento', 'N/A')
                print(f"   📊 Cliente: {cliente}")
                print(f"   🔧 Equipamento: {equipamento}")
            else:
                print("   ⚠️ Nenhuma programação encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar Desenvolvimento → Apontamentos
    print("\n3. Testando Desenvolvimento → Apontamentos...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/apontamentos")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            if isinstance(data, list) and len(data) > 0:
                primeiro = data[0]
                cliente = primeiro.get('cliente', 'N/A')
                equipamento = primeiro.get('equipamento', 'N/A')
                print(f"   📊 Cliente: {cliente}")
                print(f"   🔧 Equipamento: {equipamento}")
            else:
                print("   ⚠️ Nenhum apontamento encontrado")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Testar Consulta OS → Pesquisa Por OS
    print("\n4. Testando Consulta OS → Pesquisa Por OS...")
    try:
        response = session.get(f"{BASE_URL}/api/os/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            if data.get('data') and len(data['data']) > 0:
                primeiro = data['data'][0]
                cliente = primeiro.get('cliente', 'N/A')
                equipamento = primeiro.get('equipamento', 'N/A')
                print(f"   📊 Cliente: {cliente}")
                print(f"   🔧 Equipamento: {equipamento}")
            else:
                print("   ⚠️ Nenhuma OS encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 5. Testar buscar-ids-os (já implementado)
    print("\n5. Testando buscar-ids-os...")
    try:
        test_data = {"numeros_os": ["000012345"]}
        response = session.post(f"{BASE_URL}/api/desenvolvimento/buscar-ids-os", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            dados_completos = data.get('dados_completos', {})
            if dados_completos:
                for numero, info in dados_completos.items():
                    cliente = info.get('cliente', {})
                    equipamento = info.get('equipamento', {})
                    print(f"   📊 Cliente: {cliente.get('nome', 'N/A') if cliente else 'N/A'}")
                    print(f"   🔧 Equipamento: {equipamento.get('descricao', 'N/A') if equipamento else 'N/A'}")
                    break
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 TESTE CONCLUÍDO!")
    print("Verifique se Cliente e Equipamento aparecem em todos os endpoints acima.")

if __name__ == "__main__":
    main()
