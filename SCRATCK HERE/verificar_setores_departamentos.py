#!/usr/bin/env python3
"""
Verificar setores e departamentos disponíveis no banco
"""

import requests
import json

def verificar_setores_departamentos():
    """Verifica setores e departamentos disponíveis"""
    
    print("🧪 VERIFICAÇÃO: Setores e Departamentos Disponíveis")
    print("=" * 60)
    
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
            print("❌ Não foi possível fazer login. Abortando verificação.")
            return
        
        print("   ✅ Login realizado com sucesso!")
        
        # 2. Verificar setores disponíveis
        print("\n2️⃣ Verificando setores...")
        endpoints_setores = [
            "/api/admin/setores",
            "/api/setores",
            "/api/desenvolvimento/admin/setores",
            "/api/pcp/programacao-form-data"
        ]
        
        for endpoint in endpoints_setores:
            try:
                print(f"\n   🔗 Testando: {endpoint}")
                response = session.get(f"{base_url}{endpoint}", timeout=10)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if isinstance(data, list):
                            print(f"      ✅ {len(data)} itens encontrados")
                            for i, item in enumerate(data[:3], 1):
                                if isinstance(item, dict):
                                    nome = item.get('nome', item.get('setor', 'N/A'))
                                    dept = item.get('departamento', 'N/A')
                                    print(f"         {i}. {nome} - Dept: {dept}")
                        elif isinstance(data, dict):
                            setores = data.get('setores', [])
                            departamentos = data.get('departamentos', [])
                            print(f"      ✅ Setores: {len(setores)}, Departamentos: {len(departamentos)}")
                            
                            if setores:
                                print("      📋 Setores encontrados:")
                                for i, setor in enumerate(setores[:5], 1):
                                    if isinstance(setor, dict):
                                        nome = setor.get('nome', 'N/A')
                                        dept = setor.get('departamento', 'N/A')
                                        print(f"         {i}. {nome} - Dept: {dept}")
                            
                            if departamentos:
                                print("      🏢 Departamentos encontrados:")
                                for i, dept in enumerate(departamentos[:5], 1):
                                    if isinstance(dept, dict):
                                        nome = dept.get('nome', 'N/A')
                                        print(f"         {i}. {nome}")
                                    else:
                                        print(f"         {i}. {dept}")
                        
                    except json.JSONDecodeError:
                        print(f"      ⚠️ Resposta não é JSON: {response.text[:100]}")
                        
                elif response.status_code == 404:
                    print(f"      ❌ Endpoint não encontrado")
                else:
                    print(f"      ❌ Erro: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Erro: {e}")
        
        # 3. Verificar dados do usuário atual
        print("\n3️⃣ Verificando dados do usuário atual...")
        try:
            response = session.get(f"{base_url}/api/users/me", timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                print("   ✅ Dados do usuário:")
                print(f"      👤 Nome: {user_data.get('nome_completo', 'N/A')}")
                print(f"      🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
                print(f"      📧 Email: {user_data.get('email', 'N/A')}")
                print(f"      🎯 Privilégio: {user_data.get('privilege_level', 'N/A')}")
                
                # Tentar buscar informações do setor do usuário
                setor_id = user_data.get('id_setor')
                if setor_id:
                    print(f"\n   🔍 Buscando informações do setor ID {setor_id}...")
                    try:
                        response = session.get(f"{base_url}/api/admin/setores/{setor_id}", timeout=10)
                        if response.status_code == 200:
                            setor_data = response.json()
                            print(f"      ✅ Setor: {setor_data.get('nome', 'N/A')}")
                            print(f"      🏢 Departamento: {setor_data.get('departamento', 'N/A')}")
                        else:
                            print(f"      ❌ Erro ao buscar setor: {response.status_code}")
                    except Exception as e:
                        print(f"      ❌ Erro: {e}")
                        
            else:
                print(f"   ❌ Erro ao buscar dados do usuário: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 4. Testar com dados corretos
        print("\n4️⃣ Testando atribuição com dados genéricos...")
        try:
            dados_teste = {
                "responsavel_id": 5,  # ID do colaborador encontrado
                "setor_destino": "PRODUCAO",  # Tentar nome genérico
                "departamento_destino": "MOTORES",  # Tentar departamento genérico
                "data_inicio": "2024-01-15T08:00:00",
                "data_fim": "2024-01-15T17:00:00",
                "prioridade": "NORMAL",
                "observacoes": "Teste com dados genéricos"
            }
            
            response = session.post(
                f"{base_url}/api/pcp/programacoes/atribuir", 
                json=dados_teste, 
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Funcionou com dados genéricos!")
                data = response.json()
                print(f"   📋 ID criado: {data.get('id', 'N/A')}")
            else:
                print(f"   ❌ Ainda com erro: {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICAÇÃO CONCLUÍDA")

if __name__ == "__main__":
    verificar_setores_departamentos()
