#!/usr/bin/env python3
"""
Script para debugar o problema de acesso ao desenvolvimento com autenticação
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"

def test_with_auth():
    """Testa com autenticação usando login"""
    print("🔍 Testando acesso ao desenvolvimento com autenticação...")
    print("=" * 60)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Teste 1: Fazer login primeiro
    print("\n1. Fazendo login...")
    try:
        # Dados de login (ajuste conforme necessário)
        login_data = {
            "username": "admin@registroos.com",  # ou outro usuário
            "password": "123456"  # ou outra senha
        }
        
        # Tentar login via /api/token
        response = session.post(
            f"{BASE_URL}/api/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso")
            token_data = response.json()
            print(f"   Token type: {token_data.get('token_type', 'N/A')}")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erro ao fazer login: {e}")
        return
    
    # Teste 2: Verificar endpoint /me com autenticação
    print("\n2. Testando endpoint /me com autenticação...")
    try:
        response = session.get(f"{BASE_URL}/api/me")
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Endpoint /me funcionando")
            print(f"   Usuário: {user_data.get('nome_completo', 'N/A')}")
            print(f"   Privilege: {user_data.get('privilege_level', 'N/A')}")
            print(f"   Setor: {user_data.get('setor', 'N/A')}")
            print(f"   Departamento: {user_data.get('departamento', 'N/A')}")
            print(f"   Trabalha Produção: {user_data.get('trabalha_producao', 'N/A')}")
            
            # Salvar dados do usuário para testes posteriores
            global current_user
            current_user = user_data
            
        else:
            print(f"❌ Erro no endpoint /me: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return
    except Exception as e:
        print(f"❌ Erro ao chamar /me: {e}")
        return
    
    # Teste 3: Verificar endpoint /setores com autenticação
    print("\n3. Testando endpoint /setores com autenticação...")
    try:
        response = session.get(f"{BASE_URL}/api/setores")
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
                    
                # Salvar setores para análise
                global current_setores
                current_setores = setores_data
            else:
                print("   ⚠️ Nenhum setor encontrado")
        else:
            print(f"❌ Erro no endpoint /setores: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao chamar /setores: {e}")
    
    # Teste 4: Simular lógica de acesso do frontend
    print("\n4. Simulando lógica de acesso do frontend...")
    try:
        if 'current_user' in globals() and 'current_setores' in globals():
            user = current_user
            setores = current_setores
            
            print(f"   Dados do usuário:")
            print(f"     Privilege Level: {user.get('privilege_level', 'N/A')}")
            print(f"     Trabalha Produção: {user.get('trabalha_producao', 'N/A')}")
            print(f"     Setor: {user.get('setor', 'N/A')}")
            print(f"     Departamento: {user.get('departamento', 'N/A')}")
            
            # Lógica de acesso (baseada no SetorSelectionPage.tsx)
            privilege_level = user.get('privilege_level', '')
            trabalha_producao = user.get('trabalha_producao', False)
            
            tem_acesso = (
                privilege_level == 'ADMIN' or
                privilege_level == 'SUPERVISOR' or
                trabalha_producao == True
            )
            
            print(f"   Resultado da verificação de acesso: {'✅ TEM ACESSO' if tem_acesso else '❌ SEM ACESSO'}")
            
            if tem_acesso:
                # Simular filtro de setores
                print(f"\n   Simulando filtro de setores...")
                user_dept = user.get('departamento', '')
                user_setor = user.get('setor', '')
                
                if privilege_level == 'ADMIN':
                    setores_filtrados = [s for s in setores if s.get('ativo', True)]
                    print(f"     ADMIN: Todos os setores ativos ({len(setores_filtrados)} setores)")
                else:
                    setores_filtrados = []
                    for setor in setores:
                        if not setor.get('ativo', True):
                            continue
                            
                        # Verificar se pertence ao departamento ou setor do usuário
                        pertence_dept = user_dept == setor.get('departamento', '')
                        pertence_setor = user_setor == setor.get('nome', '')
                        
                        if pertence_dept or pertence_setor:
                            setores_filtrados.append(setor)
                    
                    print(f"     Usuário não-admin: {len(setores_filtrados)} setores filtrados")
                    
                    if len(setores_filtrados) == 0 and not trabalha_producao:
                        print("     ⚠️ PROBLEMA: Nenhum setor encontrado e usuário não trabalha na produção!")
                    
                    # Mostrar setores filtrados
                    if setores_filtrados:
                        print(f"     Setores disponíveis:")
                        for setor in setores_filtrados[:5]:  # Mostrar apenas os primeiros 5
                            print(f"       - {setor.get('nome', 'N/A')} ({setor.get('departamento', 'N/A')})")
                        if len(setores_filtrados) > 5:
                            print(f"       ... e mais {len(setores_filtrados) - 5} setores")
            else:
                print("   ⚠️ Usuário não tem acesso ao desenvolvimento!")
                print("   Para ter acesso, o usuário precisa:")
                print("     - Ser ADMIN, ou")
                print("     - Ser SUPERVISOR, ou") 
                print("     - Ter trabalha_producao = True")
        else:
            print("❌ Não foi possível obter dados necessários para simulação")
    except Exception as e:
        print(f"❌ Erro na simulação de acesso: {e}")

if __name__ == "__main__":
    test_with_auth()
