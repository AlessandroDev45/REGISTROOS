#!/usr/bin/env python3
"""
Teste para verificar se a autenticação e criação de departamentos
está funcionando corretamente.
"""

import requests
import json
import sys

def fazer_login():
    """Faz login e retorna o token"""
    
    login_url = "http://localhost:8000/api/auth/login"
    
    # Dados de login (ajuste conforme necessário)
    login_data = {
        "username": "ADMIN",  # Usuário admin do sistema
        "password": "123456"  # Senha padrão (ajuste se necessário)
    }
    
    print("🔐 Fazendo login...")
    
    try:
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("✅ Login realizado com sucesso!")
                return token
            else:
                print("❌ Token não encontrado na resposta")
                return None
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição de login: {e}")
        return None

def testar_criacao_departamento_com_auth():
    """Testa a criação de departamento com autenticação"""
    
    print("🧪 TESTE DE CRIAÇÃO DE DEPARTAMENTO COM AUTENTICAÇÃO")
    print("=" * 60)
    
    # 1. Fazer login
    token = fazer_login()
    if not token:
        print("❌ Não foi possível fazer login. Teste abortado.")
        return
    
    # 2. Preparar headers com token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 3. Dados do departamento de teste
    departamento_data = {
        "nome_tipo": "TESTE DEPARTAMENTO API",
        "descricao": "Departamento criado via teste de API",
        "ativo": True
    }
    
    # 4. Testar criação
    create_url = "http://localhost:8000/api/admin/config/departamentos"
    
    print(f"\n📤 Criando departamento...")
    print(f"   URL: {create_url}")
    print(f"   Dados: {json.dumps(departamento_data, indent=2)}")
    
    try:
        response = requests.post(create_url, json=departamento_data, headers=headers)
        
        print(f"\n📊 Resposta:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Departamento criado com sucesso!")
            print(f"   📄 Dados: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 5. Testar listagem para verificar se foi criado
            print(f"\n📋 Verificando se o departamento foi criado...")
            list_response = requests.get(create_url, headers=headers)
            
            if list_response.status_code == 200:
                departamentos = list_response.json()
                print(f"   ✅ Lista obtida com sucesso! Total: {len(departamentos)}")
                
                # Procurar o departamento criado
                departamento_criado = None
                for dept in departamentos:
                    if dept.get("nome_tipo") == departamento_data["nome_tipo"]:
                        departamento_criado = dept
                        break
                
                if departamento_criado:
                    print(f"   ✅ Departamento encontrado na lista!")
                    print(f"   📄 Dados: {json.dumps(departamento_criado, indent=2, ensure_ascii=False)}")
                    
                    # 6. Limpar - deletar o departamento de teste
                    dept_id = departamento_criado.get("id")
                    if dept_id:
                        print(f"\n🗑️ Limpando - deletando departamento de teste...")
                        delete_response = requests.delete(f"{create_url}/{dept_id}", headers=headers)
                        
                        if delete_response.status_code == 200:
                            print(f"   ✅ Departamento deletado com sucesso!")
                        else:
                            print(f"   ⚠️ Erro ao deletar: {delete_response.status_code}")
                            print(f"   📄 Resposta: {delete_response.text}")
                else:
                    print(f"   ❌ Departamento não encontrado na lista")
            else:
                print(f"   ❌ Erro ao listar departamentos: {list_response.status_code}")
                print(f"   📄 Resposta: {list_response.text}")
                
        elif response.status_code == 400:
            print(f"   ❌ Erro de validação (400)")
            print(f"   📄 Detalhes: {response.text}")
        elif response.status_code == 401:
            print(f"   ❌ Erro de autenticação (401)")
            print(f"   📄 Detalhes: {response.text}")
        elif response.status_code == 403:
            print(f"   ❌ Erro de permissão (403)")
            print(f"   📄 Detalhes: {response.text}")
        elif response.status_code == 405:
            print(f"   ❌ Método não permitido (405) - PROBLEMA AINDA EXISTE!")
            print(f"   📄 Detalhes: {response.text}")
        else:
            print(f"   ❌ Erro inesperado: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def main():
    """Função principal"""
    testar_criacao_departamento_com_auth()

if __name__ == "__main__":
    main()
