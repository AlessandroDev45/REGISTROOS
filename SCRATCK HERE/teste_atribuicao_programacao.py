#!/usr/bin/env python3
"""
Teste específico para verificar se os endpoints de atribuição de programação funcionam
"""

import requests
import json

def testar_atribuicao_programacao():
    """Testa os endpoints de atribuição de programação"""
    
    print("🧪 TESTE: Endpoints de Atribuição de Programação")
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
        
        # 2. Buscar colaboradores para usar no teste
        print("\n2️⃣ Buscando colaboradores...")
        try:
            response = session.get(f"{base_url}/api/desenvolvimento/colaboradores", timeout=10)
            
            if response.status_code == 200:
                colaboradores = response.json()
                print(f"   ✅ {len(colaboradores)} colaboradores encontrados")
                
                if len(colaboradores) > 0:
                    colaborador_teste = colaboradores[0]
                    print(f"   👤 Usando colaborador: {colaborador_teste['nome_completo']} (ID: {colaborador_teste['id']})")
                else:
                    print("   ❌ Nenhum colaborador encontrado. Usando ID 1 como teste.")
                    colaborador_teste = {"id": 1, "nome_completo": "Teste"}
            else:
                print(f"   ❌ Erro ao buscar colaboradores: {response.status_code}")
                colaborador_teste = {"id": 1, "nome_completo": "Teste"}
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            colaborador_teste = {"id": 1, "nome_completo": "Teste"}
        
        # 3. Testar POST /api/pcp/programacoes/atribuir
        print("\n3️⃣ Testando POST /api/pcp/programacoes/atribuir...")
        try:
            dados_atribuicao = {
                "responsavel_id": colaborador_teste["id"],
                "setor_destino": "PCP",
                "departamento_destino": "PCP",
                "data_inicio": "2024-01-15T08:00:00",
                "data_fim": "2024-01-15T17:00:00",
                "prioridade": "NORMAL",
                "observacoes": "Teste de atribuição via API"
            }
            
            response = session.post(
                f"{base_url}/api/pcp/programacoes/atribuir", 
                json=dados_atribuicao, 
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Atribuição funcionando!")
                data = response.json()
                programacao_id = data.get('id')
                print(f"   📋 Programação criada com ID: {programacao_id}")
                
                # 4. Testar PATCH reatribuir se a criação funcionou
                if programacao_id:
                    print(f"\n4️⃣ Testando PATCH /api/pcp/programacoes/{programacao_id}/reatribuir...")
                    try:
                        dados_reatribuicao = {
                            "responsavel_id": colaborador_teste["id"],
                            "setor_destino": "PCP",
                            "departamento_destino": "PCP",
                            "data_inicio": "2024-01-16T08:00:00",
                            "data_fim": "2024-01-16T17:00:00",
                            "prioridade": "ALTA",
                            "observacoes": "Teste de reatribuição via API"
                        }
                        
                        response = session.patch(
                            f"{base_url}/api/pcp/programacoes/{programacao_id}/reatribuir", 
                            json=dados_reatribuicao, 
                            timeout=10
                        )
                        
                        print(f"   Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print("   ✅ Reatribuição funcionando!")
                            data = response.json()
                            print(f"   🔄 Reatribuído para: {data.get('novo_responsavel_nome', 'N/A')}")
                        else:
                            print(f"   ❌ Erro na reatribuição: {response.status_code}")
                            print(f"   📄 Resposta: {response.text[:300]}")
                            
                    except Exception as e:
                        print(f"   ❌ Erro: {e}")
                    
                    # 5. Testar PUT editar
                    print(f"\n5️⃣ Testando PUT /api/pcp/programacoes/{programacao_id}...")
                    try:
                        dados_edicao = {
                            "responsavel_id": colaborador_teste["id"],
                            "setor_destino": "PCP",
                            "departamento_destino": "PCP",
                            "data_inicio": "2024-01-17T08:00:00",
                            "data_fim": "2024-01-17T17:00:00",
                            "prioridade": "BAIXA",
                            "observacoes": "Teste de edição via API"
                        }
                        
                        response = session.put(
                            f"{base_url}/api/pcp/programacoes/{programacao_id}", 
                            json=dados_edicao, 
                            timeout=10
                        )
                        
                        print(f"   Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            print("   ✅ Edição funcionando!")
                            data = response.json()
                            print(f"   ✏️ Programação editada: {data.get('message', 'N/A')}")
                        else:
                            print(f"   ❌ Erro na edição: {response.status_code}")
                            print(f"   📄 Resposta: {response.text[:300]}")
                            
                    except Exception as e:
                        print(f"   ❌ Erro: {e}")
                
            elif response.status_code == 422:
                print("   ⚠️ Erro de validação (422)")
                try:
                    error_data = response.json()
                    print(f"   📄 Detalhes: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   📄 Resposta: {response.text[:300]}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   📄 Resposta: {response.text[:300]}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    except Exception as e:
        print(f"\n❌ Erro geral no teste: {e}")
    
    print("\n" + "=" * 70)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_atribuicao_programacao()
