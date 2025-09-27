#!/usr/bin/env python3
"""
Teste com responsável correto (ID 3) para ver se aparece no desenvolvimento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE COM RESPONSÁVEL CORRETO")
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
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Verificar programações existentes no desenvolvimento
    print("\n2. 🔧 Verificando programações no desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Desenvolvimento: {len(data)} programações")
            
            if data:
                print("   📊 Programações encontradas:")
                for prog in data:
                    print(f"      ID: {prog.get('id')} | OS: {prog.get('os_numero')} | Responsável: {prog.get('responsavel_id')} | Setor: {prog.get('id_setor')}")
            else:
                print("   ❌ Nenhuma programação encontrada!")
                print("   🔍 Isso significa que o filtro está muito restritivo")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Criar programação com admin como responsável
    print("\n3. 🏭 Criando programação com admin como responsável...")
    programacao_data = {
        "os_numero": "000012345",
        "inicio_previsto": "2025-09-27T08:00:00",
        "fim_previsto": "2025-09-27T10:00:00",
        "id_departamento": 1,
        "id_setor": 42,
        "responsavel_id": 1,  # Admin como responsável
        "observacoes": "TESTE - Admin como responsável",
        "status": "PROGRAMADA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=programacao_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            programacao_id = data.get('id')
            print(f"   ✅ Programação criada! ID: {programacao_id}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Verificar novamente no desenvolvimento
    print("\n4. 🔧 Verificando novamente no desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Desenvolvimento: {len(data)} programações")
            
            if data:
                print("   📊 Programações encontradas:")
                for prog in data:
                    print(f"      ID: {prog.get('id')} | OS: {prog.get('os_numero')} | Responsável: {prog.get('responsavel_id')} | Setor: {prog.get('id_setor')}")
                    
                # Procurar a nova programação
                nova_encontrada = any(prog.get('id') == programacao_id for prog in data)
                if nova_encontrada:
                    print(f"   ✅ SUCESSO! Nova programação ID {programacao_id} aparece no desenvolvimento!")
                else:
                    print(f"   ❌ Nova programação ID {programacao_id} NÃO aparece!")
            else:
                print("   ❌ Ainda nenhuma programação encontrada!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")
    print("\n💡 EXPLICAÇÃO:")
    print("   - Usuário admin (ID 1) tem setor 42")
    print("   - Programações existentes têm responsável_id = 3")
    print("   - Filtro: (setor = 42 OR responsável = 1)")
    print("   - Deveria mostrar programações do setor 42!")

if __name__ == "__main__":
    main()
