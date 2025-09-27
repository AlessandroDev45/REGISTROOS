#!/usr/bin/env python3
"""
VERIFICAR USUÁRIOS NO SISTEMA
============================

Verifica se existem usuários no sistema e suas credenciais.
"""

import requests
import json

# Configuração
BASE_URL = "http://127.0.0.1:8000"

def verificar_servidor():
    """Verificar se o servidor está rodando"""
    print("🔍 Verificando se o servidor está rodando...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando!")
            return True
        else:
            print(f"⚠️ Servidor respondeu com status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor não está rodando: {e}")
        return False

def verificar_usuarios():
    """Verificar usuários no sistema"""
    print("\n👥 Verificando usuários no sistema...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/debug-users", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_usuarios", 0)
            usuarios = data.get("usuarios", [])
            
            print(f"✅ Total de usuários: {total}")
            
            if usuarios:
                print("\n📋 Usuários encontrados:")
                for i, user in enumerate(usuarios[:10]):  # Mostrar apenas os 10 primeiros
                    print(f"   {i+1}. {user.get('nome', 'N/A')} - {user.get('email', 'N/A')}")
                
                if len(usuarios) > 10:
                    print(f"   ... e mais {len(usuarios) - 10} usuários")
            else:
                print("⚠️ Nenhum usuário encontrado")
            
            return usuarios
        else:
            print(f"❌ Erro ao buscar usuários: {response.status_code}")
            print(f"Resposta: {response.text}")
            return []
    
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return []

def testar_login_usuario(email, senha="123456"):
    """Testar login com um usuário específico"""
    print(f"\n🔐 Testando login com {email}...")
    
    headers = {"Content-Type": "application/json"}
    login_data = {"username": email, "password": senha}
    
    response = requests.post(f"{BASE_URL}/api/login", json=login_data, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return True
    else:
        print(f"❌ Login falhou: {response.status_code}")
        if response.status_code == 401:
            print("   Credenciais inválidas")
        elif response.status_code == 403:
            print("   Usuário não aprovado")
        else:
            print(f"   Resposta: {response.text}")
        return False

def criar_usuario_teste():
    """Criar um usuário de teste"""
    print("\n👤 Criando usuário de teste...")
    
    headers = {"Content-Type": "application/json"}
    user_data = {
        "primeiro_nome": "Teste",
        "sobrenome": "Dashboard",
        "email": "teste@dashboard.com",
        "password": "123456",
        "nome_usuario": "teste_dashboard",
        "matricula": "TEST001",
        "cargo": "Desenvolvedor",
        "departamento": "TI",
        "setor_de_trabalho": "Desenvolvimento",
        "trabalha_producao": True
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=user_data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Usuário de teste criado com sucesso!")
        print("⚠️ ATENÇÃO: O usuário precisa ser aprovado por um admin antes de fazer login")
        return True
    else:
        print(f"❌ Erro ao criar usuário: {response.status_code}")
        print(f"Resposta: {response.text}")
        return False

def main():
    """Função principal"""
    print("👥 VERIFICAÇÃO DE USUÁRIOS DO SISTEMA")
    print("=" * 50)
    
    # 1. Verificar servidor
    if not verificar_servidor():
        print("❌ Servidor não está rodando. Inicie o backend primeiro.")
        return
    
    # 2. Verificar usuários existentes
    usuarios = verificar_usuarios()
    
    if not usuarios:
        print("\n💡 Nenhum usuário encontrado. Criando usuário de teste...")
        criar_usuario_teste()
        return
    
    # 3. Testar login com usuários existentes
    print("\n🧪 Testando login com usuários existentes...")
    
    senhas_comuns = ["123456", "admin", "admin123", "password", "test", "test123"]
    
    for user in usuarios[:5]:  # Testar apenas os 5 primeiros
        email = user.get('email')
        if email:
            print(f"\n👤 Testando usuário: {email}")
            
            for senha in senhas_comuns:
                if testar_login_usuario(email, senha):
                    print(f"🎉 CREDENCIAIS FUNCIONAIS ENCONTRADAS:")
                    print(f"   Email: {email}")
                    print(f"   Senha: {senha}")
                    print(f"\n💡 Use estas credenciais no teste do dashboard!")
                    return
    
    print("\n⚠️ Nenhuma credencial funcionou com os usuários existentes.")
    print("💡 Possíveis soluções:")
    print("   1. Verificar se os usuários estão aprovados")
    print("   2. Resetar senha de um usuário existente")
    print("   3. Criar um novo usuário e aprová-lo")

if __name__ == "__main__":
    main()
