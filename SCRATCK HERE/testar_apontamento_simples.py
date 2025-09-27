#!/usr/bin/env python3
"""
TESTAR APONTAMENTO SIMPLES
==========================

Testar criação de apontamento com dados mínimos para identificar o erro.
"""

import requests
import json
from datetime import datetime, date

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

def testar_apontamento_simples(session):
    """Testar criação de apontamento com dados simples"""
    print(f"\n📝 Testando criação de apontamento simples...")
    
    # Dados mínimos do apontamento
    agora = datetime.now()
    dados_apontamento = {
        "numero_os": "000012345",
        "cliente": "AIR LIQUIDE BRASIL",
        "equipamento": "MOTOR ELETRICO PARTIDA",
        "tipo_maquina": "MOTOR ELETRICO",
        "tipo_atividade": "MANUTENCAO_PREVENTIVA",
        "descricao_atividade": "Teste de apontamento simples",
        "data_inicio": agora.date().isoformat(),
        "hora_inicio": agora.strftime("%H:%M"),
        "observacao": "Teste de criação de apontamento"
    }
    
    print(f"📋 Dados do apontamento:")
    for key, value in dados_apontamento.items():
        print(f"   {key}: {value}")
    
    try:
        response = session.post(f"{BASE_URL}/api/desenvolvimento/os/apontamentos", json=dados_apontamento)
        
        print(f"\n📊 Resposta do servidor:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Apontamento criado com sucesso!")
            print(f"   ID: {data.get('id')}")
            print(f"   OS: {data.get('numero_os')}")
            print(f"   Status: {data.get('status_os')}")
            return True
        else:
            print(f"❌ Erro ao criar apontamento: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro JSON: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Erro texto: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTAR APONTAMENTO SIMPLES")
    print("=" * 35)
    
    # 1. Fazer login
    session, user_info = fazer_login()
    if not session:
        return
    
    # 2. Testar apontamento simples
    sucesso = testar_apontamento_simples(session)
    
    # 3. Resultado
    print(f"\n📊 RESULTADO:")
    if sucesso:
        print(f"✅ APONTAMENTO CRIADO COM SUCESSO!")
    else:
        print(f"❌ FALHA NA CRIAÇÃO DO APONTAMENTO")
        print(f"💡 VERIFICAR LOGS DO SERVIDOR PARA MAIS DETALHES")

if __name__ == "__main__":
    main()
