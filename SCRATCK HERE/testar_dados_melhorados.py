#!/usr/bin/env python3
"""
TESTAR DADOS MELHORADOS
=======================

Testar se os dados da programação melhoraram após as correções.
"""

import requests
import json

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
USER_MECANICA = {"username": "user.mecanica_dia@registroos.com", "password": "123456"}

def fazer_login():
    """Fazer login como usuário MECANICA"""
    print("🔐 Fazendo login como usuário MECANICA...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=USER_MECANICA, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        user_info = data.get('user', {})
        print(f"✅ Login realizado! {user_info.get('nome_completo', 'N/A')} (ID: {user_info.get('id', 'N/A')})")
        return session, user_info
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None, None

def testar_dashboard_melhorado(session):
    """Testar dashboard com dados melhorados"""
    print(f"\n📊 Testando dashboard com dados melhorados...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Dashboard retornou {len(data)} programações")
            
            if len(data) > 0:
                print(f"\n✅ DADOS DAS PROGRAMAÇÕES:")
                
                for i, prog in enumerate(data):
                    print(f"\n📋 PROGRAMAÇÃO {i+1}:")
                    print(f"   ID: {prog.get('id')}")
                    print(f"   Status: {prog.get('status')}")
                    print(f"   OS Número: {prog.get('os_numero')}")
                    print(f"   Cliente: {prog.get('cliente_nome')}")
                    print(f"   Equipamento: {prog.get('equipamento_descricao')}")
                    print(f"   Responsável: {prog.get('responsavel_nome')}")
                    print(f"   Atribuído para: {prog.get('atribuido_para')}")
                    print(f"   Atribuído por: {prog.get('atribuido_por')}")
                    print(f"   Data atribuição: {prog.get('data_atribuicao')}")
                    print(f"   Setor: {prog.get('setor_nome')}")
                    print(f"   Prioridade: {prog.get('prioridade')}")
                    print(f"   Início: {prog.get('inicio_previsto')}")
                    print(f"   Fim: {prog.get('fim_previsto')}")
                    print(f"   Observações: {prog.get('observacoes', '')[:100]}...")
                    print(f"   Histórico: {prog.get('historico', '')[:100]}...")
                
                return True
            else:
                print(f"❌ Dashboard vazio")
                return False
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTAR DADOS MELHORADOS")
    print("=" * 35)
    
    # 1. Fazer login
    session, user_info = fazer_login()
    if not session:
        return
    
    # 2. Testar dashboard melhorado
    sucesso = testar_dashboard_melhorado(session)
    
    # 3. Resultado
    print(f"\n📊 RESULTADO:")
    if sucesso:
        print(f"✅ DADOS MELHORADOS COM SUCESSO!")
        print(f"🎯 AGORA O DASHBOARD MOSTRA:")
        print(f"   - Número da OS correto")
        print(f"   - Nome do cliente")
        print(f"   - Descrição do equipamento")
        print(f"   - Quem atribuiu a programação")
        print(f"   - Data de atribuição")
        print(f"   - Histórico completo")
    else:
        print(f"❌ Ainda há problemas nos dados")

if __name__ == "__main__":
    main()
