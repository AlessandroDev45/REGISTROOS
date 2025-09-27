#!/usr/bin/env python3
"""
Debug para entender por que programação não aparece no desenvolvimento
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 DEBUG: PROGRAMAÇÃO NO DESENVOLVIMENTO")
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
            user_data = login_response.json()
            print(f"   ✅ Login: {user_data.get('nome_completo', 'N/A')}")
            print(f"   👤 ID: {user_data.get('id', 'N/A')}")
            print(f"   🏢 Setor ID: {user_data.get('id_setor', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Verificar programações no PCP
    print("\n2. 🏭 Programações no PCP...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ PCP: {len(data)} programações")
            
            for i, prog in enumerate(data):
                print(f"   {i+1}. ID: {prog.get('id')} | OS: {prog.get('os_numero')} | Responsável: {prog.get('responsavel_id')} | Setor: {prog.get('id_setor')}")
        else:
            print(f"   ❌ Erro PCP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Verificar programações no desenvolvimento
    print("\n3. 🔧 Programações no desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Desenvolvimento: {len(data)} programações")
            
            for i, prog in enumerate(data):
                print(f"   {i+1}. ID: {prog.get('id')} | OS: {prog.get('os_numero')} | Responsável: {prog.get('responsavel_id')} | Setor: {prog.get('id_setor')}")
        else:
            print(f"   ❌ Erro desenvolvimento: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Verificar tabela programacao_pcp diretamente
    print("\n4. 📊 Verificando tabela programacao_pcp...")
    try:
        # Fazer uma query SQL direta via endpoint de debug (se existir)
        # Ou criar programação específica para teste
        
        programacao_teste = {
            "os_numero": "000099999",
            "inicio_previsto": "2025-09-26T16:00:00",
            "fim_previsto": "2025-09-26T18:00:00",
            "id_departamento": 1,
            "id_setor": None,  # Sem setor específico
            "responsavel_id": 1,  # Admin como responsável
            "observacoes": "Teste debug - sem setor",
            "status": "PROGRAMADA"
        }
        
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=programacao_teste)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ Programação teste criada: ID {data.get('id')}")
            
            # Verificar se aparece no desenvolvimento
            print("\n   🔍 Verificando se aparece no desenvolvimento...")
            dev_response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
            
            if dev_response.status_code == 200:
                dev_data = dev_response.json()
                
                encontrada = False
                for prog in dev_data:
                    if prog.get('os_numero') == '000099999':
                        encontrada = True
                        print(f"   ✅ ENCONTRADA! OS: {prog.get('os_numero')}")
                        break
                
                if not encontrada:
                    print(f"   ❌ NÃO ENCONTRADA! Total: {len(dev_data)} programações")
            
        else:
            print(f"   ❌ Erro ao criar teste: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()
