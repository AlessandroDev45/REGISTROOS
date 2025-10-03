#!/usr/bin/env python3
"""
Teste da API de relatório completo
"""

import requests
import json

def test_relatorio_api():
    """Testa a API de relatório completo"""
    session = requests.Session()
    
    try:
        # Fazer login
        login_data = {
            'username': 'admin@registroos.com',
            'password': '123456'
        }
        
        print("🔐 Fazendo login...")
        login_response = session.post('http://localhost:3001/api/login', json=login_data)
        print(f"Login: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
            
            # Testar relatório completo para OS 6 (que o usuário está testando)
            print("\n📊 Testando relatório completo para OS 6...")
            response = session.get('http://localhost:3001/api/os/6/relatorio-completo')
            print(f"Relatório: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Dados recebidos: {len(data)} campos")
                print(f"🔑 Chaves: {list(data.keys())}")
                
                # Verificar estrutura dos dados
                if 'apontamentos_detalhados' in data:
                    apontamentos = data['apontamentos_detalhados']
                    print(f"📝 Apontamentos: {len(apontamentos)}")
                    
                if 'resultados_testes' in data:
                    testes = data['resultados_testes']
                    print(f"🧪 Testes: {len(testes)}")
                    
                if 'apontamentos_por_setor' in data:
                    setores = data['apontamentos_por_setor']
                    print(f"🏢 Setores: {len(setores)}")
                    
                if 'metricas_consolidadas' in data:
                    metricas = data['metricas_consolidadas']
                    print(f"📈 Métricas: {list(metricas.keys())}")
                    
                # Salvar dados para análise
                with open('SCRATCK HERE/relatorio_os6_teste.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                print("💾 Dados salvos em relatorio_os6_teste.json")
                
            else:
                print(f"❌ Erro: {response.text[:200]}")
        else:
            print(f"❌ Erro no login: {login_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_relatorio_api()
