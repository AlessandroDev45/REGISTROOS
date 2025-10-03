#!/usr/bin/env python3
"""
Teste de integração frontend-backend para relatório completo
"""

import requests
import json

def test_frontend_integration():
    """Simula o comportamento do frontend"""
    session = requests.Session()
    
    try:
        print("🔐 Simulando login do frontend...")
        
        # Login usando o mesmo método do frontend (form data)
        login_data = {
            'username': 'admin@registroos.com',
            'password': '123456'
        }
        
        # Usar form data como o frontend
        response = session.post(
            'http://localhost:3001/api/token',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"Login (token): {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login com token realizado com sucesso")
            
            # Testar relatório completo como o frontend faria
            print("\n📊 Testando relatório completo (simulando frontend)...")
            response = session.get('http://localhost:3001/api/os/5/relatorio-completo')
            print(f"Relatório: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Frontend conseguiria receber: {len(data)} campos")
                
                # Verificar se todas as abas teriam dados
                abas_status = {
                    'resumo': 'resumo_gerencial' in data,
                    'apontamentos': len(data.get('apontamentos_por_setor', {})) > 0,
                    'testes': len(data.get('resultados_testes', [])) > 0,
                    'horas': 'metricas_consolidadas' in data,
                    'retrabalhos': len(data.get('pendencias_retrabalhos', [])) > 0
                }
                
                print("\n📋 Status das abas do relatório:")
                for aba, tem_dados in abas_status.items():
                    status = "✅ COM DADOS" if tem_dados else "⚠️ SEM DADOS"
                    print(f"  {aba.upper()}: {status}")
                
                # Verificar dados específicos para cada aba
                if data.get('resumo_gerencial'):
                    resumo = data['resumo_gerencial']
                    print(f"\n📊 RESUMO GERENCIAL:")
                    print(f"  Status OS: {resumo.get('status_os')}")
                    print(f"  Desvio: {resumo.get('desvio_percentual')}%")
                    print(f"  Aprovação: {resumo.get('aprovacao_testes')}%")
                
                if data.get('resultados_testes'):
                    testes = data['resultados_testes']
                    print(f"\n🧪 TESTES:")
                    print(f"  Total: {len(testes)}")
                    aprovados = len([t for t in testes if t.get('resultado') == 'APROVADO'])
                    print(f"  Aprovados: {aprovados}")
                
                return True
                
            else:
                print(f"❌ Erro no relatório: {response.text[:200]}")
                return False
        else:
            print(f"❌ Erro no login: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_integration()
    if success:
        print("\n🎉 INTEGRAÇÃO FRONTEND-BACKEND FUNCIONANDO!")
        print("✅ O relatório completo deve funcionar no frontend agora")
    else:
        print("\n❌ PROBLEMAS NA INTEGRAÇÃO")
        print("⚠️ Verificar logs do servidor para mais detalhes")
