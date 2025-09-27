#!/usr/bin/env python3
"""
Script para simular exatamente o que o frontend faz
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("🎭 SIMULANDO COMPORTAMENTO DO FRONTEND")
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
    
    # 2. Simular getProgramacaoFormData()
    print("\n2. 📡 Simulando getProgramacaoFormData()...")
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacao-form-data")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            print("   ✅ Dados recebidos com sucesso")
            
            # Simular verificação do frontend
            print("\n3. 🔍 Verificando formato dos dados (como o frontend faz)...")
            
            if dados and isinstance(dados, dict):
                print("   ✅ dados é um objeto válido")
                
                # Verificar cada campo
                ordens_servico = dados.get('ordens_servico', [])
                usuarios = dados.get('usuarios', [])
                setores = dados.get('setores', [])
                departamentos = dados.get('departamentos', [])
                
                print(f"   📊 ordens_servico: {type(ordens_servico)} com {len(ordens_servico) if isinstance(ordens_servico, list) else 'N/A'} itens")
                print(f"   👥 usuarios: {type(usuarios)} com {len(usuarios) if isinstance(usuarios, list) else 'N/A'} itens")
                print(f"   🏭 setores: {type(setores)} com {len(setores) if isinstance(setores, list) else 'N/A'} itens")
                print(f"   🏢 departamentos: {type(departamentos)} com {len(departamentos) if isinstance(departamentos, list) else 'N/A'} itens")
                
                # Simular setFormData do frontend
                print("\n4. 🎯 Simulando setFormData do frontend...")
                formData = {
                    'ordens_servico': ordens_servico if isinstance(ordens_servico, list) else [],
                    'usuarios': usuarios if isinstance(usuarios, list) else [],
                    'setores': setores if isinstance(setores, list) else [],
                    'departamentos': departamentos if isinstance(departamentos, list) else [],
                    'status_opcoes': ['PROGRAMADA', 'EM_ANDAMENTO', 'ENVIADA', 'CONCLUIDA', 'CANCELADA']
                }
                
                print(f"   ✅ FormData criado:")
                print(f"      - OS: {len(formData['ordens_servico'])}")
                print(f"      - Usuários: {len(formData['usuarios'])}")
                print(f"      - Setores: {len(formData['setores'])}")
                print(f"      - Departamentos: {len(formData['departamentos'])}")
                
                # Mostrar estrutura dos setores
                print("\n5. 🏭 ESTRUTURA DOS SETORES (primeiros 5):")
                for i, setor in enumerate(formData['setores'][:5]):
                    print(f"   {i+1}. {setor}")
                
                # Mostrar estrutura dos departamentos
                print("\n6. 🏢 ESTRUTURA DOS DEPARTAMENTOS:")
                for i, dept in enumerate(formData['departamentos']):
                    print(f"   {i+1}. {dept}")
                
                # Simular filtro de setores por departamento (como no frontend)
                print("\n7. 🔍 SIMULANDO FILTRO DE SETORES POR DEPARTAMENTO:")
                if len(formData['departamentos']) > 0:
                    primeiro_dept_id = formData['departamentos'][0]['id']
                    print(f"   Filtrando setores para departamento ID: {primeiro_dept_id}")
                    
                    setores_filtrados = [
                        setor for setor in formData['setores'] 
                        if setor.get('id_departamento') == primeiro_dept_id
                    ]
                    
                    print(f"   📊 Setores filtrados: {len(setores_filtrados)}")
                    for i, setor in enumerate(setores_filtrados[:5]):
                        nome = setor.get('nome', 'N/A')
                        dept_nome = setor.get('departamento_nome', 'N/A')
                        print(f"   {i+1}. {nome} ({dept_nome})")
                
            else:
                print("   ❌ dados não é um objeto válido")
                
        else:
            print(f"   ❌ Erro na resposta: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 SIMULAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main()
