#!/usr/bin/env python3
"""
🧪 TESTE: Frontend Dashboard
Testa se o frontend está carregando os dados corretamente
"""

import requests
import json

def testar_frontend():
    base_url = "http://localhost:8000"
    
    print("🧪 TESTE: Frontend Dashboard")
    print("=" * 60)
    
    # 1. Fazer login primeiro
    print("\n1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/token", data=login_data)
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
            
            # Extrair cookies da resposta
            cookies = login_response.cookies
            
            # 2. Testar endpoint de apontamentos detalhados
            print("\n2. Testando endpoint /api/apontamentos-detalhados...")
            apontamentos_response = requests.get(
                f"{base_url}/api/apontamentos-detalhados",
                cookies=cookies
            )
            
            print(f"   Status Code: {apontamentos_response.status_code}")
            
            if apontamentos_response.status_code == 200:
                apontamentos = apontamentos_response.json()
                print(f"   ✅ Endpoint funcionando! Retornou {len(apontamentos)} apontamentos")
                
                if apontamentos:
                    print("\n📋 Verificando campos necessários para o frontend:")
                    primeiro_apontamento = apontamentos[0]
                    
                    campos_necessarios = [
                        'id', 'numero_os', 'tipo_atividade', 'usuario', 'nome_tecnico',
                        'data_inicio', 'data_hora_inicio', 'setor', 'tempo_trabalhado',
                        'aprovado_supervisor', 'status'
                    ]
                    
                    for campo in campos_necessarios:
                        valor = primeiro_apontamento.get(campo, 'AUSENTE')
                        status = "✅" if campo in primeiro_apontamento else "❌"
                        print(f"   {status} {campo}: {valor}")
                    
                    print(f"\n📊 Exemplo completo do primeiro apontamento:")
                    print(json.dumps(primeiro_apontamento, indent=2, ensure_ascii=False))
                    
                else:
                    print("   ⚠️ Nenhum apontamento encontrado no banco de dados")
                    
            else:
                print(f"   ❌ Erro no endpoint: {apontamentos_response.status_code}")
                print(f"   Resposta: {apontamentos_response.text}")
        
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"   1. Acesse o frontend: http://localhost:3001")
    print(f"   2. Faça login com admin@registroos.com / 123456")
    print(f"   3. Navegue para Desenvolvimento")
    print(f"   4. Verifique se o Dashboard carrega sem erros")

if __name__ == "__main__":
    testar_frontend()
