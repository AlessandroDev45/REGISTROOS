#!/usr/bin/env python3
"""
TESTE DE INTEGRAÇÃO PROGRAMAÇÃO ↔ OS
===================================

Testa os novos endpoints implementados:
1. GET /api/desenvolvimento/verificar-programacao-os/{os_numero}
2. POST /api/desenvolvimento/finalizar-atividade
3. POST /api/desenvolvimento/finalizar-programacao

"""

import requests
import json
from datetime import datetime

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
        print(f"Resposta: {response.text}")
        return None

def testar_verificar_programacao_os(session, os_numero):
    """Testar verificação de programação por OS"""
    print(f"\n🔍 Testando verificação de programação para OS: {os_numero}")
    
    url = f"{BASE_URL}/api/desenvolvimento/verificar-programacao-os/{os_numero}"
    response = session.get(url)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Resposta recebida:")
        print(f"   Tem programação: {data.get('tem_programacao')}")
        
        if data.get('tem_programacao'):
            print(f"   ID da programação: {data.get('programacao_id')}")
            print(f"   Status: {data.get('status_programacao')}")
            print(f"   Responsável: {data.get('responsavel_nome')}")
            print(f"   OS: {data.get('os_numero')}")
        else:
            print(f"   Mensagem: {data.get('mensagem')}")
        
        return data
    else:
        print(f"❌ Erro: {response.text}")
        return None

def testar_finalizar_atividade(session, programacao_id, apontamento_id=1):
    """Testar finalização de atividade"""
    print(f"\n✅ Testando finalização de atividade...")
    
    url = f"{BASE_URL}/api/desenvolvimento/finalizar-atividade"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "apontamento_id": apontamento_id,
        "programacao_id": programacao_id,
        "descricao_atividade": "Limpeza da peça X concluída"
    }
    
    response = session.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Atividade finalizada com sucesso!")
        print(f"   Mensagem: {result.get('message')}")
        print(f"   Status da programação: {result.get('status_programacao')}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False

def testar_finalizar_programacao(session, programacao_id):
    """Testar finalização de programação completa"""
    print(f"\n🏁 Testando finalização de programação completa...")
    
    url = f"{BASE_URL}/api/desenvolvimento/finalizar-programacao"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "programacao_id": programacao_id,
        "observacoes_finais": "Todas as atividades foram concluídas com sucesso"
    }
    
    response = session.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Programação finalizada com sucesso!")
        print(f"   Mensagem: {result.get('message')}")
        print(f"   Status da programação: {result.get('status_programacao')}")
        return True
    else:
        print(f"❌ Erro: {response.text}")
        return False

def listar_programacoes_existentes(session):
    """Listar programações existentes para teste"""
    print("\n📋 Buscando programações existentes...")
    
    url = f"{BASE_URL}/api/desenvolvimento/minhas-programacoes"
    response = session.get(url)
    
    if response.status_code == 200:
        programacoes = response.json()
        print(f"✅ Encontradas {len(programacoes)} programações")
        
        for i, prog in enumerate(programacoes[:3]):
            print(f"\n📋 Programação {i+1}:")
            print(f"   ID: {prog.get('id')}")
            print(f"   OS: {prog.get('os_numero')}")
            print(f"   Status: {prog.get('status')}")
            print(f"   Cliente: {prog.get('cliente_nome')}")
        
        return programacoes
    else:
        print(f"❌ Erro ao buscar programações: {response.text}")
        return []

def main():
    """Função principal"""
    print("🧪 TESTE DE INTEGRAÇÃO PROGRAMAÇÃO ↔ OS")
    print("=" * 60)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        print("❌ Não foi possível fazer login. Teste abortado.")
        return
    
    # 2. Listar programações existentes
    programacoes = listar_programacoes_existentes(session)
    
    if not programacoes:
        print("\n⚠️ Nenhuma programação encontrada.")
        print("💡 Crie uma programação no PCP primeiro para testar o fluxo completo.")
        
        # Testar com OS fictícia
        print("\n🧪 Testando com OS fictícia...")
        testar_verificar_programacao_os(session, "OS-12345")
        return
    
    # 3. Usar primeira programação para testes
    primeira_programacao = programacoes[0]
    programacao_id = primeira_programacao.get('id')
    os_numero = primeira_programacao.get('os_numero')
    
    print(f"\n🎯 Testando com programação ID {programacao_id} (OS: {os_numero})")
    
    # 4. Testar verificação de programação por OS
    dados_programacao = testar_verificar_programacao_os(session, os_numero)
    
    if not dados_programacao or not dados_programacao.get('tem_programacao'):
        print("⚠️ Programação não foi encontrada pela verificação de OS")
        return
    
    # 5. Testar finalização de atividade
    print("\n" + "="*50)
    print("TESTANDO FINALIZAÇÃO DE ATIVIDADE")
    print("="*50)
    
    sucesso_atividade = testar_finalizar_atividade(session, programacao_id)
    
    # 6. Testar finalização de programação
    print("\n" + "="*50)
    print("TESTANDO FINALIZAÇÃO DE PROGRAMAÇÃO")
    print("="*50)
    
    sucesso_programacao = testar_finalizar_programacao(session, programacao_id)
    
    # 7. Verificar estado final
    if sucesso_programacao:
        print("\n🔍 Verificando estado final da programação...")
        programacoes_finais = listar_programacoes_existentes(session)
        
        prog_atualizada = next((p for p in programacoes_finais if p.get('id') == programacao_id), None)
        if prog_atualizada:
            status_final = prog_atualizada.get('status')
            print(f"✅ Status final da programação: {status_final}")
            
            if status_final == 'AGUARDANDO_APROVACAO':
                print("🎉 FLUXO COMPLETO FUNCIONANDO!")
            else:
                print(f"⚠️ Status inesperado: {status_final}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("\n📊 RESUMO:")
    print(f"   ✅ Login: OK")
    print(f"   ✅ Verificação OS ↔ Programação: OK")
    print(f"   ✅ Finalizar Atividade: {'OK' if sucesso_atividade else 'ERRO'}")
    print(f"   ✅ Finalizar Programação: {'OK' if sucesso_programacao else 'ERRO'}")

if __name__ == "__main__":
    main()
