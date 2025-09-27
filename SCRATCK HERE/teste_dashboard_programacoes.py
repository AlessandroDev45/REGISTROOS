#!/usr/bin/env python3
"""
TESTE DO DASHBOARD DE PROGRAMAÇÕES
=================================

Testa os novos endpoints implementados:
1. GET /api/desenvolvimento/minhas-programacoes - Buscar programações do usuário
2. PATCH /api/pcp/programacoes/{id}/status - Atualizar status da programação

"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Credenciais de teste (funcionais encontradas)
TEST_USERS = [
    {"username": "admin@registroos.com", "password": "123456"},
    {"username": "supervisor.pcp@registroos.com", "password": "123456"},
    {"username": "user.pcp@registroos.com", "password": "123456"},
    {"username": "supervisor.mecanica_dia@registroos.com", "password": "123456"},
    {"username": "user.mecanica_dia@registroos.com", "password": "123456"}
]

def fazer_login():
    """Fazer login e obter session com cookies"""
    print("🔐 Tentando fazer login...")

    # Criar uma sessão para manter cookies
    session = requests.Session()
    headers = {"Content-Type": "application/json"}

    # Tentar diferentes credenciais
    for i, test_user in enumerate(TEST_USERS):
        print(f"   Tentativa {i+1}: {test_user['username']}")
        response = session.post(LOGIN_URL, json=test_user, headers=headers)

        if response.status_code == 200:
            # O login retorna dados do usuário, e o token fica no cookie da sessão
            print(f"✅ Login realizado com sucesso com {test_user['username']}!")
            return session  # Retornar a sessão com cookies
        else:
            print(f"   ❌ Falhou: {response.status_code}")

    print("❌ Nenhuma credencial funcionou")
    return None

def testar_minhas_programacoes(session):
    """Testar endpoint de minhas programações"""
    print("\n📋 Testando endpoint /api/desenvolvimento/minhas-programacoes...")

    url = f"{BASE_URL}/api/desenvolvimento/minhas-programacoes"

    response = session.get(url)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        programacoes = response.json()
        print(f"✅ Encontradas {len(programacoes)} programações")
        
        for i, prog in enumerate(programacoes[:3]):  # Mostrar apenas as 3 primeiras
            print(f"\n📋 Programação {i+1}:")
            print(f"   ID: {prog.get('id')}")
            print(f"   OS: {prog.get('os_numero')}")
            print(f"   Cliente: {prog.get('cliente_nome')}")
            print(f"   Status: {prog.get('status')}")
            print(f"   Início: {prog.get('inicio_previsto')}")
            print(f"   Fim: {prog.get('fim_previsto')}")
        
        return programacoes
    else:
        print(f"❌ Erro: {response.text}")
        return []

def testar_atualizar_status(session, programacao_id, novo_status):
    """Testar endpoint de atualização de status"""
    print(f"\n🔄 Testando atualização de status da programação {programacao_id} para {novo_status}...")

    headers = {"Content-Type": "application/json"}
    url = f"{BASE_URL}/api/pcp/programacoes/{programacao_id}/status"

    data = {"status": novo_status}

    response = session.patch(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ Status atualizado com sucesso!")
        print(f"   Mensagem: {resultado.get('message')}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False

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

def main():
    """Função principal"""
    print("🧪 TESTE DO DASHBOARD DE PROGRAMAÇÕES")
    print("=" * 50)

    # 0. Verificar servidor
    if not verificar_servidor():
        print("❌ Servidor não está rodando. Inicie o backend primeiro.")
        print("💡 Execute: uvicorn main:app --reload --host 127.0.0.1 --port 8000")
        return

    # 1. Fazer login
    session = fazer_login()
    if not session:
        print("❌ Não foi possível fazer login. Teste abortado.")
        print("💡 Verifique se existe um usuário no sistema ou crie um.")
        return

    # 2. Testar busca de programações
    programacoes = testar_minhas_programacoes(session)
    
    if not programacoes:
        print("\n⚠️ Nenhuma programação encontrada para testar atualização de status.")
        print("💡 Dica: Crie uma programação primeiro no PCP para testar o fluxo completo.")
        return
    
    # 3. Testar atualização de status (se houver programações)
    primeira_programacao = programacoes[0]
    programacao_id = primeira_programacao.get('id')
    status_atual = primeira_programacao.get('status')
    
    print(f"\n🎯 Testando com programação ID {programacao_id} (status atual: {status_atual})")
    
    # Definir próximo status baseado no atual
    if status_atual == 'PROGRAMADA':
        novo_status = 'EM_ANDAMENTO'
    elif status_atual == 'EM_ANDAMENTO':
        novo_status = 'AGUARDANDO_APROVACAO'
    else:
        novo_status = 'PROGRAMADA'  # Reset para testar
    
    sucesso = testar_atualizar_status(session, programacao_id, novo_status)

    if sucesso:
        # 4. Verificar se a mudança foi aplicada
        print("\n🔍 Verificando se a mudança foi aplicada...")
        programacoes_atualizadas = testar_minhas_programacoes(session)
        
        if programacoes_atualizadas:
            prog_atualizada = next((p for p in programacoes_atualizadas if p.get('id') == programacao_id), None)
            if prog_atualizada:
                status_novo = prog_atualizada.get('status')
                if status_novo == novo_status:
                    print(f"✅ Status atualizado corretamente: {status_atual} → {status_novo}")
                else:
                    print(f"⚠️ Status não foi atualizado: esperado {novo_status}, atual {status_novo}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("\n📊 RESUMO:")
    print(f"   ✅ Login: OK")
    print(f"   ✅ Buscar programações: OK ({len(programacoes)} encontradas)")
    print(f"   ✅ Atualizar status: {'OK' if sucesso else 'ERRO'}")

if __name__ == "__main__":
    main()
