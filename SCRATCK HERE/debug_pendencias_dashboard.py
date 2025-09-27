#!/usr/bin/env python3
"""
Script para debugar o problema das pendências no dashboard
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_pendencias_endpoints():
    """Testar endpoints de pendências"""
    
    # Primeiro fazer login
    print("🔐 Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }

    session = requests.Session()

    try:
        # Login usando o endpoint correto
        response = session.post(f"{BASE_URL}/api/token", data=login_data)
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            return
        
        print("✅ Login realizado com sucesso!")
        
        # 1. Testar endpoint de pendências simples
        print("\n1. 📋 Testando endpoint /api/pcp/pendencias...")
        response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} pendências retornadas")
            
            if data:
                print("   📊 Primeiras 3 pendências:")
                for i, pend in enumerate(data[:3], 1):
                    print(f"      {i}. ID: {pend.get('id')} | OS: {pend.get('numero_os')} | Status: {pend.get('status')}")
            else:
                print("   📋 Lista vazia - nenhuma pendência encontrada")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:300]}")
        
        # 2. Testar endpoint de dashboard de pendências
        print("\n2. 📊 Testando endpoint /api/pcp/pendencias/dashboard...")
        response = session.get(f"{BASE_URL}/api/pcp/pendencias/dashboard")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! Dashboard retornado")
            print(f"   📊 Métricas gerais:")
            metricas = data.get('metricas_gerais', {})
            print(f"      - Total: {metricas.get('total_pendencias', 0)}")
            print(f"      - Abertas: {metricas.get('pendencias_abertas', 0)}")
            print(f"      - Fechadas: {metricas.get('pendencias_fechadas', 0)}")
            print(f"      - Período: {metricas.get('pendencias_periodo', 0)}")
            print(f"      - Críticas: {metricas.get('pendencias_criticas', 0)}")
            print(f"      - Tempo médio: {metricas.get('tempo_medio_resolucao_horas', 0)}h")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:300]}")
        
        # 3. Verificar diferença entre PCP e Desenvolvimento
        print("\n3. 🔧 Testando endpoint /api/desenvolvimento/pendencias...")
        response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data)} pendências retornadas (Desenvolvimento)")

            if data:
                print("   📊 Primeiras 3 pendências (Desenvolvimento):")
                for i, pend in enumerate(data[:3], 1):
                    print(f"      {i}. ID: {pend.get('id')} | OS: {pend.get('numero_os')} | Status: {pend.get('status')}")
            else:
                print("   📋 Lista vazia - nenhuma pendência encontrada (Desenvolvimento)")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text[:300]}")

        # 4. Verificar estrutura da tabela
        print("\n4. 🗃️ Verificando estrutura da tabela pendências...")
        # Vamos verificar se o problema está na query SQL do dashboard
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    print("🔍 DEBUGANDO PENDÊNCIAS NO DASHBOARD")
    print("=" * 50)
    test_pendencias_endpoints()
