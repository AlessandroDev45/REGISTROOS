#!/usr/bin/env python3
import requests
import json

def testar_apontamentos():
    base_url = "http://localhost:8000"
    
    # 1. Fazer login
    login_data = {
        "username": "ADMIN",
        "password": "admin123"
    }

    try:
        print("🔐 Fazendo login...")
        login_response = requests.post(f"{base_url}/api/login", json=login_data)
        
        if login_response.status_code == 200:
            print(f"✅ Login realizado com sucesso!")

            # O token está no cookie, não precisamos extrair
            # Usar a sessão para manter os cookies
            session = requests.Session()
            session.post(f"{base_url}/api/login", json=login_data)

            # Headers básicos
            headers = {
                "Content-Type": "application/json"
            }
            
            # 2. Testar endpoint de apontamentos detalhados
            print("\n🔍 Testando endpoint /api/apontamentos-detalhados...")
            apontamentos_response = session.get(f"{base_url}/api/apontamentos-detalhados")
            
            if apontamentos_response.status_code == 200:
                apontamentos = apontamentos_response.json()
                print(f"✅ Endpoint funcionando! Retornou {len(apontamentos)} apontamentos")
                
                if apontamentos:
                    primeiro = apontamentos[0]
                    print(f"\n📋 Primeiro apontamento:")
                    print(f"  Número OS: {primeiro.get('numero_os', 'N/A')}")
                    print(f"  Setor: {primeiro.get('setor', 'N/A')}")
                    print(f"  Departamento: {primeiro.get('departamento', 'N/A')}")
                    print(f"  Técnico: {primeiro.get('nome_tecnico', 'N/A')}")
                    
                    # Verificar se os setores/departamentos estão corretos
                    setores_nao_informado = [apt for apt in apontamentos if apt.get('setor') == 'Não informado']
                    print(f"\n📊 Estatísticas:")
                    print(f"  Total de apontamentos: {len(apontamentos)}")
                    print(f"  Com setor 'Não informado': {len(setores_nao_informado)}")
                    print(f"  Com setor preenchido: {len(apontamentos) - len(setores_nao_informado)}")
                    
                else:
                    print("⚠️ Nenhum apontamento retornado")
                    
            else:
                print(f"❌ Erro no endpoint: {apontamentos_response.status_code}")
                print(f"Resposta: {apontamentos_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"Resposta: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_apontamentos()
