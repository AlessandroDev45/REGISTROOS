#!/usr/bin/env python3
"""
Debug colaboradores e pendências
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 DEBUG: COLABORADORES E PENDÊNCIAS")
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
    
    # 2. Testar colaboradores
    print("\n2. 👥 COLABORADORES:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/colaboradores")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} colaboradores")
            
            if data:
                for i, colab in enumerate(data, 1):
                    nome = colab.get('nome_completo', 'N/A')
                    setor = colab.get('setor', 'N/A')
                    privilege = colab.get('privilege_level', 'N/A')
                    print(f"      {i}. {nome} | Setor: {setor} | Nível: {privilege}")
            else:
                print("   ❌ Lista vazia!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar usuários gerais
    print("\n3. 👤 USUÁRIOS GERAIS:")
    try:
        response = session.get(f"{BASE_URL}/api/usuarios")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} usuários")
            
            if data:
                setor_42_users = [u for u in data if u.get('id_setor') == 42]
                print(f"   🏢 Usuários do setor 42: {len(setor_42_users)}")
                
                for i, user in enumerate(setor_42_users, 1):
                    nome = user.get('nome_completo', 'N/A')
                    ativo = user.get('ativo', False)
                    privilege = user.get('privilege_level', 'N/A')
                    print(f"      {i}. {nome} | Ativo: {ativo} | Nível: {privilege}")
            else:
                print("   ❌ Lista vazia!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Testar pendências PCP com debug
    print("\n4. 🏭 PENDÊNCIAS PCP (com debug):")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/pendencias")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} pendências")
            
            if data:
                for i, pend in enumerate(data, 1):
                    os_numero = pend.get('numero_os', 'N/A')
                    responsavel = pend.get('responsavel_nome', 'N/A')
                    status = pend.get('status', 'N/A')
                    print(f"      {i}. OS: {os_numero} | Responsável: {responsavel} | Status: {status}")
            else:
                print("   ❌ Lista vazia!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 5. Testar pendências desenvolvimento
    print("\n5. 🔧 PENDÊNCIAS DESENVOLVIMENTO:")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/pendencias")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total: {len(data)} pendências")
            
            if data:
                for i, pend in enumerate(data, 1):
                    os_numero = pend.get('numero_os', 'N/A')
                    responsavel = pend.get('responsavel_nome', 'N/A')
                    status = pend.get('status', 'N/A')
                    print(f"      {i}. OS: {os_numero} | Responsável: {responsavel} | Status: {status}")
            else:
                print("   ❌ Lista vazia!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()
