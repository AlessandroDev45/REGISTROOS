#!/usr/bin/env python3
"""
Teste final para verificar se programação do PCP aparece no desenvolvimento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE FINAL: PROGRAMAÇÃO PCP → DESENVOLVIMENTO")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            user_data = login_response.json().get('user', {})
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
            user_id = user_data.get('id')
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Criar programação no PCP com responsável = usuário logado
    print("\n2. 🏭 Criando programação no PCP...")
    programacao_data = {
        "os_numero": "000012345",
        "inicio_previsto": "2025-09-26T20:00:00",
        "fim_previsto": "2025-09-26T22:00:00",
        "id_departamento": 1,
        "id_setor": 42,
        "responsavel_id": user_id,  # Usuário logado como responsável
        "observacoes": "TESTE FINAL - Deve aparecer no desenvolvimento",
        "status": "PROGRAMADA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=programacao_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            programacao_id = data.get('id')
            print(f"   ✅ Programação criada! ID: {programacao_id}")
            print(f"   📊 Responsável: {user_id} (usuário logado)")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # 3. Verificar se aparece no desenvolvimento
    print("\n3. 🔧 Verificando no desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Desenvolvimento: {len(data)} programações")
            
            # Procurar a programação criada
            encontrada = False
            for prog in data:
                if prog.get('id') == programacao_id:
                    encontrada = True
                    print(f"   🎯 ENCONTRADA! ID: {prog.get('id')} | OS: {prog.get('os_numero')}")
                    print(f"      Responsável: {prog.get('responsavel_nome')} | Setor: {prog.get('id_setor')}")
                    break
            
            if not encontrada:
                print(f"   ❌ PROGRAMAÇÃO ID {programacao_id} NÃO ENCONTRADA!")
                print("   📊 Programações disponíveis:")
                for prog in data:
                    print(f"      ID: {prog.get('id')} | Responsável: {prog.get('responsavel_id')} | Setor: {prog.get('id_setor')}")
            else:
                print("   ✅ SUCESSO! Programação do PCP aparece no desenvolvimento!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Verificar query SQL diretamente
    print("\n4. 🔍 Debug da query SQL...")
    print(f"   Filtro aplicado: (p.id_setor = {user_data.get('id_setor')} OR p.responsavel_id = {user_id})")
    
    if user_data.get('id_setor') is None:
        print(f"   ⚠️ Usuário não tem setor definido, então só vê programações onde é responsável")
    else:
        print(f"   ✅ Usuário tem setor {user_data.get('id_setor')}, vê programações do setor OU onde é responsável")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
