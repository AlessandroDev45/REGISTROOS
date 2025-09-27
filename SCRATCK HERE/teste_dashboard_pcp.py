#!/usr/bin/env python3
"""
Teste específico do dashboard PCP
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 TESTE: DASHBOARD PCP")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. 🔐 Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar dashboard
    print("\n2. 📊 Testando dashboard de pendências:")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias/dashboard")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dashboard funcionando!")
            print(f"   📊 Estrutura: {list(data.keys())}")
            
            if 'metricas_gerais' in data:
                metricas = data['metricas_gerais']
                print(f"   📈 Métricas gerais:")
                for key, value in metricas.items():
                    print(f"      {key}: {value}")
            
            if 'distribuicao_setor' in data:
                setores = data['distribuicao_setor']
                print(f"   🏢 Distribuição por setor: {len(setores)} setores")
                for setor in setores:
                    print(f"      {setor}")
            
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:500]}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar com parâmetros
    print("\n3. 📊 Testando dashboard com período específico:")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias/dashboard?periodo_dias=7")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dashboard com período funcionando!")
            
            if 'metricas_gerais' in data:
                metricas = data['metricas_gerais']
                print(f"   📈 Métricas para 7 dias:")
                print(f"      Total: {metricas.get('total_pendencias', 0)}")
                print(f"      Abertas: {metricas.get('pendencias_abertas', 0)}")
                print(f"      Fechadas: {metricas.get('pendencias_fechadas', 0)}")
                print(f"      Período: {metricas.get('pendencias_periodo', 0)}")
                print(f"      Críticas: {metricas.get('pendencias_criticas', 0)}")
                print(f"      Tempo médio: {metricas.get('tempo_medio_resolucao_horas', 0)}h")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
