#!/usr/bin/env python3
"""
Teste para verificar o endpoint de dashboard de pendências
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🧪 TESTE: Dashboard de Pendências")
    print("=" * 50)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Fazer login
    print("\n1. Fazendo login...")
    try:
        login_data = {
            'username': 'admin@registroos.com',
            'password': '123456'
        }
        
        response = session.post(f"{BASE_URL}/api/token", data=login_data)
        if response.status_code != 200:
            print(f"   ❌ Erro no login: {response.status_code}")
            return
        print("   ✅ Login realizado com sucesso")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição de login: {e}")
        return
    
    # Testar endpoint de dashboard de pendências
    print("\n2. Testando endpoint /api/pcp/pendencias/dashboard...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias/dashboard")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint funcionando")
            print(f"   Estrutura retornada:")
            print(f"   - metricas_gerais: {'✅' if 'metricas_gerais' in data else '❌'}")
            print(f"   - distribuicao_prioridade: {'✅' if 'distribuicao_prioridade' in data else '❌'}")
            print(f"   - distribuicao_setor: {'✅' if 'distribuicao_setor' in data else '❌'}")
            print(f"   - evolucao_7_dias: {'✅' if 'evolucao_7_dias' in data else '❌'}")
            
            if 'metricas_gerais' in data:
                metricas = data['metricas_gerais']
                print(f"   Métricas gerais:")
                print(f"   - total_pendencias: {metricas.get('total_pendencias', 'N/A')}")
                print(f"   - pendencias_abertas: {metricas.get('pendencias_abertas', 'N/A')}")
                print(f"   - pendencias_fechadas: {metricas.get('pendencias_fechadas', 'N/A')}")
            
            print(f"\n   JSON completo:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"   ❌ Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n🏁 Teste concluído!")

if __name__ == "__main__":
    main()
