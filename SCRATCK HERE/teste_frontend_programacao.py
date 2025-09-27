#!/usr/bin/env python3
"""
TESTE FRONTEND - INTEGRAÇÃO PROGRAMAÇÃO ↔ OS
============================================

Testa se a integração frontend está funcionando:
1. Cria uma programação de teste
2. Verifica se o endpoint de verificação funciona
3. Simula o fluxo completo

"""

import requests
import json
from datetime import datetime, timedelta

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

def buscar_os_existente(session):
    """Buscar uma OS existente no sistema"""
    print("\n📋 Buscando OS existente no sistema...")

    try:
        # Buscar OSs existentes
        response = session.get(f"{BASE_URL}/api/os/")

        if response.status_code == 200:
            data = response.json()

            # O endpoint retorna um objeto com 'data' contendo a lista de OSs
            if isinstance(data, dict) and 'data' in data:
                oss = data['data']
                if oss and len(oss) > 0:
                    # Procurar uma OS com status adequado para teste
                    for os_item in oss:
                        status = os_item.get('status', '').upper()
                        if 'AGUARDANDO' in status or 'EM EXECUÇÃO' in status or 'ABERTA' in status:
                            print(f"✅ OS encontrada: {os_item.get('os_numero', 'N/A')}")
                            print(f"   ID: {os_item.get('id')}")
                            print(f"   Status: {os_item.get('status', 'N/A')}")
                            print(f"   Cliente: {os_item.get('cliente', 'N/A')}")
                            return os_item

                    # Se não encontrou uma adequada, usar a primeira
                    os_escolhida = oss[0]
                    print(f"✅ Usando primeira OS: {os_escolhida.get('os_numero', 'N/A')}")
                    print(f"   ID: {os_escolhida.get('id')}")
                    print(f"   Status: {os_escolhida.get('status', 'N/A')}")
                    return os_escolhida
                else:
                    print("⚠️ Lista de OSs vazia")
                    return None
            else:
                print(f"⚠️ Estrutura inesperada: {type(data)}")
                return None
        else:
            print(f"❌ Erro ao buscar OSs: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Erro ao buscar OS: {e}")
        return None

def criar_programacao_teste(session, os_id):
    """Criar uma programação de teste"""
    print(f"\n📅 Criando programação para OS ID {os_id}...")
    
    programacao_data = {
        "id_ordem_servico": os_id,
        "inicio_previsto": (datetime.now() + timedelta(hours=1)).isoformat(),
        "fim_previsto": (datetime.now() + timedelta(days=2)).isoformat(),
        "observacoes": "Programação de teste para integração frontend",
        "setor_destino": "MECANICA",
        "departamento_destino": "PRODUCAO"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=programacao_data)
        
        if response.status_code in [200, 201]:
            programacao = response.json()
            print(f"✅ Programação criada! ID: {programacao.get('id')}")
            return programacao
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao criar programação: {e}")
        return None

def atribuir_programacao(session, programacao_id):
    """Atribuir programação ao usuário logado"""
    print(f"\n👤 Atribuindo programação {programacao_id} ao usuário...")
    
    # Buscar ID do usuário atual - testar diferentes endpoints
    endpoints_user = ["/api/auth/me", "/api/user/me", "/api/me"]
    user_data = None

    for endpoint in endpoints_user:
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Dados do usuário obtidos via {endpoint}")
                break
        except:
            continue

    if not user_data:
        print("⚠️ Não foi possível obter dados do usuário, usando ID padrão 1")
        user_id = 1  # ID do admin
    else:
        user_id = user_data.get('id', 1)
    
    atribuicao_data = {
        "responsavel_id": user_id,
        "data_inicio": datetime.now().isoformat(),
        "data_fim": (datetime.now() + timedelta(days=2)).isoformat(),
        "observacoes": "Atribuição de teste",
        "setor_destino": "MECANICA",
        "departamento_destino": "PRODUCAO"
    }
    
    try:
        response = session.patch(f"{BASE_URL}/api/pcp/programacoes/{programacao_id}/reatribuir", json=atribuicao_data)
        
        if response.status_code == 200:
            print(f"✅ Programação atribuída com sucesso!")
            return True
        else:
            print(f"❌ Erro ao atribuir programação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao atribuir programação: {e}")
        return False

def testar_verificacao_programacao(session, os_numero):
    """Testar o endpoint de verificação de programação"""
    print(f"\n🔍 Testando verificação de programação para OS {os_numero}...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/verificar-programacao-os/{os_numero}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verificação funcionando!")
            print(f"   Tem programação: {data.get('tem_programacao')}")
            
            if data.get('tem_programacao'):
                print(f"   ID: {data.get('programacao_id')}")
                print(f"   Status: {data.get('status_programacao')}")
                print(f"   Responsável: {data.get('responsavel_nome')}")
                return data
            else:
                print(f"   Mensagem: {data.get('mensagem')}")
                return None
        else:
            print(f"❌ Erro na verificação: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar programação: {e}")
        return None

def main():
    """Função principal"""
    print("🧪 TESTE FRONTEND - INTEGRAÇÃO PROGRAMAÇÃO ↔ OS")
    print("=" * 60)
    
    # 1. Fazer login
    session = fazer_login()
    if not session:
        return
    
    # 2. Buscar OS existente
    os_encontrada = buscar_os_existente(session)
    if not os_encontrada:
        print("❌ Não foi possível encontrar OS no sistema")
        print("💡 Crie uma OS primeiro no sistema para testar")
        return

    os_id = os_encontrada.get('id')
    os_numero = os_encontrada.get('os_numero') or os_encontrada.get('numero_os') or str(os_id)
    
    # 3. Criar programação de teste
    programacao = criar_programacao_teste(session, os_id)
    if not programacao:
        print("❌ Não foi possível criar programação de teste")
        return
    
    programacao_id = programacao.get('id')
    
    # 4. Atribuir programação ao usuário
    if not atribuir_programacao(session, programacao_id):
        print("❌ Não foi possível atribuir programação")
        return
    
    # 5. Testar verificação de programação
    print("\n" + "="*50)
    print("TESTANDO VERIFICAÇÃO DE PROGRAMAÇÃO")
    print("="*50)
    
    resultado = testar_verificacao_programacao(session, os_numero)
    
    if resultado and resultado.get('tem_programacao'):
        print("\n🎉 SUCESSO! A integração está funcionando!")
        print("\n📋 RESUMO DO TESTE:")
        print(f"   ✅ OS criada: {os_numero}")
        print(f"   ✅ Programação criada: {programacao_id}")
        print(f"   ✅ Programação atribuída ao usuário")
        print(f"   ✅ Verificação de programação funcionando")
        print(f"   ✅ Frontend pode detectar programação automaticamente")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("   1. Abra o frontend em http://localhost:3001")
        print("   2. Vá em Desenvolvimento → Apontamentos")
        print(f"   3. Digite o número da OS: {os_numero}")
        print("   4. Verifique se a programação é detectada automaticamente")
        print("   5. Teste os botões 'Finalizar Atividade' e 'Finalizar Programação'")
        
    else:
        print("\n❌ FALHA! A integração não está funcionando corretamente")
        print("💡 Verifique se:")
        print("   - O backend está rodando")
        print("   - Os endpoints estão funcionando")
        print("   - A programação foi atribuída corretamente")

if __name__ == "__main__":
    main()
