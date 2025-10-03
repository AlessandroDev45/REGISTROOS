#!/usr/bin/env python3
"""
Teste para verificar a funcionalidade de aprovação de colaboradores
"""

import requests
import json
import sys
import os

# Configurações
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@teste.com"
ADMIN_PASSWORD = "admin123"

def fazer_login_admin():
    """Faz login como administrador"""
    print("🔐 Fazendo login como administrador...")
    
    login_data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user_info = data.get("user", {})
        print(f"✅ Login realizado com sucesso!")
        print(f"👤 Usuário: {user_info.get('nome_completo')}")
        print(f"🔑 Privilégio: {user_info.get('privilege_level')}")
        return token
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None

def buscar_usuarios_pendentes(token):
    """Busca usuários pendentes de aprovação"""
    print("\n📋 Buscando usuários pendentes...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/pending-approval", headers=headers)
    
    if response.status_code == 200:
        usuarios = response.json()
        print(f"✅ Encontrados {len(usuarios)} usuários pendentes")
        
        for i, usuario in enumerate(usuarios, 1):
            print(f"\n👤 Usuário {i}:")
            print(f"   ID: {usuario.get('id')}")
            print(f"   Nome: {usuario.get('nome_completo')}")
            print(f"   Email: {usuario.get('email')}")
            print(f"   Setor: {usuario.get('setor', 'Não definido')}")
            print(f"   Aprovado: {usuario.get('is_approved')}")
            print(f"   Privilégio: {usuario.get('privilege_level')}")
        
        return usuarios
    else:
        print(f"❌ Erro ao buscar usuários pendentes: {response.status_code}")
        print(f"Resposta: {response.text}")
        return []

def aprovar_usuario(token, user_id, privilege_level="USER"):
    """Aprova um usuário"""
    print(f"\n✅ Aprovando usuário ID {user_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "privilege_level": privilege_level,
        "trabalha_producao": True
    }
    
    response = requests.put(f"{BASE_URL}/users/usuarios/{user_id}/approve", 
                          headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"✅ Usuário {user_id} aprovado com sucesso!")
        return True
    else:
        print(f"❌ Erro ao aprovar usuário {user_id}: {response.status_code}")
        print(f"Resposta: {response.text}")
        return False

def reprovar_usuario(token, user_id, motivo="Teste de reprovação"):
    """Reprova um usuário"""
    print(f"\n❌ Reprovando usuário ID {user_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"motivo": motivo}
    
    response = requests.put(f"{BASE_URL}/users/usuarios/{user_id}/reject", 
                          headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"❌ Usuário {user_id} reprovado com sucesso!")
        return True
    else:
        print(f"❌ Erro ao reprovar usuário {user_id}: {response.status_code}")
        print(f"Resposta: {response.text}")
        return False

def main():
    print("🧪 TESTE DE APROVAÇÃO DE COLABORADORES")
    print("=" * 50)
    
    # 1. Fazer login
    token = fazer_login_admin()
    if not token:
        print("❌ Não foi possível fazer login. Teste abortado.")
        return
    
    # 2. Buscar usuários pendentes
    usuarios_pendentes = buscar_usuarios_pendentes(token)
    
    if not usuarios_pendentes:
        print("\n✅ Não há usuários pendentes para testar.")
        print("💡 Para testar, registre um novo usuário primeiro.")
        return
    
    # 3. Testar aprovação/reprovação
    print("\n🔧 OPÇÕES DE TESTE:")
    print("1. Aprovar primeiro usuário")
    print("2. Reprovar primeiro usuário")
    print("3. Apenas visualizar (não fazer alterações)")
    
    try:
        opcao = input("\nEscolha uma opção (1-3): ").strip()
        
        if opcao == "1":
            primeiro_usuario = usuarios_pendentes[0]
            aprovar_usuario(token, primeiro_usuario['id'])
            
        elif opcao == "2":
            primeiro_usuario = usuarios_pendentes[0]
            reprovar_usuario(token, primeiro_usuario['id'])
            
        elif opcao == "3":
            print("✅ Teste concluído sem alterações.")
            
        else:
            print("❌ Opção inválida.")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
    
    print("\n🏁 Teste finalizado!")

if __name__ == "__main__":
    main()
