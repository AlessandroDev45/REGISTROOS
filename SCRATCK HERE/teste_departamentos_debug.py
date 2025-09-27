#!/usr/bin/env python3
"""
Script para debugar a consulta de departamentos
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🔍 DEBUG: TESTANDO CONSULTA DE DEPARTAMENTOS")
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
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return
    
    # 2. Testar endpoint direto de departamentos (se existir)
    print("\n2. Testando endpoint de departamentos...")
    try:
        response = session.get(f"{BASE_URL}/api/admin/departamentos")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Departamentos encontrados: {len(data)}")
            for i, dept in enumerate(data[:5]):
                print(f"   {i+1}. ID: {dept.get('id', 'N/A')} - Nome: {dept.get('nome_tipo', dept.get('nome', 'N/A'))}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 3. Testar endpoint de setores para ver departamentos
    print("\n3. Testando endpoint de setores...")
    try:
        response = session.get(f"{BASE_URL}/api/admin/setores")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Setores encontrados: {len(data)}")
            
            # Extrair departamentos únicos dos setores
            departamentos_setores = set()
            for setor in data[:10]:
                dept = setor.get('departamento', setor.get('departamento_nome', 'N/A'))
                if dept and dept != 'N/A':
                    departamentos_setores.add(dept)
            
            print(f"   📊 Departamentos únicos nos setores: {list(departamentos_setores)}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 4. Testar novamente o endpoint do PCP
    print("\n4. Re-testando /api/pcp/programacao-form-data...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        if response.status_code == 200:
            data = response.json()
            departamentos = data.get('departamentos', [])
            print(f"   📊 Departamentos retornados: {len(departamentos)}")
            
            if len(departamentos) > 0:
                print("   🏭 DEPARTAMENTOS DETALHADOS:")
                for i, dept in enumerate(departamentos):
                    print(f"   {i+1}. {dept}")
            else:
                print("   ⚠️ NENHUM DEPARTAMENTO RETORNADO!")
                
                # Verificar se há erro
                if 'erro' in data:
                    print(f"   ❌ Erro reportado: {data['erro']}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG CONCLUÍDO!")

if __name__ == "__main__":
    main()
