#!/usr/bin/env python3
"""
Script para debugar o problema com usuários não-admin
"""

import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"

def test_non_admin_user():
    """Testa com usuário não-admin"""
    print("🔍 Testando acesso com usuário não-admin...")
    print("=" * 60)
    
    # Criar sessão para manter cookies
    session = requests.Session()
    
    # Lista de usuários para testar (usuários reais do sistema)
    test_users = [
        {"username": "user.laboratorio_de_ensaios_eletricos@registroos.com", "password": "123456"},
        {"username": "supervisor.laboratorio_de_ensaios_eletricos@registroos.com", "password": "123456"},
        {"username": "user.mecanica_dia@registroos.com", "password": "123456"},
        {"username": "user.pcp@registroos.com", "password": "123456"},
    ]
    
    for i, user_creds in enumerate(test_users, 1):
        print(f"\n{'='*20} TESTE {i}: {user_creds['username']} {'='*20}")
        
        # Fazer login
        print(f"\n1. Fazendo login com {user_creds['username']}...")
        try:
            response = session.post(
                f"{BASE_URL}/api/token",
                data=user_creds,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                print("✅ Login realizado com sucesso")
            else:
                print(f"❌ Erro no login: {response.status_code}")
                print(f"   Resposta: {response.text}")
                continue
                
        except Exception as e:
            print(f"❌ Erro ao fazer login: {e}")
            continue
        
        # Verificar dados do usuário
        print("\n2. Verificando dados do usuário...")
        try:
            response = session.get(f"{BASE_URL}/api/me")
            if response.status_code == 200:
                user_data = response.json()
                print("✅ Dados do usuário obtidos")
                print(f"   Usuário: {user_data.get('nome_completo', 'N/A')}")
                print(f"   Privilege: {user_data.get('privilege_level', 'N/A')}")
                print(f"   Setor: {user_data.get('setor', 'N/A')}")
                print(f"   Departamento: {user_data.get('departamento', 'N/A')}")
                print(f"   Trabalha Produção: {user_data.get('trabalha_producao', 'N/A')}")
                
                # Verificar acesso
                privilege_level = user_data.get('privilege_level', '')
                trabalha_producao = user_data.get('trabalha_producao', False)
                
                tem_acesso = (
                    privilege_level == 'ADMIN' or
                    privilege_level == 'SUPERVISOR' or
                    trabalha_producao == True
                )
                
                print(f"   Acesso ao desenvolvimento: {'✅ TEM ACESSO' if tem_acesso else '❌ SEM ACESSO'}")
                
                if tem_acesso:
                    # Testar busca de setores
                    print("\n3. Testando busca de setores...")
                    try:
                        response = session.get(f"{BASE_URL}/api/setores")
                        if response.status_code == 200:
                            setores_data = response.json()
                            print(f"✅ {len(setores_data)} setores encontrados")
                            
                            # Simular filtro do frontend
                            user_dept = user_data.get('departamento', '')
                            user_setor = user_data.get('setor', '')
                            
                            if privilege_level == 'ADMIN':
                                setores_filtrados = [s for s in setores_data if s.get('ativo', True)]
                            else:
                                setores_filtrados = []
                                for setor in setores_data:
                                    if not setor.get('ativo', True):
                                        continue
                                        
                                    # Verificar se pertence ao departamento ou setor do usuário
                                    pertence_dept = user_dept == setor.get('departamento', '')
                                    pertence_setor = user_setor == setor.get('nome', '')
                                    
                                    if pertence_dept or pertence_setor:
                                        setores_filtrados.append(setor)
                            
                            print(f"   Setores após filtro: {len(setores_filtrados)}")
                            
                            if len(setores_filtrados) == 0:
                                print("   ⚠️ PROBLEMA: Nenhum setor encontrado após filtro!")
                                print(f"   Usuário departamento: '{user_dept}'")
                                print(f"   Usuário setor: '{user_setor}'")
                                print("   Setores disponíveis:")
                                for setor in setores_data[:5]:
                                    print(f"     - {setor.get('nome', 'N/A')} (dept: {setor.get('departamento', 'N/A')})")
                                
                                # Verificar se trabalha na produção
                                if not trabalha_producao:
                                    print("   ❌ CAUSA: Usuário não trabalha na produção e não tem setores compatíveis!")
                                else:
                                    print("   ⚠️ Usuário trabalha na produção, mas não tem setores compatíveis")
                            else:
                                print("   ✅ Setores encontrados após filtro:")
                                for setor in setores_filtrados[:3]:
                                    print(f"     - {setor.get('nome', 'N/A')} ({setor.get('departamento', 'N/A')})")
                        else:
                            print(f"❌ Erro ao buscar setores: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Erro ao testar setores: {e}")
                else:
                    print("   ❌ Usuário não tem acesso ao desenvolvimento")
                    print("   Para ter acesso, precisa:")
                    print("     - Ser ADMIN ou SUPERVISOR, ou")
                    print("     - Ter trabalha_producao = True")
            else:
                print(f"❌ Erro ao obter dados do usuário: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao verificar usuário: {e}")
        
        print(f"\n{'='*60}")

if __name__ == "__main__":
    test_non_admin_user()
