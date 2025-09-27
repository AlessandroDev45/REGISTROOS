#!/usr/bin/env python3
"""
Teste para verificar se todas as programações aparecem no desenvolvimento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE: TODAS AS PROGRAMAÇÕES NO DESENVOLVIMENTO")
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
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Verificar programações no desenvolvimento
    print("\n2. 🔧 Programações no DESENVOLVIMENTO:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.data if hasattr(response, 'data') else response.json()
            print(f"   ✅ Total: {len(data)} programações")
            
            if data:
                print("   📊 Lista completa:")
                for i, prog in enumerate(data, 1):
                    print(f"      {i:2d}. ID: {prog.get('id'):2d} | OS: {prog.get('os_numero', 'N/A'):>10s} | Responsável: {prog.get('responsavel_nome', 'N/A'):>15s} | Status: {prog.get('status', 'N/A')}")
            else:
                print("   ❌ Nenhuma programação encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Verificar programações no PCP (para comparação)
    print("\n3. 🏭 Programações no PCP (para comparação):")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if response.status_code == 200:
            data = response.data if hasattr(response, 'data') else response.json()
            print(f"   ✅ Total: {len(data)} programações")
            
            if data:
                print("   📊 Lista completa:")
                for i, prog in enumerate(data, 1):
                    print(f"      {i:2d}. ID: {prog.get('id'):2d} | OS: {prog.get('os_numero', 'N/A'):>10s} | Responsável: {prog.get('responsavel_nome', 'N/A'):>15s} | Setor: {prog.get('setor_nome', 'N/A')}")
            else:
                print("   ❌ Nenhuma programação encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Comparar resultados
    print("\n4. 📊 COMPARAÇÃO:")
    try:
        dev_response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        pcp_response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if dev_response.status_code == 200 and pcp_response.status_code == 200:
            dev_data = dev_response.json()
            pcp_data = pcp_response.json()
            
            print(f"   🔧 Desenvolvimento: {len(dev_data)} programações")
            print(f"   🏭 PCP: {len(pcp_data)} programações")
            
            # Verificar se desenvolvimento mostra apenas do setor 42
            setor_42_count = sum(1 for prog in dev_data if prog.get('id_setor') == 42)
            print(f"   🏢 Setor 42 no desenvolvimento: {setor_42_count}")
            
            # Verificar se há duplicação
            dev_ids = [prog.get('id') for prog in dev_data]
            dev_unique_ids = set(dev_ids)
            if len(dev_ids) != len(dev_unique_ids):
                print(f"   ⚠️ DUPLICAÇÃO detectada! {len(dev_ids)} total vs {len(dev_unique_ids)} únicos")
            else:
                print(f"   ✅ Sem duplicação: {len(dev_unique_ids)} programações únicas")
                
        else:
            print("   ❌ Erro ao comparar dados")
            
    except Exception as e:
        print(f"   ❌ Erro na comparação: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
