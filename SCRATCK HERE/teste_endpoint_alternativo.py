#!/usr/bin/env python3
"""
Teste para verificar endpoints alternativos para usuários pendentes
"""

import requests
import json

def testar_endpoints_alternativos():
    """Testa endpoints alternativos"""
    
    print("🧪 TESTE: Endpoints Alternativos para Usuários Pendentes")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Fazer login
    try:
        print("\n1️⃣ Fazendo login...")
        
        session = requests.Session()
        
        response = session.post(
            f"{base_url}/api/login", 
            json={"username": "user.pcp@registroos.com", "password": "123456"}, 
            timeout=10
        )
        
        print(f"   Status login: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Não foi possível fazer login. Abortando testes.")
            return
        
        print("   ✅ Login realizado com sucesso!")
        
        # 2. Testar diferentes endpoints
        endpoints_para_testar = [
            "/api/users/pending-approval",
            "/api/users/usuarios/pendentes/",
            "/api/admin/usuarios-pendentes",
            "/api/usuarios/pendentes/",  # Endpoint original que estava sendo chamado
        ]
        
        for i, endpoint in enumerate(endpoints_para_testar, 2):
            print(f"\n{i}️⃣ Testando {endpoint}...")
            try:
                response = session.get(f"{base_url}{endpoint}", timeout=10)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Endpoint funcionando!")
                    
                    try:
                        data = response.json()
                        print(f"   📊 Dados: {len(data)} itens")
                        
                        if len(data) > 0:
                            primeiro = data[0]
                            if isinstance(primeiro, dict):
                                nome = primeiro.get('nome_completo', primeiro.get('nome', 'N/A'))
                                print(f"   👤 Primeiro item: {nome}")
                        
                    except json.JSONDecodeError:
                        print("   ⚠️ Resposta não é JSON válido")
                        print(f"   Resposta: {response.text[:100]}")
                        
                elif response.status_code == 404:
                    print("   ❌ Endpoint não encontrado (404)")
                elif response.status_code == 403:
                    print("   ❌ Acesso negado (403)")
                elif response.status_code == 401:
                    print("   ❌ Não autorizado (401)")
                elif response.status_code == 500:
                    print("   ❌ Erro interno do servidor (500)")
                    print(f"   Resposta: {response.text[:200]}")
                else:
                    print(f"   ⚠️ Status inesperado: {response.status_code}")
                    print(f"   Resposta: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {e}")
    
    except Exception as e:
        print(f"\n❌ Erro geral no teste: {e}")
    
    print("\n" + "=" * 70)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_endpoints_alternativos()
