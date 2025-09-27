#!/usr/bin/env python3
"""
Teste de atribuição usando setores reais do banco
"""

import requests
import json

def testar_com_setores_reais():
    """Testa atribuição com setores reais"""
    
    print("🧪 TESTE: Atribuição com Setores Reais")
    print("=" * 50)
    
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
        
        if response.status_code != 200:
            print("❌ Não foi possível fazer login.")
            return
        
        print("   ✅ Login realizado!")
        
        # 2. Buscar setores reais
        print("\n2️⃣ Buscando setores reais...")
        response = session.get(f"{base_url}/api/admin/setores", timeout=10)
        
        if response.status_code != 200:
            print("❌ Erro ao buscar setores")
            return
            
        setores = response.json()
        print(f"   ✅ {len(setores)} setores encontrados")
        
        # Usar o primeiro setor como teste
        setor_teste = setores[0]
        print(f"   🎯 Usando: {setor_teste['nome']} - {setor_teste['departamento']}")
        
        # 3. Buscar colaboradores
        response = session.get(f"{base_url}/api/desenvolvimento/colaboradores", timeout=10)
        
        if response.status_code != 200:
            print("❌ Erro ao buscar colaboradores")
            return
            
        colaboradores = response.json()
        colaborador_teste = colaboradores[0] if colaboradores else {"id": 5}
        print(f"   👤 Colaborador: {colaborador_teste.get('nome_completo', 'ID 5')} (ID: {colaborador_teste['id']})")
        
        # 4. Testar atribuição
        print("\n3️⃣ Testando atribuição...")
        dados_atribuicao = {
            "responsavel_id": colaborador_teste["id"],
            "setor_destino": setor_teste["nome"],
            "departamento_destino": setor_teste["departamento"],
            "data_inicio": "2024-01-15T08:00:00",
            "data_fim": "2024-01-15T17:00:00",
            "prioridade": "NORMAL",
            "observacoes": "Teste com setores reais"
        }
        
        print(f"   📋 Dados: {setor_teste['nome']} / {setor_teste['departamento']}")
        
        response = session.post(
            f"{base_url}/api/pcp/programacoes/atribuir", 
            json=dados_atribuicao, 
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ SUCESSO! Atribuição funcionando!")
            data = response.json()
            programacao_id = data.get('id')
            print(f"   📋 Programação criada: ID {programacao_id}")
            
            # 5. Testar reatribuição
            if programacao_id:
                print(f"\n4️⃣ Testando reatribuição...")
                dados_reatribuicao = {
                    "responsavel_id": colaborador_teste["id"],
                    "setor_destino": setor_teste["nome"],
                    "departamento_destino": setor_teste["departamento"],
                    "data_inicio": "2024-01-16T08:00:00",
                    "data_fim": "2024-01-16T17:00:00",
                    "prioridade": "ALTA",
                    "observacoes": "Teste de reatribuição"
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
                    print(f"   ❌ Erro na reatribuição: {response.text[:200]}")
                    
                # 6. Testar edição
                print(f"\n5️⃣ Testando edição...")
                dados_edicao = {
                    "responsavel_id": colaborador_teste["id"],
                    "setor_destino": setor_teste["nome"],
                    "departamento_destino": setor_teste["departamento"],
                    "data_inicio": "2024-01-17T08:00:00",
                    "data_fim": "2024-01-17T17:00:00",
                    "prioridade": "BAIXA",
                    "observacoes": "Teste de edição"
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
                    print(f"   ✏️ Editado: {data.get('message', 'N/A')}")
                else:
                    print(f"   ❌ Erro na edição: {response.text[:200]}")
            
        elif response.status_code == 422:
            print("   ⚠️ Erro de validação:")
            try:
                error_data = response.json()
                print(f"   📄 {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📄 {response.text}")
        else:
            print(f"   ❌ Erro: {response.text[:200]}")
    
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    testar_com_setores_reais()
