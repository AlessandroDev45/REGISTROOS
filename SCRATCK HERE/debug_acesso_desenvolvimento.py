#!/usr/bin/env python3
"""
Script para debugar o problema de acesso ao desenvolvimento
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_login_and_access():
    """Testa login e acesso ao desenvolvimento"""
    print("🔍 Testando acesso ao desenvolvimento...")
    print("=" * 50)
    
    # Teste 1: Verificar endpoint /me
    print("\n1. Testando endpoint /me...")
    try:
        response = requests.get(f"{BASE_URL}/me", headers=HEADERS)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Endpoint /me funcionando")
            print(f"   Usuário: {user_data.get('nome_completo', 'N/A')}")
            print(f"   Privilege: {user_data.get('privilege_level', 'N/A')}")
            print(f"   Setor: {user_data.get('setor', 'N/A')}")
            print(f"   Departamento: {user_data.get('departamento', 'N/A')}")
            print(f"   Trabalha Produção: {user_data.get('trabalha_producao', 'N/A')}")
        else:
            print(f"❌ Erro no endpoint /me: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao chamar /me: {e}")
    
    # Teste 2: Verificar endpoint /setores
    print("\n2. Testando endpoint /setores...")
    try:
        response = requests.get(f"{BASE_URL}/setores", headers=HEADERS)
        if response.status_code == 200:
            setores_data = response.json()
            print(f"✅ Endpoint /setores funcionando - {len(setores_data)} setores encontrados")
            
            # Verificar estrutura dos setores
            if setores_data:
                primeiro_setor = setores_data[0]
                print(f"   Estrutura do primeiro setor:")
                for key, value in primeiro_setor.items():
                    print(f"     {key}: {value}")
                
                # Contar setores por departamento
                dept_count = {}
                for setor in setores_data:
                    dept = setor.get('departamento', 'SEM_DEPARTAMENTO')
                    dept_count[dept] = dept_count.get(dept, 0) + 1
                
                print(f"   Setores por departamento:")
                for dept, count in dept_count.items():
                    print(f"     {dept}: {count}")
            else:
                print("   ⚠️ Nenhum setor encontrado")
        else:
            print(f"❌ Erro no endpoint /setores: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao chamar /setores: {e}")
    
    # Teste 3: Verificar endpoint /admin/setores/
    print("\n3. Testando endpoint /admin/setores/...")
    try:
        response = requests.get(f"{BASE_URL}/admin/setores/", headers=HEADERS)
        if response.status_code == 200:
            admin_setores_data = response.json()
            print(f"✅ Endpoint /admin/setores/ funcionando - {len(admin_setores_data)} setores encontrados")
            
            if admin_setores_data:
                primeiro_setor = admin_setores_data[0]
                print(f"   Estrutura do primeiro setor (admin):")
                for key, value in primeiro_setor.items():
                    print(f"     {key}: {value}")
        else:
            print(f"❌ Erro no endpoint /admin/setores/: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao chamar /admin/setores/: {e}")
    
    # Teste 4: Simular verificação de acesso
    print("\n4. Simulando verificação de acesso...")
    try:
        # Primeiro, pegar dados do usuário
        user_response = requests.get(f"{BASE_URL}/me", headers=HEADERS)
        if user_response.status_code == 200:
            user_data = user_response.json()
            
            # Verificar acesso baseado na lógica do frontend
            privilege_level = user_data.get('privilege_level', '')
            trabalha_producao = user_data.get('trabalha_producao', False)
            setor = user_data.get('setor', '')
            
            print(f"   Dados do usuário:")
            print(f"     Privilege Level: {privilege_level}")
            print(f"     Trabalha Produção: {trabalha_producao}")
            print(f"     Setor: {setor}")
            
            # Lógica de acesso (baseada no SetorSelectionPage.tsx)
            tem_acesso = (
                privilege_level == 'ADMIN' or
                privilege_level == 'SUPERVISOR' or
                trabalha_producao == True
            )
            
            print(f"   Resultado da verificação de acesso: {'✅ TEM ACESSO' if tem_acesso else '❌ SEM ACESSO'}")
            
            if not tem_acesso:
                print("   ⚠️ Usuário não tem acesso ao desenvolvimento!")
                print("   Para ter acesso, o usuário precisa:")
                print("     - Ser ADMIN, ou")
                print("     - Ser SUPERVISOR, ou") 
                print("     - Ter trabalha_producao = True")
        else:
            print(f"❌ Não foi possível obter dados do usuário para verificação")
    except Exception as e:
        print(f"❌ Erro na simulação de acesso: {e}")

if __name__ == "__main__":
    test_login_and_access()
