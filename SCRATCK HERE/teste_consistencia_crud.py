#!/usr/bin/env python3
"""
Teste de consistência entre backend e frontend para CRUD
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/admin"

def test_departamento_crud():
    """Testa CRUD de departamentos"""
    print("\n🏢 TESTANDO DEPARTAMENTOS")
    print("=" * 50)
    
    # 1. Listar departamentos
    print("1. Listando departamentos...")
    response = requests.get(f"{BASE_URL}/departamentos")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} departamentos encontrados")
        if data:
            print(f"Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Erro: {response.text}")
    
    # 2. Criar departamento
    print("\n2. Criando departamento...")
    novo_dept = {
        "nome_tipo": "TESTE_CRUD",
        "nome": "TESTE_CRUD", 
        "descricao": "Departamento de teste",
        "ativo": True
    }
    response = requests.post(f"{BASE_URL}/departamentos", json=novo_dept)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        created = response.json()
        print(f"✅ Departamento criado: {json.dumps(created, indent=2, ensure_ascii=False)}")
        return created.get('id')
    else:
        print(f"❌ Erro: {response.text}")
        return None

def test_tipo_maquina_crud():
    """Testa CRUD de tipos de máquina"""
    print("\n🔧 TESTANDO TIPOS DE MÁQUINA")
    print("=" * 50)
    
    # 1. Listar tipos de máquina
    print("1. Listando tipos de máquina...")
    response = requests.get(f"{BASE_URL}/tipos-maquina")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} tipos de máquina encontrados")
        if data:
            print(f"Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Erro: {response.text}")
    
    # 2. Criar tipo de máquina
    print("\n2. Criando tipo de máquina...")
    novo_tipo = {
        "nome_tipo": "TESTE_MAQUINA",
        "nome": "TESTE_MAQUINA",
        "departamento": "MOTORES",
        "setor": "BOBINAGEM",
        "categoria": "TESTE",
        "subcategoria": ["SUB1", "SUB2"],
        "descricao": "Tipo de máquina de teste",
        "ativo": True
    }
    response = requests.post(f"{BASE_URL}/tipos-maquina", json=novo_tipo)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        created = response.json()
        print(f"✅ Tipo de máquina criado: {json.dumps(created, indent=2, ensure_ascii=False)}")
        return created.get('id')
    else:
        print(f"❌ Erro: {response.text}")
        return None

def test_tipo_teste_crud():
    """Testa CRUD de tipos de teste"""
    print("\n🧪 TESTANDO TIPOS DE TESTE")
    print("=" * 50)
    
    # 1. Listar tipos de teste
    print("1. Listando tipos de teste...")
    response = requests.get(f"{BASE_URL}/tipos-teste")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} tipos de teste encontrados")
        if data:
            print(f"Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Erro: {response.text}")

def test_atividades_crud():
    """Testa CRUD de atividades"""
    print("\n📋 TESTANDO ATIVIDADES")
    print("=" * 50)
    
    # 1. Listar atividades
    print("1. Listando atividades...")
    response = requests.get(f"{BASE_URL}/atividades")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data)} atividades encontradas")
        if data:
            print(f"Primeiro item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Erro: {response.text}")

def main():
    print("🚀 TESTE DE CONSISTÊNCIA CRUD")
    print("=" * 60)
    
    try:
        # Testar cada endpoint
        dept_id = test_departamento_crud()
        tipo_maq_id = test_tipo_maquina_crud()
        test_tipo_teste_crud()
        test_atividades_crud()
        
        print("\n" + "=" * 60)
        print("🏁 TESTE CONCLUÍDO!")
        
        # Cleanup - deletar itens criados
        if dept_id:
            print(f"\n🧹 Limpando departamento criado (ID: {dept_id})...")
            requests.delete(f"{BASE_URL}/departamentos/{dept_id}")
        
        if tipo_maq_id:
            print(f"🧹 Limpando tipo de máquina criado (ID: {tipo_maq_id})...")
            requests.delete(f"{BASE_URL}/tipos-maquina/{tipo_maq_id}")
            
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    main()
