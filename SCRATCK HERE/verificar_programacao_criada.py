#!/usr/bin/env python3
"""
VERIFICAR PROGRAMAÇÃO CRIADA
===========================

Verifica o status da programação criada no teste anterior.
"""

import requests

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Credenciais funcionais
TEST_USER = {"username": "admin@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login e obter sessão"""
    print("🔐 Fazendo login...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=TEST_USER, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Login realizado com sucesso!")
        return session
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def verificar_programacoes(session):
    """Verificar programações existentes"""
    print("\n📋 Verificando programações...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            programacoes = response.json()
            print(f"✅ Encontradas {len(programacoes)} programações")
            
            for i, prog in enumerate(programacoes):
                print(f"\n📋 Programação {i+1}:")
                print(f"   ID: {prog.get('id')}")
                print(f"   OS: {prog.get('os_numero')}")
                print(f"   Status: {prog.get('status')}")
                print(f"   Responsável: {prog.get('responsavel_nome')}")
                print(f"   Cliente: {prog.get('cliente_nome')}")
                
                # Testar verificação para esta OS
                os_numero = prog.get('os_numero')
                if os_numero:
                    print(f"\n🔍 Testando verificação para OS {os_numero}...")
                    response_verif = session.get(f"{BASE_URL}/api/desenvolvimento/verificar-programacao-os/{os_numero}")
                    
                    if response_verif.status_code == 200:
                        data = response_verif.json()
                        print(f"   Tem programação: {data.get('tem_programacao')}")
                        if data.get('tem_programacao'):
                            print(f"   Status: {data.get('status_programacao')}")
                        else:
                            print(f"   Mensagem: {data.get('mensagem')}")
                    else:
                        print(f"   ❌ Erro na verificação: {response_verif.status_code}")
            
            return programacoes
        else:
            print(f"❌ Erro ao buscar programações: {response.status_code}")
            print(f"Resposta: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def verificar_programacoes_pcp(session):
    """Verificar programações via PCP"""
    print("\n📋 Verificando programações via PCP...")
    
    try:
        response = session.get(f"{BASE_URL}/api/pcp/programacoes")
        
        if response.status_code == 200:
            programacoes = response.json()
            print(f"✅ Encontradas {len(programacoes)} programações via PCP")
            
            for i, prog in enumerate(programacoes[-3:]):  # Últimas 3
                print(f"\n📋 Programação PCP {i+1}:")
                for key, value in prog.items():
                    print(f"   {key}: {value}")
            
            return programacoes
        else:
            print(f"❌ Erro ao buscar programações PCP: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🧪 VERIFICAR PROGRAMAÇÃO CRIADA")
    print("=" * 40)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Verificar programações do usuário
    programacoes_user = verificar_programacoes(session)
    
    # 3. Verificar programações via PCP
    programacoes_pcp = verificar_programacoes_pcp(session)
    
    print(f"\n📊 RESUMO:")
    print(f"   Programações do usuário: {len(programacoes_user)}")
    print(f"   Programações total (PCP): {len(programacoes_pcp)}")

if __name__ == "__main__":
    main()
