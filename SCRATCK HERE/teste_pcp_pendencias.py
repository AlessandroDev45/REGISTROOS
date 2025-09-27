#!/usr/bin/env python3
"""
Teste para verificar se PCP vê todas as pendências
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE: PCP VÊ TODAS AS PENDÊNCIAS")
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
    
    # 2. Verificar pendências no PCP
    print("\n2. 🏭 Pendências no PCP:")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} pendências")
            
            if data:
                print("   📊 Lista de pendências:")
                setores_encontrados = set()
                for i, pend in enumerate(data, 1):
                    os_numero = pend.get('numero_os', 'N/A')
                    responsavel = pend.get('responsavel_nome', 'N/A')
                    status = pend.get('status', 'N/A')
                    print(f"      {i:2d}. OS: {os_numero:>10s} | Responsável: {responsavel[:20]:>20s} | Status: {status}")
                    
                    # Tentar identificar setor pela OS ou responsável
                    if responsavel != 'N/A':
                        setores_encontrados.add(responsavel)
                
                print(f"\n   🏢 Responsáveis únicos encontrados: {len(setores_encontrados)}")
                for responsavel in sorted(setores_encontrados):
                    print(f"      - {responsavel}")
                    
            else:
                print("   ❌ Nenhuma pendência encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Verificar pendências no desenvolvimento (para comparação)
    print("\n3. 🔧 Pendências no DESENVOLVIMENTO (para comparação):")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} pendências")
            
            if data:
                print("   📊 Lista de pendências (filtradas por setor):")
                for i, pend in enumerate(data, 1):
                    os_numero = pend.get('numero_os', 'N/A')
                    responsavel = pend.get('responsavel_nome', 'N/A')
                    status = pend.get('status', 'N/A')
                    print(f"      {i:2d}. OS: {os_numero:>10s} | Responsável: {responsavel[:20]:>20s} | Status: {status}")
            else:
                print("   ❌ Nenhuma pendência encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Comparar resultados
    print(f"\n4. 📊 COMPARAÇÃO:")
    try:
        pcp_response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        dev_response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        
        if pcp_response.status_code == 200 and dev_response.status_code == 200:
            pcp_data = pcp_response.json()
            dev_data = dev_response.json()
            
            print(f"   🏭 PCP: {len(pcp_data)} pendências (TODAS)")
            print(f"   🔧 Desenvolvimento: {len(dev_data)} pendências (FILTRADAS)")
            
            if len(pcp_data) >= len(dev_data):
                print(f"   ✅ CORRETO: PCP vê mais ou igual pendências que desenvolvimento")
            else:
                print(f"   ❌ PROBLEMA: PCP deveria ver mais pendências que desenvolvimento")
                
        else:
            print("   ❌ Erro ao comparar dados")
            
    except Exception as e:
        print(f"   ❌ Erro na comparação: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\n💡 RESULTADO ESPERADO:")
    print("   - PCP deve ver TODAS as pendências de TODOS os setores")
    print("   - Desenvolvimento deve ver apenas pendências do seu setor")
    print("   - PCP >= Desenvolvimento em número de pendências")

if __name__ == "__main__":
    main()
