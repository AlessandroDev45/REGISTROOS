#!/usr/bin/env python3
"""
TESTAR DUPLICAÇÃO CORRIGIDA
===========================

Testar se a duplicação de programações foi corrigida.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

# Usuários reais
ADMIN_USER = {"username": "admin@registroos.com", "password": "123456"}
SUPERVISOR_USER = {"username": "supervisor.mecanica_dia@registroos.com", "password": "123456"}
USER_MECANICA = {"username": "user.mecanica_dia@registroos.com", "password": "123456"}

def fazer_login(usuario, nome_usuario):
    """Fazer login e obter sessão"""
    print(f"🔐 Fazendo login como {nome_usuario}...")
    
    session = requests.Session()
    headers = {"Content-Type": "application/json"}
    
    response = session.post(LOGIN_URL, json=usuario, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        user_info = data.get('user', {})
        print(f"✅ Login realizado! {user_info.get('nome_completo', 'N/A')} (ID: {user_info.get('id', 'N/A')})")
        return session, user_info
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None, None

def criar_programacao_pcp(session):
    """1. PCP cria programação"""
    print(f"\n📋 PASSO 1: PCP criando programação...")
    
    agora = datetime.now()
    inicio = agora + timedelta(hours=2)
    fim = agora + timedelta(hours=10)
    
    dados_programacao = {
        "id_ordem_servico": 1,
        "inicio_previsto": inicio.isoformat(),
        "fim_previsto": fim.isoformat(),
        "observacoes": "Teste de correção de duplicação",
        "id_setor": None,
        "prioridade": "ALTA"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes", json=dados_programacao)
        
        if response.status_code == 200:
            data = response.json()
            prog_id = data.get('id')
            print(f"✅ Programação criada pelo PCP! ID: {prog_id}")
            return prog_id
        else:
            print(f"❌ Erro ao criar programação: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def atribuir_programacao_supervisor(session, prog_id):
    """2. Supervisor atribui programação"""
    print(f"\n👥 PASSO 2: Supervisor atribuindo programação {prog_id}...")
    
    dados_atribuicao = {
        "responsavel_id": 8,
        "setor_destino": "MECANICA DIA",
        "departamento_destino": "MOTORES",
        "data_inicio": (datetime.now() + timedelta(hours=1)).isoformat(),
        "data_fim": (datetime.now() + timedelta(hours=9)).isoformat(),
        "observacoes": "Teste de atribuição sem duplicação"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/pcp/programacoes/atribuir", json=dados_atribuicao)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Programação atribuída! ID retornado: {data.get('id')}")
            return data.get('id')
        else:
            print(f"❌ Erro ao atribuir programação: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def verificar_dashboard_usuario(session):
    """3. Verificar dashboard do usuário"""
    print(f"\n📊 PASSO 3: Verificando dashboard do usuário...")
    
    try:
        response = session.get(f"{BASE_URL}/api/desenvolvimento/minhas-programacoes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Dashboard retornou {len(data)} programações")
            
            for i, prog in enumerate(data):
                print(f"   {i+1}. ID: {prog.get('id')} - OS: {prog.get('os_numero')} - Responsável: {prog.get('responsavel_nome')}")
            
            return data
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return []

def main():
    """Função principal"""
    print("🔧 TESTAR DUPLICAÇÃO CORRIGIDA")
    print("=" * 35)
    
    # 1. PCP cria programação
    session_admin, admin_info = fazer_login(ADMIN_USER, "ADMIN/PCP")
    if not session_admin:
        return
    
    prog_id_criado = criar_programacao_pcp(session_admin)
    if not prog_id_criado:
        return
    
    # 2. Supervisor atribui programação
    session_supervisor, supervisor_info = fazer_login(SUPERVISOR_USER, "SUPERVISOR")
    if not session_supervisor:
        return
    
    prog_id_atribuido = atribuir_programacao_supervisor(session_supervisor, prog_id_criado)
    
    # 3. Usuário verifica dashboard
    session_user, user_info = fazer_login(USER_MECANICA, "USUÁRIO")
    if not session_user:
        return
    
    programacoes_dashboard = verificar_dashboard_usuario(session_user)
    
    # 4. Análise dos resultados
    print(f"\n📊 ANÁLISE DOS RESULTADOS:")
    print(f"   Programação criada pelo PCP: ID {prog_id_criado}")
    print(f"   Programação retornada na atribuição: ID {prog_id_atribuido}")
    
    if prog_id_criado == prog_id_atribuido:
        print(f"✅ SUCESSO: Mesma programação foi atualizada (sem duplicação)")
    else:
        print(f"❌ PROBLEMA: Programações diferentes (duplicação ainda ocorre)")
        print(f"   - PCP criou: {prog_id_criado}")
        print(f"   - Atribuição retornou: {prog_id_atribuido}")
    
    print(f"\n📋 Total de programações no dashboard: {len(programacoes_dashboard)}")

if __name__ == "__main__":
    main()
