#!/usr/bin/env python3
"""
Teste direto para criar departamento via API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_login_and_create_department():
    """Testa login e criação de departamento"""
    print("🔐 TESTANDO LOGIN E CRIAÇÃO DE DEPARTAMENTO")
    print("=" * 60)
    
    # 1. Fazer login
    print("1. Fazendo login...")
    login_data = {
        "username": "ADMINISTRADOR",
        "password": "admin123"
    }
    
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"Status login: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.text}")
        return
    
    print("✅ Login realizado com sucesso!")
    
    # 2. Verificar se está autenticado
    print("\n2. Verificando autenticação...")
    response = session.get(f"{BASE_URL}/me")
    print(f"Status /me: {response.status_code}")
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Usuário autenticado: {user_data.get('nome')} - {user_data.get('privilege_level')}")
    else:
        print(f"❌ Erro na verificação: {response.text}")
        return
    
    # 3. Criar departamento
    print("\n3. Criando departamento...")
    dept_data = {
        "nome_tipo": "TESTE_FRONTEND",
        "nome": "TESTE_FRONTEND",
        "descricao": "Departamento criado via teste frontend",
        "ativo": True
    }
    
    response = session.post(f"{BASE_URL}/admin/departamentos", json=dept_data)
    print(f"Status criação: {response.status_code}")
    
    if response.status_code == 200:
        created_dept = response.json()
        print(f"✅ Departamento criado: {json.dumps(created_dept, indent=2, ensure_ascii=False)}")
        
        # 4. Listar departamentos para confirmar
        print("\n4. Listando departamentos...")
        response = session.get(f"{BASE_URL}/admin/departamentos")
        if response.status_code == 200:
            depts = response.json()
            print(f"✅ Total de departamentos: {len(depts)}")
            for dept in depts:
                if dept.get('nome_tipo') == 'TESTE_FRONTEND':
                    print(f"🎯 Departamento encontrado: {dept}")
        
        return created_dept.get('id')
    else:
        print(f"❌ Erro na criação: {response.text}")
        return None

def cleanup_test_department(dept_id):
    """Remove o departamento de teste"""
    if not dept_id:
        return
    
    print(f"\n🧹 Removendo departamento de teste (ID: {dept_id})...")
    session = requests.Session()
    
    # Login novamente
    login_data = {"username": "ADMINISTRADOR", "password": "admin123"}
    session.post(f"{BASE_URL}/login", data=login_data)
    
    # Deletar
    response = session.delete(f"{BASE_URL}/admin/departamentos/{dept_id}")
    print(f"Status remoção: {response.status_code}")

def main():
    try:
        dept_id = test_login_and_create_department()
        
        print("\n" + "=" * 60)
        print("🏁 TESTE CONCLUÍDO!")
        
        # Cleanup
        if dept_id:
            cleanup_test_department(dept_id)
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    main()
