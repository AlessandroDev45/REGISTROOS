#!/usr/bin/env python3
"""
Teste para verificar se supervisor vê programações criadas no PCP
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def main():
    print("🎯 TESTE: SUPERVISOR VÊ PROGRAMAÇÕES DO PCP")
    print("=" * 60)
    
    # Criar sessão
    session = requests.Session()
    
    # 1. Fazer login como admin (para criar programação)
    print("1. Fazendo login como admin...")
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/api/login", json=login_data)
        if login_response.status_code == 200:
            print("   ✅ Login admin realizado com sucesso")
            user_data = login_response.json()
            print(f"   👤 Usuário: {user_data.get('nome_completo', 'N/A')}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Criar programação no PCP para setor específico
    print("\n2. 🏭 Criando programação no PCP...")
    programacao_data = {
        "os_numero": "000012345",
        "inicio_previsto": "2025-09-26T14:00:00",
        "fim_previsto": "2025-09-26T16:00:00",
        "id_departamento": 1,
        "id_setor": 42,  # Setor específico
        "responsavel_id": 1,  # ID do usuário logado (admin)
        "observacoes": "Programação criada via PCP para teste",
        "status": "PROGRAMADA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=programacao_data)
        
        if response.status_code in [200, 201]:
            data = response.json()
            programacao_id = data.get('id')
            print(f"   ✅ Programação criada no PCP! ID: {programacao_id}")
            print(f"   📊 Setor: {programacao_data['id_setor']}")
            print(f"   👤 Responsável: {programacao_data['responsavel_id']}")
        else:
            print(f"   ❌ Erro ao criar programação: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
        return
    
    # 3. Verificar se aparece no desenvolvimento
    print("\n3. 🔧 Verificando no desenvolvimento...")
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/programacao")
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Desenvolvimento: {len(data)} programações retornadas")
            
            # Procurar a programação criada
            programacao_encontrada = False
            for prog in data:
                if prog.get('os_numero') == '000012345':
                    programacao_encontrada = True
                    print(f"   🎯 ENCONTRADA! OS: {prog.get('os_numero')} | Responsável: {prog.get('responsavel_nome')} | Setor: {prog.get('id_setor')}")
                    break
            
            if not programacao_encontrada:
                print("   ❌ PROGRAMAÇÃO NÃO ENCONTRADA NO DESENVOLVIMENTO!")
                print("   📊 Programações disponíveis:")
                for i, prog in enumerate(data[:3]):
                    print(f"      {i+1}. OS: {prog.get('os_numero', 'N/A')} | Setor: {prog.get('id_setor', 'N/A')}")
            else:
                print("   ✅ SUCESSO! Programação do PCP aparece no desenvolvimento!")
                
        else:
            print(f"   ❌ Erro: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # 4. Testar criação de apontamento
    print("\n4. 📝 Testando criação de apontamento...")
    apontamento_data = {
        "numero_os": "000012345",  # Campo correto
        "os_numero": "000012345",
        "usuario_id": 1,
        "cliente": "CLIENTE TESTE",  # Campo obrigatório
        "equipamento": "MOTOR TESTE",  # Campo obrigatório
        "tipo_maquina": "MOTOR ELETRICO",
        "tipo_atividade": "DESMONTAGEM",
        "descricao_atividade": "Teste de apontamento",
        "observacoes": "Teste via API",
        "hora_inicio": "14:00",
        "hora_fim": "15:00",
        "data_inicio": "2025-09-26T14:00:00",  # Campo obrigatório
        "data_apontamento": "2025-09-26",
        "setor": "LABORATORIO DE ENSAIOS ELETRICOS",
        "departamento": "MOTORES"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/desenvolvimento/os/apontamentos", json=apontamento_data)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ Apontamento criado com sucesso!")
            print(f"   📊 ID: {data.get('id', 'N/A')}")
        else:
            print(f"   ❌ Erro ao criar apontamento: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
