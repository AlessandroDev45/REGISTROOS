#!/usr/bin/env python3
"""
TESTE DO ERRO 422 NO ENDPOINT DE DEPARTAMENTOS
==============================================

Testa o endpoint PUT /api/admin/config/departamentos/{id} 
para identificar a causa do erro 422.
"""

import requests
import json

# Configurações
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
DEPT_URL = f"{BASE_URL}/api/admin/config/departamentos"

def fazer_login():
    """Faz login e retorna o token"""
    login_data = {
        "username": "admin@registroos.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login realizado com sucesso")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def listar_departamentos(token):
    """Lista todos os departamentos"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(DEPT_URL, headers=headers)
        if response.status_code == 200:
            departamentos = response.json()
            print(f"✅ Departamentos encontrados: {len(departamentos)}")
            for dept in departamentos:
                print(f"   ID: {dept['id']}, Nome: {dept['nome_tipo']}, Ativo: {dept['ativo']}")
            return departamentos
        else:
            print(f"❌ Erro ao listar departamentos: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return []

def testar_update_departamento(token, dept_id, novo_nome):
    """Testa o update de um departamento"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Dados para atualização
    update_data = {
        "nome_tipo": novo_nome,
        "descricao": "DEPARTAMENTO RESPONSAVEL POR MOTORES",
        "ativo": True
    }
    
    print(f"\n🔄 Testando update do departamento ID {dept_id}")
    print(f"📤 Dados enviados: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(f"{DEPT_URL}/{dept_id}", json=update_data, headers=headers)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Update realizado com sucesso!")
            return response.json()
        else:
            print(f"❌ Erro no update: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Detalhes do erro: {json.dumps(error_data, indent=2)}")
            except:
                print(f"❌ Resposta não é JSON: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 TESTANDO ERRO 422 NO ENDPOINT DE DEPARTAMENTOS")
    print("=" * 60)
    
    # 1. Fazer login
    token = fazer_login()
    if not token:
        return
    
    # 2. Listar departamentos
    print(f"\n📋 Listando departamentos existentes:")
    departamentos = listar_departamentos(token)
    
    # 3. Testar update no departamento ID 1 (se existir)
    if departamentos:
        dept_id = 1
        dept_existente = next((d for d in departamentos if d['id'] == dept_id), None)
        
        if dept_existente:
            print(f"\n🎯 Departamento ID {dept_id} encontrado:")
            print(f"   Nome atual: {dept_existente['nome_tipo']}")
            print(f"   Descrição: {dept_existente['descricao']}")
            print(f"   Ativo: {dept_existente['ativo']}")
            
            # Testar com o nome que está causando erro
            testar_update_departamento(token, dept_id, "T5AT4E")
            
            # Testar com um nome diferente
            print(f"\n" + "="*40)
            testar_update_departamento(token, dept_id, "MOTORES_TESTE")
            
        else:
            print(f"❌ Departamento ID {dept_id} não encontrado")
    
    print(f"\n🎉 TESTE CONCLUÍDO!")

if __name__ == "__main__":
    main()
